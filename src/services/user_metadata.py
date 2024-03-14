from typing import Optional
from src.models.dynamo.user_metadata import UserMetadataModel


async def add_or_update_user_metadata(user_id: str, **kwargs) -> UserMetadataModel:
    """Add or update a user metadata record.

    Args:
        user_id (str): The ID of the user.
        **kwargs: Additional keyword arguments representing the metadata fields and their values.

    Returns:
        UserMetadataModel: The updated user metadata record.
    """
    # Check if the user metadata record already exists
    metadata: dict = kwargs
    try:
        user_metadata = UserMetadataModel.get(user_id)
    except UserMetadataModel.DoesNotExist:
        # Create a new user metadata record if it doesn't exist
        user_metadata = await UserMetadataModel.initialize(user_id=user_id)

    # Update the existing user metadata record with partial updates
    for key, value in metadata.items():
        if key != "user_id":
            setattr(user_metadata, key, value)

    # Save the user metadata record
    await user_metadata.save()

    return user_metadata


async def link_jira(user: UserMetadataModel, email: str, server: str, api_key: str) -> UserMetadataModel:
    """Link a Jira account to a user."""
    user.jira_email = email
    user.jira_domain = server
    user.jira_api_key = api_key
    await user.save()
    return user


async def link_shortcut(user: UserMetadataModel, api_key: str, project_id: str) -> UserMetadataModel:
    """Link a Shortcut account to a user."""
    user.shortcut_api_key = api_key
    user.shortcut_project_id = project_id
    await user.save()
    return user


async def get_user_metadata_by_user_id(user_id: str) -> Optional[UserMetadataModel]:
    """Get user metadata by user ID."""
    try:
        user_metadata = UserMetadataModel.get(hash_key=user_id)
        return user_metadata
    except UserMetadataModel.DoesNotExist:
        return None
