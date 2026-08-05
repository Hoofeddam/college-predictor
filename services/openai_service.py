import os

from dotenv import load_dotenv
from openai import OpenAI

from config import Config

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def chat(messages):

    response = client.responses.create(
        model=Config.OPENAI_MODEL,
        input=messages
    )

    return response.output_text


def response(messages, tools=None):

    return client.responses.create(
        model=Config.OPENAI_MODEL,
        input=messages,
        tools=tools
    )