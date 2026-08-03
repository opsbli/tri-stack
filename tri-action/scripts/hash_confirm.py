#!/usr/bin/env python3
"""tri-action 确认记录防篡改哈希工具.

用途：为 confirm-log.md / result.md 等确认类产物计算并校验 SHA-256 内容哈希。

哈希约定：
- 哈希行格式：``<!-- HASH:sha256:<hash_value> -->``，位于文件最后一行。
- 计算范围：文件全部内容，去掉末尾已存在的哈希行（若有）。
- 审计验证：重新计算并与文件末尾记录值比对，一致则未被篡改。

用法：
    python scripts/hash_confirm.py <file>                 # 计算并打印哈希
    python scripts/hash_confirm.py <file> --write         # 计算并写回哈希行
    python scripts/hash_confirm.py <file> --verify <hash> # 与给定哈希比对
    python scripts/hash_confirm.py <file> --verify        # 与文件内记录哈希比对
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys

HASH_LINE_RE = re.compile(r"^<!--\s*HASH:sha256:([0-9a-fA-F]{64}|<[^>]*>)\s*-->\s*$")
HASH_LINE_TPL = "<!-- HASH:sha256:{digest} -->"


def split_body_and_hash(text: str) -> tuple[str, str | None]:
    """拆分正文与末尾哈希行，返回 (正文, 已记录哈希 or None)。"""
    lines = text.splitlines()
    recorded = None
    while lines and not lines[-1].strip():
        lines.pop()
    if lines:
        matched = HASH_LINE_RE.match(lines[-1].strip())
        if matched:
            value = matched.group(1)
            recorded = value.lower() if not value.startswith("<") else None
            lines.pop()
    body = "\n".join(lines)
    if body:
        body += "\n"
    return body, recorded


def compute_hash(path: str) -> str:
    """计算文件正文（不含末尾哈希行）的 SHA-256。"""
    with open(path, "r", encoding="utf-8") as handle:
        body, _ = split_body_and_hash(handle.read())
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def write_hash(path: str) -> str:
    """计算正文哈希并把哈希行写回文件末尾（替换已有哈希行）。"""
    with open(path, "r", encoding="utf-8") as handle:
        body, _ = split_body_and_hash(handle.read())
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(body + HASH_LINE_TPL.format(digest=digest) + "\n")
    return digest


def verify_hash(path: str, expected: str | None = None) -> tuple[bool, str, str | None]:
    """校验文件哈希，返回 (是否一致, 实际哈希, 期望哈希)。

    expected 为 None 时取文件末尾记录的哈希行作为期望值。
    """
    with open(path, "r", encoding="utf-8") as handle:
        body, recorded = split_body_and_hash(handle.read())
    actual = hashlib.sha256(body.encode("utf-8")).hexdigest()
    target = (expected or recorded)
    target = target.lower() if target else None
    return (target is not None and actual == target), actual, target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="tri-action 确认记录 SHA-256 防篡改工具")
    parser.add_argument("file", help="待处理文件路径（如 confirm-log.md）")
    parser.add_argument(
        "--verify",
        nargs="?",
        const="",
        metavar="HASH",
        help="校验模式；给定 HASH 则与之比对，否则与文件内记录的哈希行比对",
    )
    parser.add_argument("--write", action="store_true", help="计算并把哈希行写回文件末尾")
    args = parser.parse_args(argv)

    if args.verify is not None:
        expected = args.verify or None
        ok, actual, target = verify_hash(args.file, expected)
        if target is None:
            print(f"NO_HASH actual={actual}")
            return 2
        print(f"{'OK' if ok else 'TAMPERED'} actual={actual} expected={target}")
        return 0 if ok else 1

    if args.write:
        print(write_hash(args.file))
        return 0

    print(compute_hash(args.file))
    return 0


if __name__ == "__main__":
    sys.exit(main())
