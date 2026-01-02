import os
from typing import Any

from dotenv import load_dotenv
from langchain.tools import BaseTool

from gns3_copilot.gns3_client import Gns3Connector, Project
from gns3_copilot.log_config import setup_tool_logger

# Configure logging
logger = setup_tool_logger("gns3_project_update")

# Load environment variables
dotenv_loaded = load_dotenv()
if dotenv_loaded:
    logger.info(
        "GNS3ProjectUpdate Tool Successfully loaded environment variables from .env file"
    )
else:
    logger.warning(
        "GNS3ProjectUpdate Tool No .env file found or failed to load. Using existing environment variables."
    )


class GNS3ProjectUpdate(BaseTool):
    """
    Tool to update an existing GNS3 project configuration.

    This tool connects to GNS3 server and updates project settings including
    auto-start options, scene dimensions, display options, and other parameters.
    """

    name: str = "update_gns3_project"
    description: str = """
    Updates an existing GNS3 project configuration.

    Input parameters:
    Required:
    - project_id: The UUID of the project to update OR
    - name: The name of the project to update (one must be provided)

    Optional - Auto control options:
    - auto_start: Automatically start the project when opened (default: keep current)
    - auto_close: Automatically close the project when client disconnects (default: keep current)
    - auto_open: Automatically open the project when GNS3 starts (default: keep current)

    Optional - Scene settings:
    - scene_width: Width of the drawing area in pixels (default: keep current)
    - scene_height: Height of the drawing area in pixels (default: keep current)
    - grid_size: Grid size for the drawing area for nodes (default: keep current)
    - drawing_grid_size: Grid size for the drawing area for drawings (default: keep current)

    Optional - Display options:
    - show_grid: Show the grid on the drawing area (default: keep current)
    - show_interface_labels: Show interface labels on the drawing area (default: keep current)
    - show_layers: Show layers on the drawing area (default: keep current)
    - snap_to_grid: Snap to grid on the drawing area (default: keep current)
    - zoom: Zoom of the drawing area (default: keep current)

    Returns: Project update status and detailed information including:
    - success: Whether the operation succeeded
    - project: Updated project details (name, project_id, status, settings, etc.)
    - updated_fields: List of fields that were updated
    - message: Status message

    Example output:
        {
            "success": true,
            "project": {
                "project_id": "ff8e059c-c33d-47f4-bc11-c7dda8a1d500",
                "name": "my_project",
                "status": "opened",
                "auto_start": true,
                "auto_close": false,
                "auto_open": false
            },
            "updated_fields": ["auto_start"],
            "message": "Project 'my_project' updated successfully"
        }
    """

    def _run(self, tool_input: Any = None, run_manager: Any = None) -> dict:
        """
        Execute the project update operation.

        Args:
            tool_input: Dictionary containing project identifier and update parameters
            run_manager: Run manager for tool execution (optional)

        Returns:
            Dictionary with operation result and updated project details
        """
        # Log received input
        logger.info("Received input: %s", tool_input)

        try:
            # Validate input
            if not tool_input:
                return {
                    "success": False,
                    "error": "No input provided",
                }

            # Check for project identifier
            project_id = tool_input.get("project_id")
            project_name = tool_input.get("name")

            if not project_id and not project_name:
                return {
                    "success": False,
                    "error": "Missing required parameter: either 'project_id' or 'name' must be provided",
                }

            # Remove project_id and name from update parameters
            update_params = {
                k: v
                for k, v in tool_input.items()
                if k not in ("project_id", "name") and v is not None
            }

            # Check if there's anything to update
            if not update_params:
                return {
                    "success": False,
                    "error": "No update parameters provided",
                }

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

            # Create project instance
            if project_id:
                project = Project(project_id=project_id, connector=server)
            else:
                project = Project(name=project_name, connector=server)

            # Get current project information
            project.get(get_nodes=False, get_links=False, get_stats=False)

            # Verify project was found
            if not project.project_id:
                if project_name:
                    return {
                        "success": False,
                        "error": f"Project with name '{project_name}' not found",
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Project with ID '{project_id}' not found",
                    }

            # Store current values for comparison
            old_values = {}
            for field in update_params:
                old_values[field] = getattr(project, field, None)

            # Update the project
            project.update(**update_params)

            # Collect updated fields
            updated_fields = []
            for field in update_params:
                new_value = getattr(project, field, None)
                if old_values[field] != new_value:
                    updated_fields.append(field)

            logger.info(
                "Project updated successfully: %s (ID: %s), updated fields: %s",
                project.name,
                project.project_id,
                ", ".join(updated_fields),
            )

            # Prepare project details for response
            project_details = {
                "project_id": project.project_id,
                "name": project.name,
                "status": project.status,
                "path": project.path,
            }

            # Add optional fields if they were updated or exist
            optional_fields = [
                "auto_start",
                "auto_close",
                "auto_open",
                "scene_width",
                "scene_height",
                "grid_size",
                "drawing_grid_size",
                "show_grid",
                "show_interface_labels",
                "show_layers",
                "snap_to_grid",
                "zoom",
            ]

            for field in optional_fields:
                value = getattr(project, field, None)
                if value is not None:
                    project_details[field] = value

            # Prepare result
            result = {
                "success": True,
                "project": project_details,
                "updated_fields": updated_fields,
                "message": f"Project '{project.name}' updated successfully",
            }

            # Log result
            logger.info("Project update result: %s", result)

            # Return success with project details
            return result

        except ValueError as e:
            logger.error("Validation error updating GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Validation error: {str(e)}",
            }
        except Exception as e:
            logger.error("Error updating GNS3 project: %s", str(e))
            return {
                "success": False,
                "error": f"Failed to update GNS3 project: {str(e)}",
            }
