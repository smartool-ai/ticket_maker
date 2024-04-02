import os
from typing import List, Optional

import boto3
from pixelum_core.errors.custom_exceptions import ServerFailureError
from pixelum_core.loggers.loggers import get_module_logger
from pynamodb.exceptions import DoesNotExist

from src.models.auth0 import auth0_client
from src.models.dynamo.user import UserManagementModel
from src.models.dynamo.user_metadata import UserMetadataModel

logger = get_module_logger()


def check_user_exists(email: str) -> bool:
    """Checks if a user account exists.

    Args:
        email (str)

    Returns:
        UserManagementModel
    """
    users = UserManagementModel.email_index.query(
        hash_key=email, scan_index_forward=True, limit=5, last_evaluated_key=None
    )
    are_there_actually_users = len([user for user in users])
    return True if are_there_actually_users > 0 else False


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


async def get_user_metadata(user_id: str) -> Optional[UserMetadataModel]:
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


async def create_auth0_user(email: str) -> dict:
    """
    Creates an Auth0 user with the specified email.

    Args:
        email (str): The email of the user.

    Returns:
        dict: The user data.
    """
    try:
        return await auth0_client.create_user(email)
    except Exception as e:
        logger.error(e)
        return {}


async def update_auth0_user(user_id: str, **kwargs) -> dict:
    """
    Updates an Auth0 user with the specified ID.

    Args:
        user_id (str): The user ID.

    Returns:
        dict: The user data.
    """
    try:
        return await auth0_client.update_user(user_id, **kwargs)
    except Exception as e:
        logger.error(e)
        return {}


async def create_new_sub_user_invite_link(
    user_id: str, inviter: UserMetadataModel
) -> dict:
    """
    Sends an invitation to a new user to join the platform.

    Args:
        user_id (str): The user ID.
        inviter (UserMetadataModel): The user sending the invitation.

    Returns:
        dict: The user data.
    """
    try:
        logger.info(
            f"User: {inviter.email} is inviting user: {user_id} to join the platform."
        )
        return await auth0_client.send_sub_user_invitation(user_id)
    except Exception as e:
        logger.error(e)
        return {}


async def get_auth0_user(user_id: str) -> dict:
    """
    Gets an Auth0 user with the specified ID.

    Args:
        user_id (str): The user ID.

    Returns:
        dict: The user data.
    """
    try:
        return await auth0_client.get_user(user_id)
    except Exception as e:
        logger.error(e)
        return {}


async def get_auth0_user_permissions(user_id: str) -> List[str]:
    """
    Gets the permissions of an Auth0 user with the specified ID.

    Args:
        user_id (str): The user ID.

    Returns:
        list: The user permissions.
    """
    try:
        return await auth0_client.get_users_permissions(user_id)
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
    try:
        await auth0_client.remove_user_permissions(user_id, permissions)
        return True
    except Exception as e:
        logger.error(e)
        return False


async def delete_auth0_user(user: UserMetadataModel) -> bool:
    """
    Deletes an Auth0 user with the specified ID.

    Args:
        user (UserMetadataModel): The user to delete.

    Returns:
        bool: True if the user was successfully deleted, False otherwise.
    """
    try:
        await auth0_client.delete_user(user.user_id)
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
    try:
        # Update on auth0
        await auth0_client.add_user_permissions(user.user_id, permissions)

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


async def create_and_send_user_invitation_email_ses(email: str, invitation_link: str):
    ses_client = boto3.client(
        "ses",
        region_name=os.getenv("AWS_REGION", "us-west-2"),
        aws_access_key_id=os.getenv("SES_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("SES_SECRET_ACCESS_KEY"),
    )
    subject = "Invitation to Join Our Platform, Smartool.ai"
    body = f"Hello,\n\nYou have been invited to join our platform. Please click on the following link to create your password: {invitation_link}"
    sender = "admin@smartool.ai"
    recipient = email

    response = ses_client.send_email(
        Source=sender,
        Destination={"ToAddresses": [recipient]},
        Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
    )

    logger.info(f"Invitation email sent to {email}")
    return response
