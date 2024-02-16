from typing import List
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    subject: str
    body: str
    estimation_points: int = Field(..., alias="estimationpoints")


class TicketList(BaseModel):
    tickets: List[Ticket]


class TicketGenerationSchema(BaseModel):
    ticket_generation_datetime: str
