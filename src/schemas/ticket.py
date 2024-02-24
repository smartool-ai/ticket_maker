from typing import List
from pydantic import BaseModel, Field


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
