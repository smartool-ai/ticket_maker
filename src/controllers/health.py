from logging import getLogger
from typing import Dict

from fastapi import APIRouter
from pixelum_core.api.authorized_api_handler import authorized_api_handler

router = APIRouter()
logger = getLogger(__name__)


@router.get("/health")
@authorized_api_handler()
async def check_health(
) -> Dict:
    """
    This endpoint is for checking the health of the service.
    """
    return {"status": "healthy"}
