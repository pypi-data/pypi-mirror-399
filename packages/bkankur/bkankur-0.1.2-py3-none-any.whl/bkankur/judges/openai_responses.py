from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import httpx

from .base import JudgeBase
from ..models import Transaction
from ..prompts import build_input_for_responses
from ..schema import BKANKUR_JSON_SCHEMA


class OpenAIResponsesJudge(JudgeBase):
    """
    OpenAI Responses API Judge with retries + HTML detection.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout_s: float = 45.0,
        store: bool = False,
        retries: int = 2,
        retry_backoff_s: float = 1.0,
        trust_env: bool = False,
        http2: bool = False,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_s = float(timeout_s)
        self.store = bool(store)
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
            "User-Agent": "bkankur-openai-responses-judge/1.0",
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

    def judge(
        self,
        tx: Optional[Transaction] = None,
        schema: Optional[Dict[str, Any]] = None,
        repair_mode: bool = False,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> str:
        if isinstance(messages, list) and messages:
            input_items = messages
        elif system_prompt is not None and user_prompt is not None:
            input_items = [
                {"role": "system", "content": str(system_prompt)},
                {"role": "user", "content": str(user_prompt)},
            ]
        else:
            if tx is None:
                raise RuntimeError("OpenAIResponsesJudge.judge(): provide tx or system_prompt+user_prompt or messages.")
            input_items = build_input_for_responses(tx, repair_mode=repair_mode)

        schema_to_use: Dict[str, Any] = schema if isinstance(schema, dict) else BKANKUR_JSON_SCHEMA

        url = f"{self.base_url}/responses"
        payload: Dict[str, Any] = {
            "model": self.model,
            "input": input_items,
            "store": self.store,
            "temperature": 0,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "bkankur_rai_scores",
                    "strict": True,
                    "schema": schema_to_use,
                }
            },
        }

        r = self._post_with_retries(url, payload)

        if self._is_html_like(r):
            preview = (r.text or "")[:300]
            raise RuntimeError(
                f"Responses API returned HTML (status={r.status_code}). "
                f"This is OpenAI edge/origin issue (or rare network interception). Preview: {preview}"
            )

        # If strict schema triggers backend instability, retry with json_object once.
        if r.status_code in (500, 502, 503, 504, 520):
            payload2 = dict(payload)
            payload2["text"] = {"format": {"type": "json_object"}}
            r2 = self._post_with_retries(url, payload2)

            if self._is_html_like(r2):
                preview2 = (r2.text or "")[:300]
                raise RuntimeError(
                    f"Responses fallback also returned HTML (status={r2.status_code}). Preview: {preview2}"
                )
            r2.raise_for_status()
            data2 = r2.json()
            for item in data2.get("output", []):
                if item.get("type") == "message" and item.get("role") == "assistant":
                    for c in item.get("content", []):
                        if c.get("type") == "output_text" and "text" in c:
                            return c["text"]

        r.raise_for_status()
        data = r.json()

        for item in data.get("output", []):
            if item.get("type") == "message" and item.get("role") == "assistant":
                for c in item.get("content", []):
                    if c.get("type") == "output_text" and "text" in c:
                        return c["text"]

        raise RuntimeError("No output_text found in Responses API response.")
