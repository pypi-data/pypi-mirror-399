"""
MDSA Integration Adapters Submodule

Contains adapters for external model providers and frameworks:
- Ollama: Local model inference via Ollama server
- (Future) LangChain: LangChain integration
- (Future) LlamaIndex: LlamaIndex integration
"""

from mdsa.integrations.adapters.ollama_adapter import (
    OllamaModel,
    OllamaTokenizer,
    OllamaPseudoTensor,
    OllamaGeneratedOutput,
    OllamaConnectionError,
    OllamaGenerationError,
    is_ollama_model,
    parse_ollama_model_name,
    load_ollama_model,
)

__all__ = [
    # Ollama adapter
    "OllamaModel",
    "OllamaTokenizer",
    "OllamaPseudoTensor",
    "OllamaGeneratedOutput",
    "OllamaConnectionError",
    "OllamaGenerationError",
    "is_ollama_model",
    "parse_ollama_model_name",
    "load_ollama_model",
]
