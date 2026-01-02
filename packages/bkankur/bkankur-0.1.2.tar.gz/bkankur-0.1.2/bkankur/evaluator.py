# bkankur/evaluator.py
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from .config import BKAnkurConfig
from .prompts import METRIC_IDS, build_system_prompt, build_user_prompt
from .schema import BKANKUR_JSON_SCHEMA, EvaluationReport, JudgeOutput, MetricResult


CORE_OVERALL_METRICS: List[str] = [
    # Quality
    "relevance",
    "faithfulness",
    "hallucination",

    # Safety/Security
    "illegal_wrongdoing",
    "jailbreak_roleplay",
    "security_prompt_injection",
    "system_prompt_exfil",
    "policy_evasion",
    "tool_injection",
    "privacy_pii",
    "hate_discrimination",
    "violence_threats",
    "self_harm",
    "sexual_content",
    "high_stakes_safety",

    # UX/Fairness/BK
    "toxicity",
    "hap",
    "fairness",
    "bias_fairness",
    "bk_tone",
    "bk_self_respect",
    "bk_society_benefit",
    "bk_benevolent_god",
]


def _risk_from_sev_conf(sev: Optional[float], conf: Optional[float]) -> Optional[float]:
    if sev is None or conf is None:
        return None
    return round((float(sev) * float(conf)) / 100.0, 1)


def _derive(metric: MetricResult) -> MetricResult:
    if metric.not_applicable:
        metric.risk_pct = None
        metric.safe_pct = None
        metric.severity = None
        metric.confidence = None
        return metric

    if metric.risk_pct is None:
        metric.risk_pct = _risk_from_sev_conf(metric.severity, metric.confidence)

    # still None -> default to moderate low-confidence (NOT 0/100)
    if metric.risk_pct is None:
        metric.severity = 50.0 if metric.severity is None else metric.severity
        metric.confidence = 40.0 if metric.confidence is None else metric.confidence
        metric.risk_pct = _risk_from_sev_conf(metric.severity, metric.confidence)

    metric.safe_pct = round(100.0 - float(metric.risk_pct), 1)
    return metric


class BKAnkurEvaluator:
    """
    Evaluates one Transaction using a judge.

    Production design goals:
    - Runner stays simple.
    - Library owns prompts + schema + decision logic.
    - Backward compatible with judges that accept different call signatures.
    """

    def __init__(self, judge: Any, config: Optional[Any] = None):
        self.judge = judge
        # If caller didn't pass config, use production defaults
        self.config: BKAnkurConfig = config if isinstance(config, BKAnkurConfig) else BKAnkurConfig()

    def _judge_call(
        self,
        tx: Any,
        system_prompt: str,
        user_prompt: str,
        schema: Dict[str, Any],
        repair_mode: bool = False,
    ) -> Any:
        """
        Try best-effort judge interfaces in a safe order.

        Preferred stable interface (Protocol-based):
          judge.judge(tx=..., schema=..., repair_mode=...)

        Backward compatible with older judges that accept:
          - judge(tx=..., repair_mode=...)
          - judge(system_prompt=..., user_prompt=..., repair_mode=...)
          - run()/evaluate() variants
          - callable(messages)
        """

        # 1) judge.judge(...) variants
        if hasattr(self.judge, "judge"):
            # Protocol-first: pass tx + schema
            try:
                return self.judge.judge(tx=tx, schema=schema, repair_mode=repair_mode)
            except TypeError:
                pass

            # Positional variant: judge(tx, schema, repair_mode=...)
            try:
                return self.judge.judge(tx, schema, repair_mode=repair_mode)
            except TypeError:
                pass

            # Backward compatible: judge(tx=..., repair_mode=...)
            try:
                return self.judge.judge(tx=tx, repair_mode=repair_mode)
            except TypeError:
                pass

            # Positional older: judge(tx, repair_mode=...)
            try:
                return self.judge.judge(tx, repair_mode=repair_mode)
            except TypeError:
                pass

            # Prompt-based (some wrappers only accept prompts)
            try:
                return self.judge.judge(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    schema=schema,
                    repair_mode=repair_mode,
                )
            except TypeError:
                pass
            try:
                return self.judge.judge(system_prompt=system_prompt, user_prompt=user_prompt, repair_mode=repair_mode)
            except TypeError:
                pass

        # 2) judge.run / judge.evaluate (legacy)
        if hasattr(self.judge, "run"):
            try:
                return self.judge.run(tx=tx, schema=schema, repair_mode=repair_mode)
            except TypeError:
                try:
                    return self.judge.run(tx=tx, repair_mode=repair_mode)
                except TypeError:
                    return self.judge.run(system_prompt=system_prompt, user_prompt=user_prompt)

        if hasattr(self.judge, "evaluate"):
            try:
                return self.judge.evaluate(tx=tx, schema=schema, repair_mode=repair_mode)
            except TypeError:
                try:
                    return self.judge.evaluate(tx=tx, repair_mode=repair_mode)
                except TypeError:
                    return self.judge.evaluate(system_prompt=system_prompt, user_prompt=user_prompt)

        # 3) callable judge (treat as function taking messages)
        if callable(self.judge):
            return self.judge(
                [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            )

        raise RuntimeError("Judge object does not expose a supported call method.")

    def _extract_inputs(self, tx: Any) -> Tuple[List[str], Dict[str, Any]]:
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

    def _parse_judge_json(self, raw: Any) -> Dict[str, Any]:
        if isinstance(raw, dict):
            return raw
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8", errors="ignore")
        return json.loads(raw)

    def evaluate(self, tx: Any) -> EvaluationReport:
        report = EvaluationReport(transaction_id=getattr(tx, "transaction_id", None))

        try:
            user_text = getattr(tx, "user_text")
            bot_text = getattr(tx, "bot_text")
        except Exception:
            report.errors.append("Transaction missing user_text/bot_text.")
            report.recommendation = self.config.on_judge_error_recommendation
            return report

        retrieved_context, ground_truth = self._extract_inputs(tx)

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(
            user_text=user_text,
            bot_text=bot_text,
            retrieved_context=retrieved_context,
            ground_truth=ground_truth,
            metadata=getattr(tx, "metadata", {}) or {},
        )

        schema = BKANKUR_JSON_SCHEMA

        # --- Judge call with optional repair attempts ---
        raw: Any = None
        judge_error: Optional[str] = None
        try:
            raw = self._judge_call(tx, system_prompt, user_prompt, schema, repair_mode=False)
        except Exception as e:
            judge_error = str(e)

        # If the first call failed, optionally try repair mode (if judge supports)
        if raw is None and self.config.json_repair_attempts > 0:
            for _ in range(self.config.json_repair_attempts):
                try:
                    raw = self._judge_call(tx, system_prompt, user_prompt, schema, repair_mode=True)
                    judge_error = None
                    break
                except Exception as e:
                    judge_error = str(e)

        if raw is None:
            report.errors.append(f"Judge call failed: {judge_error}")
            report.recommendation = self.config.on_judge_error_recommendation
            return report

        # --- Parse JSON ---
        data: Optional[Dict[str, Any]] = None
        parse_error: Optional[str] = None
        try:
            data = self._parse_judge_json(raw)
        except Exception as e:
            parse_error = str(e)

        # Attempt repair if parsing fails
        if data is None and self.config.json_repair_attempts > 0:
            for _ in range(self.config.json_repair_attempts):
                try:
                    raw2 = self._judge_call(tx, system_prompt, user_prompt, schema, repair_mode=True)
                    data = self._parse_judge_json(raw2)
                    parse_error = None
                    break
                except Exception as e:
                    parse_error = str(e)

        if data is None:
            report.errors.append(f"Judge returned non-JSON: {parse_error}")
            report.meta["raw_preview"] = str(raw)[:400]
            report.recommendation = self.config.on_judge_error_recommendation
            return report

        # --- Validate schema (pydantic) ---
        jo: Optional[JudgeOutput] = None
        schema_error: Optional[str] = None
        try:
            jo = JudgeOutput(**data)
        except Exception as e:
            schema_error = str(e)

        if jo is None and self.config.json_repair_attempts > 0:
            for _ in range(self.config.json_repair_attempts):
                try:
                    raw2 = self._judge_call(tx, system_prompt, user_prompt, schema, repair_mode=True)
                    data2 = self._parse_judge_json(raw2)
                    jo = JudgeOutput(**data2)
                    data = data2
                    schema_error = None
                    break
                except Exception as e:
                    schema_error = str(e)

        if jo is None:
            report.errors.append(f"Judge JSON schema mismatch: {schema_error}")
            report.meta["raw_preview"] = str(data)[:400]
            report.recommendation = self.config.on_judge_error_recommendation
            return report

        # --- Ensure all metrics exist ---
        metrics: Dict[str, MetricResult] = dict(jo.metrics)

        missing: List[str] = []
        for mid in METRIC_IDS:
            if mid not in metrics:
                missing.append(mid)
                metrics[mid] = MetricResult(
                    not_applicable=False,
                    severity=40.0,
                    confidence=20.0,
                    risk_pct=None,
                    reason="Metric missing from judge output; defaulted to low-confidence moderate risk.",
                    evidence=[],
                )

        if missing:
            report.errors.append(f"Missing metrics from judge output: {missing}")
            report.meta["missing_metrics"] = missing
            if self.config.strict_metric_presence:
                report.meta["strict_metric_presence"] = True

        # --- Applicability rules (N/A) ---
        if not retrieved_context and "faithfulness" in metrics:
            metrics["faithfulness"].not_applicable = True
        if (not retrieved_context) and (not ground_truth) and "hallucination" in metrics:
            metrics["hallucination"].not_applicable = True

        # --- Derive safe/risk ---
        for mid in list(metrics.keys()):
            metrics[mid] = _derive(metrics[mid])

        report.metrics = metrics

        # --- Overall score ---
        overall_ids = (
            self.config.overall_metrics
            if isinstance(getattr(self.config, "overall_metrics", None), list) and self.config.overall_metrics
            else CORE_OVERALL_METRICS
        )

        vals: List[float] = []
        for mid in overall_ids:
            m = report.metrics.get(mid)
            if not m or m.not_applicable or m.safe_pct is None:
                continue
            vals.append(float(m.safe_pct))
        report.overall_safe_pct = round(sum(vals) / max(len(vals), 1), 3) if vals else 0.0

        # --- Recommendation using config thresholds ---
        thresholds: Dict[str, float] = dict(getattr(self.config, "thresholds", {}) or {})
        block_metrics: List[str] = list(getattr(self.config, "block_metrics", []) or [])
        review_metrics: List[str] = list(getattr(self.config, "review_metrics", []) or [])

        def _safe(mid: str) -> Optional[float]:
            m = report.metrics.get(mid)
            if not m or m.not_applicable or m.safe_pct is None:
                return None
            return float(m.safe_pct)

        block_hits: List[Dict[str, Any]] = []
        review_hits: List[Dict[str, Any]] = []

        for mid in block_metrics:
            s = _safe(mid)
            if s is None:
                continue
            thr = float(thresholds.get(mid, 0.0))
            if s < thr:
                block_hits.append({"metric": mid, "safe_pct": s, "threshold": thr})

        for mid in review_metrics:
            s = _safe(mid)
            if s is None:
                continue
            thr = float(thresholds.get(mid, 0.0))
            if s < thr:
                review_hits.append({"metric": mid, "safe_pct": s, "threshold": thr})

        if block_hits:
            report.recommendation = "BLOCK"
        elif review_hits:
            report.recommendation = "REVIEW"
        else:
            report.recommendation = "ALLOW"

        report.meta["prompt_version"] = jo.prompt_version
        report.meta["notes"] = jo.notes
        report.meta["has_ground_truth"] = bool(ground_truth)
        report.meta["has_retrieved_context"] = bool(retrieved_context)
        report.meta["block_hits"] = block_hits
        report.meta["review_hits"] = review_hits

        # Optional callback for production logging
        if callable(getattr(self.config, "on_report", None)):
            try:
                self.config.on_report(report)  # type: ignore[misc]
            except Exception:
                # never break evaluation
                pass

        return report
