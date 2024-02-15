from src.models.openai import OpenAIClient


def generate_tickets(prompt: str, number_of_tickets: int, platform: str):
    client = OpenAIClient()
    completion = client.create_tickets(prompt, number_of_tickets, platform)
    return completion
