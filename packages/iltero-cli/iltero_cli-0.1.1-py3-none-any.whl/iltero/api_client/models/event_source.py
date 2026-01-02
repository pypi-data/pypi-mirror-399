from enum import Enum


class EventSource(str, Enum):
    ADMIN_PANEL = "admin_panel"
    API_GATEWAY = "api_gateway"
    AUTH_SYSTEM = "auth_system"
    BACKGROUND_TASK = "background_task"
    CI_CD_SYSTEM = "ci_cd_system"
    CLOUD_PROVIDER = "cloud_provider"
    INFRASTRUCTURE = "infrastructure"
    INTEGRATION = "integration"
    MONITORING_SYSTEM = "monitoring_system"
    SYSTEM = "system"
    USER_INTERFACE = "user_interface"

    def __str__(self) -> str:
        return str(self.value)
