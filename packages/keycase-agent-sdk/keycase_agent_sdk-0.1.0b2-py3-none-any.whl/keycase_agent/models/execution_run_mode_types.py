from enum import Enum


class ExecutionPlanRunMode(str, Enum):
    AbortOnFailure = "abortOnFailure"
    Skip = "skip"
    Default = "default"

    def __str__(self):
        return self.value
