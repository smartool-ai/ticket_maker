import os
from typing import Optional

from auth0.authentication import GetToken
from auth0.management import Auth0
from pixelum_core.loggers.loggers import get_module_logger
from pynamodb.exceptions import DoesNotExist

from src.models.dynamo.user_metadata import UserMetadataModel

logger = get_module_logger()


def get_user_metadata(user_id: str) -> Optional[UserMetadataModel]:
    """Gets user from User Metadata DynamoDB.

    Args:
        user_id (str): auth0 id of user
    Returns:
        UserMetadataModel or None
    """
    try:
        user_metadata = UserMetadataModel.get(user_id)
    except (DoesNotExist, TypeError):
        return None
    return user_metadata


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
    """
    Deletes an Auth0 user with the specified ID.

    Args:
        id (str): The ID of the user to delete.

    Returns:
        bool: True if the user was successfully deleted, False otherwise.
    """
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
