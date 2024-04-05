import uuid
from logging import getLogger
from typing import Optional

from fastapi import APIRouter, Depends
from pixelum_core.api.authorized_api_handler import authorized_api_handler
from pixelum_core.errors.custom_exceptions import TicketGenerationLimitReachedError

from src.lib.enums import EventEnum, PlatformEnum
from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.ticket import SubTicket, Ticket
from src.models.dynamo.user_metadata import UserMetadataModel
from src.schemas.ticket import SubTicketGenerationSchema, TicketGenerationSchema, TicketList, TicketParamsSchema
from src.services.ticket import get_subticket, get_tickets, invoke_ticket_generation_lambda

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:upload_transcripts"
)


@router.post("/file/{file_name}/tickets", tags=["Ticket Management"])
@authorized_api_handler()
async def invoke_ticket_generation(
    file_name: str,
    number_of_tickets: Optional[int] = 10,
    platform: Optional[PlatformEnum] = PlatformEnum.JIRA,
    user: UserMetadataModel = Depends(granted_user),
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
    logger.info(f"User has {user.generations_count} ticket generations remaining")
    generations_count = 0

    # First check if the user is a sub-user and get the parent user's ticket generations count
    if user.parent_user_id:
        logger.info("User is a sub-user. Checking parent user's ticket generations count")
        generations_count = await user.get_parent_user_generations_count()
    else:  # If the user is not a sub-user, get the user's ticket generations count
        generations_count = user.generations_count

    if generations_count == 0:
        logger.error("User has reached the maximum number of ticket generations.")
        raise TicketGenerationLimitReachedError(message="User has reached the maximum number of ticket generations.")

    # Invoke the ticket generation lambda function
    ticket_generation_datetime: str = await invoke_ticket_generation_lambda(
        document_id=file_name,
        user_id=user.user_id,
        event=EventEnum.TICKET_GENERATION,
        number_of_tickets=number_of_tickets,
        platform=platform,
    )

    # Decrement the generations count for the user
    user.generations_count -= 1
    await user.save()

    return {"ticket_generation_datetime": ticket_generation_datetime}


@router.get("/file/{file_name}/tickets", tags=["Ticket Management"])
@authorized_api_handler(models_to_initialize=[Ticket])
async def get_tickets_by_generation_time(
    file_name: str,
    generation_datetime: str,
    _: UserMetadataModel = Depends(granted_user),
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
    ticket: Optional[Ticket] = await get_tickets(
        document_id=file_name, generation_datetime=generation_datetime
    )

    if not ticket:
        return {"tickets": []}

    # Convert the ticket object to a serializable dictionary
    ticket_dict: dict = await ticket.to_serializable_dict()

    # For each ticket create a uuid for the front end to use
    for t in ticket_dict.get("tickets"):
        t["id"] = uuid.uuid4().hex

    return {"tickets": ticket_dict.get("tickets")}


@router.post("/file/{file_name}/tickets/expand", tags=["Ticket Management"])
@authorized_api_handler(models_to_initialize=[Ticket])
async def expand_ticket(
    file_name: str,
    generation_datetime: str,
    body: TicketParamsSchema,
    user: UserMetadataModel = Depends(granted_user),
) -> SubTicketGenerationSchema:
    """
    This endpoint is for expanding a ticket into a list of sub tickets.

    Args:
        file_name (str): The name of the file to retrieve tickets from.
        generation_datetime (str): The datetime when the lambda was invoked.
        _: Dict, optional): The user making the request. Defaults to Depends(granted_user).

    Returns:
        TicketList: The list of sub tickets generated from the transcript.
    """
    logger.info(f"User has {user.generations_count} ticket generations remaining")
    generations_count = 0

    # First check if the user is a sub-user and get the parent user's ticket generations count
    if user.parent_user_id:
        logger.info("User is a sub-user. Checking parent user's ticket generations count")
        generations_count = await user.get_parent_user_generations_count()
    else:  # If the user is not a sub-user, get the user's ticket generations count
        generations_count = user.generations_count

    if generations_count == 0:
        logger.error("User has reached the maximum number of ticket generations.")
        raise TicketGenerationLimitReachedError(message="User has reached the maximum number of ticket generations.")

    sub_ticket_id: str = await invoke_ticket_generation_lambda(
        document_id=file_name,
        user_id=user.user_id,
        event=EventEnum.TICKET_EXPANSION,
        number_of_tickets=3,  # TODO: Make this a query parameter
        generation_datetime=generation_datetime,
        ticket=body.model_dump(),
    )

    # Decrement the generations count for the user
    user.generations_count -= 1
    await user.save()

    return {"sub_ticket_id": sub_ticket_id}


@router.get("/ticket/sub/{sub_ticket_id}", tags=["Ticket Management"])
@authorized_api_handler(models_to_initialize=[SubTicket])
async def get_sub_ticket(
    sub_ticket_id: str,
    user: UserMetadataModel = Depends(granted_user),
) -> TicketList:
    """
    This endpoint is for retrieving a sub ticket by its ID.
    """
    sub_ticket: Optional[SubTicket] = await get_subticket(sub_ticket_id, user.user_id)

    if sub_ticket is None:
        return {"tickets": []}

    sub_ticket_dict: dict = await sub_ticket.to_serializable_dict()

    for t in sub_ticket_dict.get("tickets"):
        t["id"] = uuid.uuid4().hex

    return {"tickets": sub_ticket_dict.get("tickets")}


@router.post("/ticket", tags=["Ticket Management"])
@authorized_api_handler()
async def create_ticket(
    platform: PlatformEnum,
    body: TicketParamsSchema,
    user: UserMetadataModel = Depends(granted_user),
) -> dict:
    """
    This endpoint is for creating a ticket in a platform.

    Args:
        platform (PlatformEnum): The platform to create the ticket in.
        body (TicketParamsSchema): The ticket parameters.
        user (Dict, optional): The user making the request. Defaults to Depends(granted_user).

    Returns:
        dict: The ticket that was created.
    """
    # Get the platform client for the user
    platform_client = await user.get_platform_client(platform)

    ticket_params: dict = body.model_dump()

    # Create the ticket in the specified platform
    ticket: dict = await platform_client.create_story(**ticket_params)

    return {"ticket": ticket}
