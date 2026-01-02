"""
Sidebar component for GNS3 Copilot application.

This module provides reusable sidebar UI components for the GNS3 Copilot
Streamlit application, including page configuration controls and session
management. The sidebar is rendered centrally in app.py and provides
consistent functionality across all pages.

Features:
    - Page height adjustment slider (global)
    - Zoom scale adjustment slider (global)
    - Session history management (global)
    - About section (global)

Usage:
    The sidebar is rendered in app.py before page navigation:

        from gns3_copilot.ui_model.sidebar import render_sidebar, render_sidebar_about

        # Render sidebar with current page information
        selected_thread_id, title = render_sidebar(current_page="ui_model/chat.py")

        # Store results in session_state for use by other pages
        st.session_state["selected_thread_id"] = selected_thread_id
        st.session_state["session_title"] = title

        # Render about section after navigation
        render_sidebar_about()

Notes:
    - Configuration changes (height, zoom) are persisted to .env file
    - Thread IDs are managed through LangGraph checkpointer

See Also:
    - src/gns3_copilot/app.py: Main application entry point
    - src/gns3_copilot/agent: LangGraph agent and checkpointer
    - src/gns3_copilot/ui_model/chat: Chat page that uses sidebar state
"""

from typing import Any

import streamlit as st

from gns3_copilot.agent import agent, langgraph_checkpointer, list_thread_ids
from gns3_copilot.log_config import setup_logger
from gns3_copilot.ui_model.utils import new_session, save_config_to_env

logger = setup_logger("chat")


def render_sidebar(
    current_page: str,
) -> tuple[Any | None, str | None]:
    """
    Render the global sidebar for all pages.

    This function renders sidebar controls including:
    - Page height adjustment
    - Zoom scale adjustment
    - Session history management

    Args:
        current_page: The current active page path

    Returns:
        Tuple of (selected_thread_id, title) - can be None if no session is selected
    """
    with st.sidebar:
        # Initialize sidebar configuration values
        # Get current container height from session state or default to 1200
        current_height = st.session_state.get("CONTAINER_HEIGHT")
        if current_height is None or not isinstance(current_height, int):
            current_height = 1200

        # Get current zoom scale from session state
        current_zoom = st.session_state.get("zoom_scale_topology")
        if current_zoom is None:
            current_zoom = 0.8

        # Note: We don't use key parameter here to avoid automatic session_state management
        new_height = st.slider(
            "Page Height (px)",
            min_value=300,
            max_value=1500,
            value=current_height,
            step=50,
            help="Adjust the height for chat and GNS3 view",
        )

        # If the height changed, update session state and save to .env file
        if new_height != current_height:
            st.session_state["CONTAINER_HEIGHT"] = new_height
            # Save to .env file using the centralized save function
            try:
                save_config_to_env()
            except Exception as e:
                logger.error("Failed to update CONTAINER_HEIGHT: %s", e)

        new_zoom = st.slider(
            "Zoom Scale",
            min_value=0.5,
            max_value=1.0,
            value=current_zoom,
            step=0.05,
            help="Adjust the zoom scale for GNS3 topology view",
        )

        # If the zoom changed, update session state and save to .env file
        if new_zoom != current_zoom:
            st.session_state["zoom_scale_topology"] = new_zoom
            try:
                save_config_to_env()
            except Exception as e:
                logger.error("Failed to update ZOOM_SCALE_TOPOLOGY: %s", e)

        st.markdown("---")

        # Session management - render for all pages
        selected_thread_id = None
        title = None

        try:
            selected_thread_id, title = _render_session_management()
        except Exception as e:
            logger.error("Failed to render session management: %s", e)
            st.error("Failed to load session history. Please check the logs.")

        return selected_thread_id, title


def _render_session_management() -> tuple[Any | None, str | None]:
    """
    Render session history and management controls.

    Returns:
        Tuple of (selected_thread_id, title)
    """
    thread_ids = list_thread_ids(langgraph_checkpointer)

    # Display name/value are title and id
    # The first option is an empty/placeholder selection
    session_options: list[tuple[str, str | None]] = [("(Please select session)", None)]

    for tid in thread_ids:
        ckpt = langgraph_checkpointer.get({"configurable": {"thread_id": tid}})
        title_value = (
            ckpt.get("channel_values", {}).get("conversation_title") if ckpt else None
        ) or "New Session"
        # Same title name caused the issue where selecting conversations always selected the same thread id.
        # Use part of thread_id to avoid same title name
        unique_title = f"{title_value} ({tid[:6]})"
        session_options.append((unique_title, tid))

    logger.debug("session_options : %s", session_options)

    selected = st.selectbox(
        "Session History",
        options=session_options,
        format_func=lambda x: x[0],  # view conversation_title
        key="session_select",  # new key for state management
    )

    title, selected_thread_id = selected

    logger.debug("selectbox selected : %s, %s", title, selected_thread_id)

    st.markdown(f"Current Session: `{title} thread_id: {selected_thread_id}`")

    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "New Session",
            on_click=lambda: new_session(session_options),
            help="Create a new session",
        )
    with col2:
        # Only allow deletion if the user has selected a valid thread_id
        if selected_thread_id is not None:
            if st.button("Delete", help="Delete current selection session"):
                langgraph_checkpointer.delete_thread(thread_id=selected_thread_id)
                st.success(
                    f"_Delete Success_: {title} \n\n _Thread_id_: `{selected_thread_id}`"
                )
                st.rerun()

    # If a valid thread id is selected, load the historical messages
    if selected_thread_id is not None:
        # Store the selected ID for use in the main interface
        st.session_state["current_thread_id"] = selected_thread_id
        st.session_state["state_history"] = agent.get_state(
            {"configurable": {"thread_id": selected_thread_id}}
        )

    return selected_thread_id, title


def render_sidebar_about() -> None:
    """Render the about section in the sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            """
            **GNS3 Copilot** is an AI-powered network engineering assistant
            designed to help you with GNS3 network simulation tasks.

            📖 [Documentation](https://github.com/yueguobin/gns3-copilot)
            """
        )
