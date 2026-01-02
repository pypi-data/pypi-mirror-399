from enum import Enum


class AuditCategory(str, Enum):
    AUTH = "auth"
    COMPLIANCE = "compliance"
    DATA = "data"
    ORG = "org"
    SECURITY = "security"
    SYSTEM = "system"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
