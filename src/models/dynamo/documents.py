import datetime
import json
import os
from typing import Any, Dict, Optional

from src.lib.dynamo_utils import BaseModel
# from src.lib.enums import DocumentType
from src.lib.loggers import get_module_logger

from pynamodb.attributes import UnicodeAttribute
from pynamodb.expressions.condition import Condition


logger = get_module_logger()


class DocumentsModel(BaseModel):
    """
    Model for storing documents.

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    class Meta:
        table_name = "Document"
        region = os.getenv("AWS_REGION", "us-west-2")

    user_id = UnicodeAttribute(range_key=True)
    document_id = UnicodeAttribute(hash_key=True)
    document_type = UnicodeAttribute(null=False)
    memo = UnicodeAttribute(null=True)

    @classmethod
    async def initialize(
        cls,
        user_id: str,
        document_id: str,
        document_type: str,
        memo: Optional[str] = None,
    ) -> "DocumentsModel":
        document = DocumentsModel(
            user_id=user_id,
            document_id=document_id,
            document_type=document_type,
            created_datetime=datetime.datetime.now(),
            memo=memo,
        )

        return document

    async def save(
        self,
        condition: Optional[Condition] = None
    ) -> Dict[str, Any]:
        """Save the document to DynamoDB."""
        return super().save(
            condition=condition, add_version_condition=True
        )

    async def __eq__(self, other: Any) -> bool:
        """Return True if two records have the same attributes.

        We exclude created_datetime because serializing and
        deserializing the datetime object causes them to be
        no longer equal.
        """
        if not isinstance(other, type(self)):
            return False

        return self.user_id == other.user_id and self.document_id == other.document_id

    async def to_serializable_dict(self) -> dict:
        """Return the document as a serializable dict."""
        return {
            "user_id": self.user_id,
            "document_id": self.document_id,
            "document_type": self.document_type,
            "created_datetime": self.created_datetime,
            "memo": self.memo,
        }

    async def to_json(self) -> str:
        """Return the document as a json string."""

        return json.dumps(await self.to_serializable_dict())
