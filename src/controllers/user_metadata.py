from logging import getLogger
from typing import Dict, Optional

from fastapi import APIRouter, Depends

from src.lib.authorized_api_handler import authorized_api_handler
from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.user_metadata import UserMetadataModel
from src.schemas.user_metadata import UserMetadataSchema
from src.services.user_metadata import add_or_update_user_metadata

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:upload_transcripts"
)


@router.put("/user-metadata")
@authorized_api_handler()
async def put_user_metadata(
    user_metadata: UserMetadataSchema, user: Dict = Depends(granted_user)
) -> Dict:
    """
    Add or update user metadata

    Args:
        user_metadata (dict): The user metadata to add or update.
        user (Dict, optional): _description_. Defaults to Depends(granted_user).

    Returns:
        Dict: The updated user metadata.
    """
    user_id = user.get("sub").split("|")[1]

    user_metadata_model: UserMetadataModel = await add_or_update_user_metadata(
        user_id, **user_metadata.model_dump()
    )

    return await user_metadata_model.to_serializable_dict()
