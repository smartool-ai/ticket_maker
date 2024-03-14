import enum

from src.lib.loggers import get_module_logger


logger = get_module_logger()


class SubscriptionTier(str, enum.Enum):
    """Enum representing the subscription tier of the user."""

    FREE = "FREE"
    BASIC = "BASIC"
    STANDARD = "STANDARD"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class EventEnum(str, enum.Enum):
    """Enum representing the type of event."""

    TICKET_GENERATION = "TICKET_GENERATION"
    TICKET_EXPANSION = "TICKET_EXPANSION"
    TICKET_UPDATE = "TICKET_UPDATE"
    TICKET_DELETION = "TICKET_DELETION"
    TICKET_RETRIEVAL = "TICKET_RETRIEVAL"
    TICKET_CREATION = "TICKET_CREATION"
    TICKET_ASSIGNMENT = "TICKET_ASSIGNMENT"
    TICKET_COMMENT = "TICKET_COMMENT"
    TICKET_STATUS_CHANGE = "TICKET_STATUS_CHANGE"
    TICKET_PRIORITY_CHANGE = "TICKET_PRIORITY_CHANGE"
    TICKET_RESOLUTION_CHANGE = "TICKET_RESOLUTION_CHANGE"
    TICKET_TYPE_CHANGE = "TICKET_TYPE_CHANGE"
    TICKET_LABEL_CHANGE = "TICKET_LABEL_CHANGE"
    TICKET_EPIC_CHANGE = "TICKET_EPIC_CHANGE"
    TICKET_SPRINT_CHANGE = "TICKET_SPRINT_CHANGE"
    TICKET_COMPONENT_CHANGE = "TICKET_COMPONENT_CHANGE"
    TICKET_FIX_VERSION_CHANGE = "TICKET_FIX_VERSION_CHANGE"
    TICKET_AFFECTS_VERSION_CHANGE = "TICKET_AFFECTS_VERSION_CHANGE"
    TICKET_DUE_DATE_CHANGE = "TICKET_DUE_DATE_CHANGE"
    TICKET_ESTIMATION_POINTS_CHANGE = "TICKET_ESTIMATION_POINTS_CHANGE"
    TICKET_REPORTER_CHANGE = "TICKET_REPORTER_CHANGE"
    TICKET_ASSIGNEE_CHANGE = "TICKET_ASSIGNEE_CHANGE"
    TICKET_WATCHER_CHANGE = "TICKET_WATCHER_CHANGE"
    TICKET_LINK = "TICKET_LINK"
    TICKET_ATTACHMENT = "TICKET_ATTACHMENT"
    TICKET_SUBTASK = "TICKET_SUBTASK"
    TICKET_EPIC = "TICKET_EPIC"
    TICKET_SPRINT = "TICKET_SPRINT"
    TICKET_COMPONENT = "TICKET_COMPONENT"
    TICKET_FIX_VERSION = "TICKET_FIX_VERSION"
    TICKET_AFFECTS_VERSION = "TICKET_AFFECTS_VERSION"
    TICKET_DUE_DATE = "TICKET_DUE_DATE"
    TICKET_ESTIMATION_POINTS = "TICKET_ESTIMATION_POINTS"
    TICKET_REPORTER = "TICKET_REPORTER"
    TICKET_ASSIGNEE = "TICKET_ASSIGNEE"
    TICKET_WATCHER = "TICKET_WATCHER"


class PlatformEnum(str, enum.Enum):
    """Enum for the platform of the ticket."""

    JIRA = "JIRA"
    GITHUB = "GITHUB"
    TRELLO = "TRELLO"
    SHORTCUT = "SHORTCUT"
    ASANA = "ASANA"  # Add more platforms as needed


class Role(str, enum.Enum):
    """Enum representing the role of the user."""

    GENERAL_USER = "GENERAL_USER"
    VALIDATED_USER = "VALIDATED_USER"
    ADMIN = "ADMIN"


class AWSService(str, enum.Enum):
    """AWSService is used to initialize connections to AWS services with boto3."""

    PARAM_STORE = "ssm"
    SIMPLE_EMAIL_SERVICE = "ses"
    STEP_FUNCTIONS = "stepfunctions"
    COGNITO_IDP = "cognito-idp"
    COGNITO_IDENTITY = "cognito-identity"
    IAM = "iam"
    SNS = "sns"
    SQS = "sqs"
    S3 = "s3"
    SECRETS_MANAGER = "secretsmanager"
    APP_CONFIG_DATA = "appconfigdata"
    CLOUDWATCH = "cloudwatch"
    KMS = "kms"


class LambdaLogLevel(str, enum.Enum):
    """Acceptable Log Levels"""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Currency(str, enum.Enum):
    """Enum representing currencies."""

    USD = "USD"
