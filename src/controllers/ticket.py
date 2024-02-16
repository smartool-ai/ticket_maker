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
async def get_file(
    file_name: str,
    number_of_tickets: Optional[int] = 10,
    platform: Optional[PlatformEnum] = PlatformEnum.JIRA,
    user: Dict = Depends(granted_user),
) -> TicketGenerationSchema:
    """Get file from S3"""
    ticket_generation_datetime: str = await invoke_ticket_generation_lambda(
        document_id=file_name,
        user_id=user.get("sub"),
        number_of_tickets=number_of_tickets,
        platform=platform,
    )

    # logger.info(f"Getting file from S3: {file_name}")
    # _: str = user.get("sub").split("|")[1]
    # resp: str = download_file_from_s3(file_name)

    # logger.info(f"Generating tickets from transcript: {file_name}")
    # tickets: dict = generate_tickets(prompt=resp, number_of_tickets=number_of_tickets, platform=platform)
    # logger.info(f"Tickets generated from transcript: {tickets}")

    return {"ticket_generation_datetime": ticket_generation_datetime}


@router.get("/file/{file_name}/tickets")
@authorized_api_handler(models_to_initialize=[TicketModel])
async def get_tickets_by_generation_time(
    file_name: str,
    generation_datetime: str,
    _: Dict = Depends(granted_user),
) -> TicketList:
    """Get all tickets"""
    ticket: Optional[TicketModel] = await get_tickets(
        document_id=file_name, generation_datetime=generation_datetime
    )

    if not ticket:
        return {"tickets": []}

    ticket_dict: dict = await ticket.to_serializable_dict()

    return {"tickets": ticket_dict.get("tickets")}
