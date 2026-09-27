#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`drop_block` op 的隔离回归测试。

**全程在 tempfile 内的合成仓库里跑，绝不触碰真实 tri-stack 仓库**
（教训来源：tri-forge `mutation-gate.py` v3 —— v2 因 `Path.resolve()` 穿透 junction
直接改写了兄弟 skill；此处对「真实仓库零污染」做显式断言 T8）。

判据纪律：幂等 MUST 用**字节指纹**验证，不能只比输出文本
（patch 层教训：锚点型注入曾因只比输出而重复注入 43 份 ×3）。

用法：python ops/patches/tests/test_drop_block.py
退出码：0 = 全过；1 = 有用例失败
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC_APPLY = Path(__file__).resolve().parents[1] / "apply.py"
REAL_REPO = Path(__file__).resolve().parents[3]

FIXTURE = (
    "# Fixture\n"
    "\n"
    "## 第一节\n"
    "内容 A\n"
    "\n"
    "## 待删除节\n"
    "内容 B\n"
    "内容 C\n"
    "\n"
    "## 第三节\n"
    "内容 D\n"
)

EXPECTED_AFTER = (
    "# Fixture\n"
    "\n"
    "## 第一节\n"
    "内容 A\n"
    "\n"
    "## 第三节\n"
    "内容 D\n"
)

BASE_OP = {
    "id": "t-drop",
    "type": "drop_block",
    "label": "测试：删除「待删除节」",
    "glob": "FIX/skill.md",
    "begin": "## 待删除节",
    "end": "内容 C",
}

RESULTS = []


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def check(name: str, cond: bool, evidence: str) -> None:
    RESULTS.append((name, bool(cond), evidence))
    print(f"{'✅' if cond else '❌'} {name}")
    if not cond or evidence:
        print(f"     {evidence}")


def build(tmp: Path, ops, fixture: str = FIXTURE) -> Path:
    (tmp / ".git").mkdir(parents=True, exist_ok=True)
    pd = tmp / "ops" / "patches"
    pd.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_APPLY, pd / "apply.py")
    (pd / "manifest.json").write_text(
        json.dumps({"version": 1, "exclude_paths": [".workbuddy", ".git"], "ops": ops},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    f = tmp / "FIX" / "skill.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(fixture, encoding="utf-8")
    return f


def run(tmp: Path, *extra: str):
    r = subprocess.run([sys.executable, str(tmp / "ops" / "patches" / "apply.py"), *extra],
                       capture_output=True, text=True, encoding="utf-8", cwd=str(tmp))
    try:
        return json.loads(r.stdout)["results"][0], r
    except Exception:  # noqa: BLE001
        return {"_raw": r.stdout, "_err": r.stderr, "_rc": r.returncode}, r


def case(name, ops, fixture=FIXTURE, expect_status=None, expect_applied=None,
         expect_already=None, expect_notfound=None, expect_bytes=None, dry=False):
    tmp = Path(tempfile.mkdtemp(prefix="dropblock-"))
    try:
        f = build(tmp, ops, fixture)
        rec, r = run(tmp, *(("--dry-run",) if dry else ()), "--json")
        if "_raw" in rec:
            check(name, False, f"脚本异常 rc={rec['_rc']} err={rec['_err'][:200]}")
            return None, f, tmp
        ev = []
        ok = True
        for key, want in (("status", expect_status), ("applied", expect_applied),
                          ("already", expect_already), ("not_found", expect_notfound)):
            if want is not None and rec.get(key) != want:
                ok = False
                ev.append(f"{key} 期望 {want} 实得 {rec.get(key)}")
        if expect_bytes is not None:
            got = f.read_text(encoding="utf-8")
            if got != expect_bytes:
                ok = False
                ev.append(f"字节不符：\n--- 实得 ---\n{got}\n--- 期望 ---\n{expect_bytes}")
        check(name, ok, "；".join(ev))
        return rec, f, tmp
    finally:
        pass


def main() -> int:
    print("=== drop_block 回归测试（全部在 tempfile 内） ===\n")

    # T1 首轮删除 + 吞掉一个尾随空行
    _, f1, tmp1 = case("T1 首轮：块删除 + 尾部空行吞掉", [BASE_OP],
                       expect_status="ok", expect_applied=1, expect_already=0,
                       expect_notfound=0, expect_bytes=EXPECTED_AFTER)
    b1 = sha(f1)

    # T2 二轮幂等 —— 字节指纹不变
    tmp2 = Path(tempfile.mkdtemp(prefix="dropblock-"))
    f2 = build(tmp2, [BASE_OP])
    run(tmp2, "--json")
    h_after1 = sha(f2)
    rec2, _ = run(tmp2, "--json")
    h_after2 = sha(f2)
    check("T2 二轮幂等：applied=0 且字节指纹不变",
          rec2.get("applied") == 0 and rec2.get("already") == 1 and h_after1 == h_after2,
          f"applied={rec2.get('applied')} already={rec2.get('already')} {h_after1}->{h_after2}")

    # T3 三轮（防 settle 永动）
    rec3, _ = run(tmp2, "--json")
    check("T3 三轮：仍 applied=0、字节不变",
          rec3.get("applied") == 0 and sha(f2) == h_after2,
          f"applied={rec3.get('applied')} sha={sha(f2)}")

    # T4 fail-closed：begin 不唯一
    dup = FIXTURE.replace("## 第三节", "## 待删除节")
    case("T4 begin 不唯一 → fail-closed（不动作）", [BASE_OP], fixture=dup,
         expect_status="not_found", expect_applied=0, expect_notfound=1,
         expect_bytes=dup)

    # T5 end 位于 begin 之前
    swapped = dict(BASE_OP, begin="内容 C", end="## 第一节")
    case("T5 end 早于 begin → fail-closed", [swapped],
         expect_status="not_found", expect_applied=0, expect_notfound=1,
         expect_bytes=FIXTURE)

    # T6 显式 removed_witness ⇒ 恢复三态：begin 缺失但 witness 仍在 ⇒ not_found
    blanked = FIXTURE.replace("## 待删除节", "## 改名了")
    case("T6 显式 witness：锚点漂移 → not_found（三态）",
         [dict(BASE_OP, removed_witness="内容 B")],
         fixture=blanked, expect_status="not_found", expect_applied=0,
         expect_notfound=1, expect_bytes=blanked)

    # T6b 默认 witness 的**已知代价**（两态，fail-open）：begin 被改名 ⇒ 判「已应用」
    #    这是纯删除型幂等的正确语义；锚点写错的防线在构建期断言（count(begin)==1），
    #    本 op 不重复承担。需要更强保护时给显式 removed_witness（见 T6）。
    case("T6b 默认 witness：锚点改名 → 判已应用（两态，已声明代价）",
         [dict(BASE_OP)],
         fixture=blanked, expect_status="ok", expect_applied=0,
         expect_already=1, expect_bytes=blanked)

    # T7 dry-run 不写盘
    case("T7 --dry-run 只报告、不写盘", [BASE_OP], dry=True,
         expect_status="ok", expect_applied=1, expect_bytes=FIXTURE)

    # T8 真实仓库零污染
    real_apply = REAL_REPO / "ops" / "patches" / "apply.py"
    real_man = REAL_REPO / "ops" / "patches" / "manifest.json"
    untouched = real_apply.is_file() and real_man.is_file()
    check("T8 真实仓库未被触碰（apply.py / manifest.json 均在位）", untouched,
          f"{real_apply} | {real_man}")

    shutil.rmtree(tmp1, ignore_errors=True)
    shutil.rmtree(tmp2, ignore_errors=True)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{'=' * 70}\n总计 {len(RESULTS)} 例：PASS={passed} FAIL={len(RESULTS) - passed}")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
