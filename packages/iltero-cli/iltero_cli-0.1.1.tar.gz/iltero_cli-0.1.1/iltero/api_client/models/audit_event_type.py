from enum import Enum


class AuditEventType(str, Enum):
    ACCESS = "access"
    CREATE = "create"
    DELETE = "delete"
    FAILED_LOGIN = "failed_login"
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_RESET = "password_reset"
    PERMISSION_CHANGE = "permission_change"
    REGISTRATION = "registration"
    SECURITY_ALERT = "security_alert"
    SETTINGS_CHANGE = "settings_change"
    UPDATE = "update"

    def __str__(self) -> str:
        return str(self.value)
