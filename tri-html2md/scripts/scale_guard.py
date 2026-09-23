#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输入规模守卫（P2-2）——蒸馏自 anydoc limits.rs 固定资源限制方法论。

对输入文件做「先预算后干活」式规模检查：
- ZIP 容器族（OOXML/ODF/EPUB）：条目数 / 总解压量 / 单条目解压量三硬上限；
- 表格类（.xlsx/.xlsm）：网格槽位展开面积估算（dimension + mergeCells），超预算固定走 L1 流式路径；
- 其余格式（OLE 旧格式 / PDF / CSV / HTML）：文件体积硬上限（解压量不可廉价计算，以文件体积为代理）。

硬上限语义对齐 anydoc「ResourceLimit = fatal = 完全不可能产出」：超硬上限 → grade_suggestion=BLOCK。
上限数值引用 anydoc limits.rs 口径（12 项固定限制，刻意不可配置），见蒸馏报告 docs/distill-anydoc-main-20260908.md P2-2。

用法（preflight.py 内部调用）：
    from scale_guard import apply_scale_guard
    apply_scale_guard(result, path, force_grade_on_slots_over="L1")  # 表格类传 force 参数
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

# anydoc limits.rs 口径（蒸馏报告 v1.3.0 P2-2）
LIMITS = {
    "max_single_entry_bytes": 128 * 1024 * 1024,      # 单条目解压 128MiB
    "max_total_uncompressed_bytes": 512 * 1024 * 1024,  # 总解压 512MiB
    "max_entries": 100_000,                            # 条目数 100k
    "max_grid_slots": 4_000_000,                       # 网格槽位 4M
    "max_raw_file_bytes": 512 * 1024 * 1024,           # 非容器格式文件体积代理上限
}
LIMITS_REF = "anydoc limits.rs 口径（12 项固定资源限制，刻意不可配置）——蒸馏报告 v1.3.0 P2-2"

_ZIP_EXTS = {".docx", ".docm", ".pptx", ".pptm", ".ppsx", ".ppsm",
             ".xlsx", ".xlsm", ".odt", ".odp", ".ods", ".epub"}
_TABLE_ZIP_EXTS = {".xlsx", ".xlsm"}
_SHEET_RE = re.compile(r"^xl/worksheets/sheet\d+\.xml$")
_MERGE_RE = re.compile(r'<mergeCell ref="([A-Z]+)(\d+):([A-Z]+)(\d+)"')
_DIM_RE = re.compile(r'<dimension ref="[A-Z]+\d+:([A-Z]+)(\d+)"')
_XML_READ_CAP = 2_000_000  # 单工作表 XML 读取上限（启发式估算，超长部分不参与估算，如实标注）


def _col_to_num(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n


def _zip_stats(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        entries = len(infos)
        total = sum(i.file_size for i in infos)
        single = max((i.file_size for i in infos), default=0)
        slots = None
        if path.suffix.lower() in _TABLE_ZIP_EXTS:
            slots = 0
            estimated_any = False
            for name in zf.namelist():
                if not _SHEET_RE.match(name):
                    continue
                xml = zf.read(name)[:_XML_READ_CAP].decode("utf-8", "replace")
                dim = _DIM_RE.search(xml)
                if dim:
                    slots += _col_to_num(dim.group(1)) * int(dim.group(2))
                    estimated_any = True
                for m in _MERGE_RE.finditer(xml):
                    area = ((_col_to_num(m.group(3)) - _col_to_num(m.group(1)) + 1)
                            * (int(m.group(4)) - int(m.group(2)) + 1))
                    slots += max(area - 1, 0)
                    estimated_any = True
            if not estimated_any:
                slots = None
    return {"entries": entries, "total": total, "single": single, "grid_slots_estimate": slots}


def apply_scale_guard(result: dict, path, force_grade_on_slots_over: str | None = None) -> dict:
    """在 preflight 结果上执行规模守卫：写 result["scale_guard"]、追加 risks、必要时改判等级。"""
    p = Path(path)
    violations: list[str] = []
    stats: dict = {}
    try:
        if p.suffix.lower() in _ZIP_EXTS or p.open("rb").read(2) == b"PK":
            stats = _zip_stats(p)
            if stats["entries"] > LIMITS["max_entries"]:
                violations.append(f"ZIP 条目数 {stats['entries']} 超上限 {LIMITS['max_entries']}")
            if stats["total"] > LIMITS["max_total_uncompressed_bytes"]:
                violations.append(f"总解压量 {stats['total'] / 1048576:.0f}MB 超上限 512MB")
            if stats["single"] > LIMITS["max_single_entry_bytes"]:
                violations.append(f"单条目解压量 {stats['single'] / 1048576:.0f}MB 超上限 128MB")
            if stats["grid_slots_estimate"] is not None \
                    and stats["grid_slots_estimate"] > LIMITS["max_grid_slots"]:
                violations.append(
                    f"网格槽位估算 {stats['grid_slots_estimate']} 超预算 {LIMITS['max_grid_slots']}——合并展开面积过大")
            stats["mode"] = "zip-container"
        else:
            size = p.stat().st_size
            stats = {"entries": None, "total": size, "single": None,
                     "grid_slots_estimate": None, "mode": "raw-file-proxy"}
            if size > LIMITS["max_raw_file_bytes"]:
                violations.append(f"文件体积 {size / 1048576:.0f}MB 超上限 512MB（解压量不可廉价计算，以文件体积为代理）")
    except Exception as e:  # 守卫自身永不阻断预检主流程
        result["scale_guard"] = {"status": "skipped", "reason": f"{type(e).__name__}: {e}",
                                 "limits_ref": LIMITS_REF}
        return result

    action = "none"
    hard = [v for v in violations if "网格槽位" not in v]
    soft = [v for v in violations if "网格槽位" in v]
    if hard:
        action = "block"
        result["grade_suggestion"] = "BLOCK"
        for v in hard:
            result["risks"].append(f"输入规模守卫：{v}——错误=完全不可能产出（ResourceLimit 语义），NEVER 强行转换")
    elif soft and force_grade_on_slots_over:
        action = f"force-{force_grade_on_slots_over}"
        if result.get("grade_suggestion") in (None, "L0"):
            result["grade_suggestion"] = force_grade_on_slots_over
        for v in soft:
            result["risks"].append(f"输入规模守卫：{v}——固定走 {force_grade_on_slots_over} 流式路径")
    elif soft:
        action = "warn"
        for v in soft:
            result["risks"].append(f"输入规模守卫：{v}")

    result["scale_guard"] = {
        "status": "violation" if violations else "ok",
        "action": action,
        "limits": LIMITS,
        "limits_ref": LIMITS_REF,
        "measured": stats,
        "violations": violations,
    }
    return result
