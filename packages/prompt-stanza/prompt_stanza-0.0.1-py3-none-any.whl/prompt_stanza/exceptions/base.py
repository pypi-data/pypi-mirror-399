"""Base exception classes for prompt-stanza."""


class PromptStanzaError(Exception):
    """Base exception for all prompt-stanza errors."""

    pass


class ValidationError(PromptStanzaError):
    """Raised when input validation fails."""

    pass


class StanzaNotFoundError(PromptStanzaError):
    """Raised when a stanza cannot be found."""

    pass


class AdapterError(PromptStanzaError):
    """Raised when a storage adapter operation fails."""

    pass


class SecurityError(PromptStanzaError):
    """Raised when potential jailbreak or harmful intent is detected."""

    pass
