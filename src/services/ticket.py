import datetime
import json
import os
from typing import Optional

import boto3
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from src.lib.enums import PlatformEnum

from src.lib.loggers import get_module_logger
from src.models.dynamo.ticket import TicketModel
from src.models.openai import OpenAIClient

logger = get_module_logger()


def modify_keys(data: dict) -> dict:
    if isinstance(data, dict):
        return {
            key.lower().replace(" ", ""): modify_keys(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [modify_keys(item) for item in data]
    else:
        return data


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
        logger.info("Generating tickets from transcript...")
        completion: ChatCompletionMessage = client.create_tickets(
            prompt, number_of_tickets, platform
        )

        tickets_dict: dict = json.loads(completion.content)

        logger.info("Tickets generated from transcript")
        return modify_keys(tickets_dict)
    except Exception as e:
        logger.error(e)
        raise e("Error generating tickets from transcript. Please try again.")


async def invoke_ticket_generation_lambda(
    document_id: str,
    user_id: str,
    number_of_tickets: Optional[int] = 10,
    platform: Optional[PlatformEnum] = PlatformEnum.JIRA,
) -> None:
    """Invoke the ticket generation lambda function."""
    try:
        lambda_client = boto3.client(
            "lambda", region_name=os.getenv("AWS_REGION", "us-west-2")
        )
        generation_datetime: str = datetime.datetime.now().isoformat()

        lambda_client.invoke(
            FunctionName=f'TRANSCRIBER-LAMBDA-{os.getenv("STAGE_NAME", "dev")}',
            InvocationType="Event",
            Payload=json.dumps(
                {
                    "document_id": document_id,
                    "user_id": user_id,
                    "number_of_tickets": number_of_tickets,
                    "platform": platform.value,
                    "generation_datetime": generation_datetime,
                }
            ),
        )
        return generation_datetime
    except Exception as e:
        logger.error(e)
        raise e("Error invoking ticket generation lambda function. Please try again.")


async def get_tickets(
    document_id: str, generation_datetime: str
) -> Optional[TicketModel]:
    """Get the generated tickets from the database."""
    try:
        ticket = TicketModel.get(hash_key=document_id, range_key=generation_datetime)

        if not ticket:
            return None
        return ticket
    except TicketModel.DoesNotExist:
        return None
    except Exception as e:
        logger.error(e)
        raise e("Error getting tickets from the database. Please try again.")
