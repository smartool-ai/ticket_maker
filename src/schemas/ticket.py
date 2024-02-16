from typing import List
from pydantic import BaseModel


class Ticket(BaseModel):
    subject: str
    body: str
    estimation_points: str


class TicketList(BaseModel):
    tickets: List[Ticket]


class TicketGenerationSchema(BaseModel):
    ticket_generation_datetime: str
