"""Main Keycase Agent orchestrator module."""

import json
import logging
import os
import signal
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .auth import AuthService
from .event_handler import EventHandler
from .execution_manager import ExecutionManager
from .models.websocket_event_types import WebSocketEventType
from .state_tracker import AgentStateTracker
from .utils.auth_helper import auth_request, auth_request_with_details
from .utils.event_sender import configure_batching, send_event, status_update
from .websocket_client import WebSocketClient

logger = logging.getLogger(__name__)

# Constants
MAX_RESULT_RETRIES = 3
INITIAL_RETRY_INTERVAL_SECONDS = 2
MAX_FAILED_RESULTS_ENTRIES = 100
FAILED_RESULTS_DIR = "failed_results"

# Error codes that indicate the result was already processed (treat as success)
ALREADY_COMPLETED_CODES = {5002}  # "Execution run is already completed"


class KeycaseAgent:
    """Main Keycase Agent orchestrator.

    Manages WebSocket connections, authentication, execution management,
    and event handling for the Keycase automation platform.

    Uses AgentToken-based authentication where:
    - Agent authenticates with AgentToken to get access credentials
    - Server assigns agentId and returns wsUrl dynamically
    - WebSocket URL comes from authentication response

    Args:
        config: Configuration dictionary containing:
            - HTTP_URL: Base HTTP API URL
            - AGENT_TOKEN: AgentToken (must start with 'agt_')
            - AGENT_NAME: Unique agent name within organization
            - AGENT_VERSION: Agent version (optional)
            - AGENT_CAPABILITIES: List of capabilities (optional)
            - AGENT_TAGS: List of tags (optional)
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.http_url = config["HTTP_URL"]
        self.agent_token = config["AGENT_TOKEN"]
        self.agent_name = config["AGENT_NAME"]
        self.agent_version = config.get("AGENT_VERSION", "1.0.0")
        self.capabilities: List[str] = config.get("AGENT_CAPABILITIES", [])
        self.tags: List[str] = config.get("AGENT_TAGS", [])

        # These will be set after authentication
        self.agent_id: Optional[int] = None
        self.ws_url: Optional[str] = None

        # Initialize components
        self.state_tracker = AgentStateTracker()
        self.auth_service = AuthService(
            http_url=self.http_url,
            agent_token=self.agent_token,
            agent_name=self.agent_name,
            version=self.agent_version,
            capabilities=self.capabilities,
            tags=self.tags,
        )
        self.execution_manager = ExecutionManager(
            send_result_callback=self._send_result,
            update_status_callback=self._update_status,
        )

        self.event_handler = EventHandler(
            execution_manager=self.execution_manager,
            state_tracker=self.state_tracker,
            get_execution_plan=self._get_execution_plan,
        )

        # WebSocket client will be initialized after authentication
        self.ws_client: Optional[WebSocketClient] = None

        # Handle shutdown gracefully
        signal.signal(signal.SIGINT, self._on_shutdown_signal)
        signal.signal(signal.SIGTERM, self._on_shutdown_signal)

    def start(self) -> None:
        """Start the agent by authenticating and establishing WebSocket connection."""
        logger.info("Starting Keycase Agent")
        logger.info(f"Agent name: {self.agent_name}")
        logger.info(f"Agent version: {self.agent_version}")

        # Authenticate and get credentials (including dynamic wsUrl and agentId)
        credentials = self.auth_service.authenticate()

        # Store the dynamic agent ID and WebSocket URL from server
        self.agent_id = credentials.agent_id
        self.ws_url = credentials.ws_url

        logger.info(f"Assigned agent ID: {self.agent_id}")
        logger.info(f"WebSocket URL: {self.ws_url}")

        # Initialize WebSocket client with dynamic URL
        self.ws_client = WebSocketClient(
            url=self.ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )

        self.ws_client.run_forever()

    def _on_open(self, ws) -> None:
        """Handle WebSocket connection opened event."""
        logger.info("WebSocket connection opened")
        configure_batching(ws, flush_interval=10.0)
        self._send_auth()

    def _on_message(self, ws, message: str) -> None:
        """Handle incoming WebSocket messages."""
        self.event_handler.handle(message)

    def _on_error(self, ws, error: Exception) -> None:
        """Handle WebSocket errors."""
        logger.error(f"WebSocket error: {error}")
        self.execution_manager.stop()

    def _on_close(self, ws, code: Optional[int], msg: Optional[str]) -> None:
        """Handle WebSocket connection closed event."""
        logger.info(f"WebSocket closed with code={code}, msg={msg}")
        self.execution_manager.stop()

    def _send_auth(self) -> None:
        """Send authentication event to WebSocket server."""
        token = self.auth_service.get_token()
        payload = {
            "accessToken": token,
            "agentId": self.agent_id,
        }
        logger.info(f"Sending auth event for agent ID: {self.agent_id}")
        send_event(WebSocketEventType.AGENT_AUTH_REQUEST, payload, immediate=True)

    def _send_result(
        self, project_id: int, run_id: int, result: Dict[str, Any]
    ) -> Optional[Any]:
        """Send execution result to server with retry mechanism and local fallback.

        Args:
            project_id: Project identifier
            run_id: Run identifier
            result: Execution result data

        Returns:
            Server response or None if failed and saved locally
        """
        url = f"{self.http_url}/projects/{project_id}/runs/{run_id}/results"
        token = self.auth_service.get_token()

        if not token:
            logger.error("No authentication token available")
            self._save_result_locally(
                project_id, run_id, result, "No authentication token"
            )
            return None

        retry_interval = INITIAL_RETRY_INTERVAL_SECONDS

        for attempt in range(1, MAX_RESULT_RETRIES + 1):
            try:
                logger.info(
                    f"Sending run result to {url} "
                    f"(attempt {attempt}/{MAX_RESULT_RETRIES})"
                )
                response = auth_request_with_details("POST", url, token, data=result)

                if response.success:
                    logger.info(f"Successfully sent result on attempt {attempt}")
                    return response.data

                # Check if this is an "already completed" error - treat as success
                if response.error_code in ALREADY_COMPLETED_CODES:
                    logger.info(
                        f"Run {run_id} already completed (server confirmed). "
                        "Treating as success."
                    )
                    return response.data

                # Log the error for other failures
                logger.warning(
                    f"Attempt {attempt} failed: {response.error_message} "
                    f"(code: {response.error_code})"
                )

            except Exception as e:
                logger.error(f"Attempt {attempt} failed to send result: {str(e)}")

            # If not the last attempt, wait before retrying
            if attempt < MAX_RESULT_RETRIES:
                logger.info(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
                retry_interval *= 1.5  # Exponential backoff

        # All attempts failed, save locally
        logger.error(
            f"All {MAX_RESULT_RETRIES} attempts to send result failed. Saving locally."
        )
        self._save_result_locally(
            project_id, run_id, result, "All retry attempts failed"
        )
        return None

    def _save_result_locally(
        self, project_id: int, run_id: int, result: Dict[str, Any], reason: str
    ) -> None:
        """Save execution result to local directory when remote sending fails.

        Args:
            project_id: Project identifier
            run_id: Run identifier
            result: Execution result data
            reason: Reason for local saving
        """
        try:
            # Create results directory if it doesn't exist
            results_dir = os.path.join(os.getcwd(), FAILED_RESULTS_DIR)
            os.makedirs(results_dir, exist_ok=True)

            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"result_p{project_id}_r{run_id}_{timestamp}.json"
            filepath = os.path.join(results_dir, filename)

            # Prepare result data with metadata
            result_data = {
                "metadata": {
                    "project_id": project_id,
                    "run_id": run_id,
                    "timestamp": datetime.now().isoformat(),
                    "reason": reason,
                    "agent_id": self.agent_id,
                    "agent_name": self.agent_name,
                },
                "result": result,
            }

            # Save to file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2, default=str)

            logger.info(f"Execution result saved locally to: {filepath}")

            # Update summary file tracking all failed results
            self._update_failed_results_summary(filepath, project_id, run_id, reason)

        except Exception as e:
            logger.error(f"Failed to save result locally: {str(e)}")

    def _update_failed_results_summary(
        self, filepath: str, project_id: int, run_id: int, reason: str
    ) -> None:
        """Update summary file of all failed result submissions.

        Args:
            filepath: Path where result was saved
            project_id: Project identifier
            run_id: Run identifier
            reason: Reason for failure
        """
        try:
            results_dir = os.path.join(os.getcwd(), FAILED_RESULTS_DIR)
            summary_file = os.path.join(results_dir, "failed_results_summary.json")

            # Load existing summary or create new
            summary_data: Dict[str, Any] = {"failed_results": []}
            if os.path.exists(summary_file):
                try:
                    with open(summary_file, "r", encoding="utf-8") as f:
                        summary_data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    pass  # Use default structure if file is corrupted

            # Add new entry
            entry = {
                "timestamp": datetime.now().isoformat(),
                "project_id": project_id,
                "run_id": run_id,
                "reason": reason,
                "filepath": filepath,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
            }

            summary_data["failed_results"].append(entry)

            # Keep only last N entries to avoid file growing too large
            if len(summary_data["failed_results"]) > MAX_FAILED_RESULTS_ENTRIES:
                summary_data["failed_results"] = summary_data["failed_results"][
                    -MAX_FAILED_RESULTS_ENTRIES:
                ]

            # Save summary
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary_data, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to update failed results summary: {str(e)}")

    def _update_status(self, busy: bool) -> None:
        """Update agent status (busy/idle)."""
        status = self.state_tracker.set_busy(busy)
        status_update("AGENT_STATUS_NOTIFY", status)

    def _get_execution_plan(self, project_id: int, run_id: int) -> str:
        """Fetch execution plan from server.

        Args:
            project_id: Project identifier
            run_id: Run identifier

        Returns:
            JSON string of execution plan

        Raises:
            Exception: If plan fetch fails
        """
        url = f"{self.http_url}/projects/{project_id}/runs/{run_id}?includePlan=true"
        token = self.auth_service.get_token()

        if not token:
            raise Exception("No authentication token available")

        logger.info(f"Fetching execution plan from {url}")
        response = auth_request("GET", url, token)

        if not response:
            raise Exception("Failed to fetch execution plan")

        if isinstance(response, str):
            response = json.loads(response)

        logger.debug(f"Received execution plan response: {response}")
        return json.dumps(response.get("plan", {}))

    def _on_shutdown_signal(self, signum: int, frame) -> None:
        """Handle shutdown signals for graceful cleanup."""
        logger.info(f"Received shutdown signal ({signum}); cleaning up")
        self.state_tracker.request_shutdown()
        self.execution_manager.stop()
        self.auth_service.stop()
        if self.ws_client:
            self.ws_client.stop()
