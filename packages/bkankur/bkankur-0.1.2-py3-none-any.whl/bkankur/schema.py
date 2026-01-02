# bkankur/schema.py
# Purpose:
# - Pydantic models for judge output + evaluation report
# - JSON Schema constant used by OpenAIResponsesJudge (Responses API structured outputs):
#     BKANKUR_JSON_SCHEMA  (RAW schema dict)

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

from .prompts import METRIC_IDS


def clamp_pct(x: float) -> float:
    if x < 0:
        return 0.0
    if x > 100:
        return 100.0
    return float(x)


class MetricResult(BaseModel):
    not_applicable: bool = False

    # Judge-provided signals
    severity: Optional[float] = Field(default=None, description="0-100 impact if misused")
    confidence: Optional[float] = Field(default=None, description="0-100 how sure")
    risk_pct: Optional[float] = Field(default=None, description="0-100 risk (optional; evaluator can derive)")

    # Derived in evaluator
    safe_pct: Optional[float] = Field(default=None, description="100 - risk_pct")

    reason: str = ""
    evidence: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_ranges(self):
        if self.not_applicable:
            self.severity = None
            self.confidence = None
            self.risk_pct = None
            self.safe_pct = None
            return self

        if self.severity is not None:
            self.severity = clamp_pct(self.severity)
        if self.confidence is not None:
            self.confidence = clamp_pct(self.confidence)
        if self.risk_pct is not None:
            self.risk_pct = clamp_pct(self.risk_pct)
        if self.safe_pct is not None:
            self.safe_pct = clamp_pct(self.safe_pct)

        return self


class JudgeOutput(BaseModel):
    prompt_version: str
    metrics: Dict[str, MetricResult]
    notes: str = ""


class EvaluationReport(BaseModel):
    transaction_id: Optional[str] = None
    metrics: Dict[str, MetricResult] = Field(default_factory=dict)
    overall_safe_pct: float = 0.0

    # NOTE: suggestion only; developer decides allow/block
    recommendation: str = "UNKNOWN"

    errors: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "transaction_id": self.transaction_id,
            "recommendation": self.recommendation,
            "overall_safe_pct": self.overall_safe_pct,
            "metrics": {},
            "errors": self.errors,
            "meta": self.meta,
        }
        for k, v in self.metrics.items():
            out["metrics"][k] = {
                "not_applicable": v.not_applicable,
                "severity": v.severity,
                "confidence": v.confidence,
                "risk_pct": v.risk_pct,
                "safe_pct": v.safe_pct,
                "reason": v.reason,
                "evidence": v.evidence,
            }
        return out

    # -------- Library-level pretty output (minimal dev code) --------
    def pretty(
        self,
        *,
        include_evidence: bool = False,
        include_meta: bool = False,
        compact: bool = True,
        max_reason_len: int = 180,
    ) -> str:
        from .reporting import format_report_dict  # local import to avoid cycles

        return format_report_dict(
            self.to_dict(),
            include_evidence=include_evidence,
            include_meta=include_meta,
            compact=compact,
            max_reason_len=max_reason_len,
        )

    def __str__(self) -> str:
        return self.pretty()


# -------------------------------------------------------------------
# JSON Schema for OpenAI Structured Outputs (Responses API)
# -------------------------------------------------------------------

def _nullable_number() -> Dict[str, Any]:
    """
    We keep Optional in Pydantic, but structured output schema asks the model
    to always output numbers. If N/A, it should output 0 and set not_applicable=true.
    """
    return {"type": "number"}


METRIC_RESULT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "not_applicable": {"type": "boolean"},
        "severity": _nullable_number(),
        "confidence": _nullable_number(),
        "risk_pct": _nullable_number(),
        "reason": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["not_applicable", "severity", "confidence", "risk_pct", "reason", "evidence"],
}

# Explicitly enumerate ALL metric IDs (no dynamic keys)
_METRICS_PROPERTIES: Dict[str, Any] = {mid: METRIC_RESULT_SCHEMA for mid in METRIC_IDS}

BKANKUR_OUTPUT_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "prompt_version": {"type": "string"},
        "metrics": {
            "type": "object",
            "additionalProperties": False,
            "properties": _METRICS_PROPERTIES,
            "required": list(METRIC_IDS),
        },
        "notes": {"type": "string"},
    },
    "required": ["prompt_version", "metrics", "notes"],
}

# -------------------------------------------------------------------
# Backward compatibility constants
# -------------------------------------------------------------------

# RAW schema dict for Responses API structured outputs:
BKANKUR_JSON_SCHEMA: Dict[str, Any] = BKANKUR_OUTPUT_JSON_SCHEMA

BKANKUR_RESPONSE_FORMAT: Dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "bkankur_eval",
        "schema": BKANKUR_OUTPUT_JSON_SCHEMA,
        "strict": True,
    },
}
