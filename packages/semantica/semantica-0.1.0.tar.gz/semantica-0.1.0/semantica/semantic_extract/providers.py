"""
LLM Providers and Model Loaders Module

This module provides a unified interface for all LLM providers and HuggingFace model
loaders, enabling seamless integration with multiple language model services and
custom HuggingFace models for semantic extraction tasks.

Supported Providers:
    - "openai": OpenAI API (GPT-3.5, GPT-4, etc.)
    - "gemini": Google Gemini API (gemini-pro, etc.)
    - "groq": Groq API (llama2, mixtral, etc.)
    - "anthropic": Anthropic Claude API (claude-3-sonnet, etc.)
    - "ollama": Ollama local provider (local open-source models)
    - "huggingface_llm": HuggingFace Transformers for LLM tasks

Supported Model Types:
    - NER Models: Token classification models for named entity recognition
    - Relation Models: Sequence classification models for relation extraction
    - Triplet Models: Seq2Seq models for triplet extraction

Algorithms Used:
    - Transformer Architecture: Attention mechanism-based neural networks
    - Token Classification: BERT, RoBERTa, DistilBERT for NER tasks
    - Sequence Classification: Transformer encoders for relation classification
    - Sequence-to-Sequence: Encoder-decoder transformers for triplet generation
    - Autoregressive Generation: GPT-style models for text generation
    - API Integration: RESTful API communication and JSON parsing
    - Model Caching: LRU cache and memory management for model loading
    - Device Management: CPU/GPU allocation and tensor operations

Key Features:
    - Unified provider interface for all LLM services
    - Support for multiple LLM providers:
        * OpenAI (GPT-3.5, GPT-4, etc.)
        * Google Gemini (gemini-pro, etc.)
        * Groq (llama2, mixtral, etc.)
        * Anthropic Claude (claude-3-sonnet, etc.)
        * Ollama (local open-source models)
        * HuggingFace Transformers (custom LLM models)
    - HuggingFace model loader for NER, relation extraction, and triplet extraction
    - Automatic API key management from environment variables
    - Structured JSON output generation
    - Model caching and device management (CPU/GPU)
    - Graceful fallback when providers are unavailable
    - Custom provider registration support

Main Classes:
    - BaseProvider: Abstract base class for all providers
    - OpenAIProvider: OpenAI API provider implementation
    - GeminiProvider: Google Gemini API provider implementation
    - GroqProvider: Groq API provider implementation
    - AnthropicProvider: Anthropic Claude API provider implementation
    - OllamaProvider: Ollama local provider implementation
    - HuggingFaceLLMProvider: HuggingFace transformers for LLM tasks
    - HuggingFaceModelLoader: Loader for HuggingFace models (NER, RE, TE)

Functions:
    - create_provider: Factory function to create provider instances

Example Usage:
    >>> from semantica.semantic_extract.providers import create_provider
    >>> provider = create_provider("openai", model="gpt-4")
    >>> response = provider.generate("Extract entities from: Apple Inc. was founded in 1976.")
    >>> 
    >>> loader = HuggingFaceModelLoader(device="cuda")
    >>> ner_model = loader.load_ner_model("dslim/bert-base-NER")

Author: Semantica Contributors
License: MIT
"""

import json
import os
from typing import Any, Dict, List, Optional, Union

import torch

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from .config import config
from .registry import provider_registry


class BaseProvider:
    """Base class for providers - makes it easy to add custom providers."""

    def __init__(self, **kwargs):
        """Initialize provider."""
        self.config = kwargs
        self.logger = get_logger(f"provider_{self.__class__.__name__}")

    def is_available(self) -> bool:
        """Check if provider is available."""
        return True

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text - must be implemented."""
        raise NotImplementedError

    def generate_structured(self, prompt: str, **kwargs) -> Union[dict, list]:
        """Generate structured output - must be implemented."""
        raise NotImplementedError

    def _parse_json(self, text: str) -> Union[dict, list]:
        """Extract and parse JSON from text, supporting objects and lists."""
        if not text:
            raise ProcessingError("Empty response from LLM")
            
        # Clean up text - remove markdown code blocks if present
        cleaned_text = text.strip()
        if "```json" in cleaned_text:
            cleaned_text = cleaned_text.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_text:
            # Try to find the block that looks most like JSON
            blocks = cleaned_text.split("```")
            for block in blocks:
                block = block.strip()
                if (block.startswith("{") and block.endswith("}")) or \
                   (block.startswith("[") and block.endswith("]")):
                    cleaned_text = block
                    break

        def fix_json(json_str: str) -> str:
            """Basic JSON fixing for common LLM errors."""
            # Remove trailing commas before closing braces/brackets
            json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
            return json_str

        import re

        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Try to find JSON boundaries (outermost { } or [ ])
            start_obj = cleaned_text.find("{")
            start_list = cleaned_text.find("[")
            
            # Determine which one starts first
            start = -1
            if start_obj >= 0 and (start_list < 0 or start_obj < start_list):
                start = start_obj
            elif start_list >= 0:
                start = start_list
            
            if start >= 0:
                # Find the corresponding end
                end_obj = cleaned_text.rfind("}")
                end_list = cleaned_text.rfind("]")
                end = max(end_obj, end_list)
                
                if end > start:
                    candidate = cleaned_text[start:end+1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        # Try fixing common errors
                        try:
                            return json.loads(fix_json(candidate))
                        except json.JSONDecodeError:
                            # Last resort: if it's truncated, try to close it
                            if candidate.endswith("..."):
                                candidate = candidate[:-3].strip()
                            
                            # Simple attempt to close unclosed structures
                            # This is very basic and might not work for complex cases
                            open_braces = candidate.count("{") - candidate.count("}")
                            open_brackets = candidate.count("[") - candidate.count("]")
                            
                            fixed_candidate = candidate
                            if open_braces > 0:
                                fixed_candidate += "}" * open_braces
                            if open_brackets > 0:
                                fixed_candidate += "]" * open_brackets
                                
                            try:
                                return json.loads(fix_json(fixed_candidate))
                            except json.JSONDecodeError as e:
                                raise ProcessingError(f"Failed to parse extracted JSON: {e}\nRaw snippet: {candidate[:50]}...")
            
            raise ProcessingError(f"No JSON structure found in response. Raw response: {text[:100]}...")

class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", **kwargs
    ):
        """Initialize OpenAI provider."""
        super().__init__(**kwargs)
        self.api_key = api_key or config.get_api_key("openai")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            if self.api_key:
                self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            self.client = None
            self.logger.warning(
                "openai library not installed. Install with: pip install semantica[llm-openai]"
            )

    def is_available(self) -> bool:
        """Check if provider is available."""
        return self.client is not None

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if not self.client:
            raise ProcessingError(
                "OpenAI client not initialized. Set OPENAI_API_KEY or pass api_key."
            )

        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.3),
        )
        return response.choices[0].message.content

    def generate_structured(self, prompt: str, **kwargs) -> dict:
        """Generate structured JSON output."""
        if not self.client:
            raise ProcessingError("OpenAI client not initialized.")

        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=kwargs.get("temperature", 0.3),
        )
        try:
            return self._parse_json(response.choices[0].message.content)
        except Exception as e:
            raise ProcessingError(f"Failed to parse JSON from OpenAI response: {e}")


class GeminiProvider(BaseProvider):
    """Google Gemini provider implementation."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gemini-pro", **kwargs
    ):
        """Initialize Gemini provider."""
        super().__init__(**kwargs)
        self.api_key = api_key or config.get_api_key("gemini")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai

            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
        except ImportError:
            self.client = None
            self.logger.warning(
                "google-generativeai library not installed. Install with: pip install semantica[llm-gemini]"
            )

    def is_available(self) -> bool:
        """Check if provider is available."""
        return self.client is not None

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if not self.client:
            raise ProcessingError(
                "Gemini client not initialized. Set GEMINI_API_KEY or pass api_key."
            )

        response = self.client.generate_content(
            prompt, generation_config={"temperature": kwargs.get("temperature", 0.3)}
        )
        return response.text

    def generate_structured(self, prompt: str, **kwargs) -> dict:
        """Generate structured output."""
        if not self.client:
            raise ProcessingError("Gemini client not initialized.")

        # Add JSON format instruction to prompt
        json_prompt = f"{prompt}\n\nReturn the response as valid JSON only."
        response = self.client.generate_content(json_prompt)
        try:
            return self._parse_json(response.text)
        except Exception as e:
            raise ProcessingError(f"Failed to parse JSON from Gemini response: {e}")


class GroqProvider(BaseProvider):
    """Groq provider implementation."""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "llama2-70b-4096", **kwargs
    ):
        """Initialize Groq provider."""
        super().__init__(**kwargs)
        self.api_key = api_key or config.get_api_key("groq")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Groq client."""
        try:
            from groq import Groq

            if self.api_key:
                self.client = Groq(api_key=self.api_key)
        except ImportError:
            self.client = None
            self.logger.warning(
                "groq library not installed. Install with: pip install semantica[llm-groq]"
            )

    def is_available(self) -> bool:
        """Check if provider is available."""
        return self.client is not None

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if not self.client:
            raise ProcessingError(
                "Groq client not initialized. Set GROQ_API_KEY or pass api_key."
            )

        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.3),
        )
        return response.choices[0].message.content

    def generate_structured(self, prompt: str, **kwargs) -> dict:
        """Generate structured output."""
        if not self.client:
            raise ProcessingError("Groq client not initialized.")

        json_prompt = f"{prompt}\n\nReturn the response as valid JSON only."
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "user", "content": json_prompt}],
            temperature=kwargs.get("temperature", 0.3),
        )
        try:
            return self._parse_json(response.choices[0].message.content)
        except Exception as e:
            raise ProcessingError(f"Failed to parse JSON from Groq response: {e}")


class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229",
        **kwargs,
    ):
        """Initialize Anthropic provider."""
        super().__init__(**kwargs)
        self.api_key = api_key or config.get_api_key("anthropic")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Anthropic client."""
        try:
            from anthropic import Anthropic

            if self.api_key:
                self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            self.client = None
            self.logger.warning(
                "anthropic library not installed. Install with: pip install semantica[llm-anthropic]"
            )

    def is_available(self) -> bool:
        """Check if provider is available."""
        return self.client is not None

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if not self.client:
            raise ProcessingError(
                "Anthropic client not initialized. Set ANTHROPIC_API_KEY or pass api_key."
            )

        response = self.client.messages.create(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", 4096),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def generate_structured(self, prompt: str, **kwargs) -> dict:
        """Generate structured output."""
        if not self.client:
            raise ProcessingError("Anthropic client not initialized.")

        json_prompt = f"{prompt}\n\nReturn the response as valid JSON only."
        response = self.client.messages.create(
            model=kwargs.get("model", self.model),
            max_tokens=kwargs.get("max_tokens", 4096),
            messages=[{"role": "user", "content": json_prompt}],
        )
        try:
            return self._parse_json(response.content[0].text)
        except Exception as e:
            raise ProcessingError(f"Failed to parse JSON from Anthropic response: {e}")


class OllamaProvider(BaseProvider):
    """Ollama local provider implementation."""

    def __init__(
        self, base_url: str = "http://localhost:11434", model: str = "llama2", **kwargs
    ):
        """Initialize Ollama provider."""
        super().__init__(**kwargs)
        self.base_url = base_url
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Ollama client."""
        try:
            import ollama

            self.client = ollama
            # Test connection
            try:
                self.client.list()  # Test if Ollama is running
            except Exception:
                self.client = None
                self.logger.warning(
                    "Ollama server not accessible. Make sure Ollama is running."
                )
        except ImportError:
            self.client = None
            self.logger.warning(
                "ollama library not installed. Install with: pip install semantica[llm-ollama]"
            )

    def is_available(self) -> bool:
        """Check if provider is available."""
        return self.client is not None

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if not self.client:
            raise ProcessingError(
                "Ollama client not initialized. Make sure Ollama is running."
            )

        response = self.client.generate(
            model=kwargs.get("model", self.model),
            prompt=prompt,
            options={"temperature": kwargs.get("temperature", 0.3)},
        )
        return response.get("response", "")

    def generate_structured(self, prompt: str, **kwargs) -> dict:
        """Generate structured output."""
        if not self.client:
            raise ProcessingError("Ollama client not initialized.")

        json_prompt = f"{prompt}\n\nReturn the response as valid JSON only."
        response = self.client.generate(
            model=kwargs.get("model", self.model),
            prompt=json_prompt,
            options={"temperature": kwargs.get("temperature", 0.3)},
        )
        try:
            return self._parse_json(response.get("response", "{}"))
        except Exception as e:
            raise ProcessingError(f"Failed to parse JSON from Ollama response: {e}")


class DeepSeekProvider(BaseProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat", **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key or config.get_api_key("deepseek")
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            import deepseek

            if self.api_key:
                self.client = deepseek.Client(api_key=self.api_key)
        except ImportError:
            self.client = None
            self.logger.warning(
                "deepseek library not installed. Install with: pip install semantica[llm-deepseek]"
            )

    def is_available(self) -> bool:
        return self.client is not None

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.client:
            raise ProcessingError("DeepSeek client not initialized. Set DEEPSEEK_API_KEY or pass api_key.")
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.3),
        )
        return response.choices[0].message.content
    def generate_structured(self, prompt: str, **kwargs) -> Union[dict, list]:
        """Generate structured output."""
        if not self.client:
            raise ProcessingError("DeepSeek client not initialized.")
        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.3),
        )
        try:
            return self._parse_json(response.choices[0].message.content)
        except Exception as e:
            raise ProcessingError(f"Failed to parse JSON from DeepSeek response: {e}")

class HuggingFaceLLMProvider(BaseProvider):
    """HuggingFace transformers for LLM tasks."""

    def __init__(
        self, model_name: str = "gpt2", device: Optional[str] = None, **kwargs
    ):
        """Initialize HuggingFace LLM provider."""
        super().__init__(**kwargs)
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self._init_model()

    def _init_model(self):
        """Initialize HuggingFace model."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
        except ImportError:
            self.logger.warning(
                "transformers library not installed. Install with: pip install semantica[models-huggingface]"
            )
        except Exception as e:
            self.logger.warning(
                f"Failed to load HuggingFace model {self.model_name}: {e}"
            )
            self.model = None

    def is_available(self) -> bool:
        """Check if provider is available."""
        return self.model is not None and self.tokenizer is not None

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        if not self.model or not self.tokenizer:
            raise ProcessingError("HuggingFace model not initialized.")

        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            inputs,
            max_length=kwargs.get("max_length", 100),
            temperature=kwargs.get("temperature", 0.7),
            do_sample=True,
        )
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the original prompt from the response
        return generated_text[len(prompt) :].strip()

    def generate_structured(self, prompt: str, **kwargs) -> dict:
        """Generate structured output."""
        response = self.generate(prompt, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
            raise ProcessingError("Failed to parse JSON from HuggingFace response")


class HuggingFaceModelLoader:
    """HuggingFace model loader for NER, RE, Triplets."""

    def __init__(self, device: Optional[str] = None):
        """Initialize HuggingFace model loader."""
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._cache: Dict[str, Any] = {}
        self.logger = get_logger("huggingface_loader")

    def load_ner_model(self, model_name: str, **kwargs):
        """Load NER model."""
        cache_key = f"{model_name}_ner"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            from transformers import pipeline

            nlp = pipeline(
                "ner",
                model=model_name,
                device=self.device if torch.cuda.is_available() else -1,
                aggregation_strategy="simple",
            )
            self._cache[cache_key] = nlp
            return nlp
        except ImportError:
            raise ImportError(
                "transformers library not installed. Install with: pip install semantica[models-huggingface]"
            )
        except Exception as e:
            self.logger.error(f"Failed to load NER model {model_name}: {e}")
            raise

    def load_relation_model(self, model_name: str, **kwargs):
        """Load relation extraction model."""
        cache_key = f"{model_name}_relation"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            from transformers import pipeline

            nlp = pipeline(
                "text-classification",
                model=model_name,
                device=self.device if torch.cuda.is_available() else -1,
            )
            self._cache[cache_key] = nlp
            return nlp
        except ImportError:
            raise ImportError(
                "transformers library not installed. Install with: pip install semantica[models-huggingface]"
            )
        except Exception as e:
            self.logger.error(f"Failed to load relation model {model_name}: {e}")
            raise

    def load_triplet_model(self, model_name: str, **kwargs):
        """Load triplet extraction model."""
        cache_key = f"{model_name}_triplet"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            model.to(self.device)

            nlp = {"tokenizer": tokenizer, "model": model, "device": self.device}
            self._cache[cache_key] = nlp
            return nlp
        except ImportError:
            raise ImportError(
                "transformers library not installed. Install with: pip install semantica[models-huggingface]"
            )
        except Exception as e:
            self.logger.error(f"Failed to load triplet model {model_name}: {e}")
            raise

    def extract_entities(self, model, text: str) -> List[Dict]:
        """Extract entities using loaded model."""
        return model(text)

    def extract_relations(self, model, text: str, entities: List) -> List[Dict]:
        """Extract relations using loaded model."""
        # This would need to be customized based on the model architecture
        return model(text)

    def extract_triplets(self, model, text: str) -> List[Dict]:
        """Extract triplets using loaded model."""
        tokenizer = model["tokenizer"]
        model_obj = model["model"]
        device = model["device"]

        inputs = tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        ).to(device)
        outputs = model_obj.generate(**inputs, max_length=128)
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Parse decoded output (format depends on model)
        # This is a placeholder - actual parsing would depend on model output format
        return [{"triplet": decoded}]


def create_provider(name: str, **kwargs) -> BaseProvider:
    """Create provider - checks registry for custom providers."""
    # Check registry first
    custom_provider = provider_registry.get(name)
    if custom_provider:
        return custom_provider(**kwargs)

    # Built-in providers
    builtin = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "groq": GroqProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "huggingface_llm": HuggingFaceLLMProvider,
        "deepseek": DeepSeekProvider,
    }

    provider_class = builtin.get(name.lower())
    if not provider_class:
        raise ValueError(
            f"Unknown provider: {name}. Register custom provider or use built-in: {list(builtin.keys())}"
        )

    return provider_class(**kwargs)
