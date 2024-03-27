from typing import List

from pydantic import BaseModel


class FileSchema(BaseModel):
    document_id: str
    document_type: str


class FileListSchema(BaseModel):
    documents: List[FileSchema]
