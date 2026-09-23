#!/usr/bin/env python3
"""图片资产落盘适配层（P0-4 唯一路径 · tri-xx2md 家族通用）

anydoc 的图片 bytes 保存在文档模型（to_document().assets），MD 渲染不输出
![]() 引用——与 tri 契约「assets/ 图片落盘 + MD 引用」之间唯一的结构性冲突。
本脚本按确定性规则堵住该冲突：
  1. to_document() 遍历 assets 逐个落盘 assets/asset_<id>.<ext>（media_type → 扩展名映射写死）；
  2. 在 MD 末尾追加「图片资产清单」段（每资产一行 `![asset_<id>](assets/asset_<id>.<ext>)`），
     保证 assets/ 与 MD 引用一一对应；幂等：已有清单段先移除再重写，NEVER 重复追加。

用法：
    python scripts/dump_assets.py --doc <file> --md <同名>.md [--assets-dir assets] --json

退出码：0 成功（含零资产）；2 参数/IO 错误。NEVER 在 anydoc 转换失败时被调用
（本脚本仅处理已成功转换的产物）。
"""
from _io_safe import safe_print
import argparse
import json
import re
import sys
from pathlib import Path

# media_type → 扩展名映射（确定性，NEVER 现场裁量）
MEDIA_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/tiff": ".tif",
    "image/svg+xml": ".svg",
    "image/x-emf": ".emf",
    "image/emf": ".emf",
    "image/x-wmf": ".wmf",
    "image/wmf": ".wmf",
    "application/vnd.ms-ole-object": ".ole.bin",
}
DEFAULT_EXT = ".bin"
ASSET_SECTION_HEADING = "## 图片资产清单"


def dump_assets(doc_path: Path, md_path: Path, assets_dir_name: str) -> dict:
    try:
        import anydoc
    except ImportError:
        raise RuntimeError(
            "dump_assets 依赖 python:anydoc 绑定（pip install anydoc）——"
            "npx CLI 模式不产出文档模型 assets；请先 pip install anydoc "
            "并用 python:anydoc 路径重新转换后再落盘资产")

    doc = anydoc.to_document(doc_path.read_bytes())
    assets = list(doc.assets)
    assets_dir = md_path.parent / assets_dir_name
    md_text = md_path.read_text(encoding="utf-8")

    # 幂等：移除既有资产清单段（本脚本产生的重复运行防护）
    section_re = re.compile(rf"\n*{re.escape(ASSET_SECTION_HEADING)}\n(?:.*\n?)*", re.MULTILINE)
    md_text = section_re.sub("\n", md_text).rstrip() + "\n" if assets else md_text

    lines = []
    dumped = []
    for a in assets:
        ext = MEDIA_EXT.get(a.media_type, DEFAULT_EXT)
        fname = f"asset_{a.id}{ext}"
        rel_ref = f"{assets_dir_name}/{fname}"
        target = md_path.parent / assets_dir_name / fname
        if not assets_dir.exists():
            assets_dir.mkdir(parents=True, exist_ok=True)
        target.write_bytes(bytes(a.data))
        dumped.append({"id": a.id, "media_type": a.media_type, "file": str(target), "bytes": len(a.data)})
        lines.append(f"![asset_{a.id}]({rel_ref})")

    if assets:
        md_text = md_text.rstrip() + f"\n\n{ASSET_SECTION_HEADING}\n\n" + "\n".join(lines) + "\n"
        md_path.write_text(md_text, encoding="utf-8")

    return {
        "ok": True,
        "doc": str(doc_path),
        "md": str(md_path),
        "assets_dumped": len(dumped),
        "assets": dumped,
        "md_updated": bool(assets),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="anydoc 图片资产落盘适配层（P0-4）")
    ap.add_argument("--doc", required=True, help="源文档路径（anydoc 已成功转换）")
    ap.add_argument("--md", required=True, help="anydoc 产出的 MD 路径")
    ap.add_argument("--assets-dir", default="assets", help="资产目录名（默认 assets）")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    doc_path = Path(args.doc)
    md_path = Path(args.md)
    if not doc_path.exists():
        safe_print(json.dumps({"ok": False, "error": f"源文档不存在: {doc_path}"}, ensure_ascii=False))
        return 2
    if not md_path.exists():
        safe_print(json.dumps({"ok": False, "error": f"MD 文件不存在: {md_path}"}, ensure_ascii=False))
        return 2

    try:
        result = dump_assets(doc_path, md_path, args.assets_dir)
    except Exception as e:  # noqa: BLE001 —— 兜底转 JSON，NEVER 半成品交付
        safe_print(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False))
        return 2

    if args.json or True:
        safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
