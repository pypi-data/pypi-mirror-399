from enum import Enum


class AuditStatus(str, Enum):
    FAILURE = "failure"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
