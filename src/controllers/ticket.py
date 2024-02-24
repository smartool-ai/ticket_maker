from logging import getLogger
from typing import Dict, Optional

from fastapi import APIRouter, Depends

from src.lib.enums import PlatformEnum
from src.lib.authorized_api_handler import authorized_api_handler
from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.ticket import TicketModel
from src.schemas.ticket import TicketGenerationSchema, TicketList
from src.services.ticket import get_tickets, invoke_ticket_generation_lambda

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:upload_transcripts"
)


@router.post("/file/{file_name}/tickets")
@authorized_api_handler()
async def invoke_ticket_generation(
    file_name: str,
    number_of_tickets: Optional[int] = 10,
    platform: Optional[PlatformEnum] = PlatformEnum.JIRA,
    user: Dict = Depends(granted_user),
) -> TicketGenerationSchema:
    """
    This endpoint is for generating tickets from a transcript. It invokes a long
    running lambda function to generate the tickets and returns the datetime when the
    lambda was invoked. The tickets can be retrieved using the datetime returned.

    Args:
        file_name (str): The name of the file to generate tickets from.
        number_of_tickets (Optional[int], optional): The number of tickets to generate. Defaults to 10.
        platform (Optional[PlatformEnum], optional): The platform to generate the tickets for. Defaults to PlatformEnum.JIRA.
        user (Dict, optional): The user making the request. Defaults to Depends(granted_user).

    Returns:
        TicketGenerationSchema: The datetime when the lambda was invoked.
    """
    # Invoke the ticket generation lambda function
    ticket_generation_datetime: str = await invoke_ticket_generation_lambda(
        document_id=file_name,
        user_id=user.get("sub"),
        number_of_tickets=number_of_tickets,
        platform=platform,
    )

    return {"ticket_generation_datetime": ticket_generation_datetime}


@router.get("/file/{file_name}/tickets")
@authorized_api_handler(models_to_initialize=[TicketModel])
async def get_tickets_by_generation_time(
    file_name: str,
    generation_datetime: str,
    _: Dict = Depends(granted_user),
) -> TicketList:
    """
    This endpoint is for retrieving tickets generated from a transcript using the
    datetime when the lambda was invoked.

    Args:
        file_name (str): The name of the file to retrieve tickets from.
        generation_datetime (str): The datetime when the lambda was invoked.
        _: Dict, optional): The user making the request. Defaults to Depends(granted_user).

    Returns:
        TicketList: The list of tickets generated from the transcript.
    """
    # Get the tickets generated at the specified datetime
    ticket: Optional[TicketModel] = await get_tickets(
        document_id=file_name, generation_datetime=generation_datetime
    )

    if not ticket:
        return {"tickets": []}

    # Convert the ticket object to a serializable dictionary
    ticket_dict: dict = await ticket.to_serializable_dict()

    return {"tickets": ticket_dict.get("tickets")}
