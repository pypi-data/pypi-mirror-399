"""
General Application UI Utilities for GNS3 Copilot.

This module provides common UI rendering functions used across the GNS3 Copilot
application. It includes reusable components such as the sidebar about section
and other general-purpose UI elements.

Functions:
    render_sidebar_about(): Render the About section in the sidebar displaying
                            application information and feature highlights.
    initialize_page_config(): Initialize Streamlit page configuration.
    inject_chat_styles(): Inject CSS styles for chat messages.

Constants:
    ABOUT_TEXT: Markdown-formatted text containing application description,
                features, usage instructions, and GitHub repository link.

Example:
    Import and use in app.py:
        from gns3_copilot.ui_model.utils import (
            render_sidebar_about,
            initialize_page_config,
            inject_chat_styles
        )

        initialize_page_config()
        inject_chat_styles()
        render_sidebar_about()
"""

import streamlit as st

ABOUT_TEXT = """
GNS3 Copilot is an AI-powered assistant designed to help network engineers with
GNS3-related tasks. It leverages advanced language models to provide insights,
answer questions, and assist with network simulations.

**Features:**
- Answer GNS3-related queries
- Provide configuration examples
- Assist with troubleshooting

**Usage:**
Simply type your questions or commands in the chat interface,
and GNS3 Copilot will respond accordingly.

**Note:** This is a prototype version. For more information,
visit the [GNS3 Copilot GitHub Repository](https://github.com/yueguobin/gns3-copilot).
"""


def render_sidebar_about() -> None:
    """Render the About section in the sidebar."""
    with st.sidebar:
        st.header("About")
        st.markdown(ABOUT_TEXT)


def initialize_page_config() -> None:
    """
    Initialize Streamlit page configuration.

    This function sets up the page title, layout, and sidebar state.
    Should be called once at application startup.
    """
    st.set_page_config(
        page_title="GNS3 Copilot", layout="wide", initial_sidebar_state="expanded"
    )


def inject_chat_styles() -> None:
    """
    Inject CSS styles for chat messages.

    This function injects custom CSS to adjust padding for chat messages
    in fixed-height containers, improving the visual presentation of the
    chat interface.
    """
    st.html("""
<style>
[data-testid="stVerticalBlockBorderWrapper"] .stChatMessage {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""")
