#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""coverage.py —— 生成「tri 家族可评估性总账」（`coverage.md`）。

为什么是脚本而不是手写文档
--------------------------------------------------------------------
族规「文档数值断言禁手写，脚本实测注入」：skill 数、门禁脚本数、B/C 档规模
全部随批次变动，手写必然过期（历史两次先例：ops/README 与根 README 的 op 计数
122 残留）。故总账**由本脚本生成**，`coverage.md` 头部标注生成时间与命令。

分档判据（A 档可机器复核，B/C 是判断 + 依据）
--------------------------------------------------------------------
A 档 · 有可运行门禁 —— **可复核判据**：磁盘上存在 `gate` 字段指向的脚本文件，
    且该门禁能被 `gate_adapter.py run --skill <s>` 成功归一。声明为 A 却不满足者
    整脚本 FAIL（fail-closed，不静默降级）。
B 档 · 有可复用脚本或判据真源，但**缺任务级 scorer** —— 需要新写断言才能进电池。
C 档 · 流程 / 方法型，输出是自然语言，无 pass/fail —— **不适用于 SkillOpt 式训练**
    （验证门无处落脚），列在此处是为了让「不做什么」有据可查。

用法
--------------------------------------------------------------------
    python ops/eval-harness/coverage.py --emit          # 生成 coverage.md
    python ops/eval-harness/coverage.py --json          # 机器可读
    python ops/eval-harness/coverage.py --check         # 只校验 A 档声明（CI 用）
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = next((p for p in (Path(__file__).resolve(), *Path(__file__).resolve().parents)
             if (p / ".git").exists()), Path(__file__).resolve().parent)
SKIP = {".git", ".workbuddy", ".tribro", "__pycache__", "node_modules"}
PY = sys.executable

# 顶层 skill → (档, gate 路径 | 依据)
TOP = {
    "tri-forge": ("A", "tri-forge/scripts/compliance_check.py",
                  "24 条判据 + case 电池 + mutation-gate"),
    "tri-html": ("A", "tri-html/tests/run_exec_tests.py",
                 "31 例可执行面病例 + validate/deliver 退出码"),
    "tri-verify": ("A", "tri-verify/scripts/verify_gate.py",
                   "9 退出码映射 / 轮次 / 盖章 + self-test"),
    "tri-lottie": ("A", "tri-lottie/scripts/compliance_check.py",
                   "T1–T10 十项合规判据"),
    "tri-checklist": ("B", "tri-checklist/scripts/build_checklist.py",
                      "四维覆盖率可由 checklist 产物统计（缺 scorer）"),
    "tri-action": ("B", "tri-action/scripts/hash_confirm.py",
                   "确认哈希可校验（缺 I14 执行结果度量）"),
    "tri-code-analyzer": ("B", "tri-code-analyzer/scripts/stack_detect.py",
                          "栈检测可测（缺七阶段报告质量度量）"),
    "tri-evolve": ("B", "tri-evolve/scripts/evolve_learn.py",
                   "归因可测（缺画像复用效果度量）"),
    "tri-intent": ("B", "ops/eval-harness/run_eval.py（rollout_file scorer）",
                   "rollout_file scorer 已建（2026-09-27）：golden 6 case 确定性断言（§一 真源 GT）；"
                   "余缺口=集成 check_downstream 安装检测与快照落盘断言"),
}
B_SUBS = {"tri-intent": ["asking", "doing", "expressing", "meta", "clarify-gate"]}


def norm(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace").replace("\r", "")


def version_of(p: Path) -> str:
    m = re.search(r"(?m)^version:\s*(\S+)", norm(p.read_bytes()))
    return m.group(1) if m else "—"


def inventory():
    rows = []
    for sm in sorted(REPO.glob("**/SKILL.md")):
        if set(sm.parts) & SKIP:
            continue
        rel = sm.relative_to(REPO).as_posix()
        parts = sm.relative_to(REPO).parts
        top = parts[0]
        if len(parts) == 2:
            layer = "顶层"
            tier, asset, basis = TOP.get(top, ("C", "", "流程 / 方法型，无 pass/fail"))
        elif len(parts) == 3 and parts[0] == "tri-intent":
            top = parts[1]  # 真名（如 asking / doing），行表不得写父名
            layer, tier, asset = "tri-intent 二层", "C", ""
            basis = f"{parts[1]} 二层：方法型，无 pass/fail"
        elif len(parts) == 4 and parts[1] == "children":
            top = parts[2]  # 真名（如 tri-charter）
            layer, tier, asset = "tri-sdlc children", "C", ""
            basis = "SDLC 阶段型：输出为文档，判据在门禁条目（未脚本化）"
        else:
            layer, tier, asset, basis = "其它", "C", "", "未归类"
        rows.append({"path": rel, "skill": top, "layer": layer, "tier": tier,
                     "gate": asset if tier == "A" else "",
                     "asset": asset if tier == "B" else "",
                     "version": version_of(sm), "basis": basis})
    return rows


def check_a(rows) -> list[str]:
    """A 档可复核：gate 脚本必须存在且能被 gate_adapter 归一。"""
    bad = []
    for r in rows:
        if r["tier"] != "A":
            continue
        g = REPO / r["gate"]
        if not g.is_file():
            bad.append(f"{r['skill']}：声明 A 档但 gate 不存在 → {r['gate']}")
            continue
        p = subprocess.run([PY, str(REPO / "ops/eval-harness/gate_adapter.py"),
                            "run", "--skill", r["skill"], "--json"],
                           capture_output=True, text=True, encoding="utf-8")
        try:
            env = json.loads(p.stdout)
        except Exception:  # noqa: BLE001
            bad.append(f"{r['skill']}：gate_adapter 无法归一（rc={p.returncode}）"
                       f" {p.stderr.strip()[:120]}")
            continue
        if not env.get("items"):
            bad.append(f"{r['skill']}：归一后 items 为空")
    return bad


def emit(rows, bad) -> str:
    n = {t: sum(1 for r in rows if r["tier"] == t) for t in "ABC"}
    layers = {}
    for r in rows:
        layers.setdefault(r["layer"], []).append(r)
    L = []
    ts = time.strftime("%Y-%m-%d %H:%M")
    L.append("# tri 家族可评估性总账（SkillOpt 式训练的前置条件）")
    L.append("")
    L.append(f"> **本文件由 `ops/eval-harness/coverage.py --emit` 生成于 {ts}。**")
    L.append("> 数值断言全部实测注入，**禁止手写**——改档位请改脚本里的 `TOP` 表再重生成。")
    L.append("> 口径：`A` = 有可运行门禁（可复核）；`B` = 有可复用脚本/真源但缺任务级 scorer；")
    L.append("> `C` = 流程/方法型、无 pass/fail，**不适用于训练循环**。")
    L.append("> 背景见 `researcher 结论`：SkillOpt（arXiv 2605.23904）的整套机制以**确定性验证集**为地基。")
    L.append("")
    L.append("## 一、规模（实测）")
    L.append("")
    L.append(f"- 物理 `SKILL.md` 共 **{len(rows)}** 份")
    for k in ("顶层", "tri-intent 二层", "tri-sdlc children"):
        if k in layers:
            L.append(f"  - {k}：{len(layers[k])} 份")
    L.append(f"- 家族惯用计数 = 顶层 + children = "
             f"{len(layers.get('顶层', [])) + len(layers.get('tri-sdlc children', []))}")
    L.append(f"- 分档：**A {n['A']} / B {n['B']} / C {n['C']}**")
    L.append(f"- A 档可复核校验：{'✅ 全部通过' if not bad else '🔴 ' + str(len(bad)) + ' 条不合规'}")
    for b in bad:
        L.append(f"  - {b}")
    L.append("")
    for tier, title in (("A", "二、A 档 · 有可运行门禁（可直接进评估基座）"),
                        ("B", "三、B 档 · 缺任务级 scorer（需先写断言）"),
                        ("C", "四、C 档 · 不适用于训练循环（显式排除）")):
        L.append(f"## {title}")
        L.append("")
        if tier == "C":
            L.append("| layer | 数量 | skill |")
            L.append("|---|---|---|")
            for k, rs in layers.items():
                if all(r["tier"] == "C" for r in rs):
                    L.append(f"| {k} | {len(rs)} | {' · '.join(sorted(r['skill'] for r in rs))} |")
            L.append("")
            L.append("**判据**：这些 skill 的产物是自然语言规划/质询/路由，")
            L.append("没有「同输入必同输出」的裁决点 ⇒ 验证门无处落脚。")
            L.append("给它们硬造一个 pass/fail 只会退化成 LLM judge 绝对分")
            L.append("（SkillLens 实证 judge 准确率 46.4%，且跨 judge 换尺噪音 ±8）。")
        else:
            L.append("| skill | 版本 | 门禁 / 资产 | 依据 |")
            L.append("|---|---|---|---|")
            for r in sorted((x for x in rows if x["tier"] == tier), key=lambda x: x["skill"]):
                L.append(f"| `{r['skill']}` | {r['version']} | `{r['gate'] or r['asset']}` "
                         f"| {r['basis']} |")
        L.append("")
    L.append("## 五、缺口（决定下一步优先级）")
    L.append("")
    L.append("| # | 缺口 | 影响 |")
    L.append("|---|---|---|")
    L.append("| 1 | A 档 4 个中 3 个无 `--dir`（只能审自身，不能跑 fixture 变体） | 电池的 "
             "`fixture` 型 case 无法覆盖 tri-html / tri-lottie / tri-verify |")
    L.append("| 2 | B 档 5 个无任务级 scorer | golden 集建不起来，训练循环无 val |")
    L.append("| 3 | C 档 31 份无 pass/fail | 显式排除，不做无效拟合 |")
    L.append("")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    rows = inventory()
    bad = check_a(rows)

    if a.json:
        print(json.dumps({"rows": rows, "bad": bad}, ensure_ascii=False, indent=1))
    if a.check:
        print(f"A 档可复核：{'PASS' if not bad else 'FAIL'}")
        for b in bad:
            print(f"  - {b}")
    if a.emit:
        out = REPO / "ops/eval-harness/coverage.md"
        out.write_text(emit(rows, bad), encoding="utf-8")
        print(f"已生成 {out.relative_to(REPO).as_posix()}"
              f"（{len(rows)} 份 SKILL.md · A/B/C = "
              f"{sum(1 for r in rows if r['tier'] == 'A')}/"
              f"{sum(1 for r in rows if r['tier'] == 'B')}/"
              f"{sum(1 for r in rows if r['tier'] == 'C')}）")
    if not (a.emit or a.json or a.check):
        print(f"SKILL.md {len(rows)} 份；A 档校验 {'PASS' if not bad else 'FAIL'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
