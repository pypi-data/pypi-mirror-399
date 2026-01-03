import json
import logging

from .models.websocket_event_types import WebSocketEventType
from .utils.event_sender import accepted_execution, busy_message, send_event

logger = logging.getLogger(__name__)


class EventHandler:
    def __init__(self, execution_manager, state_tracker, get_execution_plan):
        self.execution_manager = execution_manager
        self.state_tracker = state_tracker
        self.get_execution_plan = get_execution_plan

    def handle(self, message):
        try:
            data = json.loads(message)
            event_type = data.get("event")
            payload = data.get("payload", {})

            logger.info(f"Received event: {event_type}")

            if event_type == WebSocketEventType.AGENT_EXECUTE_PLAN_COMMAND.value:
                self._handle_execute_plan(payload)

            elif event_type == WebSocketEventType.AGENT_STOP_EXECUTION_COMMAND.value:
                self._handle_stop_execution(payload)

            elif event_type == WebSocketEventType.AGENT_EXECUTION_STATUS_REQUEST.value:
                self._handle_status_request(payload)

            elif event_type == WebSocketEventType.AUTH_SUCCESS_RESPONSE.value:
                logger.info("Authentication successful.")

            elif event_type == WebSocketEventType.AUTH_FAILURE_RESPONSE.value:
                logger.error("Authentication failed. Exiting." + str(payload))
                raise SystemExit(1)

            else:
                logger.warning(f"Unhandled event type: {event_type}")

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.state_tracker.set_busy(False)

    def _handle_execute_plan(self, payload):
        run_id = payload.get("runId")
        project_id = payload.get("projectId")

        if not self.state_tracker.try_set_busy():
            logger.info("Agent is busy. Rejecting execute request.")
            busy_message(
                WebSocketEventType.AGENT_EXECUTION_DENIED_NOTIFY,
                run_id,
                "Agent is busy",
            )
            return

        logger.info("Execution request accepted")
        accepted_execution(WebSocketEventType.AGENT_EXECUTION_ACCEPTED_NOTIFY, run_id)
        execution_plan_json = self.get_execution_plan(project_id, run_id)
        self.execution_manager.start_execution(project_id, run_id, execution_plan_json)

    def _handle_stop_execution(self, payload):
        run_id = payload.get("runId")
        logger.info(f"Stop requested for run_id {run_id}")
        self.execution_manager.stop()
        self.state_tracker.set_busy(False)
        send_event(
            WebSocketEventType.AGENT_EXECUTION_ABORTED_NOTIFY, {"runId": run_id}, True
        )

    def _handle_status_request(self, payload):
        run_id = payload.get("runId")
        recipient_id = payload.get("recipientId")
        tracker = self.execution_manager.execution_tracker

        with self.execution_manager.execution_tracker_lock:
            if run_id in tracker:
                status = {
                    "runId": run_id,
                    "recipientId": recipient_id,
                    "startDateTime": tracker[run_id]["startDateTime"],
                    "endDateTime": tracker[run_id]["endDateTime"],
                    "flowResults": tracker[run_id]["flowResults"],
                }
                logger.info(f"Sending execution status for run_id {run_id}")
                send_event(
                    WebSocketEventType.AGENT_EXECUTION_STATUS_RESPONSE, status, True
                )
            else:
                logger.warning(f"No active execution found for run_id {run_id}")
