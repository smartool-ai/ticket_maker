import requests
from jira import JIRA

from src.lib.enums import PlatformEnum
from src.lib.loggers import get_module_logger


logger = get_module_logger()


class Jira(JIRA):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def create_story(self: JIRA, ticket_params: dict) -> dict:
        """Create a ticket in Jira."""
        logger.info(f"Creating ticket in Jira: {ticket_params}")
        return await self.create_issue(fields=ticket_params)


class Shortcut:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": ""
    }
    base_url = "https://api.app.shortcut.com/api/v3/"

    def __init__(self, **kwargs):
        self.api_token = kwargs.get("api_token")
        self.headers["Authorization"] = {self.api_token}

    async def _url(self, path):
        logger.debug(f"URL path: {self.base_url}{path}")
        return f"{self.base_url}{path}"

    async def _request(self, method, path, body, headers=None):
        logger.debug(f"[Shortcut] request path: {path}")
        logger.debug(f"[Shortcut] request body: {body}")
        logger.info(f"[Shortcut] sending request to {method} {path}...")

        response = requests.request(
            method,
            await self._url(path),
            headers=headers if headers else self.headers,
            json=body,
        )

        logger.debug(f"[Shortcut] response status: {response.status_code}")
        logger.debug(f"[Shortcut] response body: {response.content}")

        response.raise_for_status()

        return response

    async def create_story(self, **kwargs):
        """
        Create a ticket in Shortcut.

        Kwargs:
            - name (str): Required. The name of the story.
            - workflow_state_id (int): The ID of the workflow state the story will be in.
            - description (str): The description of the story.
            - requested_by_id (UUID): The ID of the member that requested the story.
            - story_type (Enum[bug, chore, feature]): The type of story (feature, bug, chore).
            - archived (bool): Controls the story's archived state.
            - comments (List[CreateStoryCommentParams]): An array of comments to add to the story.
            - completed_at_override (Date): A manual override for the time/date the Story was completed.
            - created_at (Date): The time/date the Story was created.
            - custom_fields (List[CustomFieldValueParams]): A map specifying a CustomField ID and CustomFieldEnumValue ID that represents an assertion of some value for a CustomField.
            - deadline (Date or None): The due date of the story.
            - epic_id (int or None): The ID of the epic the story belongs to.
            - estimate (int or None): The numeric point estimate of the story. Can also be None, which means unestimated.
            - external_id (str): This field can be set to another unique ID. In the case that the Story has been imported from another tool, the ID in the other tool can be indicated here.
            - external_links (List[str]): An array of External Links associated with this story.
            - file_ids (List[int]): An array of IDs of files attached to the story.
            - follower_ids (List[UUID]): An array of UUIDs of the followers of this story.
            - group_id (UUID or None): The id of the group to associate with this story.
            - iteration_id (int or None): The ID of the iteration the story belongs to.
            - labels (List[CreateLabelParams]): An array of labels attached to the story.
            - linked_file_ids (List[int]): An array of IDs of linked files attached to the story.
            - move_to (Enum[first, last]): One of "first" or "last". This can be used to move the given story to the first or last position in the workflow state.
            - owner_ids (List[UUID]): An array of UUIDs of the owners of this story.
            - project_id (int or None): The ID of the project the story belongs to.
            - started_at_override (Date): A manual override for the time/date the Story was started.
            - story_links (List[CreateStoryLinkParams]): An array of story links attached to the story.
            - story_template_id (UUID or None): The id of the story template used to create this story, if applicable. This is just an association; no content from the story template is inherited by the story simply by setting this field.
            - tasks (List[CreateTaskParams]): An array of tasks connected to the story.
            - updated_at (Date): The time/date the Story was updated.
        """
        create_story_resp = await self._request("POST", "stories", kwargs)

        return create_story_resp.json()

    async def create_epic(self, *args, **kwargs):
        pass

    async def get_story(self, *args, **kwargs):
        pass

    async def get_epic(self, *args, **kwargs):
        pass

    async def update_story(self, *args, **kwargs):
        pass


class PlatformClient:
    def __init__(self, platform: PlatformEnum, **kwargs):
        match platform:
            case PlatformEnum.JIRA:
                self.platform = Jira(kwargs)
            case PlatformEnum.SHORTCUT:
                self.platform = Shortcut(kwargs)
            case _:
                raise ValueError(f"Invalid platform: {platform}. Must be one of {PlatformEnum.JIRA, PlatformEnum.SHORTCUT}")
    
    async def create_story(self, **kwargs):
        return await self.platform.create_story(**kwargs)

    async def get_story(self, *args, **kwargs):
        return await self.platform.get_story(*args, **kwargs)
