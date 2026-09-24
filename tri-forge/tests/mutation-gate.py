#!/usr/bin/env python3
"""门④ 负向测试（mutation testing）—— 验证 compliance_check.py 的 22 条判据「有牙」。

流程：对真实 skill（tri-guard）逐项注入合规缺陷 → 运行门④ → 确认对应条目 FAIL → 还原 → 确认恢复 PASS。
若注入缺陷后门④仍 PASS，说明判据失效。

用法：
    python tri-forge/tests/mutation-gate.py          # 运行全部 mutation 用例

退出码：0 = 全部 mutation 被抓到且还原后 PASS；1 = 有未抓到的 mutation 或终态异常。

v1 缺陷（v2 已修）：
- M1 只替换 1 处内部指针（count=1），其余 2 处仍在 → self_ref 仍 True → 未抓到。v2 改为替换全部。
- M3/M6 的 CHANGELOG 恢复放在 mutate 内部而非 finally → 部分场景未还原。
  v2 把 SM 与 CHANGELOG 的备份都放在模块级，finally 统一还原。

教训：mutation testing 本身也要验证测试脚本的还原逻辑——
「先注入再还原」的还原必须放在 finally，且备份必须在 mutate 之前截取。


v1 缺陷：
- M1 只替换 1 处内部指针（count=1），其余 2 处仍在 → self_ref 仍 True → 未抓到。v2 改为替换全部。
- M3/M6 的 CHANGELOG 恢复放在 mutate 内部而非 finally → 部分场景未还原。v2 把 SM 与 CHANGELOG
  的备份都放在模块级，finally 统一还原。
- v1 的终态复验报 FAIL 是因为 M6 的 CHANGELOG 未还原 + M1 的 SM 未完全还原。
"""
import json
import pathlib
import re
import subprocess
import sys

def find_repo_root(start):
    for cand in (start, *start.parents):
        if (cand / ".git").exists():
            return cand
    return start


REPO = find_repo_root(pathlib.Path(__file__).resolve().parent)
SCRIPT = REPO / "tri-forge" / "scripts" / "compliance_check.py"
TARGET = "tri-guard"
TD = REPO / TARGET
SM = TD / "SKILL.md"
CL = TD / "CHANGELOG.md"

BAK_SM = SM.read_text(encoding="utf-8")
BAK_CL = CL.read_text(encoding="utf-8")

results = []


def restore():
    SM.write_text(BAK_SM, encoding="utf-8")
    CL.write_text(BAK_CL, encoding="utf-8")


def run_check():
    r = subprocess.run([sys.executable, str(SCRIPT), "--skill", TARGET, "--json"],
                       capture_output=True, text=True, timeout=90)
    d = json.loads(r.stdout)
    out = {}
    for it in d["results"][0]["items"]:
        out[it["n"]] = it["status"]
    out["verdict"] = d["results"][0].get("verdict")
    return out


def inject(name, expect_n, note, mutate):
    try:
        mutate()
        after = run_check()
        caught = after.get(expect_n) == "FAIL"
        results.append((name, expect_n, "✅ 抓到" if caught else "🔴 未抓到",
                        f"门④={after['verdict']} | {note}"))
    finally:
        restore()


# 基线
restore()
base = run_check()
results.append(("基线（未注入）", "—", "✅ PASS" if base["verdict"] == "PASS" else "🔴 非 PASS",
                f"门④={base['verdict']}"))

# M1 · 把全部内部指针换成外部 skill 的路径（self_ref → False）
inject("M1 版本检查全部指向外部（#22）", 22,
       "把全部 references/version-check-spec.md 换成 tri-intent/references/version-gate.md",
       lambda: SM.write_text(
           BAK_SM.replace("references/version-check-spec.md",
                          "tri-intent/references/version-gate.md"),
           encoding="utf-8"))

# M2 · 删独立安装声明
inject("M2 删独立安装声明（#2）", 2,
       "description 删「支持独立安装，含上游依赖检测N态逻辑」",
       lambda: SM.write_text(re.sub(
           r"支持独立安装[，,]含上游依赖检测[^\s，,；。]*逻辑", "", BAK_SM, count=1),
           encoding="utf-8"))

# M3 · CHANGELOG 首条版本改成比 frontmatter 低
def m3():
    CL.write_text(re.sub(r"^##\s*\[[0-9.]+\]", "## [0.0.1]",
                         BAK_CL, count=1, flags=re.M), encoding="utf-8")
inject("M3 CHANGELOG 首条≠frontmatter（#11）", 11, "首条版本改为 0.0.1", m3)

# M4 · 插入硬编码家族计数
inject("M4 插入硬编码家族计数（#17）", 17,
       "追加「共 19 个下游 skill」",
       lambda: SM.write_text(BAK_SM + "\n- 本家族共 19 个下游 skill。\n", encoding="utf-8"))

# M5 · 删自检句
inject("M5 删自检句（#5/#15）", 5,
       "把「本次意图=」改成「本次自检=」",
       lambda: SM.write_text(re.sub(r"本次(意图|模式|操作)\s*=", "本次自检=", BAK_SM, count=1),
                             encoding="utf-8"))

# M6 · 删除 CHANGELOG.md
def m6():
    CL.unlink()
inject("M6 删除 CHANGELOG.md（#1）", 1, "删除 CHANGELOG.md 文件", m6)

# 汇总
print("== 门④ 负向测试（mutation testing）v2 ==\n")
print(f"{'用例':<36} {'约束':<6} {'判定':<10} 说明")
print("-" * 100)
caught = total = 0
for name, n, verdict, note in results:
    print(f"{name:<36} #{str(n):<5} {verdict:<10} {note}")
    if verdict.startswith("✅"):
        caught += 1
    if name != "基线（未注入）":
        total += 1
print("-" * 100)
print(f"\n结果：{caught}/{total} 项注入被门④ 抓到")
restore()
final = run_check()
print(f"终态复验：门④={final['verdict']}（还原后应 PASS）")
sys.exit(0 if (final["verdict"] == "PASS" and caught == total) else 1)
