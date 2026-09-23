#!/usr/bin/env python3
"""tri-cache 确定性逻辑实现：归一化 / cache_key 指纹 / 隐私脱敏 / 向量嵌入 / 余弦相似度 / 轻量摘要 / 关键词 / 滑动窗口。

四层架构确定性算法层（L1 滑动窗口 / L2 结构化 / L3 摘要 / L4 向量）：
    - L4 向量检索：字符 n-gram 哈希嵌入（语言无关、确定性、零外部依赖）+ 余弦相似度
    - L3 轻量摘要：抽取式摘要（首句 + 关键词）+ 关键词提取
    - L1 滑动窗口：FIFO 窗口管理（追加 / 滑出）
    - L2 结构化：cache_key 指纹 / 归一化（供 SQLite 精确查询）

用法：
    python scripts/cache_ops.py "<query>"                       # 归一化 + cache_key
    python scripts/cache_ops.py --mask "<text>"                 # 隐私脱敏
    python scripts/cache_ops.py --embed "<text>" [--dim 256]    # 向量嵌入
    python scripts/cache_ops.py --sim "<textA>" "<textB>"       # 余弦相似度
    python scripts/cache_ops.py --summary "<answer>" [--question "<q>"] [--max-chars 200]
    python scripts/cache_ops.py --tags "<text>" [--top-n 5]     # 关键词提取
    python scripts/cache_ops.py --window "<entry_json>" [--max-size 50]  # 滑动窗口（stdin 读窗口）
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import unicodedata
from collections import Counter

KEY_LENGTH = 16
DEFAULT_EMBED_DIM = 256
DEFAULT_NGRAM = (1, 2)
DEFAULT_WINDOW_SIZE = 50
DEFAULT_SUMMARY_MAX_CHARS = 200

# 隐私密钥模式：命中即脱敏为 ***REDACTED***（关键词连同 =value / : value 一并脱敏，防止密钥值泄露）
SECRET_PATTERN = re.compile(
    r"(?i)(?:password|passwd|secret|api[_-]?key|token)"
    r"(?:\s*[=:]\s*[^\s,;]+)?"
    r"|sk-[a-zA-Z0-9]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|-----BEGIN[\s\S]*?PRIVATE KEY-----"
)

REDACTED = "***REDACTED***"

# 归一化时剔除的标点（中英文）
_PUNCT_PATTERN = re.compile(r"[^\w\s]", flags=re.UNICODE)
_SPACE_PATTERN = re.compile(r"\s+")

# 中文停用词（摘要/关键词提取用）
_STOPWORDS = set(
    "的了是在和有就都而及与或一个我你他她它们这那之其于被把让对从到为以不也还又再很更最等"
    "and or the a an of to in for on with is are was were be been it this that these those".split()
)

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_LATIN_RE = re.compile(r"[a-zA-Z0-9]+")


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


# ---------------------------------------------------------------------------
# L4 向量检索：字符 n-gram 哈希嵌入 + 余弦相似度
# ---------------------------------------------------------------------------


def embed(text: str, dim: int = DEFAULT_EMBED_DIM,
          ngram: tuple[int, int] = DEFAULT_NGRAM) -> list[float]:
    """字符 n-gram 哈希嵌入：语言无关、确定性、零外部依赖。

    归一化文本 → 滑动 n-gram → 带符号哈希累加 → L2 归一化。
    中英文同构：中文按字、英文按字符 n-gram，均能捕捉语义相似。
    """
    norm = normalize_query(text)
    vec = [0.0] * dim
    for n in range(ngram[0], ngram[1] + 1):
        for i in range(len(norm) - n + 1):
            gram = norm[i:i + n]
            h = int(hashlib.md5(gram.encode("utf-8")).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if (h >> 4) & 1 else -1.0
            vec[idx] += sign
    norm_val = math.sqrt(sum(v * v for v in vec))
    if norm_val > 0:
        vec = [v / norm_val for v in vec]
    return vec


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """余弦相似度：L2 归一化向量间即点积。维度不一致返回 0。"""
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# L3 轻量摘要：抽取式摘要 + 关键词提取
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    """语言感知分词：CJK 逐字符，拉丁按单词。"""
    tokens: list[str] = []
    for seg in re.findall(r"[\u4e00-\u9fff]|[a-zA-Z0-9]+", text or ""):
        if _CJK_RE.match(seg):
            tokens.append(seg)
        else:
            tokens.append(seg.lower())
    return tokens


def extract_tags(text: str, top_n: int = 5) -> list[str]:
    """关键词提取：拉丁单词优先 + CJK 字符 bigram，词频统计去停用词。

    拉丁词权重 ×2（通常更具区分度）；CJK bigram 含功能字则剔除（避免
    「的X / X是」类无区分度组合）。bigram 天然利于子串匹配检索。
    """
    tokens = _tokenize(text)
    counter: Counter[str] = Counter()
    for t in tokens:
        if _LATIN_RE.match(t) and t not in _STOPWORDS:
            counter[t] += 2
    cjk = [t for t in tokens if _CJK_RE.match(t)]
    for i in range(len(cjk) - 1):
        gram = cjk[i] + cjk[i + 1]
        if gram in _STOPWORDS:
            continue
        if cjk[i] in _STOPWORDS or cjk[i + 1] in _STOPWORDS:
            continue
        counter[gram] += 1
    return [w for w, _ in counter.most_common(top_n)]


def _first_sentence(text: str) -> str:
    """取首句：按中文/英文句号切分。"""
    for sep in ("。", "！", "？", ". ", "! ", "? ", "\n"):
        idx = text.find(sep)
        if idx > 0:
            return text[:idx + len(sep)].strip()
    return text.strip()


def generate_summary(question: str, answer: str,
                     max_chars: int = DEFAULT_SUMMARY_MAX_CHARS) -> str:
    """抽取式摘要：回答首句。截断 ≤max_chars 字，零拼接开销。"""
    q = (question or "").strip()
    a = (answer or "").strip()
    first = _first_sentence(a) if a else q
    if len(first) > max_chars:
        first = first[:max_chars] + "…"
    return first


# ---------------------------------------------------------------------------
# L1 滑动窗口：FIFO 窗口管理
# ---------------------------------------------------------------------------


def manage_window(window: list[dict], entry: dict,
                  max_size: int = DEFAULT_WINDOW_SIZE) -> tuple[list[dict], list[dict]]:
    """滑动窗口：追加新条目，超容量 FIFO 滑出。

    返回 (新窗口, 滑出条目列表)。滑出条目由调用方降级写入 L2/L3/L4。
    """
    window = list(window or [])
    window.append(entry)
    evicted: list[dict] = []
    while len(window) > max_size:
        evicted.append(window.pop(0))
    return window, evicted


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="tri-cache 四层架构确定性算法工具")
    parser.add_argument("text", nargs="?", help="提问原文（或对应模式下的待处理文本）")
    parser.add_argument("--mask", action="store_true", help="隐私脱敏")
    parser.add_argument("--embed", action="store_true", help="计算向量嵌入")
    parser.add_argument("--dim", type=int, default=DEFAULT_EMBED_DIM, help="嵌入维度（默认 256）")
    parser.add_argument("--sim", nargs=2, metavar=("TEXT_A", "TEXT_B"), help="计算两文本余弦相似度")
    parser.add_argument("--summary", action="store_true", help="生成抽取式摘要")
    parser.add_argument("--question", default="", help="摘要模式下的提问（可选）")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_SUMMARY_MAX_CHARS, help="摘要最大字数（默认 200）")
    parser.add_argument("--tags", action="store_true", help="提取关键词")
    parser.add_argument("--top-n", type=int, default=5, help="关键词数量（默认 5）")
    parser.add_argument("--window", action="store_true", help="滑动窗口管理（stdin 读窗口 JSON 数组）")
    parser.add_argument("--max-size", type=int, default=DEFAULT_WINDOW_SIZE, help="窗口容量（默认 50）")
    args = parser.parse_args()

    if args.sim:
        a, b = args.sim
        result = {
            "similarity": round(cosine_similarity(embed(a), embed(b)), 6),
            "dim": DEFAULT_EMBED_DIM,
        }
        print(json.dumps(result, ensure_ascii=False))
        return

    if args.window:
        try:
            window = json.loads(sys.stdin.read() or "[]")
        except json.JSONDecodeError:
            window = []
        entry = json.loads(args.text or "{}")
        new_window, evicted = manage_window(window, entry, args.max_size)
        print(json.dumps({"window": new_window, "evicted": evicted}, ensure_ascii=False))
        return

    if args.mask:
        masked, hits = mask_secrets(args.text or "")
        print(json.dumps({"masked": masked, "hits": hits}, ensure_ascii=False))
        return

    if args.embed:
        vec = embed(args.text or "", dim=args.dim)
        print(json.dumps({"dim": len(vec), "vector": vec}, ensure_ascii=False))
        return

    if args.summary:
        summary = generate_summary(args.question, args.text or "", max_chars=args.max_chars)
        print(json.dumps({"summary": summary}, ensure_ascii=False))
        return

    if args.tags:
        tags = extract_tags(args.text or "", top_n=args.top_n)
        print(json.dumps({"tags": tags}, ensure_ascii=False))
        return

    result = {
        "normalized": normalize_query(args.text or ""),
        "cache_key": compute_key(args.text or ""),
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
