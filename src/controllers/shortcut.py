import datetime
from logging import getLogger
import os
from typing import Dict

from fastapi import APIRouter, Depends
from pixelum_core.api.authorized_api_handler import authorized_api_handler

from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.user_metadata import UserMetadataModel
from src.schemas.user_metadata import ShortcutWorkflowResponseSchema
from src.services.shortcut import (
    get_shortcut_workflows
)

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:upload_transcripts"
)
safe_endpoints = True if os.getenv("STAGE_NAME") != "prod" else False


@router.get("/shortcut/workflows", tags=["Shortcut"])
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def get_workflows(
    api_key: str,
    _: UserMetadataModel = Depends(granted_user)
) -> ShortcutWorkflowResponseSchema:
    """
    Get the list of shortcut workflows

    Args:
        user (UserMetadataModel, optional): The user to get the workflows for. Defaults to Depends(granted_user).

    Returns:
        Dict: The list of shortcut workflows.
    """
    resp = {
        "workflows": await get_shortcut_workflows(api_key)
    }

    return resp
