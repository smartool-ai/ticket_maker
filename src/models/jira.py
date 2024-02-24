from typing import Any
from jira.resources import Resource

from jira import JIRA


class JiraClient(JIRA):
    async def __init__(self, server: str = None, options: dict[str, str | bool | Any] = None, basic_auth: tuple[str, str] | None = None, token_auth: str | None = None, oauth: dict[str, Any] = None, jwt: dict[str, Any] = None, kerberos=False, kerberos_options: dict[str, Any] = None, validate=False, get_server_info: bool = True, async_: bool = False, async_workers: int = 5, logging: bool = True, max_retries: int = 3, proxies: Any = None, timeout: float | tuple[float, float] | tuple[float, None] | None = None, auth: tuple[str, str] = None, default_batch_sizes: dict[type[Resource], int | None] | None = None):
        super().__init__(server, options, basic_auth, token_auth, oauth, jwt, kerberos, kerberos_options, validate, get_server_info, async_, async_workers, logging, max_retries, proxies, timeout, auth, default_batch_sizes)
