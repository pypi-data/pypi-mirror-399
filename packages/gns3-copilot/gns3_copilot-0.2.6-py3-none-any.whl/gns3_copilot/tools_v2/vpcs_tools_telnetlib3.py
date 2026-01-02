"""
Multi-device VPCS command execution tool using telnetlib3 with threading.
Supports concurrent execution of multiple command groups across multiple VPCS devices.
"""

import json
import os
import threading
from time import sleep
from typing import Any

from dotenv import load_dotenv
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from telnetlib3 import Telnet

from gns3_copilot.log_config import setup_tool_logger
from gns3_copilot.public_model import get_device_ports_from_topology

logger = setup_tool_logger("vpcs_multi_commands")

# Load environment variables
dotenv_loaded = load_dotenv()
if dotenv_loaded:
    logger.info(
        "VPCSMultiCommands Successfully loaded environment variables from .env file"
    )
else:
    logger.warning(
        "VPCSMultiCommands No .env file found or failed to load. Using existing environment variables."
    )


class VPCSMultiCommands(BaseTool):
    """
    A tool to execute multiple command groups across multiple VPCS devices concurrently.
    Supports parallel execution with threading for improved performance.

    Input should be a JSON object containing project_id and device configurations.
    Example input:
        {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.10.0.12/24 10.10.0.254", "ping 10.10.0.254"]
                },
                {
                    "device_name": "PC2",
                    "commands": ["ip 10.10.0.13/24 10.10.0.254"]
                }
            ]
        }

    Returns a list of results, one for each command group.
    """

    name: str = "execute_vpcs_multi_commands"
    description: str = """
    Executes multiple command groups across multiple VPCS devices concurrently using telnetlib3.
    Supports parallel execution with threading for improved performance.

    Input should be a JSON object containing project_id and device configurations.
    Example input:
        {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": ["ip 10.10.0.12/24 10.10.0.254", "ping 10.10.0.254"]
                },
                {
                    "device_name": "PC2",
                    "commands": ["ip 10.10.0.13/24 10.10.0.254"]
                }
            ]
        }

    Returns a list of results, each containing device_name, status, output, and commands.
    """

    def _connect_and_execute_commands(
        self,
        device_name: str,
        commands: list[str],
        results_list: list[Any],
        index: int,
        device_ports: dict[str, Any],
        gns3_host: str,
    ) -> None:
        """Internal method to connect to device and execute multiple commands"""

        logger.info(
            "Starting connection for device '%s' with %d commands",
            device_name,
            len(commands),
        )

        # Check if device has port information
        if device_name not in device_ports:
            logger.warning(
                "Device '%s' not found in topology or missing console port", device_name
            )
            results_list[index] = {
                "device_name": device_name,
                "status": "error",
                "output": f"Device '{device_name}' not found in topology or missing console port",
                "commands": commands,
            }
            return

        port = device_ports[device_name]["port"]
        host = gns3_host

        logger.info("Connecting to device '%s' at %s:%d", device_name, host, port)

        tn = Telnet()
        try:
            tn.open(host=host, port=port, timeout=30)
            logger.info(
                "Successfully connected to device '%s' at %s:%d",
                device_name,
                host,
                port,
            )

            # Initialize connection
            tn.write(b"\n")
            sleep(0.5)
            tn.write(b"\n")
            sleep(0.5)
            tn.write(b"\n")
            sleep(0.5)
            tn.write(b"\n")
            sleep(0.5)
            tn.expect([rb"PC\d+>"])
            logger.info("Connection initialized for device '%s'", device_name)

            # Execute all commands and merge output
            combined_output = ""
            for i, command in enumerate(commands):
                logger.info(
                    "Executing command %d/%d on device '%s': %s",
                    i + 1,
                    len(commands),
                    device_name,
                    command,
                )
                tn.write(command.encode(encoding="ascii") + b"\n")
                sleep(5)
                tn.expect([rb"PC\d+>"])
                output = tn.read_very_eager().decode("utf-8")
                combined_output += output
                logger.debug(
                    "Command '%s' executed on device '%s', output length: %d",
                    command,
                    device_name,
                    len(output),
                )

            # Add result to list
            results_list[index] = {
                "device_name": device_name,
                "status": "success",
                "output": combined_output,
                "commands": commands,
            }
            logger.info(
                "Successfully executed all %d commands on device '%s'",
                len(commands),
                device_name,
            )

        except Exception as e:
            logger.error(
                "Error executing commands on device '%s': %s", device_name, str(e)
            )
            results_list[index] = {
                "device_name": device_name,
                "status": "error",
                "output": str(e),
                "commands": commands,
            }
        finally:
            tn.close()
            logger.debug("Connection closed for device '%s'", device_name)

    def _validate_project_id(self, project_id: str) -> bool:
        """
        Validate project_id format (UUID).

        Args:
            project_id: The project ID to validate

        Returns:
            True if valid UUID format, False otherwise
        """
        import re

        uuid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        is_valid = bool(re.match(uuid_pattern, project_id, re.IGNORECASE))
        if is_valid:
            logger.debug("project_id '%s' is valid UUID format", project_id)
        else:
            logger.warning("project_id '%s' is not a valid UUID format", project_id)
        return is_valid

    def _validate_tool_input(
        self, tool_input: str | bytes | list[Any] | dict[str, Any]
    ) -> tuple[list[dict[str, Any]], str]:
        """
        Validate device command input and extract project_id and device_configs.

        Args:
            tool_input: The input received from the LangChain/LangGraph tool call.

        Returns:
            Tuple containing (device_configs_list, project_id) or (error_list, "")
        """

        parsed_input = None

        # Compatibility Check and Parsing ---
        # Check if the input is a string (or bytes) which needs to be parsed.
        if isinstance(tool_input, (str, bytes, bytearray)):
            # Handle models that return a raw JSON string.
            try:
                parsed_input = json.loads(tool_input)
                logger.info("Successfully parsed tool input from JSON string.")
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON string received as tool input: %s", e)
                return ([{"error": f"Invalid JSON input: {e}"}], "")
        else:
            # Handle standard models where the framework has already parsed the JSON.
            parsed_input = tool_input
            logger.info(
                "Using tool input directly as type: %s", type(parsed_input).__name__
            )

        # Validate input is a dictionary
        if not isinstance(parsed_input, dict):
            error_msg = (
                "Tool input must be a JSON object containing 'project_id' and 'device_configs', "
                f"but got {type(parsed_input).__name__}"
            )
            logger.error(error_msg)
            return ([{"error": error_msg}], "")

        # Extract and validate project_id
        project_id = parsed_input.get("project_id")
        if not project_id:
            error_msg = "Missing required field 'project_id' in input"
            logger.error(error_msg)
            return ([{"error": error_msg}], "")

        # Validate project_id format
        if not self._validate_project_id(project_id):
            error_msg = (
                f"Invalid project_id format: {project_id}. Expected UUID format."
            )
            logger.error(error_msg)
            return ([{"error": error_msg}], "")

        # Extract and validate device_configs
        device_configs = parsed_input.get("device_configs")
        if device_configs is None:
            error_msg = "Missing required field 'device_configs' in input"
            logger.error(error_msg)
            return ([{"error": error_msg}], "")

        # Validate device_configs is a list
        if not isinstance(device_configs, list):
            error_msg = f"'device_configs' must be a list, but got {type(device_configs).__name__}"
            logger.error(error_msg)
            return ([{"error": error_msg}], "")

        # Handle empty list
        if not device_configs:
            logger.warning("Device configs list is empty.")
            return [], ""

        # Validate each item in device_configs
        for i, item in enumerate(device_configs):
            if not isinstance(item, dict):
                error_msg = (
                    f"Item at index {i} must be a dictionary, got {type(item).__name__}"
                )
                logger.error(error_msg)
                return ([{"error": error_msg}], "")

            # Validate required fields in each device config
            if "device_name" not in item:
                error_msg = f"Item at index {i} missing required field 'device_name'"
                logger.error(error_msg)
                return ([{"error": error_msg}], "")

            if "commands" not in item:
                error_msg = f"Item at index {i} missing required field 'commands'"
                logger.error(error_msg)
                return ([{"error": error_msg}], "")

            if not isinstance(item["commands"], list):
                error_msg = (
                    f"'commands' in item at index {i} must be a list, "
                    f"but got {type(item['commands']).__name__}"
                )
                logger.error(error_msg)
                return ([{"error": error_msg}], "")

        logger.info(
            "Input validated successfully. project_id=%s, device_configs_count=%d",
            project_id,
            len(device_configs),
        )
        return device_configs, project_id

    def _run(
        self, tool_input: str, run_manager: CallbackManagerForToolRun | None = None
    ) -> list[dict[str, Any]]:
        """Main method to execute multi-device multi-commands"""

        # Log received input
        logger.info("Received input: %s", tool_input)

        # Validate tool input and extract project_id and device_configs
        device_configs, project_id = self._validate_tool_input(tool_input)

        # Check if validation returned an error
        if (
            isinstance(device_configs, list)
            and len(device_configs) > 0
            and "error" in device_configs[0]
        ):
            return device_configs

        # Extract all device names from input using set comprehension
        device_names = {config["device_name"] for config in device_configs}
        logger.debug("Extracted device names: %s", list(device_names))

        # Get device port mapping with project_id
        logger.debug("Retrieving device port mapping for project_id=%s", project_id)
        device_ports = get_device_ports_from_topology(
            list(device_names), project_id=project_id
        )
        logger.info(
            "Retrieved port mappings for %d devices: %s",
            len(device_ports),
            list(device_ports.keys()),
        )

        # Get host IP from environment variable
        gns3_host = os.getenv("GNS3_SERVER_HOST", "127.0.0.1")
        logger.info("Using GNS3 server host: %s", gns3_host)

        # Initialize results list (pre-allocate space for concurrent writes)
        results: list[dict[str, Any]] = [{} for _ in range(len(device_configs))]
        threads = []

        # Create thread for each command group
        logger.info("Starting parallel execution for %d devices", len(device_configs))
        for i, cmd_group in enumerate(device_configs):
            device_name = cmd_group["device_name"]
            logger.debug(
                "Creating thread for device '%s' (index %d) with %d commands",
                device_name,
                i,
                len(cmd_group["commands"]),
            )
            thread = threading.Thread(
                target=self._connect_and_execute_commands,
                args=(
                    cmd_group["device_name"],
                    cmd_group["commands"],
                    results,
                    i,
                    device_ports,
                    gns3_host,
                ),
            )
            threads.append(thread)
            thread.start()
            logger.debug("Thread started for device '%s'", device_name)

        # Wait for all threads to complete
        logger.debug("Waiting for all threads to complete...")
        for thread in threads:
            thread.join()

        # Count successful and failed executions
        success_count = sum(1 for r in results if r.get("status") == "success")
        error_count = sum(1 for r in results if r.get("status") == "error")

        logger.info(
            "Multi-device command execution completed. Total: %d, Success: %d, Error: %d",
            len(results),
            success_count,
            error_count,
        )

        return results


if __name__ == "__main__":
    # Example usage
    command_groups = json.dumps(
        {
            "project_id": "f32ebf3d-ef8c-4910-b0d6-566ed828cd24",
            "device_configs": [
                {
                    "device_name": "PC1",
                    "commands": [
                        "ip 10.10.0.12/24 10.10.0.254",
                        "ping 10.10.0.254",
                    ],
                },
                {
                    "device_name": "PC2",
                    "commands": ["ip 10.10.0.13/24 10.10.0.254"],
                },
                {
                    "device_name": "PC3",
                    "commands": [
                        "ip 10.20.0.22/24 10.20.0.254",
                        "ping 10.20.0.254",
                    ],
                },
                {
                    "device_name": "PC4",
                    "commands": ["ip 10.20.0.23/24 10.20.0.254"],
                },
            ],
        }
    )

    exe_cmd = VPCSMultiCommands()
    result = exe_cmd._run(tool_input=command_groups)
    print("Execution results:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
