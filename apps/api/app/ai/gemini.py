
"""Real Gemini implementation using Google's official Gen AI SDK."""

from collections.abc import Iterator, Sequence

from google import genai
from google.genai import types
from pydantic import BaseModel, SecretStr, ValidationError

from app.ai.errors import (
    AIProviderError,
    AIUnavailableError,
    AIValidationError,
)
from app.ai.provider import T
from app.ai.types import AIMessage, AIResponse, AIUsage, ModelTier


class GeminiProvider:
    name = "gemini"

    def __init__(
        self,
        api_key: SecretStr | None,
        model_fast: str | None = None,
        model_strong: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._models = {
            ModelTier.FAST: model_fast,
            ModelTier.STRONG: model_strong,
        }
        self._client_instance: genai.Client | None = None

    @property
    def configured(self) -> bool:
        return self._api_key is not None and all(self._models.values())

    def _get_model(self, tier: ModelTier) -> str:
        model = self._models[tier]
        if not self._api_key or not model:
            raise AIUnavailableError(
                "Gemini is not configured. Set GEMINI_API_KEY "
                "and both model IDs."
            )
        return model

    def _client(self) -> genai.Client:
        """Return a reusable Gemini client."""
        if not self._api_key:
            raise AIUnavailableError("Gemini API key is missing.")

        if self._client_instance is None:
            self._client_instance = genai.Client(
                api_key=self._api_key.get_secret_value()
            )

        return self._client_instance

    @staticmethod
    def _prepare_messages(
        messages: Sequence[AIMessage],
    ) -> tuple[str | None, list[types.Content]]:
        system_parts = [
            message.content
            for message in messages
            if message.role == "system"
        ]

        contents = [
            types.Content(
                role="model" if message.role == "assistant" else "user",
                parts=[types.Part.from_text(text=message.content)],
            )
            for message in messages
            if message.role != "system"
        ]

        return "\n\n".join(system_parts) or None, contents

    @staticmethod
    def _config(
        *,
        max_tokens: int,
        temperature: float,
        timeout_s: float,
        system_instruction: str | None,
        response_schema: type[BaseModel] | None = None,
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_instruction,
            response_mime_type="application/json" if response_schema else None,
            response_schema=response_schema,
            http_options=types.HttpOptions(
                timeout=int(timeout_s * 1000)
            ),
        )

    @staticmethod
    def _usage(response: object) -> AIUsage:
        metadata = getattr(response, "usage_metadata", None)
        return AIUsage(
            tokens_in=getattr(metadata, "prompt_token_count", 0) or 0,
            tokens_out=getattr(metadata, "candidates_token_count", 0) or 0,
        )

    def generate_text(
        self,
        messages: Sequence[AIMessage],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout_s: float = 120.0,
    ) -> AIResponse:
        model = self._get_model(tier)
        system_instruction, contents = self._prepare_messages(messages)

        try:
            response = self._client().models.generate_content(
                model=model,
                contents=contents,
                config=self._config(
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout_s=timeout_s,
                    system_instruction=system_instruction,
                ),
            )

            return AIResponse(
                text=response.text or "",
                provider=self.name,
                model=model,
                usage=self._usage(response),
            )

        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError(
                f"Gemini text generation failed: {exc}"
            ) from exc

    def generate_structured(
        self,
        messages: Sequence[AIMessage],
        schema: type[T],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.0,
        timeout_s: float = 30.0,
    ) -> T:
        model = self._get_model(tier)
        system_instruction, contents = self._prepare_messages(messages)

        try:
            response = self._client().models.generate_content(
                model=model,
                contents=contents,
                config=self._config(
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout_s=timeout_s,
                    system_instruction=system_instruction,
                    response_schema=schema,
                ),
            )

            if isinstance(response.parsed, schema):
                return response.parsed

            if response.parsed is not None:
                return schema.model_validate(response.parsed)

            if response.text:
                return schema.model_validate_json(response.text)

            raise AIValidationError(
                "Gemini returned an empty structured response."
            )

        except ValidationError as exc:
            raise AIValidationError(
                f"Gemini returned invalid structured data: {exc}"
            ) from exc
        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError(
                f"Gemini structured generation failed: {exc}"
            ) from exc

    def stream_text(
        self,
        messages: Sequence[AIMessage],
        *,
        tier: ModelTier = ModelTier.FAST,
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout_s: float = 30.0,
    ) -> Iterator[str]:
        model = self._get_model(tier)
        system_instruction, contents = self._prepare_messages(messages)

        try:
            chunks = self._client().models.generate_content_stream(
                model=model,
                contents=contents,
                config=self._config(
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout_s=timeout_s,
                    system_instruction=system_instruction,
                ),
            )

            for chunk in chunks:
                if chunk.text:
                    yield chunk.text

        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError(
                f"Gemini streaming failed: {exc}"
            ) from exc
