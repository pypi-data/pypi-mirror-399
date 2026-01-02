from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from .base import JudgeBase
from ..models import Transaction
from ..prompts import build_messages_for_chat, build_input_for_responses


def _is_openai_base_url(base_url: str) -> bool:
    return base_url.rstrip("/").lower() == "https://api.openai.com/v1"


class OpenAICompatibleChatJudge(JudgeBase):
    """
    /v1/chat/completions Judge for OpenAI-compatible providers.

    Production hardening + IMPORTANT:
    If base_url is OpenAI and chat/completions returns 520/HTML/5xx,
    auto-fallback to /v1/responses json_object so the demo does not die.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        timeout_s: float = 30.0,
        retries: int = 2,
        retry_backoff_s: float = 1.0,
        trust_env: bool = False,
        http2: bool = False,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_s = float(timeout_s)
        self.retries = int(retries or 0)
        self.retry_backoff_s = float(retry_backoff_s or 1.0)

        limits = httpx.Limits(max_connections=50, max_keepalive_connections=20)
        self._client = httpx.Client(
            timeout=httpx.Timeout(self.timeout_s),
            follow_redirects=True,
            trust_env=bool(trust_env),
            http2=bool(http2),
            limits=limits,
        )

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass

    def __del__(self) -> None:
        self.close()

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "bkankur-openai-chat-judge/1.0",
        }

    @staticmethod
    def _is_html_like(r: httpx.Response) -> bool:
        ct = (r.headers.get("content-type") or "").lower()
        if "text/html" in ct:
            return True
        try:
            t = (r.text or "").lstrip()[:30].lower()
            return t.startswith("<!doctype html") or t.startswith("<html")
        except Exception:
            return False

    def _post_with_retries(self, url: str, payload: Dict[str, Any]) -> httpx.Response:
        retry_statuses = {408, 409, 425, 429, 500, 502, 503, 504, 520}
        attempt = 0
        while True:
            try:
                r = self._client.post(url, headers=self._headers(), json=payload)
                if r.status_code in retry_statuses and attempt < self.retries:
                    time.sleep(min(self.retry_backoff_s * (2 ** attempt), 12.0))
                    attempt += 1
                    continue
                return r
            except (httpx.TimeoutException, httpx.NetworkError):
                if attempt >= self.retries:
                    raise
                time.sleep(min(self.retry_backoff_s * (2 ** attempt), 12.0))
                attempt += 1

    def _chat_completions(self, messages: Any) -> str:
        url = f"{self.base_url}/chat/completions"

        # Try with response_format first (nice when supported)
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        r = self._post_with_retries(url, payload)

        # Some edges/models behave badly; retry once without response_format
        if r.status_code in (400, 415, 500, 502, 503, 504, 520) or self._is_html_like(r):
            payload2 = {
                "model": self.model,
                "messages": messages,
                "temperature": 0,
            }
            r2 = self._post_with_retries(url, payload2)
            r = r2

        if self._is_html_like(r):
            preview = (r.text or "")[:300]
            raise RuntimeError(
                f"Chat Completions returned HTML (status={r.status_code}). Preview: {preview}"
            )

        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]

    def _responses_fallback(self, tx: Transaction, repair_mode: bool) -> str:
        url = f"{self.base_url}/responses"
        input_items = build_input_for_responses(tx, repair_mode=repair_mode)

        payload = {
            "model": self.model,
            "input": input_items,
            "temperature": 0,
            "text": {"format": {"type": "json_object"}},
        }

        r = self._post_with_retries(url, payload)

        if self._is_html_like(r):
            preview = (r.text or "")[:300]
            raise RuntimeError(
                f"Responses fallback returned HTML (status={r.status_code}). Preview: {preview}"
            )

        r.raise_for_status()
        data = r.json()

        for item in data.get("output", []):
            if item.get("type") == "message" and item.get("role") == "assistant":
                for c in item.get("content", []):
                    if c.get("type") == "output_text" and "text" in c:
                        return c["text"]

        raise RuntimeError("No output_text found in Responses fallback response.")

    def judge(
        self,
        tx: Transaction,
        schema: Optional[Dict[str, Any]] = None,
        repair_mode: bool = False,
        **kwargs: Any,
    ) -> str:
        messages = build_messages_for_chat(tx, repair_mode=repair_mode)

        try:
            return self._chat_completions(messages)
        except Exception as e:
            # Only do this fallback for OpenAI.
            if _is_openai_base_url(self.base_url):
                # This is exactly your case: /chat/completions gives 520 HTML.
                return self._responses_fallback(tx, repair_mode=repair_mode)
            raise
