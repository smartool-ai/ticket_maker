from src.lib.constants import JIRA_BASE_URL

import requests
from requests.auth import HTTPBasicAuth


class JiraClient:
    def __init__(self, email, api_key):
        self.auth = HTTPBasicAuth(email, api_key)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_issue(self, issue_key: str):
        """
        Get an issue from Jira

        Args:
            issue_key (str): The issue key

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """
        url = f"{JIRA_BASE_URL}/issue/{issue_key}"
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get issue: {response.text}")

    def create_issue(self, issue_data: dict):
        url = f"{JIRA_BASE_URL}/issue"
        response = requests.post(url, json=issue_data, headers=self.headers, auth=self.auth)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create issue: {response.text}")
