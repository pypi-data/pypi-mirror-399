import json
import subprocess
from typing import List, Optional

import httpx
from yaspin import yaspin

from .exceptions import OllamaAPIError, OllamaConnectionError
from .models import EmbeddingResponse, OllamaResponse


class CamelClient:
    """
    CamelClient: A lightweight client for interacting with Ollama models.

    This client provides:
      - Model management (list, pull, delete).
      - Chat with context persistence (single-shot or streaming).
      - Embeddings.
      - Context save/load for multi-turn conversations.

    Example:
        >>> from camel.api import CamelClient
        >>> with CamelClient(model="llama3") as client:
        ...     resp = client.chat("Hello, world!")
        ...     print(resp.text)
    """

    def __init__(
        self, model: str = "gemma3:1b", base_url: str = "http://localhost:11434"
    ):
        """
        Initialize a CamelClient.

        Args:
            model (str): Model name to use (must be available locally or will be pulled).
            base_url (str): Base URL for Ollama server.
        """
        self.model = model
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=30.0)
        self._context: Optional[list[int]] = None  # in-memory context store

        if not self._model_installed(model):
            print(f"Model '{model}' not found locally. Pulling it now...")
            self.pull(model)

    # ---------------------------
    # Model management
    # ---------------------------
    def _model_installed(self, model_name: str) -> bool:
        """Check if a given model is installed locally."""
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        return model_name in result.stdout

    def pull(self, model_name: str):
        """
        Pull a model from Ollama Hub (if not available locally).

        Args:
            model_name (str): Name of the model to pull.

        Raises:
            OllamaAPIError: If model pull fails.
        """
        with yaspin(text=f"Pulling {model_name}...", color="cyan") as spinner:
            result = subprocess.run(
                ["ollama", "pull", model_name], capture_output=True, text=True
            )
            if result.returncode != 0:
                spinner.fail("💥 ")
                raise OllamaAPIError(
                    f"Failed to pull model {model_name}:\n{result.stderr}"
                )
            spinner.ok("✅ ")
            print(f"Model '{model_name}' pulled successfully.")

    def list_models(self) -> List[str]:
        """
        List all models available locally.

        Returns:
            List[str]: Names of available models.

        Raises:
            OllamaAPIError: If the `ollama list` command fails.
        """
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            raise OllamaAPIError(f"Failed to list models:\n{result.stderr}")

        models = []
        for line in result.stdout.strip().splitlines()[1:]:  # skip header row
            parts = line.split()
            if parts:
                models.append(parts[0])  # first column is model name
        return models

    def delete(self, model: str):
        """
        Delete a locally available model.

        Args:
            model (str): Model name to delete.

        Raises:
            OllamaAPIError: If deletion fails.
        """
        if model not in self.list_models():
            print(f"Model '{model}' is not available.")
            return
        res = subprocess.run(["ollama", "rm", model], capture_output=True, text=True)
        if res.returncode != 0:
            raise OllamaAPIError(f"Failed to delete {model}:\n{res.stderr}")
        print(f"Model '{model}' deleted successfully.")

    # ---------------------------
    # Context management
    # ---------------------------
    def save_context(self) -> Optional[list[int]]:
        """
        Save current conversation context.

        Returns:
            Optional[list[int]]: Encoded context state (can be stored externally).
        """
        return self._context

    def load_context(self, context: list[int]):
        """
        Load a saved context into memory.

        Args:
            context (list[int]): Previously saved context.
        """
        self._context = context

    def clear_context(self):
        """Clear in-memory conversation context."""
        self._context = None

    # ---------------------------
    # Chat
    # ---------------------------
    def chat(self, prompt: str, stream: bool = False):
        """
        Get a response from the model.

        Args:
            prompt (str): User input.
            stream (bool):
                - False → returns a single `OllamaResponse`.
                - True → returns a generator yielding `OllamaResponse` chunks.

        Returns:
            OllamaResponse | Generator[OllamaResponse, None, None]
        """
        payload = {"model": self.model, "prompt": prompt, "stream": stream}
        if self._context:
            payload["context"] = self._context

        try:
            if not stream:
                r = self.client.post("/api/generate", json=payload)
                r.raise_for_status()
                data = r.json()
                if "context" in data:
                    self._context = data["context"]
                return OllamaResponse(text=data.get("response", ""), raw=data)
            else:

                def generator():
                    with self.client.stream("POST", "/api/generate", json=payload) as r:
                        r.raise_for_status()
                        for line in r.iter_lines():
                            if line:
                                data = json.loads(line)
                                if "context" in data:
                                    self._context = data["context"]
                                yield OllamaResponse(
                                    text=data.get("response", ""), raw=data
                                )

                return generator()
        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Failed to connect to Ollama: {e}") from e
        except httpx.HTTPStatusError as e:
            raise OllamaAPIError(e.response.text) from e

    def stream(self, prompt: str) -> OllamaResponse:
        """
        Stream response progressively and return the full response.

        Prints tokens as they arrive (good for CLI apps).

        Args:
            prompt (str): User input.

        Returns:
            OllamaResponse: Final accumulated response.
        """
        payload = {"model": self.model, "prompt": prompt, "stream": True}
        if self._context:
            payload["context"] = self._context

        full_text = ""

        try:
            with self.client.stream("POST", "/api/generate", json=payload) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "context" in data:
                            self._context = data["context"]
                        chunk = data.get("response", "")
                        print(chunk, end="", flush=True)  # progressive output
                        full_text += chunk

            print()  # newline after completion
            return OllamaResponse(text=full_text, raw={"response": full_text})

        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Failed to connect to Ollama: {e}") from e
        except httpx.HTTPStatusError as e:
            raise OllamaAPIError(e.response.text) from e

    # ---------------------------
    # Embeddings
    # ---------------------------
    def embed(self, text: str) -> EmbeddingResponse:
        """
        Generate embeddings for text.

        Args:
            text (str): Input text.

        Returns:
            EmbeddingResponse: Embedding vector + raw server response.
        """
        payload = {"model": self.model, "input": text}
        try:
            r = self.client.post("/api/embed", json=payload)
        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Failed to connect to Ollama: {e}") from e

        if r.status_code != 200:
            raise OllamaAPIError(r.text)

        data = r.json()
        embedding_vector = data.get("embeddings", [[]])[0]
        return EmbeddingResponse(embedding=embedding_vector, raw=data)

    # ---------------------------
    # Lifecycle
    # ---------------------------
    def close(self):
        """Close the underlying HTTP client."""
        self.client.close()

    def __enter__(self):
        """Enter context manager, returns self."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit context manager and close HTTP client."""
        self.close()

    def chat_with_tools(
        self, messages: list, tools: Optional[list] = None
    ) -> OllamaResponse:
        """
        Chat with tool/function calling support (uses /api/chat endpoint).

        Args:
            messages (list): List of message dicts with 'role' and 'content'.
            tools (list, optional): Tool definitions for function calling.

        Returns:
            OllamaResponse: Response with potential tool_calls in raw data.
        """
        payload = {"model": self.model, "messages": messages, "stream": False}

        if tools:
            payload["tools"] = tools

        try:
            r = self.client.post("/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()

            # Extract text from message content
            message = data.get("message", {})
            text = message.get("content", "")

            return OllamaResponse(text=text, raw=data)

        except httpx.RequestError as e:
            raise OllamaConnectionError(f"Failed to connect to Ollama: {e}") from e
        except httpx.HTTPStatusError as e:
            raise OllamaAPIError(e.response.text) from e
