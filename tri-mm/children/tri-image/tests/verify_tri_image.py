#!/usr/bin/env python3
"""tri-image 静态门禁自检。

把「能力是否保全 / 清理是否彻底 / 版本是否联动」变成可机械校验的判定，
NEVER 依赖人眼或模型自述。

用法：
    python tests/verify_tri_image.py            # 人读输出
    python tests/verify_tri_image.py --json     # 结构化输出
退出码：0 全通过；2 存在 P0/P1 级不通过；3 仅提示级（P2）不通过。
"""
import argparse
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)

# 期望的 Gallery 条目数（合订后仍须等于原始条目数）
EXPECTED_ENTRIES = {
    "references/scenes/cover/palettes.md": 11,
    "references/scenes/cover/renderings.md": 7,
    "references/scenes/cover/dimensions.md": 3,
    "references/scenes/infographic/layouts.md": 21,
    "references/scenes/infographic/styles.md": 22,
    "references/scenes/illustration/styles.md": 23,
    "references/scenes/illustration/palettes.md": 4,
    "references/scenes/cards/presets.md": 12,
    "references/scenes/cards/palettes.md": 3,
    "references/scenes/cards/elements.md": 4,
    "references/scenes/slides/styles.md": 17,
    "references/scenes/slides/dimensions.md": 5,
    "references/scenes/comic/art-styles.md": 6,
    "references/scenes/comic/layouts.md": 7,
    "references/scenes/comic/presets.md": 5,
    "references/scenes/comic/tones.md": 7,
    "references/scenes/diagram/types.md": 4,
}

# 去标识化：这些标识 MUST 完全消失。
# 运行时拼接构造，避免自检脚本源码出现连续字面量而自我命中。
_FORBID_TOKENS = [
    "ba" + "oyu",                       # 参考基准前缀
    "Ji" + "mLiu",                      # 参考基准作者
    "github.com/" + "Ji" + "mLiu",       # 参考基准仓库地址
    "." + "ba" + "oyu" + "-skills",      # 参考基准配置目录
]
FORBIDDEN = [(t, "第三方归属标识") for t in _FORBID_TOKENS]

# 能力保全：这些关键机制 MUST 存在
REQUIRED_SNIPPETS = [
    ("references/common/image-backend-rules.md", "n=1", "coderef 批语义（并集项，易丢）"),
    ("references/common/image-backend-rules.md", "首图锚链", "跨图一致性机制"),
    ("references/common/image-backend-rules.md", "NEVER 用 SVG", "Track-R 红线 1（须限定作用域）"),
    ("references/common/image-backend-rules.md", "NEVER 用程序修补", "Track-R 红线 2"),
    ("references/scenes/comic/README.md", "characters", "漫画角色表机制"),
    ("references/scenes/cover/README.md", "prompt-template", "封面提示词模板"),
    ("references/scenes/infographic/README.md", "structured-content", "信息图中间产物"),
]

EXPECTED_PROVIDERS = ["agnes", "azure", "codex-cli", "dashscope", "google",
                      "jimeng", "minimax", "openai", "openrouter", "replicate",
                      "seedream", "zai"]


def read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def count_h2(path):
    return len(re.findall(r"^## ", read(path), re.M))


def walk_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, fn), root))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    checks = []

    def add(name, level, ok, evidence):
        checks.append({"name": name, "level": level, "ok": bool(ok), "evidence": evidence})

    # 1. SKILL.md frontmatter 与版本
    skill_text = read(os.path.join(SKILL, "SKILL.md"))
    fm = re.match(r"^---\n(.*?)\n---\n", skill_text, re.S)
    add("SKILL.md 有 frontmatter", "P0", fm is not None, "--- 块存在" if fm else "缺失")
    version = None
    if fm:
        m = re.search(r"^version:\s*(\S+)", fm.group(1), re.M)
        version = m.group(1) if m else None
        add("frontmatter slug==tri-image", "P0",
            re.search(r"^slug:\s*tri-image", fm.group(1), re.M) and
            re.search(r"^name:\s*\S+", fm.group(1), re.M), "slug=tri-image, name 非空")
        desc = re.search(r"^description:\s*(.+)$", fm.group(1), re.M)
        add("description 含独立安装字样", "P0",
            desc and "支持独立安装" in desc.group(1), "支持独立安装，含上游依赖检测两态逻辑")
    add("SKILL version 已取到", "P0", version is not None, version or "缺失")

    # 2. 版本五处联动
    changelog = read(os.path.join(SKILL, "CHANGELOG.md"))
    m = re.search(r"^## \[([0-9]+\.[0-9]+\.[0-9]+)\]", changelog, re.M)
    changelog_version = m.group(1) if m else None
    add("CHANGELOG 置顶版本 == SKILL version", "P0",
        changelog_version == version, "%s vs %s" % (changelog_version, version))

    meta_path = os.path.join(SKILL, "_meta.json")
    meta_version = None
    if os.path.isfile(meta_path):
        meta_version = json.loads(read(meta_path)).get("version")
    add("_meta.json 版本 == SKILL version", "P0", meta_version == version,
        "%s vs %s" % (meta_version, version))

    tests_path = os.path.join(HERE, "tri-image-full-testcases.md")
    tests_version = None
    if os.path.isfile(tests_path):
        m = re.search(r"v([0-9]+\.[0-9]+\.[0-9]+)", read(tests_path)[:400])
        tests_version = m.group(1) if m else None
    add("tests frontmatter 版本 == SKILL version", "P0", tests_version == version,
        "%s vs %s" % (tests_version, version))

    readme = read(os.path.join(SKILL, "README.md"))
    add("README 版本字样一致", "P1", version in readme, "含 %s" % version if version in readme else "未提及")

    # 3. 行数与文件数
    lines = skill_text.count("\n") + 1
    add("SKILL.md ≤500 行", "P0", lines <= 500, "%d 行" % lines)
    all_files = walk_files(SKILL)
    add("文件总数 ≤200", "P1", len(all_files) <= 200, "%d 个" % len(all_files))

    # 4. 去标识化
    alltext = {}
    for rel in all_files:
        full = os.path.join(SKILL, rel)
        if rel.endswith((".md", ".ts", ".py", ".json")):
            alltext[rel] = read(full)
    offenders = []
    for rel, txt in alltext.items():
        for pat, label in FORBIDDEN:
            if re.search(pat, txt, re.I):
                offenders.append("%s: %s" % (rel, label))
    add("无第三方归属信息残留", "P0", not offenders,
        "干净" if not offenders else "; ".join(offenders[:6]))

    # 5. Gallery 条目守恒
    missing, wrong = [], []
    for rel, expected in EXPECTED_ENTRIES.items():
        full = os.path.join(SKILL, rel)
        if not os.path.isfile(full):
            missing.append(rel)
            continue
        got = count_h2(full)
        if got != expected:
            wrong.append("%s 期望 %d 实得 %d" % (rel, expected, got))
    add("Gallery 合订本条目守恒", "P0", not missing and not wrong,
        "全部一致（%d 个文件）" % len(EXPECTED_ENTRIES) if not missing and not wrong
        else "缺:%s 差:%s" % (missing, wrong))

    # 6. provider 数量守恒
    pdir = os.path.join(SKILL, "scripts", "engine", "providers")
    providers = sorted(f[:-3] for f in os.listdir(pdir) if f.endswith(".ts")) if os.path.isdir(pdir) else []
    add("引擎 provider 12 个且无测试残留", "P0",
        providers == sorted(EXPECTED_PROVIDERS),
        "%d 个：%s" % (len(providers), ",".join(providers)))

    # 7. 关键机制存在性
    lost = []
    for rel, needle, label in REQUIRED_SNIPPETS:
        full = os.path.join(SKILL, rel)
        if not os.path.isfile(full) or needle not in read(full):
            lost.append("%s（%s）" % (rel, label))
    add("关键机制与并集内容齐全", "P0", not lost, "齐全" if not lost else "; ".join(lost))

    # 8. 引用不越出 skill 根
    escaped = []
    for rel, txt in alltext.items():
        if not rel.endswith(".md"):
            continue
        base = os.path.dirname(os.path.join(SKILL, rel))
        for target in re.findall(r"\]\((?!http|#)([^)]+)\)", txt):
            clean = target.split("#")[0].strip()
            if not clean:
                continue
            resolved = os.path.normpath(os.path.join(base, clean))
            if os.path.commonpath([resolved, SKILL]) != SKILL:
                escaped.append("%s -> %s" % (rel, target))
    add("Markdown 引用未越出 skill 根", "P1", not escaped,
        "无越界" if not escaped else "; ".join(escaped[:6]))

    # 9. 必需文件
    for rel in ["SKILL.md", "README.md", "CHANGELOG.md", "_meta.json",
                "scripts/check_update.py", "scripts/aspect.py",
                "scripts/svg_to_png.py", "scripts/compress_image.py",
                "references/common/image-backend-rules.md"]:
        add("存在 %s" % rel, "P0", os.path.isfile(os.path.join(SKILL, rel)), rel)

    # 10. 禁用文件
    banned = [f for f in all_files if os.path.basename(f) in ("LICENSE", ".gitignore")]
    add("无 LICENSE/.gitignore", "P0", not banned, "干净" if not banned else ",".join(banned))

    # 11. 契约条目
    add("契约含版本检查第零步", "P0", "第零步" in skill_text, "第零步")
    add("含完成判据外化", "P0", "完成判据" in skill_text, "## 完成判据")
    add("含进化契约 + lessons.md", "P0",
        "进化契约" in skill_text and "lessons.md" in skill_text, "进化契约/lessons.md")
    add("含结论置信标注六类依据", "P0",
        all(k in skill_text for k in ["事实 known", "计算 computed", "推断 inferred",
                                      "常识 common", "框架 iframe", "猜测 guess"]), "六类依据")
    add("含知识装配顺序", "P0", "知识装配顺序" in skill_text, "## 知识装配顺序")
    add("自检句含本次意图=I15", "P0", "本次意图=I15" in skill_text, "本次意图=I15·图片")

    failed_p0 = [c for c in checks if not c["ok"] and c["level"] == "P0"]
    failed_p1 = [c for c in checks if not c["ok"] and c["level"] == "P1"]

    if args.json:
        print(json.dumps({"version": version, "checks": checks,
                          "failed_p0": len(failed_p0), "failed_p1": len(failed_p1),
                          "total_checks": len(checks)},
                         ensure_ascii=False, indent=1))
    else:
        for c in checks:
            print("[%s] %-36s %s  (%s)" % (c["level"], c["name"],
                                           "PASS" if c["ok"] else "FAIL", c["evidence"]))
        print("\n合计 %d 项：P0 失败 %d，P1 失败 %d" % (len(checks), len(failed_p0), len(failed_p1)))

    if failed_p0 or failed_p1:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
