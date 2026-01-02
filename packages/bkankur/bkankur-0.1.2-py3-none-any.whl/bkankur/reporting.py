from __future__ import annotations

from typing import Any, Dict, List, Optional


DEFAULT_METRIC_LABELS: Dict[str, str] = {
    # Quality / grounding
    "relevance": "Relevance to User Query",
    "faithfulness": "Faithfulness to Provided Context",
    "hallucination": "Hallucination Risk",
    "completeness": "Completeness",
    "accuracy": "Accuracy",
    "refusal": "Appropriate Refusal",
    "overrefusal": "Over-refusal Risk",

    # Security / privacy
    "security_prompt_injection": "Prompt Injection Resilience",
    "system_prompt_exfil": "Secret / System Prompt Leakage",
    "privacy_pii": "PII / Privacy Leakage",

    # Safety
    "self_harm": "Self-harm Safety",
    "hate_discrimination": "Hate / Discrimination Safety",
    "sexual_content": "Sexual Content Safety",
    "violence": "Violence Safety",
    "illicit_behavior": "Illicit Behavior Safety",

    # Fairness
    "fairness": "Fairness",
    "bias_fairness": "Bias & Fairness",

    # BK naming (your ask)
    "bk_self_respect": "User Respect & Empathy",           # customer support
    "bk_society_benefit": "Org Safety & Responsibility",   # organization-level
    "bk_benevolent_god": "Positive / Benevolent Guidance",

    # Other
    "hap": "Helpfulness & Positivity",
}


def _label(k: str) -> str:
    return DEFAULT_METRIC_LABELS.get(k, k)


def _short(s: Any, max_len: int) -> str:
    t = (s or "")
    if not isinstance(t, str):
        t = str(t)
    t = t.strip().replace("\n", " ").replace("\r", " ")
    if len(t) > max_len:
        return t[:max_len] + "..."
    return t


def _fmt(x: Any, *, width: int = 6, decimals: int = 1, na: bool = False) -> str:
    if na or x is None:
        return " " * (width - 3) + "n/a"
    try:
        return f"{float(x):{width}.{decimals}f}"
    except Exception:
        return " " * (width - 3) + "n/a"


def format_report_dict(
    d: Dict[str, Any],
    *,
    include_evidence: bool = False,
    include_meta: bool = False,
    compact: bool = True,
    max_reason_len: int = 180,
) -> str:
    rec = d.get("recommendation", "UNKNOWN")
    overall = d.get("overall_safe_pct")
    txid = d.get("transaction_id")

    lines: List[str] = []
    lines.append(f"Recommendation: {rec} | Overall safe%: {_fmt(overall, width=6, decimals=3)}")
    if txid:
        lines.append(f"Transaction ID: {txid}")

    metrics = d.get("metrics") or {}
    if not isinstance(metrics, dict) or not metrics:
        lines.append("(No metrics present)")
    else:
        # Stable order: print known metrics in the order from prompts.METRIC_IDS if available,
        # otherwise print in sorted order.
        order: List[str]
        try:
            from .prompts import METRIC_IDS  # lazy import to avoid cycles
            order = list(METRIC_IDS)
        except Exception:
            order = sorted(metrics.keys())

        printed = set()

        def emit(mid: str, mm: Dict[str, Any]) -> None:
            na = bool(mm.get("not_applicable", False))
            lines.append(
                f"{_label(mid):28s} "
                f"safe%={_fmt(mm.get('safe_pct'), na=na)}  "
                f"risk%={_fmt(mm.get('risk_pct'), na=na)}  "
                f"sev={_fmt(mm.get('severity'), na=na)}  "
                f"conf={_fmt(mm.get('confidence'), na=na)}  "
                f"n/a={str(na):5s}  "
                f"reason={_short(mm.get('reason'), max_reason_len)}"
            )
            if include_evidence:
                ev = mm.get("evidence") or []
                if isinstance(ev, list) and ev:
                    if compact:
                        lines.append(f"  evidence: {str(ev[:3])}" + (" ..." if len(ev) > 3 else ""))
                    else:
                        lines.append("  evidence:")
                        for e in ev:
                            lines.append(f"    - {str(e)}")

        for mid in order:
            mm = metrics.get(mid)
            if isinstance(mm, dict):
                emit(mid, mm)
                printed.add(mid)

        # Any unknown metrics at end (never hide)
        for mid, mm in metrics.items():
            if mid in printed:
                continue
            if isinstance(mm, dict):
                emit(mid, mm)

    errs = d.get("errors") or []
    if errs:
        lines.append("\nErrors:")
        for e in errs:
            lines.append(f"  - {str(e)}")

    if include_meta:
        meta = d.get("meta") or {}
        if meta:
            lines.append("\nMeta:")
            lines.append(str(meta))

    return "\n".join(lines)
