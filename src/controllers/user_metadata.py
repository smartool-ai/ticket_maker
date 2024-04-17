import datetime
from logging import getLogger
import os
from typing import Dict

from fastapi import APIRouter, Depends
from pixelum_core.api.authorized_api_handler import authorized_api_handler
from pixelum_core.errors.custom_exceptions import InvalidInput
from pixelum_core.enums.enums import SubscriptionTier

from src.lib.enums import PlatformEnum
from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.user_metadata import UserMetadataModel
from src.schemas.user_metadata import (
    PlatformDetailsSchema,
    PlatformParamsSchema,
    UserMetadataSchema,
    UserMetadataReturnSchema,
)
from src.services.user import update_auth0_user
from src.services.user_metadata import (
    add_or_update_user_metadata,
    get_user_metadata_by_user_id,
    link_asana,
    link_jira,
    link_shortcut,
)

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:upload_transcripts"
)
admin_user = token_authentication.require_user_with_permission("manage:admin")
safe_endpoints = True if os.getenv("STAGE_NAME") != "prod" else False


@router.put("/user-metadata", tags=["User Metadata"])
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def put_user_metadata(
    user_metadata: UserMetadataSchema, user: UserMetadataModel = Depends(granted_user)
) -> Dict:
    """
    Add or update user metadata

    Args:
        user_metadata (UserMetadataSchema): The user metadata to add or update.
        user (UserMetadataModel, optional): The user to add or update the metadata for. Defaults to Depends(granted_user).

    Returns:
        Dict: The updated user metadata.
    """
    # Separate out the auth0 user store fields to update separately
    auth0_user_store_fields = {
        "name": user_metadata.name,
    }
    signup_plat: str = user.signup_method if user.signup_method != "Username-Password-Authentication" else "auth0"

    if signup_plat != "auth0":
        logger.error(f'Cannot update user store fields: {user_metadata.name} if account used social login.')
    else:
        auth0_user_id = f"{signup_plat}|{user.user_id}"
        updated_auth0_user: dict = await update_auth0_user(
            auth0_user_id, **auth0_user_store_fields
        )

        if not updated_auth0_user:
            logger.error(
                f"Failed to update user {user.user_id} in Auth0 for fields {auth0_user_store_fields}"
            )
            raise InvalidInput(
                f"Failed to update user {user.user_id} in Auth0 for fields {auth0_user_store_fields}"
            )

    # Add or update the user metadata in the database
    user_metadata_model: UserMetadataModel = await add_or_update_user_metadata(
        user.user_id, **user_metadata.model_dump()
    )

    # Convert the user metadata model to a serializable dictionary
    return await user_metadata_model.to_serializable_dict()


@router.get("/user-metadata", tags=["User Metadata"])
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def get_user_metadata(
    user: UserMetadataModel = Depends(granted_user),
) -> UserMetadataReturnSchema:
    """
    Get user metadata

    Args:
        user (UserMetadataModel, optional): The user to get the metadata for. Defaults to Depends(granted_user).

    Returns:
        Dict: The user metadata.
    """
    return await user.to_serializable_dict()


@router.put("/user-metadata/link", tags=["User Metadata"])
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
    link_parameters_dict: dict = body.model_dump(exclude_none=True)

    match platform:
        case PlatformEnum.JIRA:
            user_metadata: UserMetadataModel = await link_jira(
                user, **link_parameters_dict
            )
        case PlatformEnum.SHORTCUT:
            user_metadata: UserMetadataModel = await link_shortcut(
                user, **link_parameters_dict
            )
        case PlatformEnum.ASANA:
            user_metadata: UserMetadataModel = await link_asana(
                user, **link_parameters_dict
            )
        case _:
            raise ValueError(f"Service {platform} not supported at this time.")

    return await user_metadata.to_serializable_dict()


@router.post(
    "/user-metadata/subscribe", include_in_schema=safe_endpoints, tags=["User Metadata"]
)
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def subscribe_to_service(
    tier: SubscriptionTier,
    user_id: str,
    _: UserMetadataModel = Depends(admin_user),
) -> Dict:
    """
    Subscribe to a service

    Args:
        tier (SubscriptionTier): The subscription tier to subscribe to.
        user (UserMetadataModel, optional): The user to subscribe. Defaults to Depends(admin_user).

    Returns:
        Dict: The updated user metadata.
    """
    user: UserMetadataModel = await get_user_metadata_by_user_id(user_id)

    if not user:
        raise ValueError(f"User with ID {user_id} not found.")

    user.subscription_tier = tier
    user.renew_datetime = datetime.datetime.now() + datetime.timedelta(days=30)
    user.renew_datetime = user.renew_datetime.isoformat()

    match tier:
        case SubscriptionTier.FREE:
            user.generations_count = 10
            user.file_uploads_count = 3
        case SubscriptionTier.BASIC:
            user.generations_count = 150
            user.file_uploads_count = 10
        case SubscriptionTier.STANDARD:
            user.generations_count = 500
            user.file_uploads_count = 50
        case SubscriptionTier.PRO:
            user.generations_count = 1000
            user.file_uploads_count = 100
        case SubscriptionTier.ENTERPRISE:
            user.generations_count = 1000000
            user.file_uploads_count = 100000

    await user.save()

    return await user.to_serializable_dict()


@router.get("/user-metadata/platforms/details", tags=["User Metadata"])
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def get_platform_details(
    user: UserMetadataModel = Depends(granted_user),
) -> PlatformDetailsSchema:
    """
    Get the details of the platforms linked to the user

    Args:
        user (UserMetadataModel, optional): The user to get the platform details for. Defaults to Depends(granted_user).

    Returns:
        Dict: The details of the platforms linked to the user.
    """
    resp = await user.get_platform_details()

    return resp
