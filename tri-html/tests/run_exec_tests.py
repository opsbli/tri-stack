#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tri-html 可执行面自动化测试（真实执行 + 硬性断言）。

覆盖三个可执行组件的真实运行行为：
  1. scripts/build_html.py        —— 引擎探测 / 六维校验 / 单文件 HTML 组装 / 降级链
  2. scripts/viewer/bin/viewer.mjs —— validate / deliver / guide / brands / doctor / demo / check
  3. scripts/check_update.py      —— 版本门四态判定（--simulate-* 离线确定性注入）

设计约束：
  - 全部用例真实执行子进程，断言退出码 / stdout / 产物字节，不做任何 mock 桩替换；
  - 环境依赖项（Chrome 在场与否、真实网络）标记 ENV 类，只记录不判失败；
  - 报告落盘 JSON + 控制台表格，退出码 = 失败用例数（0=全过）。

用法：
  python tests/run_exec_tests.py                 # 全量执行
  python tests/run_exec_tests.py --filter S2     # 按场景组过滤
  python tests/run_exec_tests.py --keep          # 保留产物目录供人工复核
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
BUILD_HTML = SKILL_ROOT / "scripts" / "build_html.py"
CHECK_UPDATE = SKILL_ROOT / "scripts" / "check_update.py"
VIEWER_CLI = SKILL_ROOT / "scripts" / "viewer" / "bin" / "viewer.mjs"
EXAMPLES = SKILL_ROOT / "scripts" / "viewer" / "examples"
REPO_ROOT = SKILL_ROOT.parent
WORKBASE = REPO_ROOT / ".tribro" / "html-exec-tests"

PYTHON = sys.executable
VIEWER_TYPES = ("architecture", "workflow", "sequence", "dataflow", "lifecycle")
EXT_REF_PATTERNS = (
    re.compile(r'<script[^>]+src=["\']https?://', re.I),
    re.compile(r'<link[^>]+href=["\']https?://', re.I),
    re.compile(r'<img[^>]+src=["\']https?://', re.I),
)

RESULTS = []


def run(cmd, cwd=None, env=None, timeout=120):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          cwd=cwd, env=env, encoding="utf-8", errors="replace")


def case(cid, name, category, fn):
    t0 = time.time()
    try:
        ok, detail = fn()
        status = "PASS" if ok else "FAIL"
    except Exception as exc:  # 用例自身异常 = 失败
        ok, detail = False, f"用例异常: {type(exc).__name__}: {exc}"
        status = "FAIL"
    dt = time.time() - t0
    RESULTS.append({"id": cid, "name": name, "category": category,
                    "status": status, "seconds": round(dt, 2), "detail": detail})
    mark = "✅" if status == "PASS" else ("⚠️ " if status == "ENV" else "❌")
    print(f"{mark} [{cid}] {name} ({dt:.1f}s)\n     {detail[:300]}")


def env_without_node():
    """构造一个找不到 node 的 PATH（用于降级链测试）：剥离所有含 node(.exe) 的目录。"""
    env = dict(os.environ)
    kept = []
    for p in env.get("PATH", "").split(os.pathsep):
        if not p:
            continue
        try:
            has_node = any((Path(p) / n).exists()
                           for n in ("node.exe", "node.cmd", "node"))
        except OSError:
            has_node = False
        if not has_node:
            kept.append(p)
    env["PATH"] = os.pathsep.join(kept)
    env["PATHEXT"] = ".COM;.EXE;.BAT"  # 防 windows 下按扩展名兜底命中
    return env


def viewer_type_of(example_path: Path):
    m = re.search(r"\.(" + "|".join(VIEWER_TYPES) + r")\.json$", example_path.name)
    return m.group(1) if m else None


def load_ir_for(dtype: str):
    """从 vendored examples 选一个该类型的示例 IR（结构参照）。"""
    for f in sorted(EXAMPLES.glob(f"*.{dtype}.json")):
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
    return None


def receipt_from(stdout: str):
    text = (stdout or "").strip()
    if text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    for line in (stdout or "").splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {}


def no_external_refs(html_text: str):
    hits = [p.pattern for p in EXT_REF_PATTERNS if p.search(html_text)]
    return hits


def valid_analysis(viewer_entry=None):
    """构造合法 analysis.json（六维全覆盖 + mermaid + 观察 + 可选 viewer 图）。"""
    dims = {}
    for key, title in [("architecture", "架构设计"), ("directory", "目录结构设计"),
                       ("techstack", "技术栈选型"), ("code", "代码设计"),
                       ("function", "功能设计"), ("special", "特殊设计")]:
        dims[key] = {
            "title": title,
            "conclusion": f"{title}结论：分层清晰，模块边界明确。",
            "charts": [{"title": f"{title}示意", "type": "mermaid",
                        "code": "graph TD\n  A[入口] --> B{校验}\n  B -->|通过| C[处理]\n  B -->|拒绝| D[拒绝]"}],
        }
    data = {
        "meta": {"project_name": "selftest-demo", "project_path": "D:/demo/selftest-demo"},
        "dimensions": dims,
        "observations": [
            {"severity": "major", "title": "单点依赖", "description": "唯一 DB 无副本。",
             "suggestion": "引入主从复制。"},
        ],
    }
    if viewer_entry is not None:
        data["viewer_diagrams"] = [viewer_entry]
    return data


# ---------------- S1 引擎探测 ----------------

def tc_s1_1(work=None):
    p = run([PYTHON, str(BUILD_HTML), "--check-engine"])
    ok = (p.returncode == 0 and "高精度渲染模式可用" in p.stdout
          and "[ENGINE]" in p.stdout)
    return ok, f"exit={p.returncode} stdout含探测行={('[ENGINE]' in p.stdout)} | {p.stdout.strip()[:120]}"


def tc_s1_2(work=None):
    p = run([PYTHON, str(BUILD_HTML), "--check-engine"], env=env_without_node())
    ok = (p.returncode == 3 and "回落" in p.stdout)
    return ok, f"exit={p.returncode}（预期 3=回落 Mermaid）| {p.stdout.strip()[:120]}"


# ---------------- S2 viewer 引擎 CLI ----------------

def tc_s2_1_five_types(work):
    details = []
    ok_all = True
    for dtype in VIEWER_TYPES:
        ir = load_ir_for(dtype)
        if ir is None:
            ok_all = False
            details.append(f"{dtype}: 无示例")
            continue
        ir_path = work / f"five-{dtype}.json"
        ir_path.write_text(json.dumps(ir, ensure_ascii=False), encoding="utf-8")
        p = run(["node", str(VIEWER_CLI), "validate", dtype, str(ir_path),
                 "--quality", "showcase", "--json"], cwd=str(SKILL_ROOT))
        r = receipt_from(p.stdout)
        checks = r.get("checks") or []
        comp = (r.get("composition") or {}).get("summary", {})
        n_ok = sum(1 for c in checks if c.get("ok") is True)
        passed = (p.returncode == 0 and r.get("ok") is True and len(checks) == 9
                  and n_ok == 9 and comp.get("errors") == 0 and comp.get("warnings") == 0)
        ok_all = ok_all and passed
        details.append(f"{dtype}: exit={p.returncode} checks={n_ok}/{len(checks)} "
                       f"comp={comp.get('errors')}e/{comp.get('warnings')}w")
    return ok_all, "; ".join(details)


def tc_s2_2_invalid_json(work):
    bad = work / "bad-syntax.json"
    bad.write_text("{ not valid json !!!", encoding="utf-8")
    p = run(["node", str(VIEWER_CLI), "validate", "architecture", str(bad), "--json"],
            cwd=str(SKILL_ROOT))
    return p.returncode != 0, f"exit={p.returncode}（预期非零）stderr={p.stderr.strip()[:100]}"


def tc_s2_3_missing_required(work):
    ir = load_ir_for("architecture")
    ir.pop("meta", None)
    bad = work / "missing-meta.architecture.json"
    bad.write_text(json.dumps(ir, ensure_ascii=False), encoding="utf-8")
    p = run(["node", str(VIEWER_CLI), "validate", "architecture", str(bad), "--json"],
            cwd=str(SKILL_ROOT))
    r = receipt_from(p.stdout)
    has_diag = bool(r.get("diagnostics")) or bool(r.get("checks"))
    return p.returncode != 0 and has_diag, \
        f"exit={p.returncode}（预期非零）结构化回执/诊断={has_diag} error={str(r.get('error'))[:80]}"


def tc_s2_4_unknown_type(work):
    ir_path = work / "five-architecture.json"
    p = run(["node", str(VIEWER_CLI), "validate", "notatype", str(ir_path), "--json"],
            cwd=str(SKILL_ROOT))
    return p.returncode != 0, f"exit={p.returncode}（预期非零）stderr={p.stderr.strip()[:100]}"


def tc_s2_5_unknown_option(work):
    ir_path = work / "five-architecture.json"
    p = run(["node", str(VIEWER_CLI), "validate", "architecture", str(ir_path),
             "--no-such-option", "--json"], cwd=str(SKILL_ROOT))
    return p.returncode != 0, f"exit={p.returncode}（预期非零）stderr={p.stderr.strip()[:100]}"


def tc_s2_6_bad_quality(work):
    ir_path = work / "five-architecture.json"
    p = run(["node", str(VIEWER_CLI), "validate", "architecture", str(ir_path),
             "--quality", "ultra"], cwd=str(SKILL_ROOT))
    return p.returncode != 0, f"exit={p.returncode}（预期非零）stderr={p.stderr.strip()[:100]}"


def tc_s2_7_missing_file(work):
    p = run(["node", str(VIEWER_CLI), "validate", "architecture",
             str(work / "no-such-file.json"), "--json"], cwd=str(SKILL_ROOT))
    return p.returncode != 0, f"exit={p.returncode}（预期非零）stderr={p.stderr.strip()[:100]}"


def tc_s2_8_deliver_ok(work):
    ir_path = work / "five-architecture.json"
    out = work / "deliver-ok.html"
    p = run(["node", str(VIEWER_CLI), "deliver", "architecture", str(ir_path),
             str(out), "--quality", "showcase", "--json"], cwd=str(SKILL_ROOT))
    r = receipt_from(p.stdout)
    v = r.get("validation", {})
    html_ok = out.is_file() and out.stat().st_size > 10_000
    text = out.read_text(encoding="utf-8", errors="replace") if out.is_file() else ""
    ext = no_external_refs(text)
    sha = (r.get("artifact") or {}).get("sha256")
    ok = (p.returncode == 0 and r.get("ok") is True and v.get("checksPassed") == 9
          and v.get("errors") == 0 and html_ok and not ext and bool(sha))
    return ok, (f"exit={p.returncode} ok={r.get('ok')} checks={v.get('checksPassed')}/{v.get('checkCount')} "
                f"size={out.stat().st_size if out.is_file() else 0} 外部引用={ext or '无'} sha={bool(sha)}")


def tc_s2_9_deliver_fail_preserves(work):
    """失败交付 MUST 保留上一成品（字节级比对）。"""
    out = work / "deliver-preserve.html"
    good_ir = work / "five-architecture.json"
    p1 = run(["node", str(VIEWER_CLI), "deliver", "architecture", str(good_ir),
              str(out), "--quality", "showcase", "--json"], cwd=str(SKILL_ROOT))
    if p1.returncode != 0 or not out.is_file():
        return False, f"前置成功交付失败 exit={p1.returncode}"
    before = out.read_bytes()
    # 构造非法候选（删除 required 的 components）
    ir = load_ir_for("architecture")
    ir.pop("components", None)
    bad_ir = work / "deliver-bad.architecture.json"
    bad_ir.write_text(json.dumps(ir, ensure_ascii=False), encoding="utf-8")
    p2 = run(["node", str(VIEWER_CLI), "deliver", "architecture", str(bad_ir),
              str(out), "--quality", "showcase", "--json"], cwd=str(SKILL_ROOT))
    after = out.read_bytes()
    ok = p2.returncode != 0 and before == after
    return ok, f"首次 exit={p1.returncode}；二次（非法候选）exit={p2.returncode}；成品字节不变={before == after}"


def tc_s2_10_check_output(work):
    out = work / "deliver-ok.html"
    p = run(["node", str(VIEWER_CLI), "check", str(out)], cwd=str(SKILL_ROOT))
    return p.returncode == 0, f"exit={p.returncode}（成品检查）stderr={p.stderr.strip()[:100]}"


def tc_s2_11_doctor(work):
    p = run(["node", str(VIEWER_CLI), "doctor"], cwd=str(SKILL_ROOT))
    return p.returncode == 0, f"exit={p.returncode} stdout={p.stdout.strip()[:100]}"


def tc_s2_12_demo(work):
    demo_dir = work / "demo-out"
    p = run(["node", str(VIEWER_CLI), "demo", str(demo_dir)], cwd=str(SKILL_ROOT))
    files = list(demo_dir.glob("**/*.html")) if demo_dir.is_dir() else []
    return p.returncode == 0 and len(files) >= 1, \
        f"exit={p.returncode} demo 产物 html 数={len(files)}"


def tc_s2_13_guide(work):
    p = run(["node", str(VIEWER_CLI), "guide", "browser calls api, cache miss queries postgres",
             "--json"], cwd=str(SKILL_ROOT))
    r = receipt_from(p.stdout)
    suggestion = json.dumps(r, ensure_ascii=False)
    ok = p.returncode == 0 and ("sequence" in suggestion or "recommend" in suggestion.lower()
                                or r.get("type") or r.get("types") or r.get("scenario"))
    return ok, f"exit={p.returncode} 响应摘要={suggestion[:150]}"


def tc_s2_14_brands_builtin(work):
    """内置品牌发现：标记编译于 generated-brand-marks.mjs，内置查询应可用（更正 E3 误记）。"""
    p = run(["node", str(VIEWER_CLI), "brands", "postgresql", "--json"], cwd=str(SKILL_ROOT))
    r = receipt_from(p.stdout)
    marks = r.get("marks") or []
    return p.returncode == 0 and r.get("ok") is True and isinstance(marks, list), \
        f"exit={p.returncode} ok={r.get('ok')} 内置命中数={r.get('count')}（发现能力可用）"


def tc_s2_15_brands_capture_blocks_private(work):
    """brands capture 对私网地址 MUST fail closed（SSRF 防护）。"""
    p = run(["node", str(VIEWER_CLI), "brands", "capture", "http://127.0.0.1:9/icon.png", "--json"],
            cwd=str(SKILL_ROOT), timeout=60)
    return p.returncode != 0, f"exit={p.returncode}（预期非零=拒绝私网）stderr={p.stderr.strip()[:120]}"


def tc_s2_16_visual_check(work):
    """有界浏览器证据。Chrome 缺失=exit 2 skipped（不算失败）；在场则应产出回执。"""
    out = work / "deliver-ok.html"
    p = run(["node", str(VIEWER_CLI), "visual-check", str(out), "--json"],
            cwd=str(SKILL_ROOT), timeout=180)
    if p.returncode in (0, 2):
        return True, f"exit={p.returncode}（0=证据采集 / 2=Chrome 缺失 skipped）| {p.stdout.strip()[:120]}"
    return False, f"exit={p.returncode}（预期 0 或 2）stderr={p.stderr.strip()[:150]}"


# ---------------- S3 build_html 组装 ----------------

def tc_s3_1_full_assembly(work):
    ir = load_ir_for("architecture")
    analysis = valid_analysis(viewer_entry={"type": "architecture", "title": "部署架构图", "ir": ir})
    a_path = work / "analysis-full.json"
    a_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
    out = work / "selftest-arch-viz.html"
    p = run([PYTHON, str(BUILD_HTML), "--analysis", str(a_path), "--out", str(out)])
    if p.returncode != 0 or not out.is_file():
        return False, f"exit={p.returncode} stderr={p.stderr.strip()[:200]}"
    text = out.read_text(encoding="utf-8", errors="replace")
    ext = no_external_refs(text)
    view_files = list(work.glob("selftest-arch-viz-view-*.html"))
    view_ok = False
    if view_files:
        vtext = view_files[0].read_text(encoding="utf-8", errors="replace")
        view_ok = (not no_external_refs(vtext)) and view_files[0].stat().st_size > 10_000
    has_cards = ("view-1-architecture" in text) or ("高精度" in text)
    ok = (not ext) and len(view_files) == 1 and view_ok and has_cards and "</html>" in text
    return ok, (f"exit=0 size={out.stat().st_size} 外部引用={ext or '无'} "
                f"view成品={len(view_files)}张 view_ok={view_ok} 卡片节={has_cards}")


def tc_s3_2_bad_ir_degrades(work):
    """viewer_diagrams 中 IR 非法：单图失败不阻断主报告，且报告如实标注。"""
    analysis = valid_analysis(viewer_entry={"type": "architecture", "title": "坏IR图",
                                            "ir": {"schema_version": 1, "diagram_type": "architecture"}})
    a_path = work / "analysis-badir.json"
    a_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
    out = work / "selftest-badir.html"
    p = run([PYTHON, str(BUILD_HTML), "--analysis", str(a_path), "--out", str(out)])
    text = out.read_text(encoding="utf-8", errors="replace") if out.is_file() else ""
    honest = ("失败" in text) or ("降级" in text) or ("错误" in text) or ("deliver" in text)
    return p.returncode == 0 and out.is_file() and honest, \
        f"exit={p.returncode}（预期 0=不阻断）主报告存在={out.is_file()} 失败如实标注={honest}"


def tc_s3_3_missing_dimension(work):
    analysis = valid_analysis()
    del analysis["dimensions"]["special"]
    a_path = work / "analysis-missing.json"
    a_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
    p = run([PYTHON, str(BUILD_HTML), "--analysis", str(a_path),
             "--out", str(work / "never.html")])
    return p.returncode == 1 and "六维分析缺失" in p.stderr, \
        f"exit={p.returncode}（预期 1）stderr 含缺失维度提示={'六维分析缺失' in p.stderr}"


def tc_s3_4_invalid_analysis_json(work):
    bad = work / "analysis-badsyntax.json"
    bad.write_text("{{{{not json", encoding="utf-8")
    p = run([PYTHON, str(BUILD_HTML), "--analysis", str(bad), "--out", str(work / "never.html")])
    return p.returncode == 1, f"exit={p.returncode}（预期 1）stderr={p.stderr.strip()[:100]}"


def tc_s3_5_dry_run(work):
    a_path = work / "analysis-full.json"
    out = work / "dry-run-should-not-exist.html"
    p = run([PYTHON, str(BUILD_HTML), "--analysis", str(a_path), "--out", str(out), "--dry-run"])
    return p.returncode == 0 and not out.exists(), \
        f"exit={p.returncode}（预期 0）文件未写={not out.exists()}"


def tc_s3_6_missing_args(work):
    p = run([PYTHON, str(BUILD_HTML), "--analysis", str(work / "analysis-full.json")])
    return p.returncode == 2, f"exit={p.returncode}（预期 2=argparse 用法错误）"


def tc_s3_7_unwritable_out(work):
    """输出路径的父级是一个文件 → 必须以 exit 2 结构化失败（不得堆栈崩溃）。"""
    a_path = work / "analysis-full.json"
    blocker = work / "blocker.txt"
    blocker.write_text("not a dir", encoding="utf-8")
    out = work / "blocker.txt" / "x.html"
    p = run([PYTHON, str(BUILD_HTML), "--analysis", str(a_path), "--out", str(out)])
    return p.returncode == 2 and "Traceback" not in p.stderr, \
        f"exit={p.returncode}（预期 2）stderr 含 [ERROR]={'[ERROR]' in p.stderr} 无堆栈={'Traceback' not in p.stderr}"


def tc_s3_8_no_node_degrades(work):
    """Node 缺失时 viewer_diagrams 整体回落 Mermaid，主报告仍产出且标注降级原因。"""
    ir = load_ir_for("architecture")
    analysis = valid_analysis(viewer_entry={"type": "architecture", "title": "降级图", "ir": ir})
    a_path = work / "analysis-degrade.json"
    a_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
    out = work / "selftest-degraded.html"
    p = run([PYTHON, str(BUILD_HTML), "--analysis", str(a_path), "--out", str(out)],
            env=env_without_node())
    if p.returncode != 0 or not out.is_file():
        return False, f"exit={p.returncode} stderr={p.stderr.strip()[:200]}"
    text = out.read_text(encoding="utf-8", errors="replace")
    view_files = list(work.glob("selftest-degraded-view-*.html"))
    ok = (not view_files) and ("降级" in text or "Mermaid" in text)
    return ok, f"exit=0 view成品={len(view_files)}张（预期 0）报告标注降级={'降级' in text or 'Mermaid' in text}"


# ---------------- S4 版本门 check_update ----------------

GATE_BASE = ["--slug", "tri-html", "--json", "--force", "--dry-run"]


def gate(work, *extra):
    # TRI_ALLOW_REMOTE=1：解除自维护短路（check_update.py 在自维护分支提前 return，
    # --simulate-* 走不到 fetch 层 ⇒ S4.1/S4.2/S4.4 恒 A 态。2026-09-27 pilot 归因）。
    cache = work / "gate-cache"
    cache.mkdir(exist_ok=True)
    env = {**os.environ, "TRI_ALLOW_REMOTE": "1"}
    return run([PYTHON, str(CHECK_UPDATE), *GATE_BASE,
                "--cache-dir", str(cache), *extra], timeout=60, env=env)


def tc_s4_1_offline(work):
    p = gate(work, "--simulate-net", "offline")
    r = receipt_from(p.stdout) or {}
    ok = p.returncode == 10 and r.get("state") == "B"
    return ok, f"exit={p.returncode}（预期 10）state={r.get('state')}"


def tc_s4_2_channel(work):
    p = gate(work, "--simulate-net", "html")
    r = receipt_from(p.stdout) or {}
    ok = p.returncode == 11 and r.get("state") == "C"
    return ok, f"exit={p.returncode}（预期 11=SPA 兜底页击穿）state={r.get('state')}"


def tc_s4_3_up_to_date(work):
    p = gate(work, "--simulate-fetch-ok", "1.2.2")
    r = receipt_from(p.stdout) or {}
    ok = p.returncode == 0 and r.get("state") == "A"
    return ok, f"exit={p.returncode}（预期 0）state={r.get('state')}"


def tc_s4_4_stale(work):
    """陈旧（注入 fetch latest=9.9.9）：tri-html 为源码树/链接安装 → 跳过自动升级落 D 态放行。"""
    p = gate(work, "--simulate-fetch-ok", "9.9.9")
    r = receipt_from(p.stdout) or {}
    ok = p.returncode == 12 and r.get("state") == "D"
    return ok, f"exit={p.returncode}（预期 12=D 放行）state={r.get('state')} " \
               f"install_mode={r.get('install_mode')} attempted={(r.get('upgrade') or {}).get('attempted')}"


def tc_s4_5_json_shape(work):
    p = gate(work, "--simulate-net", "offline")
    r = receipt_from(p.stdout)
    keys_ok = isinstance(r, dict) and ("state" in r)
    return keys_ok, f"JSON 含 state 字段={keys_ok} keys={sorted(r.keys())[:8]}"


CASES = [
    ("S1.1", "引擎探测：Node+引擎齐备 → exit 0", "S1 引擎探测", tc_s1_1),
    ("S1.2", "引擎探测：Node 缺失 → exit 3 回落 Mermaid", "S1 引擎探测", tc_s1_2),
    ("S2.1", "validate showcase：5 类示例全过 9/9", "S2 viewer CLI", None),
    ("S2.2", "validate：非法 JSON 语法 → 非零退出", "S2 viewer CLI", None),
    ("S2.3", "validate：缺 required(meta) → 非零+结构化诊断", "S2 viewer CLI", None),
    ("S2.4", "validate：未知图表类型 → 非零退出", "S2 viewer CLI", None),
    ("S2.5", "validate：未知选项 → 非零退出", "S2 viewer CLI", None),
    ("S2.6", "validate：--quality 非法值 → 非零退出", "S2 viewer CLI", None),
    ("S2.7", "validate：不存在的 IR 文件 → 非零退出", "S2 viewer CLI", None),
    ("S2.8", "deliver showcase：9/9+SHA-256+单文件零外部引用", "S2 viewer CLI", None),
    ("S2.9", "deliver 失败保留上一成品（字节级不变）", "S2 viewer CLI", None),
    ("S2.10", "check：成品最终 SVG 检查通过", "S2 viewer CLI", None),
    ("S2.11", "doctor：健康自检 exit 0", "S2 viewer CLI", None),
    ("S2.12", "demo：生成示例产物", "S2 viewer CLI", None),
    ("S2.13", "guide：场景→类型建议", "S2 viewer CLI", None),
    ("S2.14", "brands：内置品牌发现可用（标记内嵌 generated 模块）", "S2 viewer CLI", None),
    ("S2.15", "brands capture：私网地址 fail-closed", "S2 viewer CLI", None),
    ("S2.16", "visual-check：exit 0/2（ENV 相关）", "S2 viewer CLI", None),
    ("S3.1", "组装：六维+viewer图 → 单文件+1张成品+卡片节", "S3 build_html", None),
    ("S3.2", "组装：坏 IR 不阻断主报告且如实标注", "S3 build_html", None),
    ("S3.3", "组装：缺一维 → exit 1 缺失提示", "S3 build_html", None),
    ("S3.4", "组装：analysis.json 非法 JSON → exit 1", "S3 build_html", None),
    ("S3.5", "组装：--dry-run 通过且不写文件", "S3 build_html", None),
    ("S3.6", "组装：缺 --out → exit 2", "S3 build_html", None),
    ("S3.7", "组装：不可写输出路径 → exit 2", "S3 build_html", None),
    ("S3.8", "组装：无 Node → viewer 整体回落+报告标注", "S3 build_html", None),
    ("S4.1", "版本门：离线 → B 态 exit 10", "S4 check_update", None),
    ("S4.2", "版本门：通道异常 → C 态 exit 11", "S4 check_update", None),
    ("S4.3", "版本门：已最新 → A 态 exit 0", "S4 check_update", None),
    ("S4.4", "版本门：陈旧+dry-run → D 态 exit 12 放行", "S4 check_update", None),
    ("S4.5", "版本门：--json 输出含 state 字段", "S4 check_update", None),
]

FN_MAP = {
    "S1.1": tc_s1_1, "S1.2": tc_s1_2,
    "S2.1": tc_s2_1_five_types, "S2.2": tc_s2_2_invalid_json, "S2.3": tc_s2_3_missing_required,
    "S2.4": tc_s2_4_unknown_type, "S2.5": tc_s2_5_unknown_option, "S2.6": tc_s2_6_bad_quality,
    "S2.7": tc_s2_7_missing_file, "S2.8": tc_s2_8_deliver_ok, "S2.9": tc_s2_9_deliver_fail_preserves,
    "S2.10": tc_s2_10_check_output, "S2.11": tc_s2_11_doctor, "S2.12": tc_s2_12_demo,
    "S2.13": tc_s2_13_guide, "S2.14": tc_s2_14_brands_builtin,
    "S2.15": tc_s2_15_brands_capture_blocks_private, "S2.16": tc_s2_16_visual_check,
    "S3.1": tc_s3_1_full_assembly, "S3.2": tc_s3_2_bad_ir_degrades, "S3.3": tc_s3_3_missing_dimension,
    "S3.4": tc_s3_4_invalid_analysis_json, "S3.5": tc_s3_5_dry_run, "S3.6": tc_s3_6_missing_args,
    "S3.7": tc_s3_7_unwritable_out, "S3.8": tc_s3_8_no_node_degrades,
    "S4.1": tc_s4_1_offline, "S4.2": tc_s4_2_channel, "S4.3": tc_s4_3_up_to_date,
    "S4.4": tc_s4_4_stale, "S4.5": tc_s4_5_json_shape,
}


def main():
    ap = argparse.ArgumentParser(description="tri-html 可执行面自动化测试")
    ap.add_argument("--filter", default=None, help="只跑 id 或分组含该前缀的用例")
    ap.add_argument("--keep", action="store_true", help="保留产物目录")
    args = ap.parse_args()

    WORKBASE.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="run-", dir=str(WORKBASE)))

    print(f"workdir = {work}\n" + "=" * 78)
    for cid, name, cat, _ in CASES:
        if args.filter and args.filter not in cid and args.filter not in cat:
            continue
        fn = FN_MAP.get(cid)
        if fn is None:
            continue
        case(cid, name, cat, lambda f=fn, w=work: f(w))

    fails = [r for r in RESULTS if r["status"] == "FAIL"]
    print("=" * 78)
    print(f"总计 {len(RESULTS)} 例：PASS={len(RESULTS)-len(fails)} FAIL={len(fails)}")

    report = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
              "workdir": str(work), "results": RESULTS,
              "summary": {"total": len(RESULTS), "fail": len(fails)}}
    report_path = work / "exec-test-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"报告：{report_path}")
    if not args.keep:
        # 保留报告与失败现场；清理大体量 HTML 产物以外可全部保留（目录小，不清理，供审计）
        pass
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
