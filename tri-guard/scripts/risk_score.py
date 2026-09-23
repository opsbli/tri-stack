#!/usr/bin/env python3
"""tri-guard 风险评分确定性实现（按 references/risk-scoring.md 契约）。

输入 : findings 列表（可从 skillspector JSON 报告提取，或降级轨自构造）
       每项需含 severity / rule_id / confidence，可选 executable(0/1)。
输出 : {score, severity, recommendation, exit_code, breakdown}
用法 : python scripts/risk_score.py findings.json [--json]
"""
import json
import sys
from pathlib import Path

POINTS = {"CRITICAL": 50, "HIGH": 25, "MEDIUM": 10, "LOW": 5}
RISK_THRESHOLD = 50
SEVERITY_BANDS = [(81, "CRITICAL"), (51, "HIGH"), (21, "MEDIUM"), (0, "LOW")]
RECOMMENDATION = {
    "LOW": "SAFE",
    "MEDIUM": "CAUTION",
    "HIGH": "DO_NOT_INSTALL",
    "CRITICAL": "DO_NOT_INSTALL",
}


def _band(score: int) -> str:
    for lo, sev in SEVERITY_BANDS:
        if score >= lo:
            return sev
    return "LOW"


def compute(findings: list) -> dict:
    total = 0.0
    counts: dict = {}
    for f in findings:
        sev = (f.get("severity") or "LOW").upper()
        base = POINTS.get(sev, POINTS["LOW"])
        conf = max(0.0, min(1.0, float(f.get("confidence") or 1.0)))
        if conf == 0:
            continue
        rule_id = f.get("rule_id") or f.get("id") or "UNKNOWN"
        counts[rule_id] = counts.get(rule_id, 0) + 1
        weights = {1: 1.0, 2: 0.5, 3: 0.25}
        dim = weights.get(counts[rule_id], 0.0)
        if dim == 0:
            continue
        mult = 1.3 if f.get("executable") else 1.0
        total += base * dim * conf * mult
    any_sc8 = any(
        ((f.get("rule_id") or f.get("id")) == "SC8" and float(f.get("confidence") or 0) > 0)
        for f in findings
    )
    score = min(100, max(51 if any_sc8 else 0, int(round(total))))
    sev = _band(score)
    return {
        "score": score,
        "severity": sev,
        "recommendation": RECOMMENDATION[sev],
        "exit_code": 1 if score > RISK_THRESHOLD else 0,
        "breakdown": {"total_raw": round(total, 2), "sc8_floor": any_sc8},
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python scripts/risk_score.py findings.json [--json]", file=sys.stderr)
        return 2
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    findings = data if isinstance(data, list) else data.get("findings", [])
    result = compute(findings)
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(
            f"score={result['score']} severity={result['severity']} "
            f"recommendation={result['recommendation']} exit_code={result['exit_code']}"
        )
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())