from __future__ import annotations

"""bkankur.judges.generic

Generic OpenAI-compatible judge.

Use this when you have *any* provider exposing an OpenAI-style endpoint:
    POST {base_url}/chat/completions

Examples: DeepSeek, Groq, Together, Fireworks, vLLM gateways, Ollama OpenAI
compat servers, etc.

Notes (production):
- Most OpenAI-compatible providers support JSON mode via:
      response_format={"type": "json_object"}
  If a provider ignores it, your evaluator's JSON repair + schema validation
  will still catch bad output.
"""

import os
from typing import Any, Dict, Optional

from .openai_compatible_chat import OpenAICompatibleChatJudge
from ..models import Transaction


class GenericOpenAIJudge(OpenAICompatibleChatJudge):
    """Alias of OpenAICompatibleChatJudge with a clearer name for external devs."""

    # Keep signature explicit for IDE/autocomplete clarity
    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: Optional[str] = None,
        timeout_s: float = 45.0,
        retries: int = 0,
        retry_backoff_s: float = 1.0,
    ) -> None:
        # Allow clean developer code: api_key=None and use env vars
        resolved_key = api_key or os.getenv("BKANKUR_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not resolved_key:
            raise RuntimeError(
                "Missing API key. Set BKANKUR_API_KEY or OPENAI_API_KEY or pass api_key=..."
            )

        super().__init__(
            api_key=resolved_key,
            model=model,
            base_url=base_url,
            timeout_s=timeout_s,
            retries=retries,
            retry_backoff_s=retry_backoff_s,
        )

        # Optional: keep for debugging/printing (parent may already store it)
        self.api_key = resolved_key

    def judge(
        self,
        tx: Transaction,
        schema: Optional[Dict[str, Any]] = None,
        repair_mode: bool = False,
        **kwargs: Any,
    ) -> str:
        # delegate to parent implementation
        return super().judge(tx=tx, schema=schema, repair_mode=repair_mode, **kwargs)
