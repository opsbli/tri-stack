#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面抓取与结构化解析（fetch_page.py）——「智引」(tri-geo) 确定性脚本 02/09

职责（对应设计指南 §3.1）：
    · 抓取目标页（编码识别、超时 10s、重试 2 次）+ 原始 HTML 落盘（证据链）
    · 正文结构化解析：去导航/页脚/广告噪声，保留 H1-H6 标题层级与段落边界
    · 提取 JSON-LD、meta description、语言、列表/表格计数
    · 可选 --assets：同抓 robots.txt / llms.txt / llms-full.txt 供 site_signal.py 判定

设计约束：
    · 纯标准库（urllib + html.parser），零第三方依赖
    · 支持 --file 解析本地 HTML，保证离线可测（T1/T2 确定性回归）
    · 默认不输出时间戳，保证同输入多次运行逐字节一致（--stamp 才注入）
    · 抓取失败 MUST 报错并建议用户粘贴正文，NEVER 伪造内容块

用法：
    python fetch_page.py --url https://example.com --raw-dir .tribro/geo/raw --json
    python fetch_page.py --url https://example.com --assets --out page.json --json
    python fetch_page.py --file tests/fixtures/good-page.html --json

退出码：
    0  成功
    2  抓取失败（重试 2 次后）/ 文件不可读
    3  解析成功但正文为空（疑似 JS 渲染或反爬，需人工确认）
    64 参数或环境错误
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zlib
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

SCHEMA_VERSION = "1.0"
TOOL_NAME = "fetch_page.py"

HTTP_TIMEOUT = 10
HTTP_RETRY = 2
UA = "Mozilla/5.0 (compatible; tri-geo-zhiyin/1.0; +geoa-fetcher)"

SKIP_TAGS = {"script", "style", "noscript", "svg", "iframe", "template", "nav",
             "footer", "header", "aside", "form", "button"}
BLOCK_TAGS = {"p", "div", "li", "td", "th", "blockquote", "pre", "dd", "dt"}
HEAD_TAGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}

# 定义句式（中文「X 是/指/包括…」），用于块级判定
DEF_RE = re.compile(r"[^\s。！？；：，、]{2,24}(?:是|指的是|指|包括|定义为|即)\s")
# 问句式标题
Q_RE = re.compile(r"(什么是|如何|怎么|哪些|为什么|多久|多少钱|如何选|哪个好|吗[？?]|？)")
# 代词（自包含惩罚项）
PRON_RE = re.compile(r"[他她它其该此这那这种那种该项目该产品该服务]")


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def char_count(text: str) -> int:
    """字数：去空白后的字符数（中文按字计，设计指南 §6.1）。"""
    return len(re.sub(r"\s+", "", text or ""))


class PageParser(HTMLParser):
    """把 HTML 解析为「按标题切分的内容块」。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.lang = ""
        self.meta_desc = ""
        self.jsonld: List[str] = []
        self.blocks: List[Dict[str, Any]] = []
        self.script_chars = 0
        self.lists = 0
        self.tables = 0
        self.paragraphs = 0
        self._in_title = False
        self._in_ld = False
        self._ld: List[str] = []
        self._skip_depth = 0
        self._cur: Optional[Dict[str, Any]] = None
        self._buf: List[str] = []
        self._cur_heading_holder: List[str] = []
        self._heading_depth = 0

    # -- 工具 ---------------------------------------------------------
    def _flush(self) -> None:
        if self._cur is None:
            return
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._cur["text"] = text
        self._cur["heading"] = re.sub(r"\s+", " ", "".join(self._cur_heading_holder)).strip()
        self._cur["char_count"] = char_count(text)
        self._cur["sentences"] = len([s for s in re.split(r"[。！？；]", text) if s.strip()])
        self._cur["paragraphs"] = self._cur.get("paragraphs", 0)
        self._cur["lists"] = self._cur.get("lists", 0)
        self._cur["tables"] = self._cur.get("tables", 0)
        self._cur["has_definition_pattern"] = bool(DEF_RE.search(text[:200]))
        self._cur["first60_standalone"] = self._judge_first60(text)
        if text or self._cur["heading"]:
            self.blocks.append(self._cur)
        self._cur = None
        self._buf = []
        self._cur_heading_holder = []

    @staticmethod
    def _judge_first60(text: str) -> bool:
        """前 60 字是否可独立成答（启发式初判，最终以 site_signal.py 规则为准）。"""
        head = re.sub(r"\s+", "", text)[:60]
        if len(head) < 12:
            return False
        if head[:2] and PRON_RE.match(head[0]):
            return False
        return bool(DEF_RE.search(head) or re.search(r"\d", head))

    # -- HTMLParser 回调 ----------------------------------------------
    def handle_starttag(self, tag: str, attrs: Any) -> None:
        a = dict(attrs or {})
        if tag == "html":
            self.lang = a.get("lang", "") or self.lang
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key == "description":
                self.meta_desc = a.get("content", "") or self.meta_desc
        if tag == "title":
            self._in_title = True
        if tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json":
                self._in_ld = True
                self._ld = []
            else:
                self._skip_depth += 1
        if tag in SKIP_TAGS and tag != "script":
            self._skip_depth += 1
        if tag in HEAD_TAGS:
            self._flush()
            self._cur = {"level": HEAD_TAGS[tag], "paragraphs": 0,
                         "lists": 0, "tables": 0, "has_definition_pattern": False,
                         "first60_standalone": False}
            self._heading_depth = 1
        elif tag == "p":
            if self._cur is None:
                self._cur = {"level": 0, "paragraphs": 0, "lists": 0, "tables": 0,
                             "has_definition_pattern": False, "first60_standalone": False}
            self.paragraphs += 1
            self._cur["paragraphs"] = self._cur.get("paragraphs", 0) + 1
            self._buf.append(" ")
        elif tag in ("ul", "ol"):
            if self._cur is not None:
                self._cur["lists"] = self._cur.get("lists", 0) + 1
            self.lists += 1
        elif tag == "table":
            if self._cur is not None:
                self._cur["tables"] = self._cur.get("tables", 0) + 1
            self.tables += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "script":
            if self._in_ld:
                self._in_ld = False
                self.jsonld.append("".join(self._ld).strip())
            else:
                self._skip_depth = max(0, self._skip_depth - 1)
        if tag in SKIP_TAGS and tag != "script":
            self._skip_depth = max(0, self._skip_depth - 1)
        if tag in HEAD_TAGS:
            self._heading_depth = 0
        if tag in ("p", "li", "td", "th", "blockquote"):
            self._buf.append(" ")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
            return
        if self._in_ld:
            self._ld.append(data)
            return
        if self._skip_depth:
            return
        if self._heading_depth:
            self._cur_heading_holder.append(data)
            return
        if self._cur is None:
            self._cur = {"level": 0, "paragraphs": 0, "lists": 0, "tables": 0,
                         "has_definition_pattern": False, "first60_standalone": False}
        self._buf.append(data)

    def close_out(self) -> None:
        self._flush()


def decode_body(raw: bytes, header_ct: str) -> str:
    """按 header/meta charset 解码，失败回退 utf-8（errors=replace）。"""
    charset = None
    m = re.search(r"charset=([\w-]+)", header_ct or "", re.I)
    if m:
        charset = m.group(1)
    if not charset:
        m = re.search(rb'charset=["\']?([\w-]+)', raw[:4096], re.I)
        if m:
            charset = m.group(1).decode("ascii", "ignore")
    for enc in [charset, "utf-8", "gb18030", "latin-1"]:
        if not enc:
            continue
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def http_get(url: str) -> Tuple[Optional[bytes], Optional[int], Optional[str], str]:
    """抓取 URL。返回 (body, status, content_type, error)。"""
    last_err = ""
    for attempt in range(HTTP_RETRY + 1):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
                              "Accept-Encoding": "gzip, deflate"})
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                body = resp.read()
                ctype = (resp.headers.get("Content-Type") or "")
                enc = (resp.headers.get("Content-Encoding") or "").lower()
                if "gzip" in enc:
                    try:
                        body = gzip.decompress(body)
                    except (OSError, zlib.error):
                        pass
                elif "deflate" in enc:
                    try:
                        body = zlib.decompress(body, -zlib.MAX_WBITS)
                    except zlib.error:
                        pass
                return body, resp.getcode(), ctype, ""
        except urllib.error.HTTPError as e:
            return None, e.code, "", f"HTTP {e.code} {e.reason}"
        except urllib.error.URLError as e:
            last_err = f"网络不可达：{e.reason}"
        except (TimeoutError, OSError) as e:
            last_err = f"网络异常/超时：{type(e).__name__}: {e}"
        if attempt < HTTP_RETRY:
            time.sleep(0.5)
    return None, None, "", last_err or "未知网络错误"


def save_raw(raw_dir: Optional[Path], name: str, data: bytes) -> Optional[str]:
    if raw_dir is None:
        return None
    try:
        raw_dir.mkdir(parents=True, exist_ok=True)
        p = raw_dir / name
        p.write_bytes(data)
        return str(p)
    except OSError:
        return None


def parse_html(html: str) -> PageParser:
    p = PageParser()
    p.feed(html)
    p.close_out()
    p.close()
    return p


def build_content(url: str, html: str, raw_path: Optional[str],
                  assets: Dict[str, Any]) -> Dict[str, Any]:
    p = parse_html(html)
    body_chars = sum(b["char_count"] for b in p.blocks)
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "url": url,
        "title": re.sub(r"\s+", " ", p.title).strip(),
        "lang": p.lang,
        "meta": {"description": p.meta_desc},
        "blocks": p.blocks,
        "jsonld_raw": p.jsonld,
        "stats": {
            "blocks": len(p.blocks),
            "body_text_chars": body_chars,
            "script_chars": p.script_chars,
            "lists": p.lists,
            "tables": p.tables,
            "paragraphs": p.paragraphs,
        },
        "evidence": {
            "raw_path": raw_path,
            "html_sha256": sha256_of(html.encode("utf-8", errors="replace")),
        },
        "assets": assets,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="「智引」页面抓取与结构化解析")
    ap.add_argument("--url", default=None, help="目标页面 URL")
    ap.add_argument("--file", default=None, help="本地 HTML 文件（离线解析，用于回归测试）")
    ap.add_argument("--raw-dir", default=".tribro/geo/raw", help="原始证据落盘目录")
    ap.add_argument("--assets", action="store_true", help="同抓 robots.txt / llms.txt")
    ap.add_argument("--out", default=None, help="内容 JSON 落盘路径（默认仅 stdout）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--stamp", action="store_true", help="注入时间戳（默认不注入）")
    args = ap.parse_args(argv)

    if not args.url and not args.file:
        print("[智引·抓取] 必须提供 --url 或 --file", file=sys.stderr)
        return 64

    assets: Dict[str, Any] = {}
    if args.file:
        try:
            html = Path(args.file).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"[智引·抓取] 文件不可读：{e}", file=sys.stderr)
            return 2
        url = args.url or f"file://{Path(args.file).resolve().as_posix()}"
        raw_path = str(Path(args.file).resolve())
    else:
        url = args.url
        body, status, ctype, err = http_get(url)
        if body is None:
            print(f"[智引·抓取] 抓取失败（已重试 {HTTP_RETRY} 次）：{err}", file=sys.stderr)
            print("  建议：让用户在对话中粘贴正文，或改用 --file 解析本地快照", file=sys.stderr)
            return 2
        html = decode_body(body, ctype)
        host = (urlparse(url).hostname or "site").replace(".", "_")
        raw_path = save_raw(Path(args.raw_dir), f"{host}.html", body)

    content = build_content(url, html, raw_path, assets)

    # ---- 可选资产：robots.txt / llms.txt ----
    if args.assets and not args.file:
        base = "{0}://{1}".format(urlparse(url).scheme, urlparse(url).netloc)
        raw_dir = Path(args.raw_dir) if args.raw_dir else None
        for name, path in (("robots", "/robots.txt"), ("llmstxt", "/llms.txt"),
                           ("llmstxt_full", "/llms-full.txt")):
            b, st, _, e = http_get(urljoin(base, path))
            if b is None:
                assets[name] = {"url": urljoin(base, path), "status": st, "exists": False,
                                "error": e, "path": None, "sha256": None}
                continue
            assets[name] = {
                "url": urljoin(base, path), "status": st, "exists": True, "error": None,
                "path": save_raw(raw_dir, f"{name}.txt", b), "sha256": sha256_of(b),
                "text": b.decode("utf-8", errors="replace")[:20000],
            }
        content["assets"] = assets

    if args.stamp:
        content["fetched_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    payload = json.dumps(content, ensure_ascii=False, indent=2)
    if args.out:
        try:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(payload, encoding="utf-8")
        except OSError as e:
            print(f"[智引·抓取] 落盘失败：{e}", file=sys.stderr)
            return 64
    if args.json or args.out:
        print(payload)

    empty = content["stats"]["body_text_chars"] < 100
    if not args.json and not args.out:
        s = content["stats"]
        print(f"[智引·抓取] {url}")
        print(f"  标题：{content['title'][:60]}")
        print(f"  内容块 {s['blocks']} 个 / 正文 {s['body_text_chars']} 字 / "
              f"列表 {s['lists']} / 表格 {s['tables']}")
        print(f"  证据：{raw_path}")
    return 3 if empty else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"[智引·抓取] 脚本异常：{type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(64)
