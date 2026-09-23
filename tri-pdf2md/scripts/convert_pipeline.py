#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""convert_pipeline.py · 降级链执行器（tri-pdf2md · 每 skill 独立完整副本，单 skill 可单独运行）

本文件为自包含单文件脚本：仅依赖标准库 + 本 skill detect_backends 探测过的可选后端包，
NEVER import 其它 skill 的任何模块。缺后端时对应 runner 跳过并计入 attempts。
MIT 归属：设计模式（priority 链 + FailedConversionAttempt 异常聚合）源自 Microsoft
markitdown（MIT），按家族规范重新实现为编排层代码——见 docs/markitdown-analysis-migration-20260909.md M1。
批次二增强：M6 无边框表格词坐标聚类（pdfplumber runner 内置 · pdf_form_extract 副本）· M9 内容二次校验（sniffer 同源副本）——见同报告 §五。

职责（对应报告 M1）：
  按 detect_backends.py 产出的 fallback_chain 顺序逐后端尝试转换；每个后端的异常被
  捕获聚合为结构化 attempts（类型/消息/耗时/栈尾）；全失败时输出聚合诊断
  （FileConversionException 语义）。降级从「Agent 手工逐次重试」变为「一次调用、全程留痕」。

档位链（与 detect_backends.py GRADE_ORDER 一致）：
  L0 快速：anydoc → pymupdf4llm → markitdown → pdfplumber
  L1 标准：docling → marker → pymupdf4llm → markitdown → pdfplumber
  L2 精细：mineru → docling → marker → pymupdf4llm → markitdown → pdfplumber
用法：
    python scripts/convert_pipeline.py --doc <file> --md <out.md> \
        --chain "anydoc,pymupdf4llm,markitdown,pdfplumber" --json
退出码：0 至少一个后端成功；3 全部后端失败（聚合诊断见 diagnosis）；2 参数错误。
"""
from _io_safe import safe_print
import argparse
import json
import subprocess
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Optional

PIPELINE_TIMEOUT = 300  # 单后端执行上限（秒），防挂死


@dataclass
class FailedConversionAttempt:
    """单次后端尝试的失败证据（迁移自 markitdown FailedConversionAttempt）。"""
    backend: str
    exc_type: str = ""
    exc_message: str = ""
    elapsed_ms: int = 0
    traceback_tail: str = ""   # 末 5 行栈，报告引用


@dataclass
class PipelineResult:
    ok: bool
    backend_used: Optional[str] = None
    attempts: list = field(default_factory=list)
    md_path: Optional[str] = None
    elapsed_ms: int = 0
    meta: dict = field(default_factory=dict)   # M4/M9：runner 附加信息（fallback/charset/repair 等），由 _runner_meta() 提供

    def diagnose(self) -> str:
        """全失败时的聚合诊断（迁移自 markitdown FileConversionException.message 生成逻辑）。"""
        if not self.attempts:
            return "无任何后端尝试（链条为空）。"
        msg = f"转换失败：{len(self.attempts)} 个后端全部尝试失败：\n"
        for a in self.attempts:
            msg += f"  - {a.backend}: {a.exc_type}: {a.exc_message}（{a.elapsed_ms}ms）\n"
            if a.exc_type == "UnicodeDecodeError":
                msg += "    提示：charset 可能自动猜测错误，可尝试显式指定编码后重试。\n"
        return msg


RUN_META: dict = {}


def _runner_meta() -> dict:
    """M4/M9 钩子：返回本次成功后端的 runner 元数据（pages_with_form_tables 等）。"""
    return dict(RUN_META)


def _which_any() -> str:
    import shutil
    return shutil.which("npx") or "npx"


def _run_anydoc(doc: str, md: str) -> Optional[str]:
    """anydoc 双通道：Python 绑定优先，npx CLI 兜底（与 detect_backends dual 探测对齐）。"""
    try:
        import anydoc
        Path(md).write_text(anydoc.to_markdown(doc), encoding="utf-8")
        return "python:anydoc"
    except ImportError:
        pass
    npx = _which_any()
    r = subprocess.run([npx, "-y", "@firecrawl/anydoc", doc, "-o", md],
                       capture_output=True, text=True, timeout=PIPELINE_TIMEOUT)
    if r.returncode != 0:
        raise RuntimeError(f"anydoc CLI 退出码 {r.returncode}: {(r.stderr or r.stdout)[:300]}")
    return "cli:npx"


def _run_markitdown(doc: str, md: str) -> Optional[str]:
    from markitdown import MarkItDown
    r = MarkItDown().convert(doc)
    Path(md).write_text(r.text_content, encoding="utf-8")
    return "python:markitdown"

def _run_pymupdf4llm(doc: str, md: str) -> Optional[str]:
    import pymupdf4llm
    Path(md).write_text(pymupdf4llm.to_markdown(doc), encoding="utf-8")
    return "python:pymupdf4llm"


def _run_pdfplumber(doc: str, md: str) -> Optional[str]:
    """pdfplumber 文本兜底 + M6 无边框表格增强（逐页先试词坐标聚类，失败回退普通文本）。"""
    import pdfplumber
    from pdf_form_extract import extract_form_content_from_words
    parts = []
    with pdfplumber.open(doc) as pdf:
        for page in pdf.pages:
            try:
                form = extract_form_content_from_words(page)
            except Exception:
                form = None  # M6 启发式异常不阻断文本兜底
            if form and form.strip():
                parts.append(form.strip())
                RUN_META["pages_with_form_tables"] = RUN_META.get("pages_with_form_tables", 0) + 1
            else:
                t = page.extract_text()
                if t and t.strip():
                    parts.append(t.strip())
            page.close()
    if not parts:
        raise RuntimeError("pdfplumber 未提取到文本（可能为扫描件）")
    Path(md).write_text("\n\n".join(parts), encoding="utf-8")
    return "python:pdfplumber"


def _run_docling(doc: str, md: str) -> Optional[str]:
    from docling.document_converter import DocumentConverter
    r = DocumentConverter().convert(doc)
    Path(md).write_text(r.document.export_to_markdown(), encoding="utf-8")
    return "python:docling"


def _run_marker(doc: str, md: str) -> Optional[str]:
    raise RuntimeError("marker 未接入 pipeline runner（L1 DL 重型链，按门C 由 Agent 指引执行）")


def _run_mineru(doc: str, md: str) -> Optional[str]:
    """MinerU CLI（magic-pdf）：-p 输入 -o 输出目录 → 定位产物 md。"""
    import shutil
    exe = shutil.which("mineru") or shutil.which("magic-pdf")
    if not exe:
        raise RuntimeError("mineru/magic-pdf 可执行文件未找到")
    with tempfile.TemporaryDirectory(prefix="tri_pdf2md_mineru_") as td:
        r = subprocess.run([exe, "-p", doc, "-o", td], capture_output=True,
                           text=True, timeout=PIPELINE_TIMEOUT)
        mds = list(Path(td).rglob("*.md"))
        if r.returncode != 0 or not mds:
            raise RuntimeError(f"MinerU 失败 rc={r.returncode}，未找到产物 md")
        Path(md).write_text(mds[0].read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        return "cli:mineru"


BACKEND_RUNNERS: dict[str, Callable[[str, str], Optional[str]]] = {
    "anydoc": _run_anydoc, "pymupdf4llm": _run_pymupdf4llm,
    "markitdown": _run_markitdown, "pdfplumber": _run_pdfplumber,
    "docling": _run_docling, "marker": _run_marker, "mineru": _run_mineru,
}


# ---------------- 执行核心（家族同源，迁移自 markitdown _convert 循环设计） ----------------

def run_pipeline(doc: str, md: str, chain: list) -> PipelineResult:
    result = PipelineResult(ok=False)
    t0 = time.monotonic()
    for backend in chain:
        runner = BACKEND_RUNNERS.get(backend)
        if runner is None:
            result.attempts.append(FailedConversionAttempt(
                backend=backend, exc_type="UnknownBackend",
                exc_message="BACKEND_RUNNERS 未注册该后端执行器"))
            continue
        bt0 = time.monotonic()
        RUN_META.clear()  # M4/M9：每次尝试前清空 runner 元数据（防上次尝试残留）
        try:
            via = runner(doc, md)
            if via is None:
                result.attempts.append(FailedConversionAttempt(
                    backend=backend, exc_type="NotAccepted",
                    exc_message="后端不认此文件（返回 None）"))
                continue
            if Path(md).read_text(encoding="utf-8", errors="replace").strip() == "":
                result.attempts.append(FailedConversionAttempt(
                    backend=backend, exc_type="EmptyOutput",
                    exc_message="转换产物为空"))
                continue
            result.ok = True
            result.backend_used = backend
            result.md_path = md
            result.meta.update(_runner_meta())  # M4/M9：每 skill runner 元数据钩子（各 skill 均定义）
            break
        except Exception as e:
            tb = traceback.format_exc().strip().splitlines()[-5:]
            result.attempts.append(FailedConversionAttempt(
                backend=backend, exc_type=type(e).__name__,
                exc_message=str(e)[:500], traceback_tail="\n".join(tb)))
        finally:
            # 耗时记到本后端刚追加的 attempt 上（成功路径无 attempt，不误写他人）
            if result.attempts and result.attempts[-1].backend == backend \
                    and result.attempts[-1].elapsed_ms == 0:
                result.attempts[-1].elapsed_ms = int((time.monotonic() - bt0) * 1000)
    result.elapsed_ms = int((time.monotonic() - t0) * 1000)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-pdf2md 降级链执行器（M1）")
    ap.add_argument("--doc", required=True, help="输入文件路径")
    ap.add_argument("--md", required=True, help="输出 Markdown 路径")
    ap.add_argument("--chain", required=True,
                    help="逗号分隔，与 detect_backends 的 selected+fallback_chain 对齐")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc, md = Path(args.doc), Path(args.md)
    if not doc.is_file():
        safe_print(json.dumps({"ok": False, "errors": [f"文件不存在：{doc}"]}, ensure_ascii=False))
        return 2

    result = run_pipeline(str(doc), str(md), [c.strip() for c in args.chain.split(",") if c.strip()])
    payload = asdict(result)
    payload["diagnosis"] = None if result.ok else result.diagnose()
    safe_print(json.dumps(payload, ensure_ascii=False))
    return 0 if result.ok else 3


if __name__ == "__main__":
    sys.exit(main())
