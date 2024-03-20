import datetime
import json
import os
from typing import Any, Dict

from src.lib.dynamo_utils import BaseModel
from src.lib.loggers import get_module_logger

from pynamodb.attributes import (
    NumberAttribute,
    UnicodeAttribute,
)
from pynamodb.expressions.condition import Condition


logger = get_module_logger()


class Transaction(BaseModel):
    """
    Represents a transaction in the system.
    """

    class Meta:
        table_name = "Transaction"
        region = os.getenv("AWS_REGION", "us-west-2")

    user_id = UnicodeAttribute(hash_key=True)
    transaction_id = UnicodeAttribute(range_key=True)
    amount = NumberAttribute()
    currency = UnicodeAttribute()
    token = UnicodeAttribute()
    created_at = UnicodeAttribute(default=datetime.datetime.now().isoformat())

    @classmethod
    async def initialize(
        cls,
        user_id: str,
        transaction_id: str,
        amount: int,
        currency: str,
        token: str,
    ) -> "Transaction":
        """
        Initialize a new Transaction instance.
        """
        transaction = cls(
            user_id=user_id,
            transaction_id=transaction_id,
            amount=amount,
            currency=currency,
            token=token,
        )
        transaction.save()
        return transaction

    async def save(self, condition: Condition | None = None, *, add_version_condition: bool = True) -> Dict[str, Any]:
        return super().save(condition, add_version_condition=add_version_condition)

    async def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value)

    async def to_serializable_dict(self) -> dict:
        """
        Convert the transaction object to a serializable dictionary.
        """
        return {
            "user_id": self.user_id,
            "transaction_id": self.transaction_id,
            "amount": self.amount,
            "currency": self.currency,
            "token": self.token,
            "created_at": self.created_at,
        }

    async def to_json(self) -> str:
        """
        Convert the transaction object to a JSON string.
        """
        return json.dumps(await self.to_serializable_dict())
