"""Execution result models for tracking flow and step execution status."""

import json
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class StatusEnum(Enum):
    """Execution status enumeration."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PASSED = "PASSED"
    SKIPPED = "SKIPPED"
    ABORTED = "ABORTED"
    ERROR = "ERROR"

    def __str__(self) -> str:
        return self.value


class FlowResult:
    """Result of a single flow execution."""

    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name
        self.failed_on_step_id: Optional[int] = None
        self.status: Optional[StatusEnum] = None
        self.message: Optional[str] = None
        self.run_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    # Legacy property aliases for backward compatibility with API responses
    @property
    def failedOnStepId(self) -> Optional[int]:
        return self.failed_on_step_id

    @property
    def runAt(self) -> Optional[datetime]:
        return self.run_at

    @property
    def completedAt(self) -> Optional[datetime]:
        return self.completed_at

    def started_execution(self) -> None:
        """Mark flow execution as started."""
        self.run_at = datetime.now(timezone.utc)

    def completed_execution(self) -> None:
        """Mark flow execution as completed."""
        self.completed_at = datetime.now(timezone.utc)

    def set_failed_on_step_id(self, failed_on_step_id: int) -> None:
        """Set the step ID where failure occurred."""
        self.failed_on_step_id = failed_on_step_id

    def set_message(self, message: str) -> None:
        """Set result message."""
        self.message = message

    def set_status(self, status: StatusEnum) -> None:
        """Set execution status."""
        self.status = status

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "failedOnStepId": self.failed_on_step_id,
            "status": str(self.status) if self.status else None,
            "message": self.message,
            "runAt": self.run_at.isoformat() if self.run_at else None,
            "completedAt": self.completed_at.isoformat() if self.completed_at else None,
            "name": self.name,
        }


class ExecutionResultData:
    """Complete execution result data for a run."""

    def __init__(self, run_id: int) -> None:
        self.run_id = run_id
        self.start_date_time: Optional[datetime] = None
        self.end_date_time: Optional[datetime] = None
        self.flow_results: List[FlowResult] = []

    # Legacy property aliases for backward compatibility
    @property
    def runId(self) -> int:
        return self.run_id

    @property
    def startDateTime(self) -> Optional[datetime]:
        return self.start_date_time

    @property
    def endDateTime(self) -> Optional[datetime]:
        return self.end_date_time

    @property
    def flowResults(self) -> List[FlowResult]:
        return self.flow_results

    def start_execution(self) -> None:
        """Mark execution as started."""
        self.start_date_time = datetime.now(timezone.utc)

    def end_execution(self) -> None:
        """Mark execution as ended."""
        self.end_date_time = datetime.now(timezone.utc)

    def add_flow_result(self, flow_result: FlowResult) -> None:
        """Add a flow result to the execution."""
        self.flow_results.append(flow_result)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "startDateTime": (
                self.start_date_time.isoformat() if self.start_date_time else None
            ),
            "runId": self.run_id,
            "endDateTime": (
                self.end_date_time.isoformat() if self.end_date_time else None
            ),
            "flowResults": [flow_result.to_dict() for flow_result in self.flow_results],
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=4)
