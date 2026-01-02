from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

from pydantic import BaseModel, Field, ValidationError


class MetricOut(BaseModel):
    safe_pct: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    reason: str


class JudgeOutput(BaseModel):
    metrics: Dict[str, MetricOut]


def extract_json_obj(text: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Tries:
      1) direct json.loads
      2) locate first '{' ... last '}' and parse
    Returns: (obj, error)
    """
    if text is None:
        return None, "Empty judge text"
    t = text.strip()
    if not t:
        return None, "Empty judge text"

    # 1) direct
    try:
        return json.loads(t), None
    except Exception:
        pass

    # 2) best-effort slice
    try:
        start = t.find("{")
        end = t.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None, "No JSON object boundaries found"
        sliced = t[start:end + 1]
        return json.loads(sliced), None
    except Exception as e:
        return None, f"JSON parse failed: {e}"


def validate_judge_output(obj: Dict[str, Any]) -> Tuple[Optional[JudgeOutput], Optional[str]]:
    try:
        parsed = JudgeOutput.model_validate(obj)
        return parsed, None
    except ValidationError as e:
        return None, f"Schema validation failed: {e}"
    except Exception as e:
        return None, f"Validation failed: {e}"
