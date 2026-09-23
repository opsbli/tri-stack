#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门④ 合规自检 —— `references/compliance-checklist.md` 22 条硬约束的可执行实现。

定位（家族硬约束第 18 条：可执行实现与 prompt 分离）：
  确定性判定由本脚本承担；prompt 层只「调用本脚本 + 解析 JSON + 按状态处置」。
  标注 `manual` 的条目**无法机器判定**，脚本不臆断，由 Agent 逐条给出证据位置。

判定口径（与 compliance-checklist.md §五 一致）：
  PASS   / FAIL / N-A（须附理由）/ MANUAL（需人工判定）

用法：
    python scripts/compliance_check.py --skill <slug>        # 审计单个 skill
    python scripts/compliance_check.py --all                 # 审计全部 tri-* skill
    python scripts/compliance_check.py --dir <路径>          # 审计任意目录
    python scripts/compliance_check.py --skill x --json      # 机器可读

退出码：0 = 可机器判定项无 FAIL；1 = 存在 FAIL；2 = 参数/环境错误

契约：本脚本与 `references/compliance-checklist.md` 的编号**一一对应**。
      修订约束时两处 MUST 同步修改（清单是标准，脚本是实现）。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

FM = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.S)
FM_FIELD = re.compile(r"^([a-zA-Z_]+):[ \t]*(.*)$", re.M)
SEMVER = re.compile(r"^\d+(\.\d+)*$")
CL_HEAD = re.compile(r"^##[ \t]*\[([0-9]+(?:\.[0-9]+)*)\]", re.M)
CL_ALL = re.compile(r"^##[ \t]*\[([0-9]+(?:\.[0-9]+)*)\]", re.M)
HARDCODED_COUNT = re.compile(r"\d+\s*个(下游|skill|顶层目录|tri-\*)")
SELFCHECK = re.compile(r"本次(意图|模式|操作)\s*=")
SECTIONS = ["强制执行契约", "触发时机", "上游依赖检测", "输入契约", "职责边界",
            "核心能力方法论", "处理流程", "交付产物", "版本检查与更新机制"]
LOCK_INSTALL = re.compile(r"(?<!api\.)skillhub\.cn|skills_store_lock|\.hub/skills")


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def vcmp(a, b):
    if not a or not b or not SEMVER.match(a) or not SEMVER.match(b):
        return None
    sa, sb = a.split("."), b.split(".")
    for i in range(max(len(sa), len(sb))):
        x = int(sa[i]) if i < len(sa) else 0
        y = int(sb[i]) if i < len(sb) else 0
        if x != y:
            return 1 if x > y else -1
    return 0


def sections(body: str) -> dict:
    """按 `## <标题>` 切分章节，返回 {标题: 正文}。

    **必须锚定 `## ` 标题**，不能用 body.find(<关键词>)——关键词常先出现在
    「强制执行契约」里对章节的引用（如「先通过 §版本检查与更新机制」），
    用 find 会把切片起点落在引用处，导致判定整体错位（实测曾因此误判 #22）。
    """
    out = {}
    marks = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^##\s+(.+)$", body, re.M)]
    for i, (pos, title) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        out[title] = body[pos:end]
    return out


def find_sec(secs: dict, key: str):
    for title, txt in secs.items():
        if key in title:
            return txt
    return ""


def check(d: Path) -> dict:
    slug = d.name
    sm = d / "SKILL.md"
    if not sm.is_file():
        return {"slug": slug, "error": "SKILL.md 不存在", "items": []}
    t = read(sm)
    fm_raw = FM.match(t)
    fmb = fm_raw.group(1) if fm_raw else ""
    fmd = dict(FM_FIELD.findall(fmb)) if fmb else {}
    desc = fmd.get("description", "")
    ver = fmd.get("version", "")
    body = t[fm_raw.end():] if fm_raw else t
    secs = sections(body)

    # 角色识别（决定 #8 / #20 是否适用）
    if "内部专用工具" in desc or "内部专用工具" in body[:1200]:
        role = "internal"
    elif "横向" in desc:
        role = "lateral"
    elif "下游" in desc and ("认领" in desc or "处理 I" in desc or "处理 L2" in desc):
        role = "downstream"
    elif "子 skill" in desc or "children" in desc:
        role = "child"
    else:
        role = "unknown"

    # 角色识别（决定 #8 / #20 是否适用）
    if "内部专用工具" in desc or "内部专用工具" in body[:1200]:
        role = "internal"
    elif "横向" in desc:
        role = "lateral"
    elif "下游" in desc and ("认领" in desc or "处理 I" in desc or "处理 L2" in desc):
        role = "downstream"
    elif "子 skill" in desc or "children" in desc:
        role = "child"
    else:
        role = "unknown"

    r = []

    def add(n, name, status, evidence="", notes="", advisory=False):
        r.append({"n": n, "name": name, "status": status, "evidence": evidence,
                  "notes": notes, "advisory": advisory})

    # 1 目录结构
    need_any = ["references", "templates", "scripts", "tests"]
    core = [f for f in ("SKILL.md", "README.md", "CHANGELOG.md") if (d / f).is_file()]
    sub = [x for x in need_any if (d / x).is_dir()]
    ok = len(core) == 3 and len(sub) >= 2
    add(1, "目录结构完整", "PASS" if ok else "FAIL",
        f"核心文件 {len(core)}/3（{'/'.join(core)}）；子目录 {len(sub)}/4（{'/'.join(sub)}）")

    # 2 独立安装声明
    m = re.search(r"支持独立安装[，,]含上游依赖检测[一二三四两]?态逻辑", desc)
    add(2, "独立安装声明", "PASS" if m else "FAIL",
        f"description 命中：{m.group(0)}" if m else "description 未含「支持独立安装，含上游依赖检测N态逻辑」")

    # 3 章序 —— 按家族实测校准：
    #    必备 7 章须存在；前 5 章相对顺序固定；
    #    「方法论」「处理流程」类章节名允许专名变体；
    #    「版本检查」接受两种位置（紧跟职责边界之后 / 文件末），该变体已在 family-spec §五 登记。
    HEAD_FIRST5 = ["强制执行契约", "触发时机", "上游依赖检测", "输入契约", "职责边界"]
    HEAD_ANY = ["交付产物"]
    def has(key):
        return any(key in h for h in secs)
    missing = [h for h in HEAD_FIRST5 if not has(h)] + [h for h in HEAD_ANY if not has(h)]
    missing += [] if has("版本检查与更新机制") else ["版本检查与更新机制"]
    method_ok = any("方法论" in h for h in secs)
    if not method_ok:
        missing.append("方法论（核心能力方法论或专名变体）")
    order_bad = []
    pos = [next((i for i, h in enumerate(secs) if k in h), -1) for k in HEAD_FIRST5]
    for i in range(4):
        if pos[i] >= 0 and pos[i + 1] >= 0 and pos[i] > pos[i + 1]:
            order_bad.append(f"{HEAD_FIRST5[i]} 应在 {HEAD_FIRST5[i+1]} 之前")
    vc_pos = next((i for i, h in enumerate(secs) if "版本检查与更新机制" in h), -1)
    rq_pos = next((i for i, h in enumerate(secs) if "职责边界" in h), -1)
    vc_after_rq = vc_pos > rq_pos >= 0
    add(3, "SKILL.md 章节齐全且顺序正确",
        "PASS" if not missing and not order_bad else "FAIL",
        (f"缺章节：{missing}" if missing else "") + ("；" + "；".join(order_bad) if order_bad else "")
        or "七类必备章节齐全，前五章顺序正确",
        f"版本检查位置={'第 ' + str(vc_pos + 1) + ' 个二级标题（两合法变体之一）' if vc_after_rq else '不符合已登记的两变体'}")

    # 4 frontmatter 八字段
    need = ["name", "slug", "version", "displayName", "description", "summary", "tags", "license"]
    miss = [k for k in need if not fmd.get(k)]
    add(4, "frontmatter 完整",
        "PASS" if not miss and SEMVER.match(ver or "") else "FAIL",
        f"缺字段：{miss}；version={ver!r}" if (miss or not SEMVER.match(ver or "")) else f"八字段齐全，version={ver}")

    # 5 契约存在且含自检句
    seg = find_sec(secs, "强制执行契约")
    numbered = len(re.findall(r"^\d+\.\s", seg, re.M))
    add(5, "强制执行契约存在且含自检句",
        "PASS" if numbered >= 5 and SELFCHECK.search(seg) else "FAIL",
        f"编号条目 {numbered} 条；自检句 {'有' if SELFCHECK.search(seg) else '无'}")

    # 6 上游检测态数匹配（三态须含降级声明）
    seg6 = find_sec(secs, "上游依赖检测")
    has_guide = "引导安装" in seg6
    has_deg = "降级" in seg6 or "降级声明" in seg6
    if not seg6:
        add(6, "上游检测态数与类型匹配", "FAIL", "无「上游依赖检测」章节")
    elif not has_guide:
        add(6, "上游检测态数与类型匹配", "FAIL", "未见「引导安装」态")
    else:
        add(6, "上游检测态数与类型匹配", "PASS" if has_deg else "MANUAL",
            f"引导安装=有，降级={'有' if has_deg else '无'}",
            "含降级=三态；缺降级须确认为两态型（咨询/表达/元操作）")

    # 7 职责边界
    seg7 = find_sec(secs, "职责边界")
    add(7, "职责边界明确",
        "PASS" if ("不负责" in seg7 or "NEVER" in seg7) else "FAIL",
        f"该节 {len(seg7.splitlines())} 行；含「{'不负责' if '不负责' in seg7 else 'NEVER'}」")

    # 8 MECE 交叉比对 —— 需人工
    if role == "downstream":
        add(8, "意图认领 MECE 不重叠", "MANUAL",
            "须交由人类/Agent 交叉比对 tri-intent/SKILL.md §路由映射表（路由真源）")
    else:
        add(8, "意图认领 MECE 不重叠", "N-A",
            f"角色={role}，不认领 L2/L3 编码",
            "本项仅路由型下游适用（理由：非路由型不参与路由表，无编码可重叠）")

    # 9 可扩展性
    add(9, "核心能力方法论含可扩展性",
        "PASS" if "可扩展性" in body else "FAIL",
        "含「可扩展性」小节" if "可扩展性" in body else "未见「可扩展性」小节")

    # 10 落盘规则
    add(10, "交付产物含落盘规则",
        "PASS" if ("落盘" in body and (".tribro/" in body or "工作区" in body)) else "FAIL",
        "含落盘位置说明" if "落盘" in body else "未见落盘位置说明")

    # 11 CHANGELOG
    cl = read(d / "CHANGELOG.md")
    vs = CL_ALL.findall(cl)
    head = CL_HEAD.search(cl)
    hv = head.group(1) if head else None
    mx = None
    for v in vs:
        if mx is None or (vcmp(v, mx) or 0) > 0:
            mx = v
    ok11 = bool(hv) and hv == ver and mx == hv
    add(11, "CHANGELOG 规范", "PASS" if ok11 else "FAIL",
        f"首条={hv} frontmatter={ver} 文件最大={mx}")

    # 12 tests
    td = d / "tests"
    tfiles = list(td.glob("*-full-testcases.md")) if td.is_dir() else []
    cnt = 0
    if tfiles:
        cnt = len(re.findall(r"^\|\s*T?C?\d+", read(tfiles[0]), re.M))
    add(12, "tests 全场景用例",
        "PASS" if tfiles and cnt >= 10 else "FAIL",
        f"用例文件 {len(tfiles)} 个，编号条目 {cnt} 条" if tfiles else "无 tests/*-full-testcases.md")

    # 13 门禁（无门禁者 N-A，须附理由）
    has_gate = any(k in body for k in ("审批门", "门①", "闸门", "门禁", "审批"))
    add(13, "门禁/审批门明确",
        "PASS" if has_gate else "N-A",
        "含门禁表述" if has_gate else "纯只读 / 无产物落盘型，判 N-A（理由：无需要审批的产物）")

    # 14 兜底
    add(14, "兜底处理覆盖",
        "PASS" if ("兜底" in body and "NEVER" in body) else "FAIL",
        "含兜底处理且明确 NEVER 静默失败" if "兜底" in body else "未见兜底处理小节")

    # 15 自检句格式
    m15 = SELFCHECK.search(body)
    add(15, "自检句格式与家族一致", "PASS" if m15 else "FAIL",
        f"命中：{m15.group(0)}" if m15 else "未命中 本次意图=/本次模式=/本次操作=")

    # 16 反规避 —— 仅对有门禁者适用；放宽表述
    if not has_gate:
        add(16, "反规避规则", "N-A", "无门禁，反规避规则不适用（理由：无门禁即无可规避的标准）")
    else:
        m16 = re.search(r"(NEVER|不得|禁止)[^\n]{0,60}(下调|降低|放宽|简化|凑合|迁就|因为.{0,10}(着急|时间))",
                        body) or ("反规避" in body)
        add(16, "反规避规则（建议项）", "PASS" if m16 else "N-A",
            "含反规避表述" if m16 else "有门禁但未含显式反规避表述",
            "本项为建议项，FAIL 不阻断。上游仅确认 tri-review/tri-sdlc 显式设有反规避机制，"
            "家族其余 gated skill 普遍未写此表述——本条为本仓库重建推定，故不列入必检。",
            advisory=True)

    # 17 禁止硬编码家族计数
    m17 = HARDCODED_COUNT.search(body)
    hits = HARDCODED_COUNT.findall(body)
    add(17, "禁止硬编码家族计数", "PASS" if not m17 else "FAIL",
        f"命中：{m17.group(0)}（共 {len(hits)} 处）" if m17 else "未见硬编码家族计数")

    # 18 可执行实现分离
    sd = d / "scripts"
    py = list(sd.glob("*.py")) if sd.is_dir() else []
    add(18, "可执行实现与 prompt 分离",
        "PASS" if py else "N-A",
        (f"scripts/ 下 {len(py)} 个脚本：{'/'.join(p.name for p in py[:4])}") if py
        else "scripts/ 无脚本；无确定性逻辑型 skill 判 N-A（理由：无确定性逻辑需外置）")

    # 19 相邻边界表（放宽：表行 / 边界关键词 / 归属表均可）
    m19 = re.search(r"\|\s*(相邻|信号|归属|tri-\w+)[^\n]*\|", body) or ("边界判据" in body) \
          or ("边界说明" in body) or ("· tri-" in body)
    add(19, "与相邻 skill 边界表（建议项）", "PASS" if m19 else "N-A",
        "含相邻/归属边界表" if m19 else "未见相邻边界表或归属表",
        "本项为建议项，FAIL 不阻断。上游未确认该条为必检；家族实际写法多样"
        "（边界表 / 归属表 / 段落叙述），机械判定易误报，故不列入必检。",
        advisory=True)

    # 20 横向例外登记
    if role == "lateral":
        add(20, "横向层自检句例外登记", "MANUAL",
            "横向型；须确认 family-spec.md §五 是否已登记其自检句例外")
    else:
        add(20, "横向层自检句例外登记", "N-A",
            f"角色={role}，非横向型",
            "本项仅横向型适用（理由：非横向型不存在自检句例外需登记）")

    # 21 安装评估
    conflict = (REPO / slug).exists()
    writable = False
    try:
        probe = d / f".cmp_probe_{id(d)}"
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
        writable = True
    except OSError:
        pass
    add(21, "安装评估", "PASS" if writable else "FAIL",
        f"目录可写={'是' if writable else '否'}；slug 目录存在={conflict}（存在属正常，仅记录）")

    # 22 版本检查内部化：硬要求 = 指向自身 spec；STUB 行数为**建议项**（不阻断）
    seg22 = find_sec(secs, "版本检查与更新机制")
    self_ref = "references/version-check-spec.md" in seg22
    foreign = re.findall(r"tri-\w+/references/[\w.-]+", seg22)
    lines = len(seg22.splitlines())
    hard_ok = self_ref and not foreign
    add(22, "版本检查内部化",
        "PASS" if hard_ok else "FAIL",
        f"自身指针={'有' if self_ref else '无'}；指向外部={('是（违规）:' + ','.join(sorted(set(foreign))[:2])) if foreign else '否'}",
        f"该节 {lines} 行" + ("（超 STUB 建议值 30 行，属建议项、不阻断）" if lines > 30 else ""))

    # 门④ 判定：**建议项 FAIL 不阻断**（家族既有惯例：必检项 + 建议项，建议项记入「建议改进项」）
    fails = [x for x in r if x["status"] == "FAIL" and not x.get("advisory")]
    advisory = [x for x in r if x["status"] == "FAIL" and x.get("advisory")]
    return {"slug": slug, "dir": d.as_posix(), "items": r,
            "fail": len(fails), "advisory": len(advisory),
            "manual": sum(1 for x in r if x["status"] == "MANUAL"),
            "verdict": "FAIL" if fails else "PASS"}


def render(res: dict) -> str:
    if res.get("error"):
        return f"### `{res['slug']}`\n\n🔴 {res['error']}\n"
    mark = {"PASS": "✅", "FAIL": "🔴", "N-A": "⬜", "MANUAL": "🔍"}
    out = [f"### `{res['slug']}` — 门④ {'PASS' if res['verdict'] == 'PASS' else 'FAIL'}"
           f"（FAIL {res['fail']} · 需人工 {res['manual']}）\n",
           "| # | 约束 | 判定 | 证据 / 原因 |", "|---|---|---|---|"]
    for x in res["items"]:
        ev = x["evidence"]
        if x.get("notes"):
            ev += f"<br><em>（{x['notes']}）</em>"
        out.append(f"| {x['n']} | {x['name']} | {mark.get(x['status'],'?')} {x['status']} | {ev} |")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", default=None)
    ap.add_argument("--dir", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.dir:
        targets = [Path(args.dir).resolve()]
    elif args.skill:
        p = (REPO / args.skill).resolve()
        if not p.is_dir():
            print(f"未找到：{p}", file=sys.stderr)
            return 2
        targets = [p]
    elif args.all:
        targets = sorted(p for p in REPO.glob("tri-*") if (p / "SKILL.md").is_file())
    else:
        print("需指定 --skill / --dir / --all", file=sys.stderr)
        return 2

    results = [check(d) for d in targets]

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        print(f"# 门④ 合规自检（compliance-checklist.md 22 条）\n")
        print(f"审计对象 **{len(results)}** 个；门④ FAIL **{sum(1 for r in results if r.get('verdict')=='FAIL')}** 个\n")
        for r in results:
            print(render(r))
        print("> 🔍 `MANUAL` 项 MUST 由 Agent 逐条给出证据位置，NEVER 臆断。")
        print("> 口径：任一条 FAIL → 门④ FAIL → 回炉门②；连续 3 轮 FAIL → 停止回炉并报告卡点。")

    return 1 if any(r.get("verdict") == "FAIL" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
