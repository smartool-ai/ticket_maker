import datetime
import json
import os
from typing import Any, Dict, Optional

from src.lib.dynamo_utils import BaseModel
from src.lib.loggers import get_module_logger

from pynamodb.attributes import UnicodeAttribute
from pynamodb.expressions.condition import Condition


logger = get_module_logger()


class UserMetadataModel(BaseModel):
    """Model representing a User and their metadata.

    fields:
        user_id (str, hash_key): Auth0 id
        email (str): Email address
        jira_api_key (str): Jira API key
        jira_email (str): Jira email address
    """

    class Meta:
        table_name = "UserMetadata"
        region = os.getenv("AWS_REGION", "us-west-2")

    user_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(null=True)
    jira_api_key = UnicodeAttribute(null=True)
    jira_email = UnicodeAttribute(null=True)
    jira_domain = UnicodeAttribute(null=True)

    @classmethod
    async def initialize(
        cls,
        user_id: str,
        email: Optional[str] = None,
        jira_api_key: Optional[str] = None,
        jira_email: Optional[str] = None,
        jira_domain: Optional[str] = None,
    ) -> "UserMetadataModel":
        """Initialize a UserMetadataModel."""
        user_metadata = UserMetadataModel(
            user_id=user_id,
            email=email,
            jira_api_key=jira_api_key,
            jira_email=jira_email,
            jira_domain=jira_domain,
            created_datetime=datetime.datetime.now(),
        )

        return user_metadata

    @classmethod
    def synchronous_initialize(
        cls,
        user_id: str,
        email: Optional[str] = None,
        jira_api_key: Optional[str] = None,
        jira_email: Optional[str] = None,
        jira_domain: Optional[str] = None,
    ) -> "UserMetadataModel":
        """Initialize a UserMetadataModel synchronously."""
        user_metadata = UserMetadataModel(
            user_id=user_id,
            email=email,
            jira_api_key=jira_api_key,
            jira_email=jira_email,
            jira_domain=jira_domain,
            created_datetime=datetime.datetime.now(),
        )

        return user_metadata

    async def save(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """Save the user metadata to DynamoDB."""
        return super().save(condition)

    def synchronous_save(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """Save the user metadata to DynamoDB synchronously."""
        return super().save(condition)

    async def __eq__(self, other: Any) -> bool:
        """Check if two UserMetadataModels are equal."""
        return self.user_id == other.user_id

    async def to_serializable_dict(self) -> dict:
        """Return a serializable dictionary representation of the UserMetadataModel."""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "jira_api_key": self.jira_api_key,
            "jira_email": self.jira_email,
            "jira_domain": self.jira_domain,
        }

    async def to_json(self) -> str:
        """Return a json string representation of the UserMetadataModel."""
        return json.dumps(await self.to_serializable_dict())
