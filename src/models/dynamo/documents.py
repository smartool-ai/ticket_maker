import datetime
import json
import os
from typing import Any, Dict, Optional

from src.lib.dynamo_utils import BaseModel
from pynamodb.attributes import UnicodeAttribute
from pynamodb.expressions.condition import Condition
from src.lib.loggers import get_module_logger

logger = get_module_logger()


class DocumentsModel(BaseModel):
    """
    Model for storing documents.
    """

    class Meta:
        table_name = "Document"
        region = os.getenv("AWS_REGION", "us-west-2")

    user_id = UnicodeAttribute(hash_key=True)
    document_id = UnicodeAttribute(range_key=True)
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
        """
        Initialize a new DocumentsModel instance.

        Args:
            user_id (str): The user ID.
            document_id (str): The document ID.
            document_type (str): The document type.
            memo (str, optional): The document memo. Defaults to None.

        Returns:
            DocumentsModel: The initialized DocumentsModel instance.
        """
        document = DocumentsModel(
            user_id=user_id,
            document_id=document_id,
            document_type=document_type,
            created_datetime=datetime.datetime.now(),
            memo=memo,
        )

        return document

    async def save(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """
        Save the document to DynamoDB.

        Args:
            condition (Condition, optional): The condition for saving the document. Defaults to None.

        Returns:
            Dict[str, Any]: The saved document as a dictionary.
        """
        return super().save(condition=condition, add_version_condition=True)

    async def __eq__(self, other: Any) -> bool:
        """
        Compare two DocumentsModel instances for equality.

        Args:
            other (Any): The other instance to compare.

        Returns:
            bool: True if the two instances have the same attributes, False otherwise.
        """
        if not isinstance(other, type(self)):
            return False

        return self.user_id == other.user_id and self.document_id == other.document_id

    async def to_serializable_dict(self) -> dict:
        """
        Convert the document to a serializable dictionary.

        Returns:
            dict: The document as a serializable dictionary.
        """
        return {
            "user_id": self.user_id,
            "document_id": self.document_id,
            "document_type": self.document_type,
            "created_datetime": self.created_datetime,
            "memo": self.memo,
        }

    async def to_json(self) -> str:
        """
        Convert the document to a JSON string.

        Returns:
            str: The document as a JSON string.
        """
        return json.dumps(await self.to_serializable_dict())
