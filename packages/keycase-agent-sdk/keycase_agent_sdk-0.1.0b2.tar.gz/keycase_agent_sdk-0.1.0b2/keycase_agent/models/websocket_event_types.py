# websocket_event_types.py

from enum import Enum


class WebSocketEventType(Enum):
    AGENT_AUTH_REQUEST = "agent_auth_request"
    AUTH_FAILURE_RESPONSE = "auth_failure_response"
    AUTH_SUCCESS_RESPONSE = "auth_success_response"

    # From web client to agent client
    AGENT_EXECUTE_PLAN_COMMAND = "agent_execute_plan_command"
    AGENT_STOP_COMMAND = "agent_stop_command"
    AGENT_STOP_EXECUTION_COMMAND = "agent_stop_execution_command"
    AGENT_EXECUTION_STATUS_REQUEST = "agent_execution_status_request"

    # From agent client to web client
    AGENT_EXECUTION_ACCEPTED_NOTIFY = "agent_execution_accepted_notify"
    AGENT_EXECUTION_PROGRESS_NOTIFY = "agent_execution_progress_notify"
    AGENT_EXECUTION_COMPLETED_NOTIFY = "agent_execution_completed_notify"
    AGENT_EXECUTION_FAILED_NOTIFY = "agent_execution_failed_notify"
    AGENT_EXECUTION_CANCELLED_NOTIFY = "agent_execution_cancelled_notify"
    AGENT_EXECUTION_STATUS_RESPONSE = "agent_execution_status_response"
    AGENT_EXECUTION_RESULT_PROCESS = "agent_execution_result_process"
    AGENT_EXECUTION_DENIED_NOTIFY = "agent_execution_denied_notify"
    AGENT_EXECUTION_ABORTED_NOTIFY = "agent_execution_aborted_notify"

    AGENT_STATUS_NOTIFY = "agent_status_notify"

    ERROR_NOTIFY = "error_notify"

    def __str__(self):
        return self.value
