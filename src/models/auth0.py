import os
from typing import List, Optional
import uuid

import requests
from auth0.authentication import GetToken
from auth0.management import Auth0
from pixelum_core.errors.custom_exceptions import ServerFailureError
from pixelum_core.loggers.loggers import get_module_logger

logger = get_module_logger()


class Auth0Client:
    client: Auth0
    headers: dict = {
        "content-type": "application/json",
        "Authorization": "Bearer {}",
    }

    def __init__(self, client_id, client_secret, domain):
        self.client_id = client_id
        self.client_secret = client_secret
        self.domain = domain

        self.base_url = f"https://{self.domain}/api/v2/"

    async def _get_token(self) -> Optional[str]:
        """
        Get the Auth0 management API token.
        """
        get_token = GetToken(
            self.domain,
            self.client_id,
            client_secret=self.client_secret,
        )

        return get_token.client_credentials(self.base_url).get("access_token")
    
    async def _url(self, path):
        logger.debug(f"URL path: {self.base_url}{path}")
        return f"{self.base_url}{path}"

    async def _request(self, method, path, body, headers=None, params=None):
        logger.debug(f"[auth0] request path: {path}")
        logger.debug(f"[auth0] request body: {body}")

        self.headers["Authorization"] = self.headers["Authorization"].format(await self._get_token())

        response = requests.request(
            method,
            await self._url(path),
            headers=headers if headers else self.headers,
            json=body,
            params=params,
        )

        logger.debug(f"[auth0] response status: {response.status_code}")
        logger.debug(f"[auth0] response body: {response.content}")

        response.raise_for_status()

        return response

    async def get_client(self):
        """
        Generate the Auth0 client.
        """
        return Auth0(self.domain, await self._get_token())

    async def create_user(self, email: str) -> dict:
        """
        Create a new Auth0 user.

        Args:
            email (str): The email of the user.

        Returns:
            dict: The user data.
        """
        auth0 = await self.get_client()

        try:
            user = auth0.users.create(
                {
                    "email": email,
                    "email_verified": False,
                    "connection": "Username-Password-Authentication",
                    "password": f"initialPassword${uuid.uuid4().hex[:8]}",  # random password
                }
            )
            return user
        except Exception as e:
            logger.error(e)
            raise ServerFailureError("Failed to create user. Please try again.")

    async def get_user(self, user_id: str) -> dict:
        """
        Gets an Auth0 user with the specified ID.

        Args:
            user_id (str): The user ID.

        Returns:
            dict: The user data.
        """
        auth0 = await self.get_client()

        try:
            user = auth0.users.get(user_id)
            return user
        except Exception as e:
            logger.error(e)
            return {}

    async def get_users_permissions(self, user_id: str) -> list:
        """
        Get the permissions of an Auth0 user.

        Args:
            user_id (str): The user ID.

        Returns:
            list: The permissions of the user.
        """
        auth0 = await self.get_client()

        try:
            permissions = auth0.users.list_permissions(user_id)
            return permissions.get("permissions", [])
        except Exception as e:
            logger.error(e)
            return []

    async def update_user(self, user_id: str, **kwargs) -> dict:
        """
        Update an Auth0 user.

        Args:
            **kwargs: The user data to update.

        Returns:
            dict: The updated user data.
        """
        auth0 = await self.get_client()

        try:
            user = auth0.users.update(user_id, kwargs)
            return user
        except Exception as e:
            logger.error(e)
            raise ServerFailureError("Failed to update user. Please try again.")

    async def remove_user_permissions(
        self, user_id: str, permissions: List[str]
    ) -> dict:
        """
        Remove permissions from an Auth0 user.

        Args:
            user_id (str): The user ID.
            permissions (List[str]): The permissions to remove.

        Returns:
            dict: The updated user data.
        """
        auth0 = await self.get_client()

        try:
            for permission in permissions:
                await auth0.users.remove_permissions(user_id, permission)

            return True
        except Exception as e:
            logger.error(e)
            raise ServerFailureError("Failed to remove permissions. Please try again.")

    async def add_user_permissions(self, user_id: str, permissions: List[str]):
        """
        Add the permissions of an Auth0 user.

        Args:
            user_id (str): The user ID.
            permissions (List[str]): The permissions to add.
        """
        auth0 = await self.get_client()

        try:
            auth0.users.add_permissions(user_id, permissions)
        except Exception as e:
            logger.error(e)
            raise ServerFailureError("Failed to update permissions. Please try again.")

    async def delete_user(self, user_id: str) -> dict:
        """
        Delete an Auth0 user.

        Args:
            user_id (str): The user ID.

        Returns:
            dict: The status of the deletion.
        """
        auth0 = await self.get_client()

        try:
            user = auth0.users.delete(user_id)
            return user
        except Exception as e:
            logger.error(e)
            raise ServerFailureError("Failed to delete user. Please try again.")

    async def send_sub_user_invitation(self, user_id: str) -> dict:
        """
        Send a sub-user invitation to an Auth0 user.

        Args:
            user_id (str): The user ID.
            connection_id (str): The connection ID.

        Returns:
            dict: The invitation data.
        """
        auth0 = await self.get_client()

        try:
            invitation = auth0.tickets.create_pswd_change(
                {
                    "user_id": user_id,
                    "result_url": os.getenv("AUTH0_INVITATION_URL"),
                    "ttl_sec": 172800,  # 2 days in seconds
                    "mark_email_as_verified": False,
                }
            )
            return invitation
            # body = {
            #         "user_id": user_id,
            #         "result_url": os.getenv("AUTH0_INVITATION_URL"),
            #         "ttl_sec": 172800,  # 2 days in seconds
            #         "mark_email_as_verified": False,
            #     }
            # resp = await self._request("POST", "tickets/password-change", body)
            # return resp.json()
        except Exception as e:
            logger.error(e)
            raise ServerFailureError("Failed to send invitation. Please try again.")


auth0_client = Auth0Client(
    client_id=os.environ["AUTH0_MGMT_CLIENT_ID"],
    client_secret=os.environ["AUTH0_MGMT_CLIENT_SECRET"],
    domain=os.environ["AUTH0_DOMAIN"],
)
