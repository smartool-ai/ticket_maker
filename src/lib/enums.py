import enum


class Role(str, enum.Enum):
    """Enum representing the role of the user."""

    GENERAL_USER = "GENERAL_USER"
    VALIDATED_USER = "VALIDATED_USER"
    ADMIN = "ADMIN"


class OrderStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    IN_PROGRESS = "IN PROGRESS"
