from openai import AsyncOpenAI

from app.ai.base import AIProvider
from app.core.config import settings


class OpenAIProvider(AIProvider):

    def __init__(self):
        if not settings.AI_API_KEY:
            raise ValueError("AI_API_KEY is not configured")

        client_options = {
            "api_key": settings.AI_API_KEY,
            "timeout": settings.AI_REQUEST_TIMEOUT,
            "max_retries": 2,
        }

        if settings.AI_BASE_URL:
            client_options["base_url"] = settings.AI_BASE_URL

        self.client = AsyncOpenAI(**client_options)

    async def generate(
        self,
        instructions: str,
        prompt: str,
    ) -> str:
        response = await self.client.responses.create(
            model=settings.AI_MODEL,
            instructions=instructions,
            input=prompt,
            max_output_tokens=settings.AI_MAX_OUTPUT_TOKENS,
            store=False,
        )

        answer = response.output_text

        if not answer:
            raise RuntimeError("AI provider returned an empty response")

        return answer