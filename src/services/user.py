import os
from typing import List, Optional

from auth0.authentication import GetToken
from auth0.management import Auth0
from pixelum_core.errors.custom_exceptions import ServerFailureError
from pixelum_core.loggers.loggers import get_module_logger
from pynamodb.exceptions import DoesNotExist

from src.models.dynamo.user_metadata import UserMetadataModel

logger = get_module_logger()


def syncronous_get_user_metadata(user_id: str) -> Optional[UserMetadataModel]:
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


def syncdronous_get_user_metadata(user_id: str) -> Optional[UserMetadataModel]:
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


async def get_auth0_user(user_id: str) -> dict:
    """
    Gets an Auth0 user with the specified ID.

    Args:
        user_id (str): The user ID.

    Returns:
        dict: The user data.
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
        user = auth0.users.get(user_id)
        return user
    except Exception as e:
        logger.error(e)
        return {}


async def get_auth0_user_permissions(user_id: str) -> list:
    """
    Gets the permissions of an Auth0 user with the specified ID.

    Args:
        user_id (str): The user ID.

    Returns:
        list: The user permissions.
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
        user = auth0.users.list_permissions(user_id)
        return user.get("permissions", [])
    except Exception as e:
        logger.error(e)
        return []


async def remove_auth0_user_permissions(user_id: str, permissions: list) -> bool:
    """
    Removes the specified permissions from an Auth0 user.

    Args:
        user_id (str): The user ID.
        permissions (list): The permissions to remove.

    Returns:
        bool: True if the permissions were successfully removed, False otherwise.
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
        auth0.users.remove_permissions(user_id, permissions)
        return True
    except Exception as e:
        logger.error(e)
        return False


def delete_auth0_user(user: UserMetadataModel) -> bool:
    """
    Deletes an Auth0 user with the specified ID.

    Args:
        user (UserMetadataModel): The user to delete.

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
        auth0.users.delete(f"{user.signup_method}|{user.user_id}")
        return True
    except Exception as e:
        logger.error(e)
        return False


async def update_users_permissions(
    user: UserMetadataModel, permissions: List[str]
) -> UserMetadataModel:
    """
    Updates the permissions of a user in Auth0.

    Args:
        user (UserMetadataModel): The user to update.
        permissions (list): The permissions to update.

    Returns:
        bool: True if the permissions were successfully updated, False otherwise.
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
        # Update on auth0
        auth0.users.add_permissions(f"{user.signup_method}|{user.user_id}", permissions)

        # Update in dynamodb
        user.permissions = [
            permission.get("permission_name", "subscription:free").upper()
            for permission in permissions
        ]
        user.subscription_tier = await user.find_subscription_tier()
        await user.save()

        return user
    except Exception as e:
        logger.error(e)
        raise ServerFailureError(f"Failed to update user permissions {e}")
