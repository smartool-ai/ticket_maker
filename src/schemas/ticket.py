from typing import List, Optional

from src.lib.loggers import get_module_logger

from pydantic import BaseModel, Field


logger = get_module_logger()


class Ticket(BaseModel):
    """
    Represents a ticket with subject, body, and estimation points.
    """
    subject: str
    body: str
    estimation_points: int = Field(..., alias="estimationpoints")


class TicketList(BaseModel):
    """
    Represents a list of tickets.
    """
    tickets: List[Ticket]


class TicketGenerationSchema(BaseModel):
    """
    Represents the schema for ticket generation.
    """
    ticket_generation_datetime: str


class SubTicketGenerationSchema(BaseModel):
    """
    Represents the schema for ticket generation.
    """
    sub_ticket_id: str


class TicketParamsSchema(BaseModel):
    """
    Represents the schema for ticket parameters.
    """
    name: str
    description: Optional[str]
    estimate: Optional[int]
