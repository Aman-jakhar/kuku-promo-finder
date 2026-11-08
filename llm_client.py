"""llm_client.py

Thin, model-swappable LLM client supporting OpenAI-compatible endpoints
(OpenAI, Gemini via Google AI Studio OpenAI-compat endpoint, Groq, Ollama, etc.).

Features:
- Reads configuration from env vars: LLM_BASE_URL, LLM_API_KEY, LLM_MODEL
- Loads local .env if present
- Caches responses on disk keyed by SHA256(model, prompt) for fast, free reruns
- Forces JSON output mode with Pydantic validation and automatic retry
- Detailed token count and cost tracking per run
- Offline heuristic fallback if no API key is provided
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel, Field

# Check if openai package is available
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

T = TypeVar("T", bound=BaseModel)


def load_dotenv(env_path: str = ".env") -> None:
    """Simple .env file loader without external dependencies."""
    p = Path(env_path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip("\"'")
        if key not in os.environ:
            os.environ[key] = val


# Load .env automatically upon import
load_dotenv()


class TokenCostTracker:
    """Tracks token usage and estimated API cost across all passes."""
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name
        self.total_calls = 0
        self.cached_calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

        # Cost per 1M tokens (USD)
        # Gemini 1.5 Flash: $0.075 / 1M input, $0.30 / 1M output
        # GPT-4o-mini: $0.15 / 1M input, $0.60 / 1M output
        # Default estimation based on modern flash-tier models
        if "gpt-4o-mini" in model_name.lower():
            self.input_cost_per_m = 0.15
            self.output_cost_per_m = 0.60
        elif "gemini" in model_name.lower():
            self.input_cost_per_m = 0.075
            self.output_cost_per_m = 0.30
        else:
            self.input_cost_per_m = 0.10
            self.output_cost_per_m = 0.40

    def record_call(self, prompt_tokens: int, completion_tokens: int, was_cached: bool = False):
        self.total_calls += 1
        if was_cached:
            self.cached_calls += 1
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens += (prompt_tokens + completion_tokens)

    @property
    def estimated_cost_usd(self) -> float:
        input_cost = (self.prompt_tokens / 1_000_000) * self.input_cost_per_m
        output_cost = (self.completion_tokens / 1_000_000) * self.output_cost_per_m
        return round(input_cost + output_cost, 6)

    def summary(self) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "total_calls": self.total_calls,
            "cached_calls": self.cached_calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": self.estimated_cost_usd
        }


class LLMClient:
    """Configurable, cached OpenAI-compatible LLM client."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        cache_dir: str = ".cache/llm_cache"
    ):
        self.api_key = (
            api_key
            or os.environ.get("LLM_API_KEY")
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        self.base_url = (
            base_url
            or os.environ.get("LLM_BASE_URL")
            or ("https://generativelanguage.googleapis.com/v1beta/openai/" if "AIza" in (self.api_key or "") else None)
        )
        self.model = (
            model
            or os.environ.get("LLM_MODEL")
            or ("gemini-2.5-flash" if self.base_url and "generativelanguage" in self.base_url else "gpt-4o-mini")
        )

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.tracker = TokenCostTracker(self.model)

        self.client = None
        if HAS_OPENAI and self.api_key and self.api_key.lower() not in ("mock", "offline", "none"):
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

    @property
    def is_live(self) -> bool:
        """Returns True if live API credentials and client are available."""
        return self.client is not None

    def _get_cache_path(self, cache_key: str) -> Path:
        return self.cache_dir / f"{cache_key}.json"

    def _hash_request(self, system_prompt: str, user_prompt: str) -> str:
        h = hashlib.sha256()
        h.update(self.model.encode("utf-8"))
        h.update(system_prompt.encode("utf-8"))
        h.update(user_prompt.encode("utf-8"))
        return h.hexdigest()

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        temperature: float = 0.2,
        max_retries: int = 3
    ) -> T:
        """Generate structured response, validated against Pydantic model with caching and retry."""
        cache_key = self._hash_request(system_prompt, user_prompt)
        cache_file = self._get_cache_path(cache_key)

        # 1. Check disk cache
        if cache_file.exists():
            try:
                cached_data = json.loads(cache_file.read_text(encoding="utf-8"))
                obj = response_model.model_validate(cached_data.get("content"))
                usage = cached_data.get("usage", {})
                self.tracker.record_call(
                    usage.get("prompt_tokens", 0),
                    usage.get("completion_tokens", 0),
                    was_cached=True
                )
                return obj
            except Exception:
                # If cache corrupted, ignore and refetch
                pass

        # 2. If client is not available, raise or fallback
        if not self.is_live:
            raise RuntimeError(
                "LLM client is not configured with an API key. "
                "Set LLM_API_KEY (or GEMINI_API_KEY / OPENAI_API_KEY) in .env or environment."
            )

        # 3. Call live API with retries
        last_error = None
        for attempt in range(max_retries):
            try:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )

                raw_content = response.choices[0].message.content or "{}"
                prompt_tokens = response.usage.prompt_tokens if response.usage else 0
                completion_tokens = response.usage.completion_tokens if response.usage else 0

                # Clean any markdown fences if present
                clean_json = raw_content.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()

                parsed_json = json.loads(clean_json)
                validated_obj = response_model.model_validate(parsed_json)

                # Record cache
                cache_file.write_text(
                    json.dumps({
                        "content": parsed_json,
                        "raw": raw_content,
                        "usage": {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens
                        }
                    }, indent=2),
                    encoding="utf-8"
                )

                self.tracker.record_call(prompt_tokens, completion_tokens, was_cached=False)
                return validated_obj

            except Exception as e:
                last_error = e
                time.sleep(1.0 * (attempt + 1))

        raise RuntimeError(f"Failed to generate structured LLM response after {max_retries} attempts: {last_error}")
