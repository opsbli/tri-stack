#!/usr/bin/env python3
"""
tri-checklist Git diff 解析器（确定性算法下沉）

用法:
    python parse_git_diff.py --mode staged --out diff.json
    python parse_git_diff.py --mode working --out diff.json
    python parse_git_diff.py --mode commit --commit abc1234 --out diff.json
    python parse_git_diff.py --mode staged --out diff.json --dry-run

功能:
    1. 按模式执行对应的 git diff 命令
    2. 解析改动文件清单（路径/状态/增删行数）
    3. 解析改动函数清单（基于 hunk 头 @@ ... @@ function_name）
    4. 检测敏感文件（.env/secret/key/credential/password/token）
    5. 检测测试文件（test/spec/__tests__）
    6. 输出 diff.json 结构化数据

零第三方依赖: 仅用 Python 标准库（subprocess/json/re/sys/pathlib）

退出码:
    0 = 成功
    1 = 参数错误/git 命令失败
    2 = 输出写入失败
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ============ 常量 ============

# 敏感文件模式（用于 .env / secret / key 等文件检测）
SENSITIVE_PATTERN = re.compile(r"\.env|secret|key|credential|password|token", re.IGNORECASE)

# 测试文件模式
TEST_PATTERN = re.compile(r"test|spec|__tests__", re.IGNORECASE)

# 函数名提取模式（从 hunk 头 @@ -a,b +c,d @@ function_name）
# 支持 C/Java/Go/Python/JS/TS 等语言的函数签名
HUNK_FUNC_PATTERN = re.compile(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@\s*(.*)$")

# 文件状态码映射
STATUS_MAP = {
    "A": "added", "M": "modified", "D": "deleted",
    "R": "renamed", "C": "copied", "T": "type-changed", "U": "unmerged",
}

# ============ Git 命令构造 ============

def build_diff_command(mode, commit=None):
    """按模式构造 git diff 命令"""
    if mode == "staged":
        return ["git", "diff", "--cached", "--numstat", "--name-status"]
    elif mode == "working":
        return ["git", "diff", "--numstat", "--name-status"]
    elif mode == "commit":
        if not commit:
            raise ValueError("commit id 模式必须提供 --commit 参数")
        return ["git", "diff", f"{commit}..HEAD", "--numstat", "--name-status"]
    else:
        raise ValueError(f"未知模式: {mode}")


def build_hunk_command(mode, commit=None, file_path=None):
    """构造获取 hunk 头的命令（用于提取函数名）"""
    if mode == "staged":
        base = ["git", "diff", "--cached"]
    elif mode == "working":
        base = ["git", "diff"]
    elif mode == "commit":
        base = ["git", "diff", f"{commit}..HEAD"]
    else:
        raise ValueError(f"未知模式: {mode}")
    if file_path:
        base.extend(["--", file_path])
    return base


def get_untracked_files():
    """工作区模式获取未跟踪文件"""
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


# ============ 解析逻辑 ============

def parse_name_status(output):
    """解析 --name-status 输出，返回文件清单（含状态）"""
    files = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status_code = parts[0][0]  # 取首字符（R99 → R）
        status = STATUS_MAP.get(status_code, "unknown")
        # R/C 状态有原路径和新路径
        if status_code in ("R", "C") and len(parts) >= 3:
            path = parts[2]
        else:
            path = parts[1]
        files.append({"path": path, "status": status, "status_code": status_code})
    return files


def parse_numstat(output, files):
    """解析 --numstat 输出，补充增删行数"""
    numstat_map = {}
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added, deleted, path = parts[0], parts[1], parts[2]
        try:
            numstat_map[path] = {"insertions": int(added) if added != "-" else 0,
                                  "deletions": int(deleted) if deleted != "-" else 0}
        except ValueError:
            numstat_map[path] = {"insertions": 0, "deletions": 0}
    for f in files:
        stat = numstat_map.get(f["path"], {"insertions": 0, "deletions": 0})
        f["insertions"] = stat["insertions"]
        f["deletions"] = stat["deletions"]
    return files


def extract_functions(mode, commit, file_path):
    """从 hunk 头提取改动的函数名"""
    cmd = build_hunk_command(mode, commit, file_path)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        return []
    functions = []
    seen = set()
    for line in result.stdout.splitlines():
        m = HUNK_FUNC_PATTERN.match(line)
        if m:
            func_ctx = m.group(1).strip()
            if func_ctx and func_ctx not in seen:
                # 提取函数名（取第一个标识符）
                func_name = re.split(r"[\s\(\{]", func_ctx)[0]
                if func_name and func_name not in seen:
                    seen.add(func_name)
                    functions.append(func_name)
    return functions


def run_git(cmd):
    """执行 git 命令，返回 stdout（失败返回空并打印错误）"""
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"[ERROR][git] {' '.join(cmd)} 失败: {result.stderr.strip()}", file=sys.stderr)
        return None
    return result.stdout


def parse_diff(mode, commit=None):
    """主解析函数：返回结构化 diff 数据"""
    # 1. 获取文件清单 + 状态
    cmd = build_diff_command(mode, commit)
    output = run_git(cmd)
    if output is None:
        return None

    # --name-status 与 --numstat 合并输出，按段解析
    # 实际 git diff 不支持同时输出两者，故分两次
    name_status_cmd = build_diff_command(mode, commit)[:-1] + ["--name-status"]
    numstat_cmd = build_diff_command(mode, commit)[:-1] + ["--numstat"]

    name_status_out = run_git(name_status_cmd)
    numstat_out = run_git(numstat_cmd)
    if name_status_out is None or numstat_out is None:
        return None

    files = parse_name_status(name_status_out)
    files = parse_numstat(numstat_out, files)

    # 2. 工作区模式补充未跟踪文件
    untracked = []
    if mode == "working":
        untracked = get_untracked_files()
        for path in untracked:
            files.append({"path": path, "status": "untracked", "status_code": "?",
                          "insertions": 0, "deletions": 0})

    # 3. 提取每个文件的改动函数
    for f in files:
        if f["status"] in ("deleted", "untracked"):
            f["functions"] = []
            continue
        f["functions"] = extract_functions(mode, commit, f["path"])

    # 4. 检测敏感文件与测试文件
    sensitive_files = [f["path"] for f in files if SENSITIVE_PATTERN.search(f["path"])]
    test_files = [f["path"] for f in files if TEST_PATTERN.search(f["path"])]

    # 5. 统计
    total_insertions = sum(f["insertions"] for f in files)
    total_deletions = sum(f["deletions"] for f in files)

    return {
        "mode": mode,
        "commit": commit,
        "stats": {
            "files_changed": len(files),
            "insertions": total_insertions,
            "deletions": total_deletions,
        },
        "files": files,
        "untracked_files": untracked,
        "sensitive_files": sensitive_files,
        "test_files": test_files,
    }


# ============ 主入口 ============

def main():
    parser = argparse.ArgumentParser(description="tri-checklist Git diff 解析器")
    parser.add_argument("--mode", required=True, choices=["staged", "working", "commit"],
                        help="Git 输入模式: staged(暂存区) / working(工作区) / commit(commit id)")
    parser.add_argument("--commit", help="commit id（仅 commit 模式需要）")
    parser.add_argument("--out", required=True, help="输出 diff.json 路径")
    parser.add_argument("--dry-run", action="store_true", help="仅解析不输出")
    args = parser.parse_args()

    if args.mode == "commit" and not args.commit:
        print("[ERROR][参数] commit 模式必须提供 --commit", file=sys.stderr)
        sys.exit(1)

    data = parse_diff(args.mode, args.commit)
    if data is None:
        print("[ERROR][解析] Git diff 解析失败", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"[INFO][校验] 通过。模式={args.mode}, 文件数={data['stats']['files_changed']}, "
              f"+{data['stats']['insertions']}/-{data['stats']['deletions']}", file=sys.stderr)
        sys.exit(0)

    try:
        Path(args.out).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[ERROR][写入] diff.json 写入失败: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"[INFO][完成] diff.json 已生成: {args.out}", file=sys.stderr)
    print(f"[INFO][摘要] 模式={args.mode}, 文件数={data['stats']['files_changed']}, "
          f"+{data['stats']['insertions']}/-{data['stats']['deletions']}, "
          f"敏感文件={len(data['sensitive_files'])}, 测试文件={len(data['test_files'])}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
