import datetime
import json
import os
from typing import Any, Dict, Optional
from src.lib.custom_exceptions import PlatformLinkError

from src.lib.dynamo_utils import BaseModel
from src.lib.enums import PlatformEnum
from src.lib.loggers import get_module_logger

from pynamodb.attributes import UnicodeAttribute, NumberAttribute
from pynamodb.expressions.condition import Condition

from src.services.clients import PlatformClient


logger = get_module_logger()


class UserMetadataModel(BaseModel):
    """Model representing a User and their metadata.

    fields:
        user_id (str, hash_key): Auth0 id
        email (str): Email address
        jira_api_key (str): Jira API key
        jira_email (str): Jira email address
        jira_domain (str): Jira domain
        shortcut_api_key (str): Shortcut API key
        generations_count (int): Number of ticket generations remaining
        file_uploads_count (int): Number of file uploads remaining
        renew_datetime (str): Datetime when the user's credentials need to be renewed
    """

    class Meta:
        table_name = "UserMetadata"
        region = os.getenv("AWS_REGION", "us-west-2")

    user_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(null=True)
    jira_api_key = UnicodeAttribute(null=True)
    jira_email = UnicodeAttribute(null=True)
    jira_domain = UnicodeAttribute(null=True)
    shortcut_api_key = UnicodeAttribute(null=True)
    shortcut_project_id = UnicodeAttribute(null=True)
    asana_workspace_id = UnicodeAttribute(null=True)
    asana_personal_access_token = UnicodeAttribute(null=True)
    asana_project_id = UnicodeAttribute(null=True)
    generations_count = NumberAttribute(null=True, default=10)
    file_uploads_count = NumberAttribute(null=True, default=3)
    renew_datetime = UnicodeAttribute(null=True)
    subscription_tier = UnicodeAttribute(null=True, default="free")

    @classmethod
    async def initialize(
        cls,
        user_id: str,
        email: Optional[str] = None,
        jira_api_key: Optional[str] = None,
        jira_email: Optional[str] = None,
        jira_domain: Optional[str] = None,
        shortcut_api_key: Optional[str] = None,
        shortcut_project_id: Optional[str] = None,
        asana_workspace_id: Optional[str] = None,
        asana_personal_access_token: Optional[str] = None,
        asana_project_id: Optional[str] = None,
        generations_count: Optional[int] = 10,
        file_uploads_count: Optional[int] = 3,
        renew_datetime: Optional[str] = None,
        subscription_tier: Optional[str] = "free",
    ) -> "UserMetadataModel":
        """Initialize a UserMetadataModel."""
        user_metadata = UserMetadataModel(
            user_id=user_id,
            email=email,
            jira_api_key=jira_api_key,
            jira_email=jira_email,
            jira_domain=jira_domain,
            shortcut_api_key=shortcut_api_key,
            shortcut_project_id=shortcut_project_id,
            asana_workspace_id=asana_workspace_id,
            asana_personal_access_token=asana_personal_access_token,
            asana_project_id=asana_project_id,
            generations_count=generations_count,
            file_uploads_count=file_uploads_count,
            created_datetime=datetime.datetime.now(),
            renew_datetime=renew_datetime if renew_datetime else (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
            subscription_tier=subscription_tier,
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
        shortcut_api_key: Optional[str] = None,
        shortcut_project_id: Optional[str] = None,
        asana_workspace_id: Optional[str] = None,
        asana_personal_access_token: Optional[str] = None,
        asana_project_id: Optional[str] = None,
        generations_count: Optional[int] = 10,
        file_uploads_count: Optional[int] = 3,
        renew_datetime: Optional[str] = None,
        subscription_tier: Optional[str] = "free",
    ) -> "UserMetadataModel":
        """Initialize a UserMetadataModel synchronously."""
        user_metadata = UserMetadataModel(
            user_id=user_id,
            email=email,
            jira_api_key=jira_api_key,
            jira_email=jira_email,
            jira_domain=jira_domain,
            shortcut_api_key=shortcut_api_key,
            shortcut_project_id=shortcut_project_id,
            asana_workspace_id=asana_workspace_id,
            asana_personal_access_token=asana_personal_access_token,
            asana_project_id=asana_project_id,
            generations_count=generations_count,
            file_uploads_count=file_uploads_count,
            created_datetime=datetime.datetime.now(),
            renew_datetime=renew_datetime if renew_datetime else (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
            subscription_tier=subscription_tier,
        )

        return user_metadata

    async def check_platform_linked(self) -> dict:
        """Check if the user has linked a platform."""
        jira: bool = getattr(self, "jira_api_key") is not None
        shortcut: bool = getattr(self, "shortcut_api_key") is not None
        asana: bool = getattr(self, "asana_workspace_id") is not None

        platforms_linked = {
            "jira": jira,
            "shortcut": shortcut,
            "asana": asana
        }

        return platforms_linked

    async def get_platform_client(self, platform: PlatformEnum) -> PlatformClient:
        """Get the platform client for the user."""
        platform_linked = await self.check_platform_linked()

        for platform_name, linked in platform_linked.items():
            if not linked:
                raise PlatformLinkError(f"User does not have {platform_name} credentials. Please link your {platform_name} credentials.")

        init_params = dict()
        match platform:
            case PlatformEnum.JIRA:
                init_params["server"] = self.jira_domain
                init_params["token_auth"] = self.jira_api_key
                init_params["email"] = self.jira_email
            case PlatformEnum.SHORTCUT:
                init_params["api_token"] = self.shortcut_api_key
            case PlatformEnum.ASANA:
                init_params["workspace_id"] = self.asana_workspace_id
                init_params["personal_access_token"] = self.asana_personal_access_token
                init_params["project_id"] = self.asana_project_id

        return PlatformClient(platform, **init_params)

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
            "email": self.email,
            "platforms_linked": await self.check_platform_linked(),
            "generations_count": self.generations_count,
            "file_uploads_count": self.file_uploads_count,
            "renew_datetime": self.renew_datetime
        }

    async def to_json(self) -> str:
        """Return a json string representation of the UserMetadataModel."""
        return json.dumps(await self.to_serializable_dict())
