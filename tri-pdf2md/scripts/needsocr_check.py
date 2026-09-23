#!/usr/bin/env python3
"""NeedsOcr 信号检测（P0-2 · tri-pdf2md）

anydoc 不做本地 OCR——扫描页/图片页触发 NeedsOcrError（带页码区间）。
本脚本按确定性规则把该信号接入预检/门C 流程：
  - anydoc 转换捕获 NeedsOcrError → 输出精确页码清单 + 等级建议自动置 L2（脚本逻辑，NEVER Agent 裁量）；
  - 转换成功 → needs_ocr=false，走 anydoc L0 主链。

用法：
    python scripts/needsocr_check.py --pdf <file> --json
退出码：0 成功（含 needs_ocr=true——信号本身就是有效结论）；2 参数/IO/其他错误。
"""
from _io_safe import safe_print
import argparse
import json
import sys
from pathlib import Path


def check(pdf_path: Path) -> dict:
    try:
        import anydoc
    except ImportError:
        raise RuntimeError(
            "needsocr_check 依赖 python:anydoc 绑定（pip install anydoc）——"
            "当前环境仅检测到 npx CLI 模式，无法读取 NeedsOcr/版面信号；"
            "请安装 python:anydoc 后重试，或将扫描件直接交给支持 OCR 的 L2 后端")

    base = {"pdf": str(pdf_path), "needs_ocr": False, "pages": [], "grade_suggestion": None, "backend": "anydoc"}
    try:
        md = anydoc.to_markdown(str(pdf_path))
        base["md_chars"] = len(md)
        return base
    except anydoc.NeedsOcrError as e:
        pages = list(getattr(e, "pages", []) or [])
        base["needs_ocr"] = True
        base["pages"] = pages
        base["grade_suggestion"] = "L2"
        base["message"] = (
            f"anydoc 报告扫描页/图片页需要 OCR（页码 {pages if pages else '全部'}）——"
            "等级建议自动置 L2，MUST 走 DL 链（MinerU/docling/marker），NEVER 对扫描件强行走 anydoc"
        )
        return base


def main() -> int:
    ap = argparse.ArgumentParser(description="anydoc NeedsOcr 信号检测（P0-2）")
    ap.add_argument("--pdf", required=True, help="PDF 路径")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        safe_print(json.dumps({"ok": False, "error": f"PDF 不存在: {pdf_path}"}, ensure_ascii=False))
        return 2

    try:
        result = check(pdf_path)
    except Exception as e:  # noqa: BLE001
        safe_print(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
        return 2

    result["ok"] = True
    if args.json or True:
        safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
