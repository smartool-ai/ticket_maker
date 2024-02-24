from typing import Optional, Union
from pydantic import BaseModel


class UserMetadataSchema(BaseModel):
    email: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_key: Optional[str] = None


class JiraParamsSchema(BaseModel):
    jira_domain: str
    jira_api_key: str


class AsanaParamsSchema(BaseModel):
    asana_domain: str
    asana_api_key: str


class ServiceParamsSchema(BaseModel):
    params: Union[JiraParamsSchema, AsanaParamsSchema]
