import os
from typing import Dict, List

from fastapi import APIRouter, Depends
from pixelum_core.api.authorized_api_handler import authorized_api_handler
from pixelum_core.enums.enums import SubscriptionTier
from pixelum_core.errors.custom_exceptions import ResourceNotFoundException
from pixelum_core.loggers.loggers import get_module_logger
import requests

from src.lib.constants import SUBSCRIPTION_TIER_MAP
from src.lib.token_authentication import TokenAuthentication
from src.models.auth0 import auth0_client
from src.models.dynamo.user_metadata import UserMetadataModel
from src.schemas.user_metadata import UserMetadataReturnSchema
from src.services.user import (
    create_auth0_user,
    delete_auth0_user,
    delete_user_metadata,
    get_auth0_user_permissions,
    remove_auth0_user_permissions,
    send_new_sub_user_invite,
    syncronous_get_user_metadata,
    update_users_permissions,
)
from src.services.user_metadata import create_user_metadata

router = APIRouter()
logger = get_module_logger()
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission("manage:users")
admin_user = token_authentication.require_user_with_permission("manage:admin")
safe_endpoints = True if os.getenv("STAGE_NAME") != "prod" else False


@router.put("/user/subscription", tags=["User Management"])
@authorized_api_handler()
async def update_user_subscription(
    user_id: str,
    tier: SubscriptionTier,
    _: UserMetadataModel = Depends(granted_user),
) -> UserMetadataReturnSchema:
    """
    Update the user subscription.

    Args:
        tier (SubscriptionTier): The subscription tier to update to.
        user (Dict): The user information obtained from the token.

    Returns:
        Dict: The updated user information.
    """
    user: UserMetadataModel = await syncronous_get_user_metadata(user_id)
    auth0_user_id: str = f"{user.signup_method}|{user.user_id}"

    # get the auth0 user
    auth0_user_permissions: List[dict] = await get_auth0_user_permissions(auth0_user_id)

    new_user_permission_name = SUBSCRIPTION_TIER_MAP.get(tier.value, "FREE")

    new_user_permission: dict = {
        "permission_name": new_user_permission_name,
        "resource_server_identifier": os.getenv("AUTH0_AUDIENCE"),
    }

    # Remove old subscription permission
    for permission in auth0_user_permissions:
        if "subscription" in permission.get("permission_name"):
            await remove_auth0_user_permissions(
                auth0_user_id, permission.get("permission_name")
            )
            break

    # Append new permission
    updated_user: UserMetadataModel = await update_users_permissions(
        user, [new_user_permission]
    )

    return await updated_user.to_serializable_dict()


@router.delete("/user", tags=["User Management"])
@authorized_api_handler()
async def delete_user(user_id: str, _: Dict = Depends(granted_user)) -> Dict:
    """
    Delete a user by email.

    Args:
        email (str): The email of the user.
        user (Dict): The user information obtained from the token.

    Returns:
        Dict: The status of the deletion.

    Raises:
        HTTPException: If the user is not found.
    """
    user: UserMetadataModel = await syncronous_get_user_metadata(user_id)

    if user is None:
        raise ResourceNotFoundException(f"User with id {user_id} not found")

    delete_user_metadata(user.email)
    await delete_auth0_user(user.user_id)

    return {"status": "ok"}


@router.post("/user/password-reset", tags=["User Management"])
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def password_reset(
    user: UserMetadataModel = Depends(token_authentication.require_any_user),
) -> dict:
    """Endpoint for sending a new password reset email.

    Args:
        user (UserMetadataModel): Credentials of an authenticated user by default.

    Returns:
        Response: Success message
    """
    logger.info(f"Sending password reset email to user: {user.email}")

    headers = {
        "content-type": "application/json",
    }
    url = f"https://{os.getenv('AUTH0_DOMAIN', 'test')}/dbconnections/change_password"

    body = {
        "client_id": os.getenv("AUTH0_CLIENT_ID", "test"),
        "email": user.email,
        "connection": user.signup_method,
    }

    response = requests.post(url, headers=headers, json=body)
    logger.info(f"Password reset response: {response.text}")

    if response.status_code != 200:
        return {
            "message": "Password reset email failed",
            "status_code": response.status_code,
        }

    return {"message": "Password reset email sent", "status_code": response.status_code}


@router.post(
    "/user-metadata/invite-sub-user",
    include_in_schema=safe_endpoints,
    tags=["User Management"],
)
@authorized_api_handler(models_to_initialize=[UserMetadataModel])
async def invite_sub_user(
    email: str, user: UserMetadataModel = Depends(granted_user)
) -> Dict:
    """
    Invite a sub user to the platform

    Invite Steps:
        1. Create new auth0 user and set permissions to same as parent user
        2. Create new user metadata with same permissions as parent user and reference parent user_id as parent_user_id
        3. Send email to sub user with link to set password

    Args:
        email (str): The email of the sub user to invite.
        user (UserMetadataModel, optional): The user to invite the sub user. Defaults to Depends(granted_user).
    """
    logger.info(f"User: {user.email} is inviting user: {email} to join the platform.")

    # Create new auth0 user
    new_user = await create_auth0_user(email)

    if not new_user:
        return {"message": "Failed to create user"}

    new_user_id: str = new_user.get("user_id")

    # Create new user metadata
    new_user_meta: dict = {
        "email": email,
        "permissions": user.permissions,
        "signup_method": "Username-Password-Authentication",
        "parent_user_id": user.user_id,
    }

    new_user_model: UserMetadataModel = await create_user_metadata(new_user_id.split("|")[1], new_user_meta)

    formatted_permissions = [
        {
            "permission_name": permission,
            "resource_server_identifier": os.getenv("AUTH0_AUDIENCE"),
        }
        for permission in new_user_model.permissions
    ]

    # Set permissions to same as parent user
    await auth0_client.add_user_permissions(new_user_id, formatted_permissions)

    # Send email to sub user
    _: dict = await send_new_sub_user_invite(new_user_id, user)

    return {"message": "User invited successfully"}
