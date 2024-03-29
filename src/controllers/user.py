import os
from typing import Dict, List

from fastapi import APIRouter, Depends
from pixelum_core.api.authorized_api_handler import authorized_api_handler
from pixelum_core.enums.enums import SubscriptionTier
from pixelum_core.errors.custom_exceptions import ResourceNotFoundException
from pixelum_core.loggers.loggers import get_module_logger

from src.lib.constants import SUBSCRIPTION_TIER_MAP
from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.user_metadata import UserMetadataModel
from src.schemas.user_metadata import UserMetadataReturnSchema
from src.services.user import (
    get_auth0_user_permissions,
    syncronous_get_user_metadata,
    delete_user_metadata,
    delete_auth0_user,
    remove_auth0_user_permissions,
    update_users_permissions,
)

router = APIRouter()
logger = get_module_logger()
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission("manage:users")


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


# @router.get("/user/{email}", tags=["User Management"])
# @authorized_api_handler()
# async def get_user(
#     email: str, response: Response, user: Dict = Depends(granted_user)
# ) -> Dict:
#     """
#     Get user information by email.

#     Args:
#         email (str): The email of the user.
#         response (Response): The FastAPI response object.
#         user (Dict): The user information obtained from the token.

#     Returns:
#         Dict: The user information.

#     Raises:
#         HTTPException: If the user is not found.
#     """
#     user_management = get_user_management_by_email(email)

#     if user_management is None:
#         response.status_code = 404
#         return {"error": "User not found"}

#     user = user_management.to_dict()

#     return user


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
    delete_auth0_user(user.user_id)

    return {"status": "ok"}
