from typing import Optional
from pydantic import BaseModel


class UserMetadataSchema(BaseModel):
    """
    Represents the schema for user metadata.
    """
    email: Optional[str] = None  # User's email address
    jira_email: Optional[str] = None  # User's Jira email address
    jira_api_key: Optional[str] = None  # User's Jira API key
    jira_domain: Optional[str] = None  # User's Jira domain
    shortcut_api_key: Optional[str] = None  # User's Shortcut API key


class JiraParamsSchema(BaseModel):
    server: str
    api_key: str
    email: str


class ShortcutParamsSchema(BaseModel):
    api_key: str


class AsanaParamsSchema(BaseModel):
    asana_api_key: str


class PlatformParamsSchema(BaseModel):
    # params: Union[JiraParamsSchema, AsanaParamsSchema, ShortcutParamsSchema]
    server: Optional[str]
    api_key: Optional[str]
    email: Optional[str]
    project_id: Optional[str]
