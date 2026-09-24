#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目技术栈扫描脚本（确定性逻辑，配合 tri-init SKILL.md 使用）。

扫描项目目录，检测技术栈（按 references/tech-stack-detection.md 规则），
输出 JSON 结果供 prompt 层消费。

用法：
    python scripts/project-scan.py --dir <项目根目录> [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def scan_tech_stack(d: Path) -> dict:
    result = {"dir": str(d), "stack": [], "code_generator": None, "db_conventions": None}

    def has(name): return (d / name).is_file()

    # Java / Maven
    if has("pom.xml"):
        pom = read(d / "pom.xml")
        java_ver = re.search(r"<java\.version>([^<]+)</java\.version>", pom)
        group = re.search(r"<groupId>([^<]+)</groupId>", pom)
        boot = re.search(r"spring-boot-starter-parent.*?<version>([^<]+)</version>", pom, re.S)
        modules = re.findall(r"<module>([^<]+)</module>", pom)
        result["stack"].append({"name": "Java/Maven", "java_version": java_ver.group(1) if java_ver else "?", "group_id": group.group(1) if group else "?"})
        if boot:
            result["stack"].append({"name": "Spring Boot", "version": boot.group(1)})
        if modules:
            result["stack"].append({"name": "Maven Modules", "list": modules})

    # RuoYi
    ruoyi_mods = [p.name for p in d.iterdir() if p.is_dir() and p.name.startswith("ruoyi-")] if d.is_dir() else []
    if ruoyi_mods:
        result["stack"].append({"name": "RuoYi Framework", "modules": ruoyi_mods})
        result["code_generator"] = {"name": "RuoYi Generator", "module": "ruoyi-generator" if "ruoyi-generator" in ruoyi_mods else "unknown"}
        # 审计字段
        base_entity = list(d.rglob("BaseEntity.java"))
        if base_entity:
            be = read(base_entity[0])
            fields = re.findall(r"private\s+(\w+)\s+(\w+);", be)
            result["db_conventions"] = {
                "source": "BaseEntity.java",
                "audit_fields": [{"name": f, "type": t} for t, f in fields if f not in ("serialVersionUID", "params", "searchValue")],
            }
        tenant_entity = list(d.rglob("TenantEntity.java"))
        if tenant_entity:
            te = read(tenant_entity[0])
            tf = re.findall(r"private\s+(\w+)\s+(\w+);", te)
            if result["db_conventions"]:
                result["db_conventions"]["tenant_fields"] = [{"name": f, "type": t} for t, f in tf]

    # TypeScript / Vite / Vue / React
    if has("package.json"):
        try:
            pkg = json.loads(read(d / "package.json"))
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            if "typescript" in deps:
                result["stack"].append({"name": "TypeScript", "version": deps["typescript"]})
            if "vite" in deps:
                result["stack"].append({"name": "Vite", "version": deps["vite"]})
            if "vue" in deps:
                result["stack"].append({"name": "Vue", "version": deps["vue"]})
            if "element-plus" in deps:
                result["stack"].append({"name": "Element Plus", "version": deps["element-plus"]})
            if "react" in deps:
                result["stack"].append({"name": "React", "version": deps["react"]})
            if "pinia" in deps:
                result["stack"].append({"name": "Pinia", "version": deps["pinia"]})
            if "unocss" in deps:
                result["stack"].append({"name": "UnoCSS", "version": deps["unocss"]})
            result["stack"].append({"name": "Package Manager", "tool": "pnpm" if (d / "pnpm-lock.yaml").is_file() else "npm"})
        except json.JSONDecodeError:
            pass

    # Go
    if has("go.mod"):
        result["stack"].append({"name": "Go", "version": read(d / "go.mod").splitlines()[0].replace("module ", "")})

    # Python
    if has("requirements.txt") or has("pyproject.toml"):
        result["stack"].append({"name": "Python"})

    # Docker / CI
    if has("Dockerfile") or has("docker-compose.yml"):
        result["stack"].append({"name": "Docker"})
    if has("Jenkinsfile"):
        result["stack"].append({"name": "Jenkins CI"})

    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="项目根目录")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    d = Path(args.dir).resolve()
    if not d.is_dir():
        print(f"目录不存在: {d}", file=sys.stderr)
        return 2

    result = scan_tech_stack(d)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"# 项目扫描结果：{d}\n")
        for s in result["stack"]:
            print(f"  ✅ {s['name']}: {json.dumps({k:v for k,v in s.items() if k!='name'}, ensure_ascii=False)}")
        if result["code_generator"]:
            print(f"\n  代码生成器: {result['code_generator']}")
        if result["db_conventions"]:
            print(f"  数据库规范: {json.dumps(result['db_conventions'], ensure_ascii=False)[:200]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
