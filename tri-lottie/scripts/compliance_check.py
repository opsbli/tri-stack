#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
tri-lottie 结构合规与六端代码模板断言测试执行器（约束 18：确定性算法下沉 scripts/）。
用法：python scripts/compliance_check.py            # 全量运行，退出码 0=全过 / 1=有失败
     python scripts/compliance_check.py --json      # JSON 输出（供 CI / agent 消费）
测试集：T1 frontmatter / T2 零残留 / T3 版本四件套 / T4 行数 / T5 目录树 diff
       T6 版本门三件套 / T7 禁文件 / T8 合规章节 / T9 六端坑位断言 / T10 黄金用例一致性
"""
import json
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(BASE, "SKILL.md")
CHANGELOG = os.path.join(BASE, "CHANGELOG.md")
TESTS_MD = os.path.join(BASE, "tests", "tri-lottie-full-testcases.md")
README = os.path.join(BASE, "README.md")
CHECK_UPDATE = os.path.join(BASE, "scripts", "check_update.py")
STACKS = ["web", "android", "ios", "harmonyos-arkts", "react-native", "flutter"]

# 第三方依赖标准安装坐标/包名白名单（技术标识符，非署名；§落盘规则/合规清单声明）
COORDINATE_WHITELIST = ["com.airbnb.android:lottie", "com.airbnb.lottie",
                        "github.com/airbnb/lottie-ios"]
# 断言载体自身豁免（禁词表定义处，非内容产物）
SELF_EXEMPT = {"compliance_check.py"}

RESULTS = []


def check(tid, name, ok, evidence):
    RESULTS.append({"id": tid, "name": name, "ok": bool(ok), "evidence": evidence})
    return ok


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


# ---------- T1 frontmatter ----------
def t1():
    fm = frontmatter(read(SKILL_MD))
    required = ["name:", "slug:", "version:", "displayName:", "description:",
                "summary:", "tags:", "license:"]
    missing = [k for k in required if k not in fm]
    name = re.search(r"^name:\s*(\S+)", fm, re.M)
    slug = re.search(r"^slug:\s*(\S+)", fm, re.M)
    kebab_ok = bool(name and slug and name.group(1) == slug.group(1)
                    and re.fullmatch(r"[a-z0-9-]+", slug.group(1)))
    desc_ok = "支持独立安装，含上游依赖检测三态逻辑" in fm
    check("T1", "frontmatter 八字段 + name==slug kebab + description 字样",
          not missing and kebab_ok and desc_ok,
          f"missing={missing}, name/slug={name and name.group(1)}, desc字样={desc_ok}")


# ---------- T2 零残留 ----------
def t2():
    banned = ["LottieFiles", "lottie.host", "lottiefiles.com",
              "Copyright (c) 2025", "© 2025 LottieFiles", "Awesome Lottie"]
    hits = []
    for root, dirs, files in os.walk(BASE):
        for fn in files:
            p = os.path.join(root, fn)
            if not fn.endswith((".md", ".py")) or fn in SELF_EXEMPT:
                continue
            body = read(p)
            # 去白名单坐标后再扫描
            for w in COORDINATE_WHITELIST:
                body = body.replace(w, "")
            for b in banned:
                if b in body:
                    hits.append(f"{os.path.relpath(p, BASE)}: {b}")
    # airbnb 仅允许出现在坐标白名单内
    for root, dirs, files in os.walk(BASE):
        for fn in files:
            p = os.path.join(root, fn)
            if not fn.endswith((".md", ".py")) or fn in SELF_EXEMPT:
                continue
            body = read(p)
            for w in COORDINATE_WHITELIST:
                body = body.replace(w, "")
            if re.search(r"airbnb", body, re.I):
                hits.append(f"{os.path.relpath(p, BASE)}: airbnb(坐标外)")
    check("T2", "上游作者/品牌/版权零残留（坐标白名单除外）", not hits, f"hits={hits or '无'}")


# ---------- T3 版本四件套 ----------
def t3():
    fm = frontmatter(read(SKILL_MD))
    v_skill = re.search(r"^version:\s*[\"']?(\d+\.\d+\.\d+)", fm, re.M)
    v_skill = v_skill.group(1) if v_skill else None
    cl = read(CHANGELOG)
    v_cl = re.search(r"^## \[(\d+\.\d+\.\d+)\]", cl, re.M)
    v_cl = v_cl.group(1) if v_cl else None
    tm = frontmatter(read(TESTS_MD))
    v_tests = re.search(r"[vV](\d+\.\d+\.\d+)", tm)
    v_tests = v_tests.group(1) if v_tests else None
    ok = v_skill and v_skill == v_cl == v_tests
    check("T3", "版本四件套一致（SKILL==CHANGELOG==tests）", ok,
          f"skill={v_skill}, changelog={v_cl}, tests={v_tests}")


# ---------- T4 行数 ----------
def t4():
    n = read(SKILL_MD).count("\n") + 1
    check("T4", "SKILL.md ≤ 500 行", n <= 500, f"lines={n}")


# ---------- T5 目录树与磁盘 diff（树为嵌套缩进，按叶子名/目录名与磁盘尾部段匹配） ----------
def t5():
    tree_declared = set()
    in_tree = False
    for line in read(SKILL_MD).splitlines():
        if line.startswith("## 目录结构"):
            in_tree = True
            continue
        if in_tree:
            if line.startswith("## "):
                break
            m = re.search(r"[├└│\s]+([A-Za-z0-9_./\-]+)", line)
            if m:
                name = m.group(1).rstrip("/")
                if name and name != "tri-lottie" and not name.startswith("#"):
                    tree_declared.add(name)
    tree_names = set()
    for d in tree_declared:
        tree_names.update(seg for seg in d.split("/") if seg)
    disk_names = set()
    for root, dirs, files in os.walk(BASE):
        rel = os.path.relpath(root, BASE).replace("\\", "/")
        if rel != ".":
            disk_names.add(os.path.basename(rel))
        disk_names.update(files)
    disk_names = {n for n in disk_names
                  if not n.endswith(".pyc") and n != "__pycache__"
                  and n != "_meta.json"}  # 安装器产物（约束21），非生成内容
    missing = disk_names - tree_names
    phantom = tree_names - disk_names
    check("T5", "目录结构声明与磁盘一致（basename 级，无遗漏/无幻影）",
          not missing and not phantom,
          f"missing={sorted(missing) or '无'}, phantom={sorted(phantom) or '无'}")


# ---------- T6 版本门三件套 ----------
def t6():
    sk = read(SKILL_MD)
    stub_ok = "## 版本检查与更新机制" in sk and "version-check-spec.md" in sk
    zero_ok = "第零步" in sk and "check_update.py" in sk
    stub_lines = 0
    in_stub = False
    for line in sk.splitlines():
        if line.startswith("## 版本检查与更新机制"):
            in_stub = True
            stub_lines = 1
            continue
        if in_stub:
            if line.startswith("## "):
                break
            stub_lines += 1
    script_ok = False
    detail = ""
    try:
        r = subprocess.run(
            [sys.executable, CHECK_UPDATE, "--slug", "tri-lottie", "--json"],
            capture_output=True, text=True, timeout=60)
        out = json.loads(r.stdout[r.stdout.index("{"):])
        script_ok = r.returncode < 20 and out.get("state") in ("A", "B", "C", "D")
        detail = f"exit={r.returncode}, state={out.get('state')}"
    except Exception as e:  # 脚本异常兜底降级放行（不得因版本门故障阻断）
        script_ok = False
        detail = f"exception={e}"
    check("T6", "版本门三件套（脚本可运行+第零步+≤30行STUB指针）",
          script_ok and zero_ok and stub_ok and stub_lines <= 30,
          f"script[{detail}], 第零步={zero_ok}, stub指针={stub_ok}, stub行数={stub_lines}")


# ---------- T7 禁文件 ----------
def t7():
    bad = [f for f in ("LICENSE", ".gitignore")
           if os.path.exists(os.path.join(BASE, f))]
    check("T7", "无 LICENSE / .gitignore", not bad, f"found={bad or '无'}")


# ---------- T8 合规章节 ----------
def t8():
    sk = read(SKILL_MD)
    marks = {
        "强制执行契约(最高优先级)": "## 强制执行契约" in sk and "最高优先级" in sk,
        "触发时机": "## 触发时机" in sk,
        "上游依赖检测(三态)": "## 上游依赖检测" in sk and "降级" in sk,
        "输入契约": "## 输入契约" in sk,
        "职责边界": "## 职责边界" in sk,
        "方法论": "## tri-lottie 方法论" in sk,
        "处理流程": "## 处理流程" in sk,
        "交付产物机制": "## 交付产物机制" in sk,
        "质量标准(独立二级)": bool(re.search(r"^## 质量标准", sk, re.M)),
        "落盘规则": "## 落盘规则" in sk,
        "目录结构": "## 目录结构" in sk,
        "知识装配顺序(约束25)": "## 知识装配顺序" in sk,
        "进化契约+三要素(约束23)": "## 进化契约" in sk and all(
            k in sk for k in ("反馈接收点", "经验沉淀位", "自我修订触发条件")),
        "完成判据+停车区分(约束24)": "## 完成判据" in sk and "停车" in sk,
        "自检句(约束5)": "本次意图=I11(motion)" in sk,
        "MECE/边界": "MECE" in sk,
    }
    bad = [k for k, v in marks.items() if not v]
    check("T8", "12+4 合规章节齐备（契约/自检句/进化契约/完成判据/装配顺序等）",
          not bad, f"missing={bad or '无'}")


# ---------- T9 六端坑位断言 ----------
STACK_ASSERTS = {
    "web": ["anim.destroy()", "prefers-reduced-motion", "renderer: 'svg'",
            "lottie.loadAnimation", "cubic-bezier(0.4, 0, 0.2, 1)"],
    "android": ["lottie-compose", "minSdk 21", "ANIMATOR_DURATION_SCALE",
                "rememberLottieComposition", "CubicBezierEasing", "android.useAndroidX"],
    "ios": ["iOS 13.0", "accessibilityReduceMotion", "LottieAnimationView",
            "timingCurve(0.4, 0, 0.2, 1", "Swift 5.7"],    "harmonyos-arkts": ["onReady", "aboutToDisappear", "lottie.destroy()",
                        "RenderingContextSettings(true)", "curves.cubicBezier(0.4, 0, 0.2, 1)",
                        "禁用 `./` `../`", "@ohos/lottie"],
    "react-native": ["npx expo install", "development build", "useIsFocused",
                     "onAnimationFinish", "colorFilters", "Easing.bezier(0.4, 0, 0.2, 1)",
                     "lottie-react-native"],
    "flutter": ["assets:", "onLoaded", "composition.duration", "disableAnimations",
                "_controller.dispose()", "Cubic(0.4, 0, 0.2, 1)", "pubspec"],
}


def t9():
    details = {}
    all_ok = True
    for stack in STACKS:
        p = os.path.join(BASE, "stacks", stack, "implementation.md")
        body = read(p)
        missing = [a for a in STACK_ASSERTS[stack] if a not in body]
        details[stack] = missing or "全命中"
        all_ok = all_ok and not missing
    check("T9", "六端 implementation.md 坑位/防御断言", all_ok, json.dumps(details, ensure_ascii=False))


# ---------- T10 黄金用例一致性 ----------
def t10():
    details = {}
    all_ok = True
    for stack in STACKS:
        body = read(os.path.join(BASE, "stacks", stack, "implementation.md"))
        has_duration = "350ms" in body or "350" in body
        has_premium_curve = ("0.4, 0, 0.2, 1" in body or "0.4,0,0.2,1" in body)
        ok = has_duration and has_premium_curve
        details[stack] = f"350ms={has_duration}, premiumCurve={has_premium_curve}"
        all_ok = all_ok and ok
    check("T10", "黄金用例一致性（六端含 350ms + Premium 缓动签名）", all_ok,
          json.dumps(details, ensure_ascii=False))


def main():
    for fn in (t1, t2, t3, t4, t5, t6, t7, t8, t9, t10):
        fn()
    passed = sum(1 for r in RESULTS if r["ok"])
    all_ok = passed == len(RESULTS)
    if "--json" in sys.argv:
        print(json.dumps({"all_ok": all_ok, "passed": passed,
                          "total": len(RESULTS), "results": RESULTS},
                         ensure_ascii=False, indent=2))
    else:
        print(f"tri-lottie compliance_check：{passed}/{len(RESULTS)} PASS")
        for r in RESULTS:
            print(f"  [{'PASS' if r['ok'] else 'FAIL'}] {r['id']} {r['name']}")
            if not r["ok"]:
                print(f"         证据: {r['evidence']}")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
