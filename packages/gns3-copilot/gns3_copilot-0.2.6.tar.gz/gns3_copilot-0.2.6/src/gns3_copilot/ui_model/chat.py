# mypy: ignore-errors
"""
GNS3 Copilot - AI-Powered Network Engineering Assistant

This module implements the main Streamlit web application for GNS3 Copilot,
an AI-powered assistant designed to help network engineers with GNS3-related
tasks through a conversational chat interface.

Features:
- Real-time chat interface with streaming responses
- Integration with LangChain agents for intelligent conversation
- Tool calling support for GNS3 network operations
- Message history and session state management
- Support for multiple message types (Human, AI, Tool messages)
- Interactive tool call and response visualization

The application leverages:
- Streamlit for the web UI
- LangGraph for AI agent functionality
- Custom GNS3 integration tools
- Session-based conversation tracking with unique thread IDs

Usage:
Run this module directly to start the GNS3 Copilot web interface:
    streamlit run app.py

Note: Requires proper configuration of GNS3 server and API credentials.
"""

import json
import uuid
from time import sleep
from typing import Any

import streamlit as st
from langchain.messages import AIMessage, HumanMessage, ToolMessage

from gns3_copilot.agent import agent
from gns3_copilot.gns3_client import (
    GNS3ProjectCreate,
    GNS3ProjectList,
    GNS3ProjectOpen,
)
from gns3_copilot.log_config import setup_logger
from gns3_copilot.public_model import (
    format_tool_response,
    get_duration,
    speech_to_text,
    text_to_speech_wav,
)

logger = setup_logger("chat")

# Initialize session state for thread ID
if "thread_id" not in st.session_state:
    # If thread_id is not in session_state, create and save a new one
    st.session_state["thread_id"] = str(uuid.uuid4())

# Initialize iframe URL mode (project page vs login page)
if "gns3_url_mode" not in st.session_state:
    st.session_state.gns3_url_mode = "project"

# Initialize iframe visibility state
# Used to show/hide GNS3 topology interface
if "show_iframe" not in st.session_state:
    st.session_state.show_iframe = False

# Initialize temp_selected_project for new sessions
if "temp_selected_project" not in st.session_state:
    st.session_state["temp_selected_project"] = None

current_thread_id = st.session_state["thread_id"]

# Get selected thread ID and title from session state (set by sidebar)
selected_thread_id = st.session_state.get("selected_thread_id")
title = st.session_state.get("session_title")


# Unique thread ID for each session
# If a session is selected, continue the conversation using its thread ID;
# otherwise, initialize a new thread ID.
if selected_thread_id:
    config = {
        "configurable": {
            "thread_id": st.session_state["current_thread_id"],
            "max_iterations": 50,
        },
        "recursion_limit": 28,
    }
else:
    config = {
        "configurable": {"thread_id": current_thread_id, "max_iterations": 50},
        "recursion_limit": 28,
    }

# --- Get current state ---
if selected_thread_id:
    # Historical session: get from agent state
    snapshot = agent.get_state(config)
    selected_p = snapshot.values.get("selected_project")
else:
    # New session: get from temp storage
    selected_p = st.session_state.get("temp_selected_project")

# --- Logic branch: If no project is selected, display project cards ---
if not selected_p:
    st.markdown(
        """
        <h3 style='text-align: left; font-size: 22px; font-weight: bold; margin-top: 20px;'>GNS3 Copilot - Workspace Selection</h3>
        """,
        unsafe_allow_html=True,
    )
    st.info(
        "Please select a project to enter the conversation context. Closed projects can be opened directly.",
        width=800,
    )

    # Create New Project expander
    with st.expander("Create New Project", expanded=False, width=800):
        new_name = st.text_input("Project Name", placeholder="Enter project name...")

        # Advanced options
        with st.expander("Advanced Options", expanded=False):
            auto_start = st.checkbox("Auto start project", value=False)
            auto_close = st.checkbox("Auto close on disconnect", value=False)
            auto_open = st.checkbox("Auto open on GNS3 start", value=False)
            col_width, col_height = st.columns(2)
            with col_width:
                scene_width = st.number_input(
                    "Scene Width", value=2000, min_value=500, max_value=5000
                )
            with col_height:
                scene_height = st.number_input(
                    "Scene Height", value=1000, min_value=500, max_value=5000
                )

        col_create, col_cancel = st.columns(2)
        with col_create:
            if st.button("Create", type="primary", key="btn_create_project"):
                if new_name and new_name.strip():
                    # Build project parameters
                    params = {"name": new_name.strip()}
                    if auto_start:
                        params["auto_start"] = True
                    if auto_close:
                        params["auto_close"] = True
                    if auto_open:
                        params["auto_open"] = True
                    params["scene_width"] = scene_width
                    params["scene_height"] = scene_height

                    # Call GNS3ProjectCreate tool
                    create_tool = GNS3ProjectCreate()
                    result = create_tool._run(params)

                    if result.get("success"):
                        st.success(f"Project '{new_name}' created successfully!")
                        sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Failed to create project: {result.get('error')}")
                else:
                    st.warning("Please enter a project name.")
        with col_cancel:
            if st.button("Clear", key="btn_clear_project"):
                st.rerun()

    # Get project list
    projects = GNS3ProjectList()._run().get("projects", [])
    if projects:
        cols = st.columns([1, 1], width=800)
        for i, p in enumerate(projects):
            # Destructure project tuple for clarity: name, ID, device count, link count, status
            name, p_id, dev_count, link_count, status = p
            # Check status
            is_opened = status.lower() == "opened"
            with cols[i % 2]:
                # If closed status, use container with background color or different title format
                with st.container(border=True, width=400):
                    # Add status icon to title
                    status_icon = "🟢" if is_opened else "⚪"
                    st.markdown(f"###### {status_icon} {name}")
                    st.caption(f"ID: {p_id[:8]}")
                    # Display device and link information
                    st.write(f"{dev_count} Devices | {link_count} Links")
                    # Dynamic status text display
                    if is_opened:
                        st.success(f"Status: {status.upper()}")
                    else:
                        st.warning(f"Status: {status.upper()} (Unavailable)")
                    # --- Button logic ---
                    # Show different buttons based on project status
                    if is_opened:
                        # Opened project: show Select Project and Close Project buttons
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button(
                                "Select Project",
                                key=f"btn_select_{p_id}",
                                use_container_width=True,
                                type="primary",
                            ):
                                if selected_thread_id:
                                    # Historical session: update agent state
                                    agent.update_state(config, {"selected_project": p})
                                else:
                                    # New session: store in temp storage
                                    st.session_state["temp_selected_project"] = p
                                st.success(f"Project {name} has been selected!")
                                st.rerun()
                        with col_btn2:
                            if st.button(
                                "Close Project",
                                key=f"btn_close_{p_id}",
                                use_container_width=True,
                                type="secondary",
                            ):
                                close_tool = GNS3ProjectOpen()
                                result = close_tool._run(
                                    {"project_id": p_id, "close": True}
                                )

                                if result.get("success"):
                                    st.success(f"Project {name} closed successfully!")
                                    # Wait a moment and refresh to update project status
                                    sleep(1)
                                    st.rerun()
                                else:
                                    st.error(
                                        f"Failed to close project {name}: {result.get('error', 'Unknown error')}"
                                    )
                    else:
                        # Closed project: show Open Project button
                        if st.button(
                            "Open Project",
                            key=f"btn_open_{p_id}",
                            use_container_width=True,
                            type="secondary",
                        ):
                            open_tool = GNS3ProjectOpen()
                            result = open_tool._run({"project_id": p_id, "open": True})
                            if result.get("success"):
                                st.success(f"Project {name} opened successfully!")
                                # Wait a moment and refresh to update project status
                                sleep(1)
                                st.rerun()
                            else:
                                st.error(
                                    f"Failed to open project {name}: {result.get('error', 'Unknown error')}"
                                )
    else:
        st.error("No projects found in GNS3.")
        if st.button("Refresh List"):
            st.rerun()
else:
    # Top status bar logic
    st.sidebar.success(f"Current Project: **{selected_p[0]}**")
    if st.sidebar.button("Switch Project / Exit"):
        if selected_thread_id:
            # Historical session: update agent state
            agent.update_state(config, {"selected_project": None})
        else:
            # New session: clear temp storage
            st.session_state["temp_selected_project"] = None
        # Clear chat history from session state
        st.session_state["state_history"] = None
        st.rerun()

# --- Main workspace (only visible when a project is selected) ---
if selected_p:
    st.markdown(
        """
        <h3 style='text-align: left; font-size: 22px; font-weight: bold; margin-top: 20px;'>Workspace</h3>
        """,
        unsafe_allow_html=True,
    )

    # Dynamic column layout based on iframe visibility
    if st.session_state.show_iframe:
        layout_col1, layout_col2 = st.columns([3, 7], gap="medium")
    else:
        layout_col1 = st.container()

    with layout_col1:
        history_container = st.container(
            height=st.session_state.CONTAINER_HEIGHT,
            border=False,
        )
        with history_container:
            # StateSnapshot state example test/langgraph_checkpoint.json file
            # Display previous messages from state history
            if st.session_state.get("state_history") is not None:
                # StateSnapshot values dictionary
                values_dict = st.session_state["state_history"].values
                message_to_render = values_dict.get("messages", [])

                # Track current open assistant message block
                current_assistant_block = None

                # StateSnapshot values messages list
                for message_object in message_to_render:
                    # Handle different message types
                    if isinstance(message_object, HumanMessage):
                        # Close any open assistant chat message block before starting a new user message
                        if current_assistant_block is not None:
                            current_assistant_block.__exit__(None, None, None)
                            current_assistant_block = None
                        # UserMessage
                        with st.chat_message("user"):
                            st.markdown(message_object.content)

                    elif isinstance(message_object, (AIMessage, ToolMessage)):
                        # Open a new assistant chat message block if none is open
                        if current_assistant_block is None:
                            current_assistant_block = st.chat_message("assistant")
                            current_assistant_block.__enter__()

                        # Handle AIMessage with tool_calls
                        if isinstance(message_object, AIMessage):
                            # AIMessage content
                            # adapted for gemini
                            # Check if content is a list and safely extract the first text element
                            if (
                                isinstance(message_object.content, list)
                                and message_object.content
                                and "text" in message_object.content[0]
                            ):
                                st.markdown(message_object.content[0]["text"])
                            # Plain string content
                            elif isinstance(message_object.content, str):
                                st.markdown(message_object.content)
                            # AIMessage tool_calls
                            if (
                                isinstance(message_object.tool_calls, list)
                                and message_object.tool_calls
                            ):
                                for tool in message_object.tool_calls:
                                    tool_id = tool.get("id", "UNKNOWN_ID")
                                    tool_name = tool.get("name", "UNKNOWN_TOOL")
                                    tool_args = tool.get("args", {})
                                    # Display tool call details
                                    with st.expander(
                                        f"**Tool Call:** `{tool_name}`",
                                        expanded=False,
                                    ):
                                        st.json(
                                            {
                                                "name": tool_name,
                                                "id": tool_id,
                                                "args": tool_args,
                                                "type": "tool_call",
                                            },
                                            expanded=True,
                                        )
                        # Handle ToolMessage
                        if isinstance(message_object, ToolMessage):
                            content_pretty = format_tool_response(
                                message_object.content
                            )
                            with st.expander(
                                "**Tool Response**",
                                expanded=False,
                            ):
                                st.json(json.loads(content_pretty), expanded=2)

                # Close any remaining open assistant chat message block
                if current_assistant_block is not None:
                    current_assistant_block.__exit__(None, None, None)

    # Only render layout_col2 content when show_iframe is True
    if st.session_state.show_iframe:
        with layout_col2:
            # Extract project_id from the selected project
            project_id = selected_p[
                1
            ]  # selected_p is a tuple: (name, p_id, dev_count, link_count, status)
            # Get GNS3 server URL from session_state (loaded from .env file)
            gns3_server_url = st.session_state.get(
                "GNS3_SERVER_URL", "http://127.0.0.1:3080/"
            )

            # Get API version and construct appropriate iframe URL
            api_version = st.session_state.get("API_VERSION", "2")
            if api_version == "3":
                if st.session_state.gns3_url_mode == "login":
                    # API v3 login page
                    iframe_url = f"{gns3_server_url}"
                else:
                    # API v3 uses 'controller' instead of 'server'
                    iframe_url = f"{gns3_server_url}/static/web-ui/controller/1/project/{project_id}"
            else:
                # API v2 uses 'server' (default behavior)
                iframe_url = (
                    f"{gns3_server_url}/static/web-ui/server/1/project/{project_id}"
                )

            iframe_container = st.container(
                height=st.session_state.CONTAINER_HEIGHT,
                # horizontal_alignment="center",
                vertical_alignment="center",
                border=False,
            )
            with iframe_container:
                # Set zoom scale (0.7 = 70%, 0.8 = 80%, 0.9 = 90%)
                zoom_scale = (
                    st.session_state.zoom_scale_topology
                )  # Scale to 80%, you can adjust between 0.7-0.9

                iframe_width = 2000
                iframe_height = 1000

                iframe_html = f"""
                <style>
                    .iframe-scroll-container {{
                        width: 100%;
                        height: {st.session_state.CONTAINER_HEIGHT};  /* Can be adjusted as needed, or use 70vh */
                        overflow: auto;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        background: #f9f9f9;
                    }}

                    .iframe-scroll-container iframe {{
                        width: {iframe_width}px;
                        height: {iframe_height}px;
                        border: none;
                        display: block;
                        /* Use zoom instead of transform to keep coordinate system correct */
                        zoom: {zoom_scale};
                        /* Or use this alternative syntax */
                        /* zoom: 80%; */
                    }}
                </style>

                <div class="iframe-scroll-container">
                    <iframe
                        src="{iframe_url}"
                        loading="lazy"
                        allowfullscreen
                        title="Embedded Content"
                    ></iframe>
                </div>
                """

                st.markdown(iframe_html, unsafe_allow_html=True)

    # st.divider()
    # --- Chat Input Area ---
    if st.session_state.show_iframe:
        # When Show Topology: there are two buttons on the right, needs to be wider
        # Left column is narrow, middle column is moderate, right column is wider
        col_ratio = [0.2, 0.6, 0.4]
    else:
        # When Hide Topology: there is only one button on the right
        # Left column is narrow, middle column is wide, right column is moderate
        col_ratio = [0.2, 0.7, 0.3]

    chat_input_left, chat_input_center, chat_input_right = st.columns(col_ratio)

    with chat_input_center:
        # Configure chat_input based on switch
        # Get voice enabled setting from session_state (loaded from .env file)
        voice_enabled = st.session_state.get("VOICE", False)
        if voice_enabled:
            prompt = st.chat_input(
                "Say or record something...",
                accept_audio=True,
                audio_sample_rate=24000,
                # width=600,
            )
        else:
            # When voice is disabled, do not enable accept_audio attribute
            prompt = st.chat_input(
                "Type your message here...",
                # width=600
            )
        # Handle input
        if prompt:
            user_text = ""
            if voice_enabled:
                # Mode A: prompt is an object (containing .text and .audio)
                if prompt.audio:
                    user_text = speech_to_text(prompt.audio)
                # If voice is not converted to text, or user directly types
                if not user_text:
                    user_text = prompt.text
            else:
                # Mode B: prompt is directly a string
                user_text = prompt
            # 3. Final check and run
            if not user_text or user_text.strip() == "":
                st.stop()

            with history_container:
                # Display user message in chat message container
                with st.chat_message("user"):
                    st.markdown(user_text)

            # Migrate temp selected project to agent state for new sessions
            if not selected_thread_id and st.session_state.get("temp_selected_project"):
                temp_project = st.session_state["temp_selected_project"]
                agent.update_state(config, {"selected_project": temp_project})
                # Don't clear temp_selected_project immediately
                # It will be cleared after rerun when selected_p is retrieved from agent state

            with history_container:
                # Display assistant response in chat message container
                with st.chat_message("assistant"):
                    active_text_placeholder = st.empty()
                    current_text_chunk = ""
                    # Core aggregation state: only stores currently streaming tool information
                    # Structure: {'id': str, 'name': str, 'args_string': str} or None
                    current_tool_state = None
                    # TTS local switch for message control
                    tts_played = False
                    # Initialize audio_bytes variable
                    audio_bytes = None
                    # Stream the agent response
                    for chunk in agent.stream(
                        {
                            "messages": [HumanMessage(content=user_text)],
                        },
                        config=config,
                        stream_mode="messages",
                    ):
                        for msg in chunk:
                            # with open('log.txt', "a", encoding='utf-8') as f:
                            #    f.write(f"{msg}\n\n")
                            if isinstance(msg, AIMessage):
                                # adapted for gemini
                                # Check if content is a list and safely extract the first text element
                                if (
                                    isinstance(msg.content, list)
                                    and msg.content
                                    and "text" in msg.content[0]
                                ):
                                    actual_text = msg.content[0]["text"]
                                    # Now actual_text is the clean text you need
                                    current_text_chunk += actual_text
                                    active_text_placeholder.markdown(
                                        current_text_chunk, unsafe_allow_html=True
                                    )
                                elif isinstance(msg.content, str):
                                    current_text_chunk += str(msg.content)
                                    active_text_placeholder.markdown(
                                        current_text_chunk, unsafe_allow_html=True
                                    )
                                # Determine if text message (i.e., msg.content) reception is complete
                                is_text_ending = (
                                    # Case 1: Tool call starts
                                    msg.tool_calls
                                    or
                                    # Case 2: End metadata received
                                    msg.response_metadata.get("finish_reason")
                                    in ["tool_calls", "stop"]
                                )
                                if (
                                    is_text_ending
                                    and not tts_played
                                    and current_text_chunk.strip()
                                    and voice_enabled
                                ):
                                    # Play once in a round of AIMessage/ToolMessage
                                    tts_played = True
                                    # Text_to_speech
                                    try:
                                        with st.spinner("Generating voice..."):
                                            audio_bytes = text_to_speech_wav(
                                                current_text_chunk
                                            )
                                            st.audio(
                                                audio_bytes,
                                                format="audio/mp3",
                                                autoplay=True,
                                            )
                                    except Exception as e:
                                        logger.error("TTS Error: %", e)
                                        st.error(f"TTS Error: {e}")
                                # Get metadata (ID and name) from tool_calls
                                if msg.tool_calls:
                                    for tool in msg.tool_calls:
                                        tool_id = tool.get("id")
                                        # Only when ID is not empty, consider it as the start of a new tool call
                                        if tool_id:
                                            # Initialize current tool state (this is the only time to get ID)
                                            # Note: only one tool can be called at a time
                                            current_tool_state = {
                                                "id": tool_id,
                                                "name": tool.get(
                                                    "name", "UNKNOWN_TOOL"
                                                ),
                                                "args_string": "",
                                            }
                                # Concatenate parameter strings from tool_call_chunk
                                if (
                                    hasattr(msg, "tool_call_chunks")
                                    and msg.tool_call_chunks
                                ):
                                    if current_tool_state:
                                        tool_data = current_tool_state
                                        for chunk_update in msg.tool_call_chunks:
                                            args_chunk = chunk_update.get("args", "")
                                            # Core: string concatenation
                                            if isinstance(args_chunk, str):
                                                tool_data["args_string"] += args_chunk
                                # Determine if the tool_calls_chunks output is complete and
                                # display the st.expander() for tool_calls
                                if msg.response_metadata.get(
                                    "finish_reason"
                                ) == "tool_calls" or (
                                    msg.response_metadata.get("finish_reason") == "STOP"
                                    and current_tool_state is not None
                                ):
                                    tool_data = current_tool_state
                                    # Parse complete parameter string
                                    parsed_args: dict[str, Any] = {}
                                    try:
                                        parsed_args = json.loads(
                                            tool_data["args_string"]
                                        )
                                    except json.JSONDecodeError:
                                        parsed_args = {
                                            "error": "JSON parse failed after stream complete."
                                        }
                                    # Serialize the tool_input value in parsed_args to a JSON array
                                    # for expansion when using st.json
                                    try:
                                        command_list = json.loads(
                                            parsed_args["tool_input"]
                                        )
                                        parsed_args["tool_input"] = command_list
                                    except (json.JSONDecodeError, KeyError, TypeError):
                                        pass
                                    # Build the final display structure that meets your requirements
                                    display_tool_call = {
                                        "name": tool_data["name"],
                                        "id": tool_data["id"],
                                        # Inject tool_input structure
                                        "args": parsed_args,
                                        "type": tool_data.get(
                                            "type", "tool_call"
                                        ),  # Maintain completeness
                                    }
                                    # Update Call Expander, display final parameters (collapsed)
                                    with st.expander(
                                        f"**Tool Call:** `{tool_data['name']}`",
                                        expanded=False,
                                    ):
                                        # Use the final complete structure
                                        st.json(display_tool_call, expanded=False)
                            if isinstance(msg, ToolMessage):
                                # Wait for audio playback to complete before returning ToolMessage to LLM
                                if voice_enabled and audio_bytes:
                                    sleep(get_duration(audio_bytes))
                                # Clear state after completion, ready to receive next tool call
                                current_tool_state = None
                                content_pretty = format_tool_response(msg.content)
                                with st.expander(
                                    "**Tool Response**",
                                    expanded=False,
                                ):
                                    st.json(json.loads(content_pretty), expanded=False)
                                active_text_placeholder = st.empty()
                                current_text_chunk = ""
                                # After a round of AIMessage/ToolMessage, reset tts_played switch, next round of AIMessage/ToolMessage can generate TTS again
                                tts_played = False
                # After the interaction, update the session state with the latest StateSnapshot
                state_history = agent.get_state(config)
                # Avoid updating if state_history is empty
                if not state_history[0]:
                    pass
                else:
                    # Update session state
                    st.session_state["state_history"] = state_history
                    # print(state_history)
                # with open('state_history.txt', "a", encoding='utf-8') as f:
                #    f.write(f"{state_history}\n\n")

    with chat_input_right:
        # Create two sub-columns in the right column, arrange buttons left and right
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button(
                "Hide" if st.session_state.show_iframe else "Show",
                icon=":material/visibility:"
                if not st.session_state.show_iframe
                else ":material/visibility_off:",
                help="Show or hide the GNS3 project topology iframe",
            ):
                st.session_state.show_iframe = not st.session_state.show_iframe
                st.rerun()

        with btn_col2:
            if st.session_state.show_iframe:
                if st.button(
                    "Login"
                    if st.session_state.gns3_url_mode == "project"
                    else "Topology",
                    icon=":material/login:"
                    if st.session_state.gns3_url_mode == "project"
                    else ":material/device_hub:",
                    help="If the page is not displayed, please click me. Need to perform GNS3 web login once.",
                ):
                    st.session_state.gns3_url_mode = (
                        "login"
                        if st.session_state.gns3_url_mode == "project"
                        else "project"
                    )
                    st.rerun()

    with chat_input_left:
        st.empty()
