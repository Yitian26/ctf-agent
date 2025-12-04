from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from .config import Config

def create_agent(cfg:Config,toolsets=None):
    model = OpenAIChatModel(
        cfg.MODEL_NAME,
        provider=OpenAIProvider(
            base_url=cfg.OPENAI_BASE_URL, api_key=cfg.OPENAI_API_KEY
        ),
    )
    return Agent(model,toolsets=toolsets)