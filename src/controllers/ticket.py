from logging import getLogger
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Response

from src.lib.enums import PlatformEnum
from src.lib.authorized_api_handler import authorized_api_handler
from src.lib.token_authentication import TokenAuthentication
from src.schemas.ticket import TicketList
from src.services.file_management import download_file_from_s3
from src.services.ticket import generate_tickets

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:upload_transcripts"
)


@router.get("/file/{file_name}/tickets")
@authorized_api_handler()
async def get_file(
    file_name: str,
    number_of_tickets: Optional[int] = 10,
    platform: Optional[PlatformEnum] = PlatformEnum.JIRA,
    user: Dict = Depends(granted_user),
) -> TicketList:
    """Get file from S3"""
    logger.info(f"Getting file from S3: {file_name}")
    _: str = user.get("sub").split("|")[1]
    resp: str = download_file_from_s3(file_name)

    tickets: dict = generate_tickets(prompt=resp, number_of_tickets=number_of_tickets, platform=platform)

    return tickets
