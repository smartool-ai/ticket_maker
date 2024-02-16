from logging import getLogger
from typing import List, Dict

from fastapi import APIRouter, Depends

from src.lib.token_authentication import TokenAuthentication

from src.services.asset import list_assets

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:brassica_offerings"
)


@router.get("/asset")
async def get_all_assets(user: Dict = Depends(granted_user)) -> List:
    return [asset.to_dict() for asset in list_assets()]
