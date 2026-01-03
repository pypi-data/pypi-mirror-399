"""LLM provider adapters for different APIs. Calling LLM APIs and returning text."""

from abc import ABC, abstractmethod
from typing import Callable
import requests
import json

DEFAULT_TIMEOUT_SECONDS = 60
DEFAULT_TEMPERATURE = 0.0
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_OPENAI_MODEL = "gpt-4.1-nano"

class BaseLLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from prompt."""
        pass


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider."""
    
    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_GEMINI_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        timeout: int = DEFAULT_TIMEOUT_SECONDS
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    def generate(self, prompt: str) -> str:
        """Call Gemini API."""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": self.temperature},
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        
        resp = requests.post(
            self.api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=self.timeout
        )
        resp.raise_for_status()

        try:
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return text
        
        except Exception as e:
            raise RuntimeError(
                f"Gemini returned an unexpected payload. HTTP {resp.status_code}. "
                f"Response body: {resp.text}"
            ) from e


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider (Responses API)."""

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_OPENAI_MODEL,
        timeout: int = DEFAULT_TIMEOUT_SECONDS
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.temperature = DEFAULT_TEMPERATURE
        self.api_url = "https://api.openai.com/v1/responses"

    def generate(self, prompt: str) -> str:
        
        payload = {
            "model": self.model,
            "input": prompt,
            "temperature": self.temperature,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
            
        result = resp.json()

        if result.get('error'):
            if result['error']['param'] == 'temperature':
                payload.pop("temperature", None)
                resp = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                result = resp.json()
            else:
                raise Exception(f"API Error: {result['error']['message']}")

        # text extraction from Responses "output" items
        texts = []
        for item in result.get("output", []):
            if item.get("type") == "message" and item.get("role") == "assistant":
                for part in item.get("content", []):
                    if part.get("type") == "output_text" and "text" in part:
                        texts.append(part["text"])
        return "".join(texts)


LLMFunction = Callable[[str], str]

class FunctionProvider(BaseLLMProvider):
    """
    Adapter that turns a plain Python function (prompt: str) -> str
    into a BaseLLMProvider.
    """

    def __init__(self, llm_function: LLMFunction):
        if not callable(llm_function):
            raise TypeError("llm_function must be callable: (prompt: str) -> str")
        self.llm_function = llm_function

    def generate(self, prompt: str) -> str:
        out = self.llm_function(prompt)
        if not isinstance(out, str):
            raise TypeError(
                f"Custom llm_function must return a str, got {type(out).__name__}"
            )
        return out
