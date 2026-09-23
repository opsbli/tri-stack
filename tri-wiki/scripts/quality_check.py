#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-wiki 门F：整库质量校验与交付报告（quality-report.md + 库内 build-report.md 副本）。

仅用 Python 标准库。指标全部确定性计算，NEVER 目测；不可计算指标显式标注「不适用」。

用法：
    python quality_check.py --kb-root <知识库根> --process-dir <.tribro/wiki/WIKI_*> [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REQUIRED_FIELDS = ["title", "type", "source", "source_format", "created"]

# 置信度阈值（调整只改此处常量）
TH_COVERAGE_A, TH_COVERAGE_B = 0.95, 0.90
TH_BROKEN_A, TH_BROKEN_B = 0.01, 0.02
TH_COMPLETENESS_B = 0.98
TH_FIDELITY_B = 0.85


def parse_frontmatter(text: str):
    fm = {}
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^([A-Za-z_][\w]*)\s*:\s*(.*)$", line.strip())
            if mm:
                fm[mm.group(1)] = mm.group(2).strip()
    return fm


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}


def compute(kb_root: Path, process_dir: Path):
    manifest = load_json(process_dir / "sources-manifest.json")
    convert = load_json(process_dir / "convert-summary.json")
    index = load_json(process_dir / "index.json")
    organize = load_json(process_dir / "organize.json")

    files = manifest.get("files", [])
    processable = [f for f in files if f.get("category") in ("direct", "convert")]
    skipped = [f for f in files if f.get("category") in ("skip", "duplicate")]

    # 覆盖率：manifest entries / 可处理源文件
    bm = load_json(kb_root / ".wiki-meta" / "build-manifest.json")
    built_srcs = {e["src"] for e in bm.get("entries", [])}
    ingested = [f for f in processable if f["path"] in built_srcs]
    coverage = round(len(ingested) / len(processable), 4) if processable else None

    # 组织完整度：frontmatter 必填字段覆盖率
    docs, missing_fields = [], []
    for md in sorted(kb_root.rglob("*.md")):
        rel = str(md.relative_to(kb_root))
        if rel.startswith(".wiki-meta") or md.name in {"build-report.md"}:
            continue
        fm = parse_frontmatter(md.read_text(encoding="utf-8", errors="replace"))
        docs.append({"rel": rel, "fm": fm})
        miss = [k for k in REQUIRED_FIELDS if not fm.get(k)]
        if miss:
            missing_fields.append({"file": rel, "missing": miss})
    completeness = round((len(docs) - len(missing_fields)) / len(docs), 4) if docs else None

    # 断链率 / 链接密度（门E index.json；若缺则置不适用）
    links = index.get("links", {})
    broken_rate = links.get("broken_rate")
    link_density = links.get("link_density")

    # 重复率：manifest 近重复标记
    near_dups = [f for f in files if (f.get("dup_flag") or "").startswith("near_dup:")]

    # 转换保真率：convert-summary 聚合
    fidelity = convert.get("avg_fidelity")

    # 置信度分级
    reasons = []
    level = "A"
    if coverage is None or coverage < TH_COVERAGE_A or completeness is None or completeness < 1.0 \
            or (broken_rate is not None and broken_rate >= TH_BROKEN_A):
        level = "B"
    if (coverage is None or coverage < TH_COVERAGE_B) or (completeness is not None and completeness < TH_COMPLETENESS_B) \
            or (broken_rate is not None and broken_rate >= TH_BROKEN_B) \
            or organize.get("failed", 0) > 0:
        level = "C"
    if coverage is None:
        reasons.append("覆盖率不可计算（无可处理源文件）")
    if completeness is not None and completeness < 1.0:
        reasons.append(f"frontmatter 完整度 {completeness:.1%} < 100%")
    if broken_rate is not None and broken_rate >= TH_BROKEN_A:
        reasons.append(f"断链率 {broken_rate:.2%} ≥ {TH_BROKEN_A:.0%}")
    if organize.get("failed", 0) > 0:
        reasons.append(f"存在 {organize.get('failed')} 个组织失败文件")
    if level == "A":
        reasons.append("全指标达到 A 级阈值")

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "kb_root": str(kb_root),
        "source_total": len(files),
        "processable": len(processable),
        "ingested": len(ingested),
        "skipped": len(skipped),
        "coverage": coverage,
        "doc_count": len(docs),
        "frontmatter_completeness": completeness,
        "missing_field_files": missing_fields,
        "avg_fidelity": fidelity,
        "broken_rate": broken_rate,
        "link_density": link_density,
        "near_duplicate_count": len(near_dups),
        "near_duplicates": [f["path"] for f in near_dups],
        "skipped_files": [{"path": f["path"], "reason": f.get("skip_reason") or f.get("dup_flag")} for f in skipped],
        "organize_failed": organize.get("failed", 0),
        "confidence": {"level": level, "reasons": reasons},
    }


def render_report(r: dict) -> str:
    def pct(v):
        return "不适用" if v is None else f"{v:.1%}"

    def num(v):
        return "不适用" if v is None else str(v)

    lines = [
        "# tri-wiki 知识库质量报告", "",
        f"> 生成时间：{r['generated_at']} · 置信度 **{r['confidence']['level']}**", "",
        "## 指标总表", "",
        "| 指标 | 值 | 目标 |", "|---|---|---|",
        f"| 覆盖率 | {pct(r['coverage'])} | ≥90% |",
        f"| 组织完整度 | {pct(r['frontmatter_completeness'])} | 100% |",
        f"| 转换保真率 | {pct(r['avg_fidelity'])} | ≥85% |",
        f"| 断链率 | {pct(r['broken_rate'])} | <2% |",
        f"| 链接密度 | {num(r['link_density'])} | ≥1（提示项） |",
        f"| 近重复笔记 | {r['near_duplicate_count']} | 人工仲裁 |",
        "",
        "## 置信度分级", "",
        f"**{r['confidence']['level']}** —— {'；'.join(r['confidence']['reasons'])}", "",
        "## 构建元数据", "",
        f"- 源文件总数：{r['source_total']}（可处理 {r['processable']} / 跳过 {r['skipped']}）",
        f"- 入库文档：{r['doc_count']} 篇；组织失败：{r['organize_failed']}",
        "",
        "## 跳过与失败清单", "",
    ]
    if r["skipped_files"]:
        lines.extend(f"- `{s['path']}` — {s['reason']}" for s in r["skipped_files"])
    else:
        lines.append("-（无）")
    lines += ["", "## 复核项清单（永不省略）", "",
              "- [ ] 主题归属仲裁：抽查各主题首尾文件分类是否准确（确认门② 是否 --auto）",
              "- [ ] 近重复仲裁：" + (f"{r['near_duplicate_count']} 组待确认" if r['near_duplicate_count'] else "无"),
              "- [ ] 断链修复：" + (f"{len(r.get('broken_list', []))} 条待修复" if r.get('broken_list') else "见 index.json broken 字段"),
              "- [ ] 转换细节复核：图片题注/表格/公式的原转换报告复核项",
              "- [ ] RAG 语料抽检（若启用 --rag）：分块边界与元数据槽位", "",
              "## 发布指引", "",
              "- Obsidian：File → Open folder as vault，选择本知识库目录",
              "- Quartz：`npx quartz create` 后将本库 md 同步至 content/（保留 frontmatter）",
              "- MkDocs Material：`mkdocs new .` 后将 md 置于 docs/（frontmatter title 可用）",
              "- RAG 接入：chunks.jsonl（父子分块结构同 tri-pdf2md rag-handoff-spec）", "",
              "> v1 仅支持全量构建；源数据更新后须重新构建并在本报告标注版本。", "",
              "---", "",
              "*本报告由 tri-wiki 门F 自动生成，指标确定性计算，不可计算项显式标注「不适用」。*",
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb-root", required=True)
    ap.add_argument("--process-dir", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    kb_root, process_dir = Path(args.kb_root), Path(args.process_dir)
    result = compute(kb_root, process_dir)

    process_dir.mkdir(parents=True, exist_ok=True)
    (process_dir / "quality.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    report = render_report(result)
    (process_dir / "quality-report.md").write_text(report, encoding="utf-8")
    (kb_root / "build-report.md").write_text(report, encoding="utf-8")

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"质量报告已生成：置信度 {result['confidence']['level']}；"
              f"覆盖率 {result['coverage']}；完整度 {result['frontmatter_completeness']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
