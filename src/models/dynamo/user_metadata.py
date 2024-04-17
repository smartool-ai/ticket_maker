import datetime
import json
import os
from typing import Any, Dict, Optional

from pixelum_core.errors.custom_exceptions import PlatformLinkError
from pixelum_core.dynamo.base_model import BaseModel
from pixelum_core.loggers.loggers import get_module_logger
from pynamodb.attributes import ListAttribute, NumberAttribute, UnicodeAttribute
from pynamodb.expressions.condition import Condition

from src.lib.enums import PlatformEnum
from src.services.clients import PlatformClient


logger = get_module_logger()


class UserMetadataModel(BaseModel):
    """Model representing a User and their metadata.

    fields:
        user_id (str, hash_key): Auth0 id
        email (str): Email address
        signup_method (str): Signup method
        permissions (list): List of permissions
        jira_api_key (str): Jira API key
        jira_email (str): Jira email address
        jira_domain (str): Jira domain
        shortcut_api_key (str): Shortcut API key
        shortcut_project_id (str): Shortcut project id
        asana_workspace_id (str): Asana workspace id
        asana_personal_access_token (str): Asana personal access token
        asana_project_id (str): Asana project id
        generations_count (int): Number of ticket generations remaining
        file_uploads_count (int): Number of file uploads remaining
        renew_datetime (str): Datetime when the user's credentials need to be renewed
        subscription_tier (str): The user's subscription tier

        name (str): Auth0 user store field

    """

    class Meta:
        table_name = "UserMetadata"
        region = os.getenv("AWS_REGION", "us-west-2")

    user_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(null=True)
    signup_method = UnicodeAttribute(null=True)
    permissions = ListAttribute(of=UnicodeAttribute, null=True)
    jira_api_key = UnicodeAttribute(null=True)
    jira_email = UnicodeAttribute(null=True)
    jira_domain = UnicodeAttribute(null=True)
    shortcut_api_key = UnicodeAttribute(null=True)
    shortcut_workspace_id = UnicodeAttribute(null=True)
    asana_workspace_id = UnicodeAttribute(null=True)
    asana_personal_access_token = UnicodeAttribute(null=True)
    asana_project_id = UnicodeAttribute(null=True)

    parent_user_id = UnicodeAttribute(null=True)  # None if user is not a sub user

    sub_users_remaining = NumberAttribute(null=True, default=0)
    generations_count = NumberAttribute(null=True, default=10)
    file_uploads_count = NumberAttribute(null=True, default=3)
    renew_datetime = UnicodeAttribute(null=True)
    subscription_tier = UnicodeAttribute(null=True, default="free")

    # Auth0 user store fields
    name = UnicodeAttribute(null=True)

    @classmethod
    async def initialize(
        cls,
        user_id: str,
        email: Optional[str] = None,
        signup_method: Optional[str] = None,
        permissions: Optional[list] = None,
        jira_api_key: Optional[str] = None,
        jira_email: Optional[str] = None,
        jira_domain: Optional[str] = None,
        shortcut_api_key: Optional[str] = None,
        shortcut_workspace_id: Optional[str] = None,
        asana_workspace_id: Optional[str] = None,
        asana_personal_access_token: Optional[str] = None,
        asana_project_id: Optional[str] = None,
        parent_user_id: Optional[str] = None,
        sub_users_remaining: Optional[int] = 0,
        generations_count: Optional[int] = 10,
        file_uploads_count: Optional[int] = 3,
        renew_datetime: Optional[str] = None,
        subscription_tier: Optional[str] = "free",
        name: Optional[str] = None,
    ) -> "UserMetadataModel":
        """Initialize a UserMetadataModel."""
        user_metadata = UserMetadataModel(
            user_id=user_id,
            email=email,
            signup_method=signup_method,
            permissions=permissions,
            jira_api_key=jira_api_key,
            jira_email=jira_email,
            jira_domain=jira_domain,
            shortcut_api_key=shortcut_api_key,
            shortcut_workspace_id=shortcut_workspace_id,
            asana_workspace_id=asana_workspace_id,
            asana_personal_access_token=asana_personal_access_token,
            asana_project_id=asana_project_id,
            parent_user_id=parent_user_id,
            sub_users_remaining=sub_users_remaining,
            generations_count=generations_count,
            file_uploads_count=file_uploads_count,
            created_datetime=datetime.datetime.now(),
            renew_datetime=(
                renew_datetime
                if renew_datetime
                else (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
            ),
            subscription_tier=subscription_tier,
            name=name,
        )

        return user_metadata

    @classmethod
    def synchronous_initialize(
        cls,
        user_id: str,
        email: Optional[str] = None,
        signup_method: Optional[str] = None,
        permissions: Optional[list] = None,
        jira_api_key: Optional[str] = None,
        jira_email: Optional[str] = None,
        jira_domain: Optional[str] = None,
        shortcut_api_key: Optional[str] = None,
        shortcut_workspace_id: Optional[str] = None,
        asana_workspace_id: Optional[str] = None,
        asana_personal_access_token: Optional[str] = None,
        asana_project_id: Optional[str] = None,
        parent_user_id: Optional[str] = None,
        sub_users_remaining: Optional[int] = 0,
        generations_count: Optional[int] = 10,
        file_uploads_count: Optional[int] = 3,
        renew_datetime: Optional[str] = None,
        subscription_tier: Optional[str] = "free",
        name: Optional[str] = None,
    ) -> "UserMetadataModel":
        """Initialize a UserMetadataModel synchronously."""
        user_metadata = UserMetadataModel(
            user_id=user_id,
            email=email,
            signup_method=signup_method,
            permissions=permissions,
            jira_api_key=jira_api_key,
            jira_email=jira_email,
            jira_domain=jira_domain,
            shortcut_api_key=shortcut_api_key,
            shortcut_workspace_id=shortcut_workspace_id,
            asana_workspace_id=asana_workspace_id,
            asana_personal_access_token=asana_personal_access_token,
            asana_project_id=asana_project_id,
            parent_user_id=parent_user_id,
            sub_users_remaining=sub_users_remaining,
            generations_count=generations_count,
            file_uploads_count=file_uploads_count,
            created_datetime=datetime.datetime.now(),
            renew_datetime=(
                renew_datetime
                if renew_datetime
                else (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat()
            ),
            subscription_tier=subscription_tier,
            name=name,
        )

        return user_metadata

    async def find_subscription_tier(self) -> str:
        """Find the subscription tier of the user from the permissions."""
        for permission in self.permissions:
            if "SUBSCRIPTION" in permission:
                return permission.split(":")[1]

        return "free"

    async def check_platform_linked(self) -> dict:
        """Check if the user has linked a platform."""
        jira: bool = getattr(self, "jira_api_key") is not None
        shortcut: bool = getattr(self, "shortcut_api_key") is not None
        asana: bool = getattr(self, "asana_workspace_id") is not None

        platforms_linked = {"jira": jira, "shortcut": shortcut, "asana": asana}

        return platforms_linked

    async def get_platform_client(self, platform: PlatformEnum) -> PlatformClient:
        """Get the platform client for the user."""
        platform_linked = await self.check_platform_linked()

        if not platform_linked.get(platform.name.lower(), False):
            raise PlatformLinkError(
                f"User does not have {platform.name} credentials. Please link your {platform.name} credentials."
            )

        init_params = dict()
        match platform:
            case PlatformEnum.JIRA:
                init_params["server"] = self.jira_domain
                init_params["token_auth"] = self.jira_api_key
                init_params["email"] = self.jira_email
            case PlatformEnum.SHORTCUT:
                init_params["api_token"] = self.shortcut_api_key
                init_params["project_id"] = self.shortcut_workspace_id
            case PlatformEnum.ASANA:
                init_params["workspace_id"] = self.asana_workspace_id
                init_params["personal_access_token"] = self.asana_personal_access_token
                init_params["project_id"] = self.asana_project_id

        return PlatformClient(platform, **init_params)

    async def get_platform_details(self) -> dict:
        """Get the platform details for the user."""
        platforms = await self.check_platform_linked()
        platform_details = {}
        for platform, linked in platforms.items():
            if linked:
                platform_client: PlatformClient = await self.get_platform_client(PlatformEnum[platform.upper()])
                platform_details[platform] = await platform_client.get_platform_details()
            else:
                platform_details[platform] = None
        return platform_details

    async def get_parent_user(self) -> Optional["UserMetadataModel"]:
        """Get the parent user of the sub user."""
        if not self.parent_user_id:
            return None

        try:
            return await UserMetadataModel.get(self.parent_user_id)
        except UserMetadataModel.DoesNotExist:
            logger.info(f"Parent user with ID {self.parent_user_id} not found.")
            return None

    async def get_parent_user_upload_count(self) -> int:
        """Get the file uploads count of the parent user."""
        parent_user = await self.get_parent_user()
        if parent_user:
            return parent_user.file_uploads_count
        return 0

    async def get_parent_user_generations_count(self) -> int:
        """Get the generations count of the parent user."""
        parent_user = await self.get_parent_user()
        if parent_user:
            return parent_user.generations_count
        return 0

    async def get_parent_user_subscription_tier(self) -> str:
        """Get the subscription tier of the parent user."""
        parent_user = await self.get_parent_user()
        if parent_user:
            return parent_user.subscription_tier
        return "free"

    async def get_sub_accounts(self) -> list:
        """Get the sub accounts of the user."""
        try:
            users_iterator = await UserMetadataModel.query(
                UserMetadataModel.parent_user_id == self.user_id
            )
        except UserMetadataModel.DoesNotExist:
            return []

        return [user for user in users_iterator]

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
            "renew_datetime": self.renew_datetime,
            "subscription_tier": self.subscription_tier.upper(),
            "signup_method": self.signup_method,
        }

    async def to_json(self) -> str:
        """Return a json string representation of the UserMetadataModel."""
        return json.dumps(await self.to_serializable_dict())
