from .base import Adapter, AdapterResult, TransportError
from .fixtures import FixturesAdapter
from .openai_compatible import OpenAICompatibleAdapter
from .anthropic_adapter import AnthropicAdapter
from .hf_local import HFLocalAdapter

ADAPTERS = {
    "openai_compatible": OpenAICompatibleAdapter,
    "anthropic": AnthropicAdapter,
    "hf_local": HFLocalAdapter,
    "fixtures": FixturesAdapter,
}
