from typing import Dict

from fastapi import APIRouter, Depends, Response
# from pixelum_core.api.authorized_api_handler import authorized_api_handler
from pixelum_core.loggers.loggers import get_module_logger

from src.lib.token_authentication import TokenAuthentication
from src.services.user import (
    get_user_management_by_email,
    delete_user_metadata,
    delete_user_management,
    delete_auth0_user,
)

router = APIRouter()
logger = get_module_logger()
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission("manage:users")


@router.get("/user/{email}")
async def get_user(
    email: str, response: Response, user: Dict = Depends(granted_user)
) -> Dict:
    """
    Get user information by email.

    Args:
        email (str): The email of the user.
        response (Response): The FastAPI response object.
        user (Dict): The user information obtained from the token.

    Returns:
        Dict: The user information.

    Raises:
        HTTPException: If the user is not found.
    """
    user_management = get_user_management_by_email(email)

    if user_management is None:
        response.status_code = 404
        return {"error": "User not found"}

    user = user_management.to_dict()

    return user


@router.delete("/user/{email}")
async def delete_user(
    email: str, response: Response, user: Dict = Depends(granted_user)
) -> Dict:
    """
    Delete a user by email.

    Args:
        email (str): The email of the user.
        response (Response): The FastAPI response object.
        user (Dict): The user information obtained from the token.

    Returns:
        Dict: The status of the deletion.

    Raises:
        HTTPException: If the user is not found.
    """
    user_management = get_user_management_by_email(email)

    if user_management is None:
        response.status_code = 404
        return {"error": "User not found"}

    delete_user_management(user_management.user_id)
    delete_user_metadata(user_management.email)
    delete_auth0_user(user_management.user_id)

    return {"status": "ok"}
