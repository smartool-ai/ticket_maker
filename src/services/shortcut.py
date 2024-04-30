import requests
from typing import List


shortcut_url = "https://api.app.shortcut.com/api/v3"


async def get_shortcut_workflows(api_key: str) -> List[dict]:
    """
    Get the list of shortcut workflows via their api

    Args:
        api_key (str): The Shortcut API key.

    Returns:
        List: The list of shortcut workflows.
    """
    domain: str = shortcut_url + "/workflows"
    headers = {
        "Shortcut-Token": api_key
    }
    response = requests.get(domain, headers=headers)
    workflows_dict: dict = response.json()

    if not response.ok:
        raise ValueError(f"Failed to get workflows from Shortcut: {workflows_dict['error']}")

    workflows = [{"id": str(workflow["id"]), "name": workflow["name"]} for workflow in workflows_dict]
    
    return workflows