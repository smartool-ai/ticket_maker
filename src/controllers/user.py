from logging import getLogger
from typing import Dict

from fastapi import APIRouter, Depends, Response

from src.lib.token_authentication import TokenAuthentication

from src.services.user import (
    get_user_management_by_email,
    get_portfolio_by_email,
    delete_user_metadata,
    delete_user_management,
    delete_auth0_user,
    delete_reserve_orders_by_email
)

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:users")


@router.get("/user/{email}")
async def get_user(
    email: str, response: Response, user: Dict = Depends(granted_user)
) -> Dict:
    user_management = get_user_management_by_email(email)

    if user_management is None:
        response.status_code = 404
        return {"error": "User not found"}

    portfolio = get_portfolio_by_email(email)
    user = user_management.to_dict()
    user["has_portfolio"] = len(portfolio) > 0

    return user


@router.delete("/user/{email}")
async def delete_user(
    email: str, response: Response, user: Dict = Depends(granted_user)
) -> Dict:
    user_management = get_user_management_by_email(email)

    if user_management is None:
        response.status_code = 404
        return {"error": "User not found"}

    portfolio = get_portfolio_by_email(email)

    if len(portfolio) > 0:
        response.status_code = 422
        return {"error": "User has portfolio entries"}

    delete_user_management(user_management.user_id)
    delete_user_metadata(user_management.email)
    delete_reserve_orders_by_email(user_management.email)
    delete_auth0_user(user_management.user_id)

    return {"status": "ok"}
