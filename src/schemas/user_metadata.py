from typing import List, Optional, Tuple
from pydantic import BaseModel

from pixelum_core.enums.enums import SubscriptionTier


class PlatformsLinkedSchema(BaseModel):
    """
    Represents the schema for platforms linked to the user.
    """
    jira: Optional[bool] = None  # Jira platform linked
    shortcut: Optional[bool] = None  # Shortcut platform linked
    asana: Optional[bool] = None  # Asana platform linked


class UserMetadataSchema(BaseModel):
    """
    Represents the schema for user metadata.
    """
    email: Optional[str] = None  # User's email address
    jira_email: Optional[str] = None  # User's Jira email address
    jira_api_key: Optional[str] = None  # User's Jira API key
    jira_domain: Optional[str] = None  # User's Jira domain
    shortcut_api_key: Optional[str] = None  # User's Shortcut API key
    shortcut_project_id: Optional[str] = None  # User's Shortcut project ID
    asana_workspace_id: Optional[str] = None  # User's Asana workspace ID
    asana_personal_access_token: Optional[str] = None  # User's Asana personal access token
    asana_project_id: Optional[str] = None  # User's Asana project ID
    renew_datetime: Optional[str] = None  # Renew datetime

    # Auth0 user store fields
    name: Optional[str] = None  # User's name


class UserMetadataReturnSchema(BaseModel):
    """
    Represents the data returned for user metadata on GET requests.
    """
    email: Optional[str] = None  # User's email address
    platforms_linked: Optional[PlatformsLinkedSchema] = None  # List of platforms linked to the user
    generations_count: Optional[int] = None  # Number of generations
    file_uploads_count: Optional[int] = None  # Number of file uploads
    renew_datetime: Optional[str] = None  # Renew datetime
    subscription_tier: Optional[SubscriptionTier] = None  # Subscription tier
    signup_method: Optional[str] = None  # Signup method


class JiraParamsSchema(BaseModel):
    server: str
    api_key: str
    email: str


class ShortcutParamsSchema(BaseModel):
    api_key: str


class AsanaParamsSchema(BaseModel):
    asana_api_key: str


class JiraPlatformDetails(BaseModel):
    projects: Optional[List[str]]


class AsanaPlatformDetails(BaseModel):
    projects: Optional[List[str]]


class ShortcutPlatformDetails(BaseModel):
    workflow_ids: Optional[List[Tuple[str, str]]]


class PlatformDetailsSchema(BaseModel):
    jira: Optional[JiraPlatformDetails]
    asana: Optional[AsanaPlatformDetails]
    shortcut: Optional[ShortcutPlatformDetails]


class PlatformParamsSchema(BaseModel):
    # params: Union[JiraParamsSchema, AsanaParamsSchema, ShortcutParamsSchema]
    server: Optional[str]
    api_key: Optional[str]
    email: Optional[str]
    project_id: Optional[str]
    personal_access_token: Optional[str]
    workspace_id: Optional[str]
