#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「智引」(tri-geo) 离线验收脚本 —— 覆盖设计指南 §4.3 的 T1/T2/T4/T5

覆盖范围：
    T1 单元与管线冒烟：9 个脚本均以固定夹具执行，校验退出码与关键字段
    T2 确定性回归：site_signal.py 同输入重复运行，输出必须逐字节一致
    T4 重写 A/B：good 稿通过、bad 稿不通过且红线命中
    T5 红线注入：捏造来源命中 → 硬阻断（退出码 3）

未覆盖（需真机环境，设计指南 §4.3）：
    T3 双样本实测（需真实站点）、T6 国内四引擎实测（需引擎会话/接口）
    ——由开发者在具备网络与引擎访问的环境按 references/ 与 SKILL.md 流程执行

用法：
    python tests/verify_tri_geo.py
    python tests/verify_tri_geo.py --keep   # 保留临时产物

退出码：0 全部通过；1 存在失败；64 环境错误
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
FIX = ROOT / "tests" / "fixtures"
RUN = ROOT / ".tribro" / "tri-geo" / "test-run"

PY = sys.executable


def run(args: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    p = subprocess.run([PY] + args, cwd=str(cwd or ROOT), capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr


def jout(out: str) -> Dict[str, Any]:
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {}


CASES: List[Dict[str, Any]] = []


def check(case_id: str, name: str, ok: bool, detail: str = "") -> None:
    CASES.append({"id": case_id, "name": name, "ok": bool(ok), "detail": detail})
    print(f"{'[PASS]' if ok else '[FAIL]'} {case_id} {name}" + (f" — {detail}" if detail else ""))


def main() -> int:
    ap = argparse.ArgumentParser(description="「智引」离线验收（T1/T2/T4/T5）")
    ap.add_argument("--keep", action="store_true", help="保留临时产物")
    args = ap.parse_args()

    if RUN.exists():
        shutil.rmtree(RUN, ignore_errors=True)
    RUN.mkdir(parents=True, exist_ok=True)

    # ---------------- T1：管线冒烟 ----------------
    rc, out, err = run([str(SCRIPTS / "validate_input.py"), "--url", "example.com",
                        "--brand", "智引", "--mode", "audit", "--json"])
    d = jout(out)
    check("T1-01", "validate_input 合法输入", rc == 0 and d.get("ok") is True,
          f"exit={rc} domain={d.get('params', {}).get('target', {}).get('domain')}")

    rc, out, _ = run([str(SCRIPTS / "validate_input.py"), "--mode", "cn_fit", "--json"])
    d = jout(out)
    check("T1-02", "validate_input 缺必填项 → 退出码 1",
          rc == 1 and bool(d.get("missing_required")), f"missing={d.get('missing_required')}")

    rc, out, _ = run([str(SCRIPTS / "validate_input.py"), "--url", "这不是网址",
                      "--mode", "quick", "--json"])
    check("T1-03", "validate_input 非法 URL → 退出码 2", rc == 2, f"exit={rc}")

    good_json = RUN / "good.json"
    rc, out, _ = run([str(SCRIPTS / "fetch_page.py"), "--file",
                      str(FIX / "good-page.html"), "--out", str(good_json), "--json"])
    gd = jout(out)
    check("T1-04", "fetch_page 解析优样本", rc == 0 and len(gd.get("blocks", [])) >= 3,
          f"blocks={len(gd.get('blocks', []))} chars={gd.get('stats', {}).get('body_text_chars')}")

    bad_json = RUN / "bad.json"
    rc, out, _ = run([str(SCRIPTS / "fetch_page.py"), "--file",
                      str(FIX / "bad-page.html"), "--out", str(bad_json), "--json"])
    bd = jout(out)
    check("T1-05", "fetch_page 解析劣样本（正文稀薄）",
          rc in (0, 3) and (bd.get("stats", {}).get("body_text_chars", 0) or 0) < 300,
          f"chars={bd.get('stats', {}).get('body_text_chars')} exit={rc}")

    good_score = RUN / "good-score.json"
    rc, out, _ = run([str(SCRIPTS / "site_signal.py"), "--content", str(good_json),
                      "--out", str(good_score), "--json"])
    gs = jout(out)
    g_total = (gs.get("score") or {}).get("total")
    check("T1-06", "site_signal 优样本评分", rc == 0 and isinstance(g_total, int),
          f"total={g_total} pillars={(gs.get('score') or {}).get('pillars')}")

    # ---------------- T2：确定性回归 ----------------
    rc2, out2, _ = run([str(SCRIPTS / "site_signal.py"), "--content", str(good_json), "--json"])
    check("T2-01", "site_signal 同输入逐字节一致", rc2 == 0 and out2 == out,
          "两次运行输出完全一致" if out2 == out else "输出不一致（确定性失败）")

    bad_score = RUN / "bad-score.json"
    rc, out, _ = run([str(SCRIPTS / "site_signal.py"), "--content", str(bad_json),
                      "--out", str(bad_score), "--json"])
    bs = jout(out)
    b_total = (bs.get("score") or {}).get("total")
    check("T2-02", "劣样本评分显著低于优样本",
          isinstance(b_total, int) and isinstance(g_total, int) and b_total < g_total,
          f"good={g_total} bad={b_total}")

    # ---------------- T4：重写 A/B ----------------
    rc, out, _ = run([str(SCRIPTS / "writing_rules.py"), "--file",
                      str(FIX / "rewrite-good.md"), "--target-query", "GEO 是什么",
                      "--out", str(RUN / "rules-good.json"), "--json"])
    rg = jout(out)
    check("T4-01", "writing_rules 优稿通过", rc == 0 and rg.get("pass") is True,
          f"exit={rc} pass={rg.get('pass')}")

    rc, out, _ = run([str(SCRIPTS / "writing_rules.py"), "--file",
                      str(FIX / "rewrite-bad.md"), "--out", str(RUN / "rules-bad.json"), "--json"])
    rb = jout(out)
    check("T4-02", "writing_rules 劣稿打回（红线：广告法禁用语）",
          rc == 3 and rb.get("redline_hit") is True,
          f"exit={rc} redline={rb.get('redline_hit')} fails={len([c for c in rb.get('checks', []) if c.get('status') == 'fail'])}")

    # ---------------- T5：红线注入 ----------------
    rc, out, _ = run([str(SCRIPTS / "citation_check.py"), "--file",
                      str(FIX / "rewrite-good.md"), "--sources",
                      str(FIX / "sources-verified.json"), "--offline",
                      "--out", str(RUN / "cite-ok.json"), "--json"])
    cv = jout(out)
    check("T5-01", "citation_check 真实来源核验通过", rc == 0,
          f"exit={rc} summary={cv.get('summary')}")

    rc, out, _ = run([str(SCRIPTS / "citation_check.py"), "--file",
                      str(FIX / "rewrite-good.md"), "--sources",
                      str(FIX / "sources-fake.json"), "--offline",
                      "--out", str(RUN / "cite-fake.json"), "--json"])
    cf = jout(out)
    check("T5-02", "citation_check 捏造来源 → 硬阻断（退出码 3）",
          rc == 3 and cf.get("blocked") is True, f"exit={rc} summary={cf.get('summary')}")

    rc, out, _ = run([str(SCRIPTS / "citation_check.py"), "--file",
                      str(FIX / "rewrite-bad.md"), "--offline",
                      "--out", str(RUN / "cite-unsourced.json"), "--json"])
    cu = jout(out)
    check("T5-03", "citation_check 无来源数据句 → 阻断",
          rc == 3 and len(cu.get("unsourced_claims", [])) > 0,
          f"exit={rc} unsourced={len(cu.get('unsourced_claims', []))}")

    # ---------------- T1：实测与快照管线 ----------------
    probe_dir = RUN / "probe"
    shutil.copytree(FIX / "answers", probe_dir, dirs_exist_ok=True)
    rc, out, _ = run([str(SCRIPTS / "probe_runner.py"), "plan", "--brand", "格力",
                      "--product-type", "空调", "--engines", "deepseek,doubao",
                      "--rounds", "1", "--out-dir", str(RUN / "snap" / "格力")])
    pl = jout(out)
    check("T1-07", "probe_runner plan 生成任务清单", rc == 0 and pl.get("total_tasks", 0) > 0,
          f"tasks={pl.get('total_tasks')}")

    rc, out, _ = run([str(SCRIPTS / "probe_runner.py"), "ingest", "--out-dir",
                      str(RUN / "snap" / "格力"), "--engine", "deepseek", "--prompt-id", "P01",
                      "--round", "1", "--file", str(probe_dir / "deepseek" / "P01-r1.txt"),
                      "--source-type", "session"])
    check("T1-08", "probe_runner ingest 回填回答", rc == 0, f"exit={rc}")

    rc, out, _ = run([str(SCRIPTS / "probe_runner.py"), "status", "--out-dir",
                      str(RUN / "snap" / "格力")])
    st = jout(out)
    check("T1-09", "probe_runner status 统计完成度", rc == 0 and st.get("filled", 0) >= 1,
          f"filled={st.get('filled')}/{st.get('total')}")

    rc, out, _ = run([str(SCRIPTS / "answer_judge.py"), "--probe-dir", str(probe_dir),
                      "--brand", "格力", "--aliases", "格力电器,GREE", "--domains", "gree.com",
                      "--out", str(RUN / "judge.json"), "--json"])
    jd = jout(out)
    mentioned = {r["prompt_id"]: r["mentioned"] for r in jd.get("rows", []) if r["engine"] == "deepseek"}
    check("T1-10", "answer_judge 提及判定（P01 命中 / P02 不误判）",
          rc == 0 and mentioned.get("P01") is True and mentioned.get("P02") is False,
          f"deepseek={mentioned}")

    rc, out, _ = run([str(SCRIPTS / "answer_judge.py"), "--probe-dir", str(probe_dir),
                      "--brand", "格力", "--domains", "gree.com", "--json"])
    jd2 = jout(out) if rc == 0 else {}
    interval = (jd2.get("overall") or {}).get("sampling", {})
    check("T1-11", "answer_judge 输出采样轮数与波动区间",
          rc == 0 and "rounds" in interval and "ci_low" in interval,
          f"sampling={interval}")

    rc, out, _ = run([str(SCRIPTS / "snapshot.py"), "append", "--brand", "智引",
                      "--root", str(RUN / "snapshots"), "--mode", "audit",
                      "--scores", str(good_score), "--date", "2026-09-01",
                      "--evidence", str(good_json)])
    check("T1-12", "snapshot append 写入快照", rc == 0, f"exit={rc}")

    rc, out, _ = run([str(SCRIPTS / "snapshot.py"), "append", "--brand", "智引",
                      "--root", str(RUN / "snapshots"), "--mode", "audit",
                      "--scores", str(good_score), "--date", "2026-09-01", "--revision", "2"])
    check("T1-13", "snapshot 同名拒绝覆盖 → --revision 生效", rc == 0, f"exit={rc}")

    rc, out, _ = run([str(SCRIPTS / "snapshot.py"), "delta", "--brand", "智引",
                      "--root", str(RUN / "snapshots")])
    dl = jout(out)
    check("T1-14", "snapshot delta 跨期对比", rc == 0 and "total" in dl,
          f"total={dl.get('total')}")

    html_out = RUN / "report.html"
    rc, out, _ = run([str(SCRIPTS / "report_build.py"), "--scores", str(good_score),
                      "--probe", str(RUN / "judge.json"), "--brand", "智引",
                      "--mode", "audit", "--out", str(html_out)])
    html = html_out.read_text(encoding="utf-8") if html_out.is_file() else ""
    check("T1-15", "report_build 渲染 HTML（占位符全部解析）",
          rc == 0 and "{{" not in html and "智引" in html,
          f"len={len(html)}")

    md_out = RUN / "report.md"
    rc, out, _ = run([str(SCRIPTS / "report_build.py"), "--scores", str(good_score),
                      "--brand", "智引", "--format", "md", "--out", str(md_out)])
    md = md_out.read_text(encoding="utf-8") if md_out.is_file() else ""
    check("T1-16", "report_build 降级/指定 Markdown", rc == 0 and "站内信号分" in md,
          f"len={len(md)}")

    # ---------------- T0：版本强一致与交付完整性（设计指南 §6.3 家族规范） ----------------
    def frontmatter_version() -> str:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            return ""
        for line in text.split("---", 2)[1].splitlines():
            if line.strip().startswith("version:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")
        return ""

    v_skill = frontmatter_version()
    check("T0-01", "SKILL.md frontmatter 声明版本", bool(v_skill), f"version={v_skill}")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8", errors="replace")
    v_log = ""
    for line in changelog.splitlines():
        s = line.strip()
        if s.startswith("## [") and "]" in s:
            v_log = s[len("## ["):s.index("]")]
            break
    check("T0-02", "CHANGELOG 最新版本 == SKILL.md 版本",
          bool(v_log) and v_log == v_skill, f"changelog={v_log} skill={v_skill}")

    meta_p = ROOT / "_meta.json"
    v_meta = ""
    if meta_p.is_file():
        try:
            v_meta = str(json.loads(meta_p.read_text(encoding="utf-8")).get("version", ""))
        except json.JSONDecodeError:
            v_meta = ""
    check("T0-03", "_meta.json 版本 == SKILL.md 版本",
          bool(v_meta) and v_meta == v_skill, f"meta={v_meta} skill={v_skill}")

    schema_dir = ROOT / "schema"
    expect_schema = {"organization.json", "local-business.json", "article-author.json",
                     "software-saas.json", "product-ecommerce.json", "searchaction.json"}
    got_schema = {p.name for p in schema_dir.glob("*.json")} if schema_dir.is_dir() else set()
    bad_json: List[str] = []
    for name in sorted(got_schema):
        try:
            data = json.loads((schema_dir / name).read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            bad_json.append(f"{name}:{e}")
            continue
        items = data if isinstance(data, list) else [data]
        if not all(isinstance(it, dict) and it.get("@type") and it.get("@context")
                   for it in items):
            bad_json.append(f"{name}:缺 @context/@type")
    check("T0-04", "schema/ 六套 JSON-LD 模板齐备且合法",
          got_schema == expect_schema and not bad_json,
          f"got={len(got_schema)}/6" + (f" bad={bad_json}" if bad_json else ""))

    ref_dir = ROOT / "references"
    refs = sorted(p.name for p in ref_dir.glob("*.md")) if ref_dir.is_dir() else []
    missing_stamp = [n for n in refs
                     if "最后验证日期" not in (ref_dir / n).read_text(encoding="utf-8",
                                                              errors="replace")]
    check("T0-05", "references 全部带「最后验证日期」戳",
          len(refs) == 6 and not missing_stamp,
          f"refs={len(refs)} 缺戳={missing_stamp}")

    # ---------------- 汇总 ----------------
    total = len(CASES)
    passed = sum(1 for c in CASES if c["ok"])
    result = {"total": total, "passed": passed, "failed": total - passed, "cases": CASES,
              "note": "T3/T6 需真实站点与引擎会话，本脚本不覆盖（NEVER 以推演冒充实测）"}
    (RUN / "verify-result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 60)
    print(f"「智引」离线验收：{passed}/{total} 通过"
          + ("" if passed == total else f"，{total - passed} 项失败"))
    print(f"产物目录：{RUN}")
    if not args.keep and passed == total:
        pass  # 保留产物以便复核（默认保留，--keep 无副作用）
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
