#!/usr/bin/env python3
"""tri-stack 批量安装脚本：为仓库内的 tri-* skill 创建 junction 到 AI 工具的 skills 目录。

用法：
    python ops/install-skills.py --target ~/.workbuddy/skills   # 建议先 --dry-run
    python ops/install-skills.py --target ~/.workbuddy/skills --dry-run
    python ops/install-skills.py --target ~/.workbuddy/skills --remove  # 卸载

原理：用 Windows junction（`mklink /J`）将仓库中的 skill 目录链接到
AI 工具的 skills 目录。源始终在仓库（单源），改仓库即生效，
NEVER 复制文件（会破坏单源原则、产生漂移）。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for cand in (start, *start.parents):
        if (cand / ".git").exists():
            return cand
    return start


REPO = find_repo_root(Path(__file__).resolve().parent)
EXCLUDE = {"tri-mece-audit"}  # 非 skill 目录


def get_skills() -> list[Path]:
    return sorted(p for p in REPO.glob("tri-*")
                  if p.is_dir() and (p / "SKILL.md").is_file()
                  and p.name not in EXCLUDE)


def is_junction(p: Path) -> bool:
    """判断路径是否为 junction/symlink。"""
    if not p.exists():
        return False
    try:
        return p.is_symlink() or bool(os.lstat(str(p)).st_file_attributes & 0x400)
    except (OSError, AttributeError):
        return False


def create_junction(src: Path, dst: Path) -> str:
    # mklink /J 在中文 Windows 上输出 GBK 编码，用 mbcs 解码避免 UnicodeDecodeError
    r = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(dst), str(src)],
        capture_output=True, text=True, encoding="mbcs", errors="replace")
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def remove_entry(p: Path) -> str:
    if is_junction(p):
        # junction 用 rmdir 删除（不删源）
        r = subprocess.run(["cmd", "/c", "rmdir", str(p)],
                           capture_output=True, text=True)
        return "已移除" if r.returncode == 0 else f"失败: {r.stderr}"
    elif p.is_dir():
        return "⚠ 是真实目录（非 junction），请手动确认后删除"
    return "不存在"


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-stack skill 批量安装（junction）")
    ap.add_argument("--target", required=True, help="AI 工具的 skills 目录（如 ~/.workbuddy/skills）")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不执行")
    ap.add_argument("--remove", action="store_true", help="卸载（移除 junction，不删源）")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    skills = get_skills()

    if args.remove:
        print(f"# 卸载 {len(skills)} 个 skill 的 junction\n")
        removed = 0
        for src in skills:
            dst = target / src.name
            if dst.exists() or dst.is_symlink():
                if not args.dry_run:
                    result = remove_entry(dst)
                    print(f"  {'✅' if '已移除' in result else '⚠'} {src.name}: {result}")
                else:
                    print(f"  [dry] {src.name}: 将移除")
                removed += 1
            else:
                print(f"  ⏭ {src.name}: 不存在")
        print(f"\n卸载 {removed} 个")
        return 0

    # 安装
    print(f"# 安装 {len(skills)} 个 skill → {target}\n")
    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)

    ok = skip = fail = 0
    for src in skills:
        dst = target / src.name
        if dst.exists():
            if is_junction(dst):
                # 检查 junction 是否指向正确位置
                try:
                    real = dst.resolve()
                    if real == src.resolve():
                        skip += 1
                        print(f"  ⏭ {src.name}（junction 已存在且正确）")
                        continue
                except OSError:
                    pass
                # junction 指向错误 → 重建
                if not args.dry_run:
                    remove_entry(dst)
                    result = create_junction(src, dst)
                ok += 1
                print(f"  🔄 {src.name}（junction 指向错误，已重建）")
            else:
                print(f"  ⚠ {src.name}: 目标已是真实目录，跳过（请手动处理）")
                fail += 1
        else:
            if not args.dry_run:
                result = create_junction(src, dst)
                if "失败" in result:
                    fail += 1
                    print(f"  🔴 {src.name}: {result}")
                    continue
            ok += 1
            print(f"  ✅ {src.name}")

    print(f"\n结果：✅ {ok} · ⏭ 跳过 {skip} · 🔴 失败 {fail}")
    if args.dry_run:
        print("\n（dry-run，未实际执行；去掉 --dry-run 执行安装）")
    else:
        print(f"\n下一步：运行版本门验证安装 → python <skill>/scripts/check_update.py --slug <slug> --json")

    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
