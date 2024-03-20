import requests
from requests.auth import HTTPBasicAuth

from src.lib.enums import PlatformEnum
from src.lib.loggers import get_module_logger


logger = get_module_logger()


class BaseClient:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = None
    base_url = "test"

    def __init__(self, client: str = None) -> None:
        self.client = client

    async def _url(self, path):
        logger.debug(f"URL path: {self.base_url}{path}")
        return f"{self.base_url}{path}"

    async def _request(self, method, path, body, headers=None, auth=None):
        logger.debug(f"[{self.client}] request path: {path}")
        logger.debug(f"[{self.client}] request body: {body}")
        logger.info(f"[{self.client}] sending request to {method} {path}...")

        response = requests.request(
            method,
            await self._url(path),
            headers=headers if headers else self.headers,
            json=body,
            auth=auth if auth else self.auth
        )

        logger.debug(f"[{self.client}] response status: {response.status_code}")
        logger.debug(f"[{self.client}] response body: {response.content}")

        response.raise_for_status()

        return response


class Jira(BaseClient):
    def __init__(self, **kwargs):
        super().__init__()
        self.client = "Jira"
        self.base_url = f"{kwargs.get('server')}/rest/api/2/"
        self.email = kwargs.get("email")
        self.token_auth = kwargs.get("token_auth")
        self.auth = HTTPBasicAuth(self.email, self.token_auth)

    async def create_story(self, ticket_params: dict) -> dict:
        """Create a ticket in Jira."""
        logger.info(f"Creating ticket in Jira: {ticket_params}")
        fields = {
            "fields": {
                "project": {
                    "key": "TRAN"
                },
                "summary": ticket_params["name"],
                "timetracking": {
                    "originalEstimate": str(ticket_params['estimate'])
                },
                "issuetype": {
                    "id": "10005"
                },
                "description": str(ticket_params["description"]) if ticket_params["description"] else "",
            }
        }
        try:
            resp = await self._request("POST", "issue", fields, auth=self.auth)
        except Exception as e:
            logger.error(f"Error creating ticket in Jira: {e}")
            raise e

        return resp.json()


class Shortcut(BaseClient):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Shortcut-Token": ""
    }
    base_url = "https://api.app.shortcut.com/api/v3/"

    def __init__(self, **kwargs):
        super().__init__()
        self.client = "Shortcut"
        self.api_token = kwargs.get("api_token")
        self.headers["Shortcut-Token"] = self.api_token

    async def create_story(self, ticket_params: dict):
        """
        Create a ticket in Shortcut.

        Kwargs:
            - name (str): Required. The name of the story.
            - description (str): The description of the story.
            - workflow_state_id (int): The ID of the workflow state the story will be in.
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
        create_story_resp = await self._request("POST", "stories", ticket_params)

        return create_story_resp.json()

    async def create_epic(self, *args, **kwargs):
        pass

    async def get_story(self, *args, **kwargs):
        pass

    async def get_epic(self, *args, **kwargs):
        pass

    async def update_story(self, *args, **kwargs):
        pass


class Asana(BaseClient):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": ""
    }
    base_url = "https://app.asana.com/api/1.0/"

    def __init__(self, **kwargs):
        super().__init__()
        self.client = "Asana"
        self.personal_access_token = kwargs.get("personal_access_token")
        self.headers["Authorization"] = f"Bearer {self.personal_access_token}"
        self.workspace_id = kwargs.get("workspace_id")
        self.project_id = kwargs.get("project_id")
    
    async def create_story(self, ticket_params: dict):
        """
        Create a task in Asana.

        Kwargs:
            - name (str): Required. The name of the task.
            - description (str): The description of the task.
            - estimate (int): The estimate of the task.
        """
        req_body = {
            "data": {
                "workspace": self.workspace_id,
                "projects": [self.project_id],
                "name": ticket_params["name"],
                "notes": ticket_params["description"]
            }
        }
        create_story_resp = await self._request("POST", "tasks", req_body)

        return create_story_resp.json()

class PlatformClient:
    def __init__(self, platform: PlatformEnum, **kwargs):
        try:
            match platform:
                case PlatformEnum.JIRA:
                    self.platform = Jira(**kwargs)
                case PlatformEnum.SHORTCUT:
                    self.platform = Shortcut(**kwargs)
                case PlatformEnum.ASANA:
                    self.platform = Asana(**kwargs)
                case _:
                    raise ValueError(f"Invalid platform: {platform}. Must be one of {PlatformEnum.JIRA, PlatformEnum.SHORTCUT, PlatformEnum.ASANA}")
        except Exception as e:
            logger.error(f"Error initializing platform client: {e}")
            raise e

    async def create_story(self, **kwargs):
        return await self.platform.create_story(kwargs)

    async def get_story(self, *args, **kwargs):
        return await self.platform.get_story(*args, **kwargs)
