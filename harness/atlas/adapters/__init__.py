from .base import Adapter, AdapterResult, TransportError
from .fixtures import FixturesAdapter
from .openai_compatible import OpenAICompatibleAdapter
from .anthropic_adapter import AnthropicAdapter
from .hf_local import HFLocalAdapter
from .ollama_native import OllamaNativeAdapter

ADAPTERS = {
    "openai_compatible": OpenAICompatibleAdapter,
    "anthropic": AnthropicAdapter,
    "hf_local": HFLocalAdapter,
    "fixtures": FixturesAdapter,
    "ollama_native": OllamaNativeAdapter,
}
