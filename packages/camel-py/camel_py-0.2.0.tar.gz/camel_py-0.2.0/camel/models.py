from dataclasses import dataclass
from typing import Any, Mapping, Optional, Union, Sequence


@dataclass
class OllamaResponse:
    text: str
    raw: dict


@dataclass
class EmbeddingResponse:
    embedding: list[float]
    raw: dict


@dataclass
class EmbedRequest:
    model: str
    input: Union[str, Sequence[str]]
    truncate: Optional[bool] = None
    options: Optional[Union[Mapping[str, Any], dict]] = None
    keep_alive: Optional[Union[float, str]] = None
