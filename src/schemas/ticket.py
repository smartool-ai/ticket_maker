from typing import List
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    subject: str
    body: str
    estimation_points: int = Field(..., alias="estimationPoints")


class TicketList(BaseModel):
    tickets: List[Ticket]
