#!/usr/bin/env python3
"""门④ 负向测试（mutation testing）v3 —— 验证 compliance_check.py 的 24 条判据「有牙」。

流程：把真实 skill（tri-coding）**复制到临时目录** → 在副本上逐项注入合规缺陷 → 运行门④
      → 确认对应条目 FAIL → 还原副本 → 确认恢复 PASS。全程**零写入真实 skill**。

用法：
    python tri-forge/tests/mutation-gate.py          # 运行全部 mutation 用例

退出码：0 = 基线 PASS + 全部 mutation 被抓到 + 真实 skill 零变更；1 = 上述任一不成立；2 = 环境错误。

---

## 本版（v3）修复的两个既有缺陷

**D1 · 计数不对称导致退出码恒为 1**
  v2 的 `verdict.startswith("✅")` 把**基线行**一并计入 `caught`（基线的 verdict 恰是 `✅ PASS`），
  而 `total` 在汇总循环里**显式排除**基线 ⇒ `caught=7 ≠ total=6` ⇒ 退出码恒为 1，脚本永远报失败。
  v3 改为**只对注入用例计数**，基线单独断言，不再混入召回分母。

**D2 · `find_repo_root` 穿透 junction，实际改写真实 skill**
  `Path(__file__).resolve()` 会穿透 junction 落到真实仓库，于是 v2 **直接写**
  `tri-coding/SKILL.md` 与 `CHANGELOG.md` —— 跑 tri-forge 的测试会静默改动兄弟 skill；
  中途中断（强杀 / 断电）会留下注入态。
  v3 改为：① 变异只在 `tempfile` 副本上进行，`compliance_check.py --dir <副本>`；
  ② 运行前后对真实 skill 的关键文件做 md5 自证，不一致即判 FAIL；
  ③ `find_repo_root` 加前置守卫（须同时存在 `.git` 与 `tri-forge/scripts/compliance_check.py`），
     定位失败即退出 2，**绝不回退到「就地变异」**。

## 历史（v2 修复的 v1 缺陷，保留记录）

- M1 只替换 1 处内部指针（count=1），其余 2 处仍在 → self_ref 仍 True → 未抓到。v2 改为替换全部。
- M3/M6 的 CHANGELOG 恢复放在 mutate 内部而非 finally → 部分场景未还原。
  v2 把 SM 与 CHANGELOG 的备份都放在模块级，finally 统一还原。

教训：mutation testing 本身也要验证测试脚本的还原逻辑——
「先注入再还原」的还原必须放在 finally，且备份必须在 mutate 之前截取。
（v3 追加教训：**还原的对象不该是真实产物**——用副本就没有「还原失败」这个失败模式。）
"""
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------- 路径与守卫


def find_repo_root(start):
    """定位仓库根：须同时含 `.git` 与 `tri-forge/scripts/compliance_check.py`。

    仅判 `.git` 不足——本机 skills 目录经 junction 安装，`resolve()` 会穿透到真实仓库，
    一旦上游布局变化，错误的根会让 SCRIPT 指向不存在的路径，或（更糟）让 TARGET 落到别处。
    """
    for cand in (start, *start.parents):
        if (cand / ".git").exists() and (cand / "tri-forge" / "scripts" / "compliance_check.py").is_file():
            return cand
    return None


HERE = pathlib.Path(__file__).resolve().parent
REPO = find_repo_root(HERE)
if REPO is None:
    print("环境错误：未能定位仓库根。", file=sys.stderr)
    print("  判定条件：目录同时含 `.git` 与 `tri-forge/scripts/compliance_check.py`。", file=sys.stderr)
    print(f"  搜索起点：{HERE}", file=sys.stderr)
    print("  NEVER 回退到「就地变异」——那会改写真实 skill。", file=sys.stderr)
    sys.exit(2)

SCRIPT = REPO / "tri-forge" / "scripts" / "compliance_check.py"
TARGET = "tri-coding"
SRC = REPO / TARGET

if not (SRC / "SKILL.md").is_file():
    print(f"环境错误：变异靶 {SRC} 不存在或不是 skill 包。", file=sys.stderr)
    sys.exit(2)


def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest() if p.is_file() else "<absent>"


# D2 的机械判据：运行前后真实 skill 必须逐字节不变
GUARDED = {"SKILL.md": SRC / "SKILL.md", "CHANGELOG.md": SRC / "CHANGELOG.md"}
GUARD_BEFORE = {k: md5(v) for k, v in GUARDED.items()}

# ---------------------------------------------------------------- 临时副本

TMPROOT = pathlib.Path(tempfile.mkdtemp(prefix="mutation-gate-"))
WORK = TMPROOT / TARGET
shutil.copytree(SRC, WORK, ignore=shutil.ignore_patterns("__pycache__", ".git", "node_modules"))

SM = WORK / "SKILL.md"
CL = WORK / "CHANGELOG.md"
BAK_SM = SM.read_text(encoding="utf-8")
BAK_CL = CL.read_text(encoding="utf-8") if CL.is_file() else ""

results = []


def restore():
    """只还原**副本**；真实 skill 从未被写过，故不存在「还原失败」这一失败模式。"""
    SM.write_text(BAK_SM, encoding="utf-8")
    CL.write_text(BAK_CL, encoding="utf-8")


def run_check():
    r = subprocess.run([sys.executable, str(SCRIPT), "--dir", str(WORK), "--json"],
                       capture_output=True, text=True, timeout=90)
    if not r.stdout.strip():
        raise RuntimeError(f"门④ 无输出（rc={r.returncode}）：{r.stderr.strip()[:200]}")
    d = json.loads(r.stdout)
    res = d["results"][0]
    out = {it["n"]: it["status"] for it in res["items"]}
    out["verdict"] = res.get("verdict")
    return out


def inject(name, expect_n, note, mutate):
    try:
        mutate()
        after = run_check()
        caught = after.get(expect_n) == "FAIL"
        results.append((name, expect_n, "✅ 抓到" if caught else "🔴 未抓到",
                        f"门④={after['verdict']} | {note}", caught))
    except Exception as e:  # noqa: BLE001 —— 测试脚本须报错而非崩溃
        results.append((name, expect_n, "🔴 异常", f"{type(e).__name__}: {e}", False))
    finally:
        restore()


# ---------------------------------------------------------------- 用例

# 基线（**不参与召回计数**，D1 的修复点）
restore()
base = run_check()
BASE_OK = base["verdict"] == "PASS"

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

# M7 · 让包内自引用指针断链（#23）—— 第 23 条的「有牙」证明
def m7():
    SM.write_text(BAK_SM + "\n- 详见 `references/__mutation_dangling__.md`。\n", encoding="utf-8")


inject("M7 制造断链自引用指针（#23）", 23,
       "追加一个不存在的 references 指针", m7)

# ---------------------------------------------------------------- 汇总

restore()
final = run_check()
FINAL_OK = final["verdict"] == "PASS"

# D2 自证：真实 skill 逐字节未变
GUARD_AFTER = {k: md5(v) for k, v in GUARDED.items()}
leaked = [k for k in GUARDED if GUARD_BEFORE[k] != GUARD_AFTER[k]]

print("== 门④ 负向测试（mutation testing）v3 ==\n")
print(f"{'用例':<36} {'约束':<6} {'判定':<10} 说明")
print("-" * 100)
caught = total = 0
for name, n, verdict, note, ok in results:
    print(f"{name:<36} #{str(n):<5} {verdict:<10} {note}")
    total += 1
    if ok:
        caught += 1
print("-" * 100)
print(f"基线（未注入）：门④={base['verdict']}（{'✅ 应 PASS' if BASE_OK else '🔴 应为 PASS'}）")
print(f"终态复验：门④={final['verdict']}（还原后应 PASS）")
print(f"结果：{caught}/{total} 项注入被门④ 抓到")
print(f"D2 自证：真实 skill {SRC}")
for k, v in GUARD_AFTER.items():
    print(f"    {k:<14} md5={v} {'✅ 未变' if GUARD_BEFORE[k] == v else '🔴 已被改写'}")

shutil.rmtree(TMPROOT, ignore_errors=True)

ok_all = BASE_OK and FINAL_OK and caught == total and not leaked
sys.exit(0 if ok_all else 1)
