import enum
from dataclasses import dataclass
from typing import List

from src.lib.loggers import get_module_logger

from pycountry import countries, subdivisions
from pycountry import db

logger = get_module_logger()


class PlatformEnum(str, enum.Enum):
    """Enum for the platform of the ticket."""

    JIRA = "JIRA"
    GITHUB = "GITHUB"
    TRELLO = "TRELLO"
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


@dataclass
class Country:
    """
    Country is a dataclass that represents a country through a fuzzy search map.
    """

    name: str

    async def get_code(self) -> str:
        """
        Convert a country name to a 2-digit representation of country code.

        Returns:
            str: The 2-digit country code.
        
        Raises:
            ValueError: If the country name is not found or the spelling is incorrect.
        """
        if self.name is None:
            return None

        name_lower = self.name.lower()
        try:
            code: List[db.Country] = countries.search_fuzzy(name_lower)
        except LookupError as err:
            logger.info(f"LookupError: {err}")
            raise ValueError(
                f"Country {self.name} not found. Please enter country code or check spelling."
            )

        return code[0].alpha_2


@dataclass
class Province:
    """
    Province is a dataclass that represents a province through a fuzzy search map.
    """

    name: str

    async def get_code(self) -> str:
        """
        Convert a province name to a 2-digit representation of province code.

        Returns:
            str: The 2-digit province code.
        
        Raises:
            ValueError: If the province name is not found or the spelling is incorrect.
        """
        if self.name is None:
            return None

        name_lower = self.name.lower()
        try:
            code: List[db.Subdivision] = subdivisions.search_fuzzy(name_lower)
        except LookupError as err:
            logger.info(f"LookupError: {err}")
            raise ValueError(
                f"Province {self.name} not found. Please enter province code or check spelling."
            )

        # code is returned as CA-XX, ex. Canadian provinces, where XX is the two-letter country code so we get the last two digits
        return code[0].code[-2:]
