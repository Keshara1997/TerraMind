from app.core.config import settings
from app.ai.openai_provider import OpenAIProvider


def get_ai_provider():
    if not settings.AI_ENABLED:
        raise RuntimeError("AI features are disabled")

    if settings.AI_PROVIDER.lower() == "openai":
        return OpenAIProvider()

    raise ValueError(
        f"Unsupported AI provider: {settings.AI_PROVIDER}"
    )