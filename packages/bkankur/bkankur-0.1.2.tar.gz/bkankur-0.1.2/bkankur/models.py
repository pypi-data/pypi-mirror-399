from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Transaction:
    """
    Minimal required:
      - user_text
      - bot_text

    Optional metadata (any keys you want):
      - retrieved_context: list[str]
      - ground_truth: str
      - system_prompt: str
      - developer_prompt: str
      - tools_spec: dict
      - tool_trace: dict/list
      - domain: str
      - language: str
    """
    user_text: str
    bot_text: str
    transaction_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MetricScore:
    safe_pct: float
    confidence: float
    reason: str

    @property
    def risk_pct(self) -> float:
        # Many teams like risk% rather than safe%. This avoids confusion.
        return max(0.0, min(100.0, 100.0 - float(self.safe_pct)))


@dataclass
class EvaluationReport:
    transaction_id: Optional[str]
    recommendation: str  # ALLOW / REVIEW / BLOCK / UNKNOWN
    overall_safe_pct: float
    overall_risk_pct: float
    failed_metrics: List[str] = field(default_factory=list)
    metrics: Dict[str, MetricScore] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    raw_judge_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "recommendation": self.recommendation,
            "overall_safe_pct": self.overall_safe_pct,
            "overall_risk_pct": self.overall_risk_pct,
            "failed_metrics": list(self.failed_metrics),
            "errors": list(self.errors),
            "metrics": {
                k: {
                    "safe_pct": v.safe_pct,
                    "risk_pct": v.risk_pct,
                    "confidence": v.confidence,
                    "reason": v.reason,
                }
                for k, v in self.metrics.items()
            },
        }
