from app.ai.fake import FakeAIProvider
from app.ai.gemini import GeminiProvider
from app.ai.provider import AIProvider
from app.config import Settings


def build_ai_provider(settings: Settings) -> AIProvider:
    """Choose the provider from configuration. ``fake`` is rejected in production by Settings."""
    if settings.ai_provider == "fake":
        return FakeAIProvider()
    return GeminiProvider(settings.gemini_api_key, settings.ai_model_fast, settings.ai_model_strong)
