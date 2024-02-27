from logging import getLogger
from typing import Dict

from fastapi import APIRouter, Depends

from src.lib.authorized_api_handler import authorized_api_handler
from src.lib.enums import PlatformEnum
from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.user_metadata import UserMetadataModel
from src.schemas.user_metadata import PlatformParamsSchema, UserMetadataSchema
from src.services.user_metadata import add_or_update_user_metadata, link_jira, link_shortcut

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
        user_metadata (UserMetadataSchema): The user metadata to add or update.
        user (Dict, optional): The user dictionary obtained from the token. Defaults to Depends(granted_user).

    Returns:
        Dict: The updated user metadata.
    """
    # Extract the user ID from the token
    user_id = user.get("sub").split("|")[1]

    # Add or update the user metadata in the database
    user_metadata_model: UserMetadataModel = await add_or_update_user_metadata(
        user_id, **user_metadata.model_dump()
    )

    # Convert the user metadata model to a serializable dictionary
    return await user_metadata_model.to_serializable_dict()


@router.put("/user-metadata/link")
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def link_ticket_service(
    body: PlatformParamsSchema,
    platform: PlatformEnum,
    user: UserMetadataModel = Depends(granted_user),
) -> Dict:
    """
    Link a ticket service to a user

    Args:
        platform (PlatformEnum): The ticket platform to link.
        body (Dict): The parameters to link the ticket service.
        user (UserMetadataModel, optional): The user to link the ticket service to. Defaults to Depends(granted_user).

    Returns:
        Dict: The updated user metadata.
    """

    match platform:
        case PlatformEnum.JIRA:
            user_metadata: UserMetadataModel = await link_jira(
                user, **body.model_dump()
            )
        case PlatformEnum.SHORTCUT:
            user_metadata: UserMetadataModel = await link_shortcut(
                user, **body.model_dump(exclude_none=True)
            )
        case _:
            raise ValueError(f"Service {platform} not supported at this time.")

    return await user_metadata.to_serializable_dict()
