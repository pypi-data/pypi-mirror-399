"""
Chat Helper Functions for GNS3 Copilot.

This module provides auxiliary functions for managing chat sessions,
including creating new sessions, switching between sessions, and
handling session-related UI operations.

Functions:
    new_session(): Create a new chat session by generating a unique thread ID

Example:
    from gns3_copilot.ui_model.utils import new_session

    # Create a new chat session
    session_options = [("(Please select session)", None), ...]
    new_session(session_options)
"""

import uuid

import streamlit as st

from gns3_copilot.log_config import setup_logger

logger = setup_logger("chat_helpers")


def new_session(session_options: list[tuple[str, str | None]]) -> None:
    """
    Create a new chat session by generating a unique thread ID and resetting session state.

    Initializes a fresh conversation session with a new UUID, clears existing session data,
    and resets the UI session selector to the default option.

    Args:
        session_options: List of tuples containing session display names and thread IDs.
                         The first element should be the default placeholder option.

    Side Effects:
        - Updates st.session_state with new thread_id
        - Clears current_thread_id and state_history
        - Resets session_select to default option (session_options[0])
        - Logs session creation
    """
    new_tid = str(uuid.uuid4())
    # Real new thread id
    st.session_state["thread_id"] = new_tid
    # Clear your own state
    st.session_state["current_thread_id"] = None
    st.session_state["state_history"] = None
    # Reset the dropdown menu to the first option ("(Please select session)", None)
    st.session_state["session_select"] = session_options[0]
    logger.debug("New Session created with thread_id= %s", new_tid)
