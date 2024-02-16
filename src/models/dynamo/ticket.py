import datetime
import json
import os
from typing import Any, Dict, Optional

from src.lib.dynamo_utils import BaseModel
from src.lib.loggers import get_module_logger

from pynamodb.attributes import (
    ListAttribute,
    MapAttribute,
    NumberAttribute,
    UnicodeAttribute,
)
from pynamodb.expressions.condition import Condition


logger = get_module_logger()


class TicketModel(MapAttribute):
    subject = UnicodeAttribute()
    body = UnicodeAttribute()
    estimationpoints = NumberAttribute()

    async def to_serializable_dict(self) -> dict:
        return {
            "subject": self.subject,
            "body": self.body,
            "estimationpoints": self.estimationpoints,
        }


class TicketModel(BaseModel):
    """
    Model for storing tickets.

    Args:
        BaseModel (_type_): _description_

    Returns:
        _type_: _description_
    """

    class Meta:
        table_name = "Ticket"
        region = os.getenv("AWS_REGION", "us-west-2")

    document_id = UnicodeAttribute(hash_key=True)
    created_datetime = UnicodeAttribute(range_key=True)
    tickets = ListAttribute(of=TicketModel)

    @classmethod
    async def initialize(
        cls,
        document_id: str,
        tickets: list[Dict[str, Any]],
    ) -> "TicketModel":
        ticket = TicketModel(
            document_id=document_id,
            created_datetime=datetime.datetime.now(),
            tickets=tickets,
        )

        return ticket

    async def save(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """Save the ticket to DynamoDB."""
        return super().save(condition)

    async def delete(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """Delete the ticket from DynamoDB."""
        return super().delete(condition)

    async def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value)

    async def to_serializable_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "created_datetime": self.created_datetime,
            "tickets": (
                [await ticket.to_serializable_dict() for ticket in self.tickets]
                if self.tickets
                else []
            ),
        }

    async def to_json(self) -> str:
        return json.dumps(await self.to_serializable_dict())
