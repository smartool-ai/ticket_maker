from typing import Optional, Union
from pydantic import BaseModel


class UserMetadataSchema(BaseModel):
    """
    Represents the schema for user metadata.
    """

    email: Optional[str] = None  # User's email address
    jira_email: Optional[str] = None  # User's Jira email address
    jira_api_key: Optional[str] = None  # User's Jira API key


class JiraParamsSchema(BaseModel):
    jira_domain: str
    jira_api_key: str


class AsanaParamsSchema(BaseModel):
    asana_domain: str
    asana_api_key: str


class ServiceParamsSchema(BaseModel):
    params: Union[JiraParamsSchema, AsanaParamsSchema]
