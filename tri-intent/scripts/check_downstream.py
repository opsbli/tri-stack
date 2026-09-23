#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tri-intent 下游安装检测脚本（check_downstream.py）

职责：在意图识别产出快照、准备分发给下游 skill 之前，确定性地判定
「该下游 skill 是否已安装、是否可被斜杠激活」，为 §下游依赖检测 的
两道确认门（门A 安装 / 门B 执行）提供机器可读依据。

检测四处路径 + 一处注册表：
  1. 家族源码树      <family_root>/<slug>/SKILL.md
  2. 锻造落盘        <project>/.tribro/skills/<slug>/SKILL.md
  3. 平台用户级      ~/.workbuddy|.trae|.cursor|.qcoder/skills/<slug>/SKILL.md
  4. 平台项目级      <project>/.workbuddy/skills/<slug>/SKILL.md
  5. 注册表          ~/.workbuddy/skills/.skills_store_lock.json（决定能否斜杠激活）

installed  = 任一路径存在 SKILL.md
activatable= 位于平台可识别目录 且 注册表有条目 且 目录含 _meta.json

用法：
    python check_downstream.py --slug tri-coding
    python check_downstream.py --slug tri-mm --slug tri-music --json
    python check_downstream.py --slug tri-coding --project-dir D:/proj --json

退出码：0=全部已安装  1=存在未安装  2=参数/环境错误
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 平台特征目录段：用户级与项目级共用同一套 <platform_dir>/skills 结构
PLATFORM_DIRS = (".workbuddy", ".trae", ".cursor", ".qcoder")

# 注册表位置（相对 HOME）。仅 workbuddy 平台提供，用于判定「可斜杠激活」
LOCK_REL = Path(".workbuddy") / "skills" / ".skills_store_lock.json"

# 安装 prompt 模板——门A 用户同意后原样发送
INSTALL_PROMPT = "请根据 https://skillhub.cn/install/skillhub.md，安装{slug}"

VERSION_RE = re.compile(r"^version:\s*([0-9]+(?:\.[0-9]+)*)", re.MULTILINE)


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------


def read_version(skill_md: Path) -> Optional[str]:
    """从 SKILL.md frontmatter 读取 version，读不到返回 None。"""
    try:
        head = skill_md.read_text(encoding="utf-8", errors="ignore")[:4000]
    except OSError:
        return None
    m = VERSION_RE.search(head)
    return m.group(1) if m else None


def family_root(script_path: Path) -> Path:
    """家族源码树根目录 = tri-intent 的父目录（scripts/../..）。"""
    return script_path.resolve().parent.parent.parent


def load_registry(home: Path) -> Dict[str, dict]:
    """读取平台注册表，返回 {slug: entry}；读不到返回空字典。"""
    lock = home / LOCK_REL
    if not lock.is_file():
        return {}
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    skills = data.get("skills")
    return skills if isinstance(skills, dict) else {}


# ---------------------------------------------------------------------------
# 候选路径枚举
# ---------------------------------------------------------------------------


def candidate_paths(slug: str, root: Path, project: Path, home: Path) -> List[dict]:
    """按优先级枚举候选安装位置。kind 决定是否计入 activatable。"""
    out: List[dict] = [
        {"kind": "source-tree", "path": root / slug, "platform_visible": False},
        {"kind": "forge-drop", "path": project / ".tribro" / "skills" / slug,
         "platform_visible": False},
    ]
    for pd in PLATFORM_DIRS:
        out.append({
            "kind": f"user-level:{pd}",
            "path": home / pd / "skills" / slug,
            "platform_visible": True,
        })
        out.append({
            "kind": f"project-level:{pd}",
            "path": project / pd / "skills" / slug,
            "platform_visible": True,
        })
    return out


def probe(slug: str, root: Path, project: Path, home: Path,
          registry: Dict[str, dict]) -> dict:
    """检测单个 slug，返回结构化结果。"""
    found: List[dict] = []
    for c in candidate_paths(slug, root, project, home):
        skill_md = c["path"] / "SKILL.md"
        if not skill_md.is_file():
            continue
        found.append({
            "kind": c["kind"],
            "path": str(c["path"]),
            "version": read_version(skill_md),
            "has_meta": (c["path"] / "_meta.json").is_file(),
            "platform_visible": c["platform_visible"],
        })

    entry = registry.get(slug)
    installed = bool(found)
    # 可斜杠激活三件套：平台可见目录 + 注册表条目 + _meta.json
    activatable = bool(
        entry and any(f["platform_visible"] and f["has_meta"] for f in found)
    )

    return {
        "slug": slug,
        "installed": installed,
        "activatable": activatable,
        "version": next((f["version"] for f in found if f["version"]), None),
        "locations": found,
        "registry": entry,
        "install_prompt": None if installed else INSTALL_PROMPT.format(slug=slug),
    }


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------


def render_human(results: List[dict]) -> str:
    lines: List[str] = []
    for r in results:
        if r["installed"]:
            act = "可斜杠激活" if r["activatable"] else "仅内部委派（未注册平台）"
            lines.append(f"[已安装] {r['slug']}  v{r['version'] or '?'}  {act}")
            for loc in r["locations"]:
                lines.append(f"         └─ {loc['kind']}: {loc['path']}")
        else:
            lines.append(f"[未安装] {r['slug']}")
            lines.append(f"         └─ 安装 prompt: {r['install_prompt']}")
    missing = [r["slug"] for r in results if not r["installed"]]
    lines.append("")
    lines.append(
        f"合计 {len(results)} 个下游，未安装 {len(missing)} 个"
        + (f"：{', '.join(missing)}" if missing else "")
    )
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="tri-intent 下游 skill 安装检测（供两道确认门消费）"
    )
    ap.add_argument("--slug", action="append", required=True,
                    help="下游 skill slug，可重复传入（如 I15 音乐子类需 tri-mm + tri-music）")
    ap.add_argument("--project-dir", default=os.getcwd(),
                    help="项目根目录，默认当前工作目录")
    ap.add_argument("--family-root", default=None,
                    help="家族源码树根目录，默认由脚本路径推导")
    ap.add_argument("--json", action="store_true", help="输出 JSON（供 Agent 解析）")
    args = ap.parse_args(argv)

    project = Path(args.project_dir).resolve()
    root = Path(args.family_root).resolve() if args.family_root \
        else family_root(Path(__file__))
    home = Path.home()
    registry = load_registry(home)

    results = [probe(s, root, project, home, registry) for s in args.slug]

    if args.json:
        print(json.dumps({
            "family_root": str(root),
            "project_dir": str(project),
            "registry_found": bool(registry),
            "all_installed": all(r["installed"] for r in results),
            "missing": [r["slug"] for r in results if not r["installed"]],
            "results": results,
        }, ensure_ascii=False, indent=2))
    else:
        print(render_human(results))

    return 0 if all(r["installed"] for r in results) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
