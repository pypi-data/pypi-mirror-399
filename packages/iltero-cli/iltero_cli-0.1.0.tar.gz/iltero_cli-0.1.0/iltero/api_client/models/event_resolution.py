from enum import Enum


class EventResolution(str, Enum):
    FALSE_POSITIVE = "false_positive"
    IGNORED = "ignored"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"

    def __str__(self) -> str:
        return str(self.value)
