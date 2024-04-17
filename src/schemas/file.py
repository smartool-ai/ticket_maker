from typing import List

from pydantic import BaseModel, Field, validator


class FileSchema(BaseModel):
    document_id: str = Field(..., serialization_alias="name")
    document_type: str
    size: float


class FileListSchema(BaseModel):
    documents: List[FileSchema]
