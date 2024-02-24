from src.models.dynamo.user_metadata import UserMetadataModel


async def add_or_update_user_metadata(user_id: str, **kwargs) -> UserMetadataModel:
    """Add or update a user metadata record."""
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


async def link_jira(user: UserMetadataModel, jira_domain: str, jira_api_key: str) -> UserMetadataModel:
    """Link a Jira account to a user."""
    user.jira_domain = jira_domain
    user.jira_api_key = jira_api_key
    await user.save()
    return user
