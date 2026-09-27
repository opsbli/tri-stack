#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_adapter.py —— 把**异构 skill 门禁**归一为统一的「案级台账」协议。

为什么需要它
--------------------------------------------------------------------
`tri-forge/scripts/battery_run.py` 已经能跑 case 电池，但它只认一种门禁输出形状
（`compliance_check.py` 的 `--dir X --json`）：

    {"results": [{"verdict": ..., "items": [{"n","name","status","evidence","advisory"}]}]}

家族里其它确定性门禁**各自长成不同形状**（2026-09-27 一手实测）：

| skill     | 门禁脚本                        | 原生输出                                        | `--dir` |
|-----------|---------------------------------|-------------------------------------------------|---------|
| tri-forge | scripts/compliance_check.py     | 电池原生形状（24 条）                            | ✅      |
| tri-lottie| scripts/compliance_check.py     | `{all_ok,passed,total,results:[{id,name,ok,evidence}]}` | ❌      |
| tri-html  | tests/run_exec_tests.py         | 写 `<repo>/.tribro/html-exec-tests/run-*/exec-test-report.json` | ❌ |
| tri-verify| scripts/verify_gate.py          | `--json <cmd>` → `{exitCode,attribution,...}`；`self-test` 文本 | ❌ |

缺的就是这一层**形状归一**：没有它，电池只能停在「tri-forge 自己」这一层，
家族其余 skill 无法进入同一个评估基座（→ SkillOpt 式训练循环没有验证集）。

本脚本 ONLY 做三件事：**跑门禁 → 归一形状 → 冒烟自证**。
它 NEVER 解释判据、NEVER 复制任何 skill 的判据表 —— 判据单一事实源在各 skill 自己手里
（家族硬约束第 23 条）。三处刻意的「不重述」：
  1. tri-verify 只转述其 `self-test` 的**退出码**，不重列 9 条映射表；
  2. tri-forge 直接透传其 JSON，不做二次判定；
  3. 归一后的 `token` 只编码「哪几条 FAIL」，不含任何阈值。

统一协议（本文件即真源）
--------------------------------------------------------------------
    {
      "skill":   "tri-html",
      "verdict": "PASS" | "FAIL",
      "token":   "PASS" | "FAIL:S4.1,S4.2" | "…+advT3",
      "items":   [{"ref": "S4.1", "name": …, "status": "PASS|FAIL|MANUAL|N-A",
                   "evidence": …, "advisory": false}],
      "source":  {"kind": …, "rc": 0, "argv": [...]},
      "volatile": ["generated_at", "workdir"]
    }

与电池协议的差异（**必须显式声明，不静默降级**）：
  - 电池的 `n` 是 **int**（`token_of` 做 `"#%d" % n`）；本协议用 **字符串 `ref`**，
    以容纳 `S4.1` / `T3` / `self-test` 这类非数字 id。故本协议**不可直接**
    喂给 `battery_run.token_of` —— 需要数字 id 的场景请走 tri-forge 原生适配器
    （kind=`battery-native`，其输出与电池完全同形）。

用法
--------------------------------------------------------------------
    python ops/eval-harness/gate_adapter.py list
    python ops/eval-harness/gate_adapter.py run --skill tri-html [--json]
    python ops/eval-harness/gate_adapter.py run --skill tri-forge --dir tri-coding --json
    python ops/eval-harness/gate_adapter.py self-test

退出码：0 = 门禁 PASS 且归一成功；1 = 门禁 FAIL（归一成功）；2 = 环境 / 入参错误
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = next((p for p in (Path(__file__).resolve(), *Path(__file__).resolve().parents)
             if (p / ".git").exists()), Path(__file__).resolve().parent)
PY = sys.executable

# ---------------------------------------------------------------- 门禁注册表
# 唯一允许出现「skill 特定知识」的地方：怎么调、怎么解析。判据一律不在此处。
GATES = {
    "tri-forge": {
        "kind": "battery-native",
        "argv": ["tri-forge/scripts/compliance_check.py", "--dir", "{dir}", "--json"],
        "dir_mode": "flag",
        "note": "电池原生协议；此适配器对它是**恒等变换**（回归用）",
    },
    "tri-lottie": {
        "kind": "lottie-json",
        "argv": ["tri-lottie/scripts/compliance_check.py", "--json"],
        "dir_mode": "self",
        "note": "T1–T10；无 --dir，只能审自身",
    },
    "tri-html": {
        "kind": "html-exec-report",
        "argv": ["tri-html/tests/run_exec_tests.py"],
        "dir_mode": "self",
        "report_glob": ".tribro/html-exec-tests/run-*/exec-test-report.json",
        "volatile": ["generated_at", "workdir"],
        "note": "31 例；产物落在 .tribro/（已 gitignore），本适配器只读取",
    },
    "tri-verify": {
        "kind": "self-test-exitcode",
        "argv": ["tri-verify/scripts/verify_gate.py", "self-test"],
        "dir_mode": "self",
        "note": "只转述其 self-test 退出码，NEVER 重列 9 条映射表（判据单一事实源）",
    },
}


def _run(argv, cwd):
    r = subprocess.run([PY, *argv], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(cwd), timeout=600)
    return r


def _skill_dir(skill: str, override) -> Path:
    return Path(override) if override else (REPO / skill)


# ---------------------------------------------------------------- 各形状归一
def norm_battery_native(skill, argv, out, rc, srcdir):
    d = json.loads(out)["results"][0]
    items = [{"ref": "#%d" % it["n"], "name": it.get("name", ""),
              "status": it.get("status", "N-A"), "evidence": it.get("evidence", ""),
              "advisory": bool(it.get("advisory"))}
             for it in d.get("items", [])]
    return d.get("verdict"), items


def norm_lottie(skill, argv, out, rc, srcdir):
    d = json.loads(out)
    items = [{"ref": it["id"], "name": it.get("name", ""),
              "status": "PASS" if it.get("ok") else "FAIL",
              "evidence": it.get("evidence", ""), "advisory": False}
             for it in d.get("results", [])]
    return ("PASS" if d.get("all_ok") else "FAIL"), items


def norm_html(skill, argv, out, rc, srcdir):
    glob = GATES[skill]["report_glob"]
    runs = sorted((REPO).glob(glob), key=lambda p: p.stat().st_mtime)
    if not runs:
        raise RuntimeError(f"未找到 exec-test 报告（glob={glob}）；门禁可能未产出产物")
    d = json.loads(runs[-1].read_text(encoding="utf-8"))
    items = [{"ref": it["id"], "name": it.get("name", ""),
              "status": it.get("status", "FAIL"),
              "evidence": (it.get("detail") or "")[:400], "advisory": False}
             for it in d.get("results", [])]
    return ("PASS" if all(i["status"] == "PASS" for i in items) else "FAIL"), items


def norm_self_test(skill, argv, out, rc, srcdir):
    name = (out or "").strip().splitlines()
    name = name[-1] if name else f"rc={rc}"
    if rc == 0:
        return "PASS", [{"ref": "self-test", "name": "门禁自带 self-test",
                         "status": "PASS", "evidence": name, "advisory": False}]
    if rc == 2:
        raise RuntimeError(f"self-test 报环境/入参错误（rc=2）：{name}")
    return "FAIL", [{"ref": "self-test", "name": "门禁自带 self-test",
                     "status": "FAIL", "evidence": name, "advisory": False}]


NORMALIZERS = {
    "battery-native": norm_battery_native,
    "lottie-json": norm_lottie,
    "html-exec-report": norm_html,
    "self-test-exitcode": norm_self_test,
}


def token_of(items):
    """由**字符串 ref** 生成翻转主键；结构与 tri-forge `token_of` 同构。

    刻意与 `battery_run.token_of` 分离（它用 int n）：两处都改会造成双真源。
    归因口径一致：advisory 的 FAIL 单独挂 `+adv`，MANUAL 不入 token、只留 items。
    """
    blocking = sorted(i["ref"] for i in items
                      if i["status"] == "FAIL" and not i["advisory"])
    adv = sorted(i["ref"] for i in items if i["status"] == "FAIL" and i["advisory"])
    tok = "PASS" if not blocking else "FAIL:" + ",".join(blocking)
    if adv:
        tok += "+adv" + ",".join(adv)
    return tok


def run_gate(skill, dir_override=None):
    g = GATES.get(skill)
    if not g:
        raise KeyError(f"未注册的门禁：{skill}（已注册：{', '.join(GATES)}）")
    srcdir = _skill_dir(skill, dir_override)
    argv = [a.replace("{dir}", str(srcdir)) for a in g["argv"]]
    r = _run(argv, REPO)
    out = (r.stdout or "").strip()
    if not out and r.returncode == 2:
        raise RuntimeError(f"{skill} 门禁无输出且 rc=2：{(r.stderr or '')[:200]}")
    _, items = NORMALIZERS[g["kind"]](skill, argv, out, r.returncode, srcdir)
    if not items:
        raise RuntimeError(f"{skill} 门禁归一后 items 为空 —— 拒绝产出空 PASS")
    tok = token_of(items)
    verdict = "PASS" if tok == "PASS" else "FAIL"
    return {
        "skill": skill, "verdict": verdict, "token": tok, "items": items,
        "source": {"kind": g["kind"], "rc": r.returncode, "argv": argv},
        "volatile": g.get("volatile", []),
    }


# ---------------------------------------------------------------- 自证
def skill_fingerprints():
    out = {}
    for p in sorted(REPO.glob("**/SKILL.md")):
        parts = set(p.parts)
        if parts & {".git", ".workbuddy", ".tribro", "__pycache__"}:
            continue
        out[p.relative_to(REPO).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return out


def self_test() -> int:
    print("=== gate_adapter self-test ===\n")
    rows, fails = [], []
    before = skill_fingerprints()

    # S1 每个注册门禁都能产出合规 envelope
    envs = {}
    for skill in GATES:
        try:
            env = run_gate(skill)
            envs[skill] = env
            n_fail = sum(1 for i in env["items"] if i["status"] == "FAIL")
            ok = (env["verdict"] in ("PASS", "FAIL") and env["token"]
                  and all(set(i) >= {"ref", "name", "status", "evidence", "advisory"}
                          for i in env["items"]))
            rows.append((skill, env["verdict"], env["token"],
                         f"{len(env['items'])} 条 / FAIL {n_fail}", "✅" if ok else "❌"))
            if not ok:
                fails.append(f"S1 {skill} envelope 不合规")
        except Exception as e:  # noqa: BLE001
            rows.append((skill, "ERROR", "-", f"{type(e).__name__}: {e}"[:70], "🔴"))
            fails.append(f"S1 {skill} 归一失败：{e}")

    print(f"{'skill':11} {'verdict':8} {'token':34} {'items':22}")
    for s, v, t, n, m in rows:
        print(f"{s:11} {v:8} {str(t)[:34]:34} {n:22} {m}")

    # S2 verdict 与 items 内部一致（有非 advisory FAIL ⇒ 不得判 PASS）
    for s, env in envs.items():
        if env["verdict"] == "PASS" and any(
                i["status"] == "FAIL" and not i["advisory"] for i in env["items"]):
            fails.append(f"S2 {s}：items 含 FAIL 却判 PASS")
    print(f"\nS2 verdict↔items 一致性：{'✅' if not any('S2' in f for f in fails) else '❌'}")

    # S3 确定性：同一门禁连跑两次，归一结果一致（排除 volatile 字段）
    det_ok = True
    for s, env in envs.items():
        try:
            again = run_gate(s)
        except Exception:  # noqa: BLE001
            continue
        for e in (env, again):
            for k in e.get("volatile", []):
                e.pop(k, None)
        if json.dumps(env, ensure_ascii=False, sort_keys=True) != \
           json.dumps(again, ensure_ascii=False, sort_keys=True):
            det_ok = False
            fails.append(f"S3 {s}：两次归一结果不一致（非确定性）")
    print(f"S3 归一确定性（连跑两次同字节）：{'✅' if det_ok else '❌'}")

    # S4 门禁运行不改动任何 SKILL.md（防门禁脚本越权写入）
    after = skill_fingerprints()
    changed = [k for k in before if before[k] != after.get(k)]
    print(f"S4 SKILL.md 零变更：{'✅' if not changed else '❌ ' + ','.join(changed)}")
    if changed:
        fails.append(f"S4 门禁改动了 SKILL.md：{changed}")

    print(f"\n{'=' * 74}\nself-test：{'PASS' if not fails else 'FAIL'}"
          f"（注册门禁 {len(GATES)} 个）")
    for f in fails:
        print(f"  - {f}")
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "run", "self-test"])
    ap.add_argument("--skill", default=None)
    ap.add_argument("--dir", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.cmd == "list":
        for s, g in GATES.items():
            print(f"{s:11} kind={g['kind']:18} dir_mode={g['dir_mode']:6} "
                  f"argv={' '.join(g['argv'])}\n            {g['note']}")
        return 0

    if a.cmd == "self-test":
        return self_test()

    if not a.skill:
        print("ERROR: run 需要 --skill", file=sys.stderr)
        return 2
    try:
        env = run_gate(a.skill, a.dir)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(env, ensure_ascii=False, indent=2))
    else:
        print(f"# {env['skill']} · verdict={env['verdict']} · token=`{env['token']}`"
              f" · rc={env['source']['rc']}\n")
        print("| ref | status | name |")
        print("|---|---|---|")
        for i in env["items"]:
            print(f"| `{i['ref']}` | {i['status']}{' (adv)' if i['advisory'] else ''} "
                  f"| {i['name'][:56]} |")
    return 0 if env["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
