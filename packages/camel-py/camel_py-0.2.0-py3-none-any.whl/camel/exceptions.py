class OllamaAPIError(Exception):
    """Raised when the Ollama API returns an error response."""


class OllamaConnectionError(Exception):
    """Raised when the client cannot connect to Ollama."""
