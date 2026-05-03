from .base import BaseProvider

_REGISTRY = {}


def register(name: str):
    def decorator(cls):
        _REGISTRY[name] = cls
        return cls
    return decorator


def get_provider(name: str) -> type:
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(f"Unknown provider '{name}'. Available: {available}")
    return _REGISTRY[name]


def list_providers():
    return sorted(_REGISTRY.keys())


from .file import FileProvider
from .mock import MockProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
