from enum import Enum


class SubscriptionTier(str, Enum):
    ENTERPRISE = "enterprise"
    FREE = "free"
    PRO = "pro"
    STARTUP = "startup"

    def __str__(self) -> str:
        return str(self.value)
