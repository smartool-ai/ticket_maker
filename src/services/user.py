import os
from typing import Optional, List

from auth0.authentication import GetToken
from auth0.management import Auth0

from pynamodb.exceptions import DoesNotExist

from src.lib.loggers import get_module_logger
from src.models.dynamo.user import UserManagementModel
from src.models.dynamo.user_metadata import UserMetadataModel
from src.models.dynamo.portfolio import PortfolioModel
from src.models.dynamo.order import OrderModel

logger = get_module_logger()


def get_user_metadata_by_email(email: str) -> Optional[UserMetadataModel]:
    """Gets a list of user metadata by email. We have the table set up so that
    only one instance of a users metadata can exist for a given email so only
    one index or none is returned.

    Args:
        email (str)

    Returns:
        Optional[UserMetadataModel]
    """
    try:
        user_metadata: UserMetadataModel = UserMetadataModel.get(email)
    except (DoesNotExist, TypeError):
        return None
    return user_metadata


def get_user_management(user_id: str) -> Optional[UserManagementModel]:
    """Gets user from User Management DynamoDB.

    Args:
        user_id (str): auth0 id of user
    Returns:
        UserManagementModel or None
    """
    try:
        user_management = UserManagementModel.get(user_id)
    except (DoesNotExist, TypeError):
        return None
    return user_management


def get_user_management_by_email(email: str) -> Optional[UserManagementModel]:
    """Gets user from User Management DynamoDB.

    Args:
        user_id (str): auth0 id of user
    Returns:
        UserManagementModel or None
    """
    user_management = UserManagementModel.email_index.query(email)
    return next(user_management, None)


def get_portfolio_by_email(email: str) -> List[PortfolioModel]:
    """Gets portfolio from Portfolio DynamoDB.

    Args:
        email (str): email of user
    Returns:
        List[PortfolioModel]
    """
    portfolio = PortfolioModel.query(email)
    return list(portfolio)


def delete_user_management(user_id: str) -> bool:
    """Deletes user from User Management DynamoDB.

    Args:
        user_id (str): auth0 id of user
    Returns:
        bool
    """
    user_management = get_user_management(user_id)
    if user_management is None:
        return False
    user_management.delete()
    return True


def delete_user_metadata(email: str) -> bool:
    """Deletes user from User Metadata DynamoDB.

    Args:
        email (str): email of user
    Returns:
        bool
    """
    user_metadata = get_user_metadata_by_email(email)
    if user_metadata is None:
        return False
    user_metadata.delete()
    return True


def delete_auth0_user(id: str) -> bool:
    domain = os.environ["AUTH0_DOMAIN"]

    get_token = GetToken(
        domain,
        os.environ["AUTH0_MGMT_CLIENT_ID"],
        client_secret=os.environ["AUTH0_MGMT_CLIENT_SECRET"],
    )

    token = get_token.client_credentials("https://{}/api/v2/".format(domain))
    mgmt_api_token = token["access_token"]

    auth0 = Auth0(domain, mgmt_api_token)

    try:
        auth0.users.delete(f"auth0|{id}")
        return True
    except Exception as e:
        logger.error(e)
        return False


def delete_reserve_orders_by_email(email):
    """Deletes all reserve orders for a given email address."""
    orders = OrderModel.query(email)
    for order in orders:
        if order.order_type == "reserve":
            order.delete()
    return True
