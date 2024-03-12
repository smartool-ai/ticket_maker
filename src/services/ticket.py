import datetime
import json
import os
from typing import Optional
import uuid

import boto3
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from src.lib.enums import EventEnum, PlatformEnum

from src.lib.loggers import get_module_logger
from src.models.dynamo.ticket import Ticket
from src.models.openai import OpenAIClient

logger = get_module_logger()


def modify_keys(data: dict) -> dict:
    """
    Recursively modifies the keys of a dictionary to be lowercase and remove spaces.

    Args:
        data (dict): The dictionary to modify.

    Returns:
        dict: The modified dictionary.
    """
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
    """
    Given a transcript prompt, generate a number of tickets for a given platform.

    Args:
        prompt (str): The transcript prompt as a string.
        number_of_tickets (int): The number of tickets to generate.
        platform (str): The platform to generate the tickets for.

    Returns:
        dict: The generated tickets or an error message as a dictionary.
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
    event: EventEnum,
    number_of_tickets: Optional[int] = 10,
    platform: Optional[PlatformEnum] = PlatformEnum.JIRA,
    generation_datetime: str = None,
    ticket: dict = None,
) -> None:
    """
    Invoke the ticket generation lambda function.

    Args:
        document_id (str): The ID of the document.
        user_id (str): The ID of the user.
        number_of_tickets (int, optional): The number of tickets to generate. Defaults to 10.
        platform (PlatformEnum, optional): The platform to generate the tickets for. Defaults to PlatformEnum.JIRA.
    """
    try:
        payload = dict()
        response_id = str()

        if generation_datetime is None:
            generation_datetime: str = datetime.datetime.now().isoformat()
        match event:
            case EventEnum.TICKET_GENERATION:
                payload = {
                    "document_id": document_id,
                    "user_id": user_id,
                    "number_of_tickets": number_of_tickets,
                    "platform": platform.value,
                    "generation_datetime": generation_datetime,
                    "event": event.value,
                }
                response_id = generation_datetime
            case EventEnum.TICKET_EXPANSION:
                if ticket is None:
                    raise ValueError("Ticket is required for ticket expansion.")

                sub_ticket_id = str(uuid.uuid4())

                payload = {
                    "document_id": document_id,
                    "user_id": user_id,
                    "number_of_tickets": number_of_tickets,
                    "generation_datetime": generation_datetime,
                    "event": event.value,
                    "ticket": ticket,
                    "sub_ticket_id": sub_ticket_id,
                }
                response_id = sub_ticket_id

        lambda_client = boto3.client(
            "lambda", region_name=os.getenv("AWS_REGION", "us-west-2")
        )

        lambda_client.invoke(
            FunctionName=f'TRANSCRIBER-LAMBDA-{os.getenv("STAGE_NAME", "dev")}',
            InvocationType="Event",
            Payload=json.dumps(payload),
        )
        return response_id
    except Exception as e:
        logger.error(e)
        raise e("Error invoking ticket generation lambda function. Please try again.")


async def get_tickets(
    document_id: str, generation_datetime: str
) -> Optional[Ticket]:
    """
    Get the generated tickets from the database.

    Args:
        document_id (str): The ID of the document.
        generation_datetime (str): The datetime when the tickets were generated.

    Returns:
        Optional[TicketModel]: The generated tickets or None if not found.
    """
    try:
        ticket = Ticket.get(hash_key=document_id, range_key=generation_datetime)

        if not ticket:
            return None
        return ticket
    except Ticket.DoesNotExist:
        return None
    except Exception as e:
        logger.error(e)
        raise e("Error getting tickets from the database. Please try again.")
