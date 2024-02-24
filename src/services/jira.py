from jira import JIRA

from src.lib.loggers import get_module_logger
from src.models.dynamo.user_metadata import UserMetadataModel


logger = get_module_logger()


async def get_jira_client(user: UserMetadataModel) -> JIRA:
    """Get the Jira client."""
    logger.info(f"Getting Jira client for user: {user.user_id}")

    if not hasattr(user, "jira_domain") or not hasattr(user, "jira_api_key"):
        raise ValueError("User does not have Jira credentials.")

    return JIRA(
        server=user.jira_domain,
        token_auth=user.jira_api_key,
        async_=True,
        logging=False,
    )


async def create_ticket(jira_client: JIRA, ticket: dict) -> dict:
    """Create a ticket in Jira."""
    logger.info(f"Creating ticket in Jira: {ticket}")
    return jira_client.create_issue(fields=ticket)
