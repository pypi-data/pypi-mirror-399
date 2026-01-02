"""
GNS3 Web UI Iframe Component

This module provides an iframe component to embed the GNS3 Web UI
into the Streamlit application.
"""

import os

import streamlit as st


def show_iframe(project_id: str) -> None:
    """
    Display GNS3 Web UI in an iframe.

    Args:
        project_id: The UUID of the GNS3 project to display.
    """
    # Get GNS3 server URL from environment variable
    gns3_server_url = os.getenv("GNS3_SERVER_URL", "http://127.0.0.1:3080/")

    # Get API version and construct appropriate iframe URL
    api_version = os.getenv("API_VERSION", "2")
    if api_version == "3":
        # API v3 uses 'controller' instead of 'server'
        iframe_url = f"{gns3_server_url}static/web-ui/controller/1/project/{project_id}"
    else:
        # API v2 uses 'server' (default behavior)
        iframe_url = f"{gns3_server_url}static/web-ui/server/1/project/{project_id}"

    # Display the iframe
    st.components.v1.iframe(iframe_url, height=800, scrolling=True)
