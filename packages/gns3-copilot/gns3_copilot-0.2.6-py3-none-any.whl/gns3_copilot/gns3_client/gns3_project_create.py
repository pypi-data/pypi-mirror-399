import os
from typing import Any

from dotenv import load_dotenv
from langchain.tools import BaseTool

from gns3_copilot.gns3_client import Gns3Connector, Project
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_project_create")

# Load environment variables
dotenv_loaded = load_dotenv()
if dotenv_loaded:
    logger.info(
        "GNS3ProjectCreate Tool Successfully loaded environment variables from .env file"
    )
else:
    logger.warning(
        "GNS3ProjectCreate Tool No .env file found or failed to load. Using existing environment variables."
    )


class GNS3ProjectCreate(BaseTool):
    """
    Tool to create a new GNS3 project.

    This tool connects to GNS3 server and creates a new project with the specified
    name and optional configuration parameters.
    """

    name: str = "create_gns3_project"
    description: str = """
    Creates a new GNS3 project with the specified name and optional parameters.

    Input parameters:
    - name: The name of the project to create (required)
    - auto_start: Automatically start the project when opened (optional, default: False)
    - auto_close: Automatically close the project when client disconnects (optional, default: False)
    - auto_open: Automatically open the project when GNS3 starts (optional, default: False)
    - scene_width: Width of the drawing area in pixels (optional)
    - scene_height: Height of the drawing area in pixels (optional)

    Returns: Project creation status and detailed information including:
    - success: Whether the operation succeeded
    - project: Project details (name, project_id, status, etc.)
    - message: Status message

    Example output:
        {
            "success": true,
            "project": {
                "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
                "name": "my_new_project",
                "status": "opened"
            },
            "message": "Project 'my_new_project' created successfully"
        }
    """

    def _run(self, tool_input: Any = None, run_manager: Any = None) -> dict:
        """
        Execute the project creation operation.

        Args:
            tool_input: Dictionary containing project parameters
            run_manager: Run manager for tool execution (optional)

        Returns:
            Dictionary with operation result and project details
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Validate input
            if not tool_input or "name" not in tool_input:
                return {
                    "success": False,
                    "error": "Missing required parameter: name",
                }

            name = tool_input["name"]

            # Validate project name is not empty
            if not name or not isinstance(name, str) or not name.strip():
                return {
                    "success": False,
                    "error": "Project name must be a non-empty string",
                }

            # Get optional parameters
            auto_start = tool_input.get("auto_start", False)
            auto_close = tool_input.get("auto_close", False)
            auto_open = tool_input.get("auto_open", False)
            scene_width = tool_input.get("scene_width")
            scene_height = tool_input.get("scene_height")

            # Get environment variables
            api_version_str = os.getenv("API_VERSION")
            server_url = os.getenv("GNS3_SERVER_URL")

            if not api_version_str:
                return {
                    "success": False,
                    "error": "API_VERSION environment variable not set",
                }

            if not server_url:
                return {
                    "success": False,
                    "error": "GNS3_SERVER_URL environment variable not set",
                }

            # Create connector based on API version
            if api_version_str == "2":
                server = Gns3Connector(
                    url=server_url,
                    api_version=int(api_version_str),
                )
            elif api_version_str == "3":
                server = Gns3Connector(
                    url=server_url,
                    user=os.getenv("GNS3_SERVER_USERNAME"),
                    cred=os.getenv("GNS3_SERVER_PASSWORD"),
                    api_version=int(api_version_str),
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported API_VERSION: {api_version_str}. Must be 2 or 3",
                }

            # Create project instance with specified parameters
            project_params = {
                "name": name,
                "auto_start": auto_start,
                "auto_close": auto_close,
                "auto_open": auto_open,
            }

            # Add optional scene parameters if provided
            if scene_width is not None:
                project_params["scene_width"] = scene_width
            if scene_height is not None:
                project_params["scene_height"] = scene_height

            project = Project(connector=server, **project_params)

            # Create the project
            project.create()

            # Verify project was created successfully
            if not project.project_id:
                return {
                    "success": False,
                    "error": "Failed to create project: project_id not returned",
                }

            logger.info(
                "Project created successfully: %s (ID: %s)",
                project.name,
                project.project_id,
            )

            # Prepare result
            result = {
                "success": True,
                "project": {
                    "project_id": project.project_id,
                    "name": project.name,
                    "status": project.status,
                    "path": project.path,
                },
                "message": f"Project '{project.name}' created successfully",
            }

            # Log result
            logger.info("Project creation result: %s", result)

            # Return success with project details
            return result

        except ValueError as e:
            logger.error("Validation error creating GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Validation error: {str(e)}",
            }
        except Exception as e:
            logger.error("Error creating GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to create GNS3 project: {str(e)}",
            }
