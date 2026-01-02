from enum import Enum


class EventCategory(str, Enum):
    CI_CD = "ci_cd"
    CLOUD = "cloud"
    COMPLIANCE = "compliance"
    INFRASTRUCTURE = "infrastructure"
    PERFORMANCE = "performance"
    SECURITY = "security"

    def __str__(self) -> str:
        return str(self.value)
