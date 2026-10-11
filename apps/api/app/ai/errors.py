class AIProviderError(Exception):
    """Base class for provider failures. Features must degrade honestly, never fabricate."""


class AIUnavailableError(AIProviderError):
    """The provider cannot serve the request (not configured, not implemented, or down)."""


class AIValidationError(AIProviderError):
    """The provider's output did not satisfy the requested schema."""
