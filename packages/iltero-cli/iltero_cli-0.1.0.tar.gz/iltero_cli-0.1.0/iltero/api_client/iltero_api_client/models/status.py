from enum import Enum


class Status(str, Enum):
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESSFUL = "SUCCESSFUL"

    def __str__(self) -> str:
        return str(self.value)
