import json
from typing import Union

from openai.types.chat.chat_completion_message import ChatCompletionMessage

from src.lib.loggers import get_module_logger
from src.models.openai import OpenAIClient

logger = get_module_logger()


def generate_tickets(prompt: str, number_of_tickets: int, platform: str) -> dict:
    """Given a transcript prompt generate a number of tickets for a given platform

    Args:
        prompt (str): The transcript prompt as a string.
        number_of_tickets (int): The number of tickets to generate.
        platform (str): The platform to generate the tickets for.

    Returns:
        Union[dict, ChatCompletionMessage]: The generated tickets or an error message as a dictionary.
    """
    client = OpenAIClient()
    try:
        completion: ChatCompletionMessage = client.create_tickets(prompt, number_of_tickets, platform)
        return json.loads(completion.content)
    except Exception as e:
        logger.error(e)
        return {
            "error": {
                "status_code": 500,
                "error": "Failed to generate tickets",
            }
        }
