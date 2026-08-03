#!/usr/bin/env python3
"""tri-cache 确定性逻辑实现：提问归一化 / cache_key 指纹 / 隐私脱敏。

用法：
    python scripts/cache_ops.py "<query>"          # 输出归一化结果与 cache_key
    python scripts/cache_ops.py --mask "<text>"    # 输出隐私脱敏后的文本
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata

KEY_LENGTH = 16

# 隐私密钥模式：命中即脱敏为 ***REDACTED***
SECRET_PATTERN = re.compile(
    r"(?i)(password|passwd|secret|api[_-]?key|token"
    r"|sk-[a-zA-Z0-9]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN[\s\S]*?PRIVATE KEY-----)"
)

REDACTED = "***REDACTED***"

# 归一化时剔除的标点（中英文）
_PUNCT_PATTERN = re.compile(r"[^\w\s]", flags=re.UNICODE)
_SPACE_PATTERN = re.compile(r"\s+")


def normalize_query(q: str) -> str:
    """提问归一化：Unicode NFKC → 去首尾空白 → 小写 → 去标点 → 压缩多余空格。"""
    text = unicodedata.normalize("NFKC", q or "")
    text = text.strip().lower()
    text = _PUNCT_PATTERN.sub(" ", text)
    return _SPACE_PATTERN.sub(" ", text).strip()


def compute_key(q: str) -> str:
    """内容指纹：归一化提问的 SHA-256 取前 16 位十六进制字符作 cache_key。"""
    normalized = normalize_query(q)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:KEY_LENGTH]


def mask_secrets(text: str) -> tuple[str, int]:
    """隐私脱敏：命中密钥模式替换为 ***REDACTED***，返回 (脱敏文本, 命中数)。"""
    masked, count = SECRET_PATTERN.subn(REDACTED, text or "")
    return masked, count


def main() -> None:
    parser = argparse.ArgumentParser(description="tri-cache 缓存键与隐私脱敏工具")
    parser.add_argument("text", help="提问原文（或 --mask 模式下的待脱敏文本）")
    parser.add_argument("--mask", action="store_true", help="执行隐私脱敏而非计算 cache_key")
    args = parser.parse_args()

    if args.mask:
        masked, hits = mask_secrets(args.text)
        result = {"masked": masked, "hits": hits}
    else:
        result = {
            "normalized": normalize_query(args.text),
            "cache_key": compute_key(args.text),
        }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
