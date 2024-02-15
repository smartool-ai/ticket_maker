import os
from typing import Optional

from openai import OpenAI

from src.lib.enums import PlatformEnum


class OpenAIClient(OpenAI):
    ticket_prompt_prefix: str = (
        "Given the following transcript from a video call, create {n} {platform} scrum stories:\n"
    )

    def __init__(self):
        super().__init__(api_key=os.getenv("OPENAI_API_KEY", "test"))

    def create_tickets(
        self,
        prompt: str,
        number_of_tickets: Optional[int] = 10,
        platform: Optional[PlatformEnum] = PlatformEnum.JIRA,
        **kwargs
    ):
        ticket_prompt: str = (
            self.ticket_prompt_prefix.format(
                n=number_of_tickets, platform=platform.value
            )
            + prompt
        )
        params: dict = {"engine": "gpt-4", "prompt": ticket_prompt, "max_tokens": 1024}
        if kwargs:
            params.update(kwargs)

        response = self.chat.completions.create(**params)
        return response.choices[0].message


# Example usage
# client = OpenAIClient()
# completion = client.create_tickets("Once upon a time")
# print(completion)
