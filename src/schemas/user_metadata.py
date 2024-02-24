from typing import Optional
from pydantic import BaseModel


class UserMetadataSchema(BaseModel):
    """
    Represents the schema for user metadata.
    """

    email: Optional[str] = None  # User's email address
    jira_email: Optional[str] = None  # User's Jira email address
    jira_api_key: Optional[str] = None  # User's Jira API key
