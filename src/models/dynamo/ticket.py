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


class Ticket(MapAttribute):
    """
    Represents a ticket in the system.
    """

    subject = UnicodeAttribute()
    body = UnicodeAttribute()
    estimationpoints = NumberAttribute()

    async def to_serializable_dict(self) -> dict:
        """
        Convert the ticket object to a serializable dictionary.
        """
        return {
            "subject": self.subject,
            "body": self.body,
            "estimationpoints": self.estimationpoints,
        }


class SubTicket(BaseModel):
    """
    Sub-ticket model used as an expansion of a higher level ticket. For example, the tech story to a story.
    """

    class Meta:
        table_name = "SubTicket"
        region = os.getenv("AWS_REGION", "us-west-2")

    user_id = UnicodeAttribute(hash_key=True)
    sub_ticket_id = UnicodeAttribute(range_key=True)
    sub_ticket_prompt = UnicodeAttribute()
    ticket = Ticket()

    @classmethod
    async def initialize(
        cls, user_id: str, sub_ticket_id: str, sub_ticket_prompt: str, ticket: Ticket
    ) -> "SubTicket":
        """
        Initialize a new SubTicketModel instance.

        Args:
            user_id (str): The user ID.
            sub_ticket_id (str): The sub-ticket ID.
            ticket (Ticket): The ticket object.

        Returns:
            SubTicketModel: The initialized SubTicketModel instance.
        """
        sub_ticket = SubTicket(
            user_id=user_id, sub_ticket_id=sub_ticket_id, sub_ticket_prompt=sub_ticket_prompt, ticket=ticket
        )

        return sub_ticket

    async def save(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """
        Save the sub-ticket to DynamoDB.

        Args:
            condition (Optional[Condition]): The condition for saving the sub-ticket.

        Returns:
            Dict[str, Any]: The result of the save operation.
        """
        return super().save(condition)

    async def delete(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """
        Delete the sub-ticket from DynamoDB.

        Args:
            condition (Optional[Condition]): The condition for deleting the sub-ticket.

        Returns:
            Dict[str, Any]: The result of the delete operation.
        """
        return super().delete(condition)

    async def __eq__(self, __value: object) -> bool:
        """
        Compare the sub-ticket with another value for equality.

        Args:
            __value (object): The value to compare with.

        Returns:
            bool: True if the sub-ticket is equal to the value, False otherwise.
        """
        return super().__eq__(__value)

    async def to_serializable_dict(self) -> dict:
        """
        Convert the sub-ticket model to a serializable dictionary.

        Returns:
            dict: The serializable dictionary representation of the sub-ticket model.
        """
        return {
            "user_id": self.user_id,
            "sub_ticket_id": self.sub_ticket_id,
            "sub_ticket_prompt": self.sub_ticket_prompt,
            "ticket": await self.ticket.to_serializable_dict(),
        }

    async def to_json(self) -> str:
        """
        Convert the sub-ticket model to a JSON string.

        Returns:
            str: The JSON string representation of the sub-ticket model.
        """
        return json.dumps(await self.to_serializable_dict())


class Ticket(BaseModel):
    """
    Model for storing tickets.
    """

    class Meta:
        table_name = "Ticket"
        region = os.getenv("AWS_REGION", "us-west-2")

    document_id = UnicodeAttribute(hash_key=True)
    created_datetime = UnicodeAttribute(range_key=True)
    tickets = ListAttribute(of=Ticket)
    original_prompt = UnicodeAttribute()

    @classmethod
    async def initialize(
        cls,
        document_id: str,
        tickets: list[Dict[str, Any]],
        original_prompt: str,
    ) -> "Ticket":
        """
        Initialize a new TicketModel instance.

        Args:
            document_id (str): The document ID.
            tickets (list[Dict[str, Any]]): List of ticket dictionaries.

        Returns:
            TicketModel: The initialized TicketModel instance.
        """
        ticket = Ticket(
            document_id=document_id,
            created_datetime=datetime.datetime.now(),
            tickets=tickets,
            original_prompt=original_prompt,
        )

        return ticket

    async def save(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """
        Save the ticket to DynamoDB.

        Args:
            condition (Optional[Condition]): The condition for saving the ticket.

        Returns:
            Dict[str, Any]: The result of the save operation.
        """
        return super().save(condition)

    async def delete(self, condition: Optional[Condition] = None) -> Dict[str, Any]:
        """
        Delete the ticket from DynamoDB.

        Args:
            condition (Optional[Condition]): The condition for deleting the ticket.

        Returns:
            Dict[str, Any]: The result of the delete operation.
        """
        return super().delete(condition)

    async def __eq__(self, __value: object) -> bool:
        """
        Compare the ticket with another value for equality.

        Args:
            __value (object): The value to compare with.

        Returns:
            bool: True if the ticket is equal to the value, False otherwise.
        """
        return super().__eq__(__value)

    async def to_serializable_dict(self) -> dict:
        """
        Convert the ticket model to a serializable dictionary.

        Returns:
            dict: The serializable dictionary representation of the ticket model.
        """
        return {
            "document_id": self.document_id,
            "created_datetime": self.created_datetime,
            "tickets": (
                [await ticket.to_serializable_dict() for ticket in self.tickets]
                if self.tickets
                else []
            ),
            "original_prompt": self.original_prompt,
        }

    async def to_json(self) -> str:
        """
        Convert the ticket model to a JSON string.

        Returns:
            str: The JSON string representation of the ticket model.
        """
        return json.dumps(await self.to_serializable_dict())
