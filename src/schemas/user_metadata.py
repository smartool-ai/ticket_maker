from typing import Optional
from pydantic import BaseModel

class UserMetadataSchema(BaseModel):
    email: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_key: Optional[str] = None
