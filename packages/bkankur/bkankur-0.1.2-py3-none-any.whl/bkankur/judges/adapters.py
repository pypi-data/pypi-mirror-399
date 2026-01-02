from __future__ import annotations

"""bkankur.judges.adapters

Adapters to make it easy for external developers to plug in *any* LLM provider.

You can integrate by supplying a single function instead of writing a full class.

Contract:
- The adapter will build BKAnkur's judge prompts/messages.
- Your function must return a JSON string matching the schema.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from .base import JudgeBase
from ..models import Transaction
from ..schema import BKANKUR_JSON_SCHEMA
from ..prompts import build_input_for_responses, build_system_prompt, build_user_prompt


PromptFn = Callable[[str, str, Dict[str, Any], bool], str]
MessagesFn = Callable[[List[Dict[str, Any]], Dict[str, Any], bool], str]


def _extract_inputs_from_tx(tx: Transaction) -> tuple[list[str], dict[str, Any]]:
    """Extract retrieved context + ground truth from tx.metadata.

    This mirrors evaluator logic so adapters behave consistently.
    """
    md = getattr(tx, "metadata", {}) or {}

    retrieved = md.get("retrieved_context") or md.get("context") or []
    if not isinstance(retrieved, list):
        retrieved = [str(retrieved)]

    gt: Dict[str, Any] = {}
    if isinstance(md.get("ground_truth"), dict):
        gt = md["ground_truth"]
    elif isinstance(md.get("expected_answer"), str) and md["expected_answer"].strip():
        gt = {"answer": md["expected_answer"].strip()}

    return retrieved, gt


@dataclass
class PromptFunctionJudge(JudgeBase):
    """Adapter for providers that are easiest to call with (system_prompt, user_prompt).

    Developer supplies one function:
        fn(system_prompt, user_prompt, schema, repair_mode) -> str
    """

    fn: PromptFn

    def judge(
        self,
        tx: Transaction,
        schema: Optional[Dict[str, Any]] = None,
        repair_mode: bool = False,
        **kwargs: Any,
    ) -> str:
        retrieved_context, ground_truth = _extract_inputs_from_tx(tx)

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            user_text=getattr(tx, "user_text", "") or "",
            bot_text=getattr(tx, "bot_text", "") or "",
            retrieved_context=retrieved_context,
            ground_truth=ground_truth,
            metadata=getattr(tx, "metadata", {}) or {},
        )
        if repair_mode:
            user_prompt = "Your previous output was invalid JSON. Return valid JSON ONLY.\n" + user_prompt

        schema_to_use: Dict[str, Any] = schema if isinstance(schema, dict) else BKANKUR_JSON_SCHEMA
        return self.fn(system_prompt, user_prompt, schema_to_use, bool(repair_mode))


@dataclass
class MessagesFunctionJudge(JudgeBase):
    """Adapter for providers that accept OpenAI-style messages.

    Developer supplies one function:
        fn(messages, schema, repair_mode) -> str
    """

    fn: MessagesFn

    def judge(
        self,
        tx: Transaction,
        schema: Optional[Dict[str, Any]] = None,
        repair_mode: bool = False,
        **kwargs: Any,
    ) -> str:
        messages = build_input_for_responses(tx, repair_mode=repair_mode)
        schema_to_use: Dict[str, Any] = schema if isinstance(schema, dict) else BKANKUR_JSON_SCHEMA
        return self.fn(messages, schema_to_use, bool(repair_mode))
