import os
from typing import Optional

from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from src.lib.enums import PlatformEnum
from src.lib.loggers import get_module_logger


logger = get_module_logger()


class OpenAIClient(OpenAI):
    ticket_prompt_prefix: str = (
        "Given the following transcript from a video call, please create {n} {platform} tickets with the following information in json format:\n\n \
        1. Subject: [Enter the subject of the ticket here]\n \
        2. Body: [Enter the detailed description of the ticket here]\n \
        3. Estimation Points: [Enter the estimation points for the ticket here]\n\n \
        Please note that the subject should be a brief summary of the ticket, the body should contain a detailed description of the work to be done, and the estimation points should be an integer representing the estimated effort required to complete the ticket."
    )

    def __init__(self):
        super().__init__(api_key=os.getenv("OPENAI_API_KEY", "test"))

    def create_tickets(
        self,
        prompt: str,
        number_of_tickets: Optional[int] = 10,
        platform: Optional[PlatformEnum] = PlatformEnum.JIRA,
        **kwargs
    ) -> ChatCompletionMessage:
        ticket_prompt: str = (
            self.ticket_prompt_prefix.format(
                n=number_of_tickets, platform=platform.value
            )
            + prompt  # noqa
        )
        params: dict = {
            "model": "gpt-4-turbo-preview",
            "messages": [{"role": "user", "content": ticket_prompt}],
            "max_tokens": 1024,
            "response_format": {"type": "json_object"},
        }
        if kwargs:
            params.update(kwargs)

        response = self.chat.completions.create(**params)
        logger.info(response)
        return response.choices[0].message


# Example usage
# client = OpenAIClient()
# completion = client.create_tickets("Once upon a time")
# print(completion)
