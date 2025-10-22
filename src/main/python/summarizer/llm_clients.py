"""LLM client implementations for different providers."""

import os
from typing import Optional, Protocol


class LLMClient(Protocol):
    """Minimal interface for a text-completion client."""
    def complete(self, prompt: str) -> str:  # pragma: no cover - interface
        ...


class OpenAIClient:
    """OpenAI Chat Completions wrapper.

    Requirements:
      pip install openai
      export OPENAI_API_KEY=...  (or pass --api-key)
    """

    def __init__(self, model: str, api_key: Optional[str] = None) -> None:
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover - import error path
            raise RuntimeError("Missing dependency: pip install openai") from e
        self._OpenAI = OpenAI
        self._client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self._model = model

    def complete(self, prompt: str) -> str:
        # Use Chat Completions for broad compatibility
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a meticulous and concise summarizer."
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""


class GeminiClient:
    """Google Gemini wrapper.

    Requirements:
      pip install google-generativeai
      export GOOGLE_API_KEY=...  (or pass --api-key)
    """

    def __init__(self, model: str, api_key: Optional[str] = None) -> None:
        try:
            import google.generativeai as genai  # type: ignore
        except Exception as e:  # pragma: no cover - import error
            raise RuntimeError(
                "Missing dependency: pip install google-generativeai"
            ) from e
        self._genai = genai
        self._genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self._model = genai.GenerativeModel(model)

    def complete(self, prompt: str) -> str:
        resp = self._model.generate_content(prompt)
        return getattr(resp, "text", "").strip()


class ClaudeClient:
    """Anthropic Claude wrapper.

    Requirements:
      pip install anthropic
      export ANTHROPIC_API_KEY=...  (or pass --api-key)
    """

    def __init__(self, model: str, api_key: Optional[str] = None) -> None:
        try:
            from anthropic import Anthropic  # type: ignore
        except Exception as e:  # pragma: no cover - import error path
            raise RuntimeError("Missing dependency: pip install anthropic") from e
        self._Anthropic = Anthropic
        self._client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self._model = model

    def complete(self, prompt: str) -> str:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system="You are a meticulous and concise summarizer.",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return resp.content[0].text if resp.content else ""


def make_client(provider: str, model: str, api_key: Optional[str]) -> LLMClient:
    """Factory function to create LLM clients based on provider."""
    p = provider.lower()
    if p in {"openai", "chatgpt", "gpt"}:
        return OpenAIClient(model=model, api_key=api_key)
    if p in {"gemini", "google"}:
        return GeminiClient(model=model, api_key=api_key)
    if p in {"claude", "anthropic"}:
        return ClaudeClient(model=model, api_key=api_key)
    raise SystemExit(
        f"Unsupported provider: {provider}. Try 'openai', 'gemini', or 'claude'."
    )
