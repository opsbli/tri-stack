#!/usr/bin/env python3
"""Model-aware token budget with graceful degradation.

Distilled from strix ``llm/context_budget.py`` (Apache-2.0), rewritten for the
tri-xxx family with **zero new hard dependencies**:

- If ``litellm`` is importable and knows the model, use its metadata
  (``max_input_tokens`` / ``max_output_tokens``) and its tokenizer.
- Otherwise fall back to a **UTF-8 byte-length upper bound**, which is a
  guaranteed over-estimate for UTF-8 tokenizers. Conservative by design: a
  budget check that over-estimates never lets a request overflow silently.

Provider routing prefixes (``openai/``, ``litellm/``, ``ollama/``, ...) are
stripped on lookup because LiteLLM keys metadata by the underlying model slug.

Usage
-----
    python token_budget.py --model openai/gpt-5.4 --window --json
    python token_budget.py --model ollama/qwen --text "hello world" --json
    python token_budget.py --model x --file prompt.txt --json
    python token_budget.py --self-test

Exit codes: 0 ok · 2 usage error · 3 self-test failure
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

# LiteLLM keys models without the routing prefix users type.
_STRIPPABLE_PREFIXES = (
    "openai/",
    "chatgpt/",
    "litellm/",
    "any-llm/",
    "ollama/",
    "ollama_chat/",
)

_DEFAULT_OUTPUT_TOKENS = 8_192
# Used when LiteLLM neither knows the model nor can count tokens.
_FALLBACK_CONTEXT_TOKENS = 128_000
# Rough bytes-per-token assumption for the byte-based estimate (deliberately
# low, so the resulting token estimate stays an upper bound).
_BYTES_PER_TOKEN = 2.5


def _lookup_key(model: str) -> str:
    for prefix in _STRIPPABLE_PREFIXES:
        if model.startswith(prefix):
            return model[len(prefix) :]
    return model


def _model_info(model: str) -> dict[str, int]:
    """Return ``max_input_tokens`` / ``max_output_tokens``; zeros when unknown."""
    try:
        import litellm  # noqa: PLC0415 - optional dependency, intentionally lazy
    except Exception:  # noqa: BLE001 - absence is a supported state, not an error
        return {"max_input_tokens": 0, "max_output_tokens": 0}
    try:
        lookup_key = _lookup_key(model)
        candidates = (lookup_key,) if model.startswith("chatgpt/") else (model, lookup_key)
        for candidate in candidates:
            try:
                info = dict(litellm.get_model_info(candidate))
            except Exception:  # noqa: BLE001 - unmapped model; try next candidate
                continue
            return {
                "max_input_tokens": int(info.get("max_input_tokens") or info.get("max_tokens") or 0),
                "max_output_tokens": int(info.get("max_output_tokens") or 0),
            }
    except Exception:  # noqa: BLE001 - any litellm quirk falls back to defaults
        pass
    return {"max_input_tokens": 0, "max_output_tokens": 0}


def context_window(model: str, fallback: int = _FALLBACK_CONTEXT_TOKENS) -> int:
    """Input token capacity for ``model`` (``fallback`` when unmapped)."""
    return _model_info(model)["max_input_tokens"] or fallback


def output_limit(model: str) -> int:
    """Max output tokens for ``model`` (conservative default when unmapped)."""
    return _model_info(model)["max_output_tokens"] or _DEFAULT_OUTPUT_TOKENS


def count_tokens(model: str, text: str) -> int:
    """Token count for ``text``; UTF-8 byte upper bound when no tokenizer."""
    if not text:
        return 0
    try:
        import litellm  # noqa: PLC0415 - optional dependency, intentionally lazy

        return int(litellm.token_counter(model=_lookup_key(model), text=text))
    except Exception:  # noqa: BLE001 - tokenizer unavailable for some models
        return byte_upper_bound(text)


def byte_upper_bound(text: str) -> int:
    """Conservative token upper bound: ``ceil(len(utf8_bytes) / 2.5)``."""
    if not text:
        return 0
    nbytes = len(text.encode("utf-8"))
    return int(nbytes / _BYTES_PER_TOKEN) + 1


def budget_report(
    model: str,
    text: str | None = None,
    *,
    buffer_tokens: int = 20_000,
    fallback: int = _FALLBACK_CONTEXT_TOKENS,
) -> dict[str, Any]:
    """Compute the budget facts for a model (and optionally a piece of text)."""
    window = context_window(model, fallback=fallback)
    out = output_limit(model)
    usable = max(window - buffer_tokens - out, 0)
    result: dict[str, Any] = {
        "model": model,
        "context_window": window,
        "output_limit": out,
        "buffer_tokens": buffer_tokens,
        "usable_input_tokens": usable,
        "source": "litellm" if _model_info(model)["max_input_tokens"] else "fallback",
    }
    if text is not None:
        tokens = count_tokens(model, text)
        result.update(
            {
                "text_tokens": tokens,
                "fits": tokens <= usable,
                "utilization": round(tokens / usable, 4) if usable else None,
                "count_source": result["source"],
            }
        )
    return result


def _self_test() -> int:
    failures: list[str] = []

    # 1) No litellm hard dependency: unmapped model must fall back, not raise.
    r = budget_report("definitely-not-a-known-model/v1", "hello world", fallback=4_096)
    if r["source"] != "fallback" or r["context_window"] != 4_096:
        failures.append(f"fallback window wrong: {r}")
    if r["text_tokens"] <= 0:
        failures.append(f"byte upper bound must be > 0: {r}")

    # 2) Empty text counts zero.
    if count_tokens("any/model", "") != 0:
        failures.append("empty text must count 0")

    # 3) Usable window is clamped at zero, never negative.
    r2 = budget_report("m/v1", fallback=1_000, buffer_tokens=50_000)
    if r2["usable_input_tokens"] != 0:
        failures.append(f"usable must clamp at 0: {r2}")

    # 4) Provider prefix stripping.
    if _lookup_key("openai/gpt-5.4") != "gpt-5.4":
        failures.append("prefix stripping broken")

    # 5) Deterministic: same input → same output.
    a = budget_report("m/v1", "abc" * 100, fallback=8_000)
    b = budget_report("m/v1", "abc" * 100, fallback=8_000)
    if a != b:
        failures.append("budget_report not deterministic")

    for f in failures:
        print(f"FAIL: {f}")
    print("self-test:", "PASS" if not failures else f"{len(failures)} FAILURE(S)")
    return 0 if not failures else 3


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Model-aware token budget (graceful degradation).")
    p.add_argument("--model", required=False, default="unknown", help="model id (any LiteLLM id)")
    p.add_argument("--window", action="store_true", help="print context window / usable budget")
    p.add_argument("--text", help="text to count")
    p.add_argument("--file", help="file to count (use - for stdin)")
    p.add_argument("--buffer-tokens", type=int, default=20_000)
    p.add_argument("--fallback", type=int, default=_FALLBACK_CONTEXT_TOKENS)
    p.add_argument("--json", action="store_true", help="emit JSON")
    p.add_argument("--self-test", action="store_true", help="run built-in assertions")
    args = p.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.window and args.text is None and args.file is None:
        args.window = True

    text: str | None = None
    if args.file:
        if args.file == "-":
            text = sys.stdin.read()
        else:
            with open(args.file, encoding="utf-8") as fh:
                text = fh.read()
    elif args.text is not None:
        text = args.text

    report = budget_report(
        args.model, text, buffer_tokens=args.buffer_tokens, fallback=args.fallback
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for k, v in report.items():
            print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
