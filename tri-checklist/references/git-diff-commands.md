# Git diff 命令参考表

> 本文件是 tri-checklist SKILL.md §方法论 三种 Git 输入模式的命令参考表。SKILL.md 仅留概览，详细命令在此检索。

> **grep 检索模式**：`grep -n "§<模式>" references/git-diff-commands.md`（如 `grep -n "§暂存区" ` 定位暂存区模式）

---

## §暂存区模式（staged）

**适用场景**：已 `git add` 但未 `git commit`，提交前自检。

### 核心命令

```bash
# 改动文件清单（含状态）
git diff --cached --name-status

# 改动详情（含上下文）
git diff --cached -U10

# 改动统计
git diff --cached --stat

# 改动文件数与行数
git diff --cached --shortstat
```

### 输出示例

```
$ git diff --cached --name-status
M       src/auth/login.ts
A       src/utils/helper.ts
D       src/old/deprecated.ts

$ git diff --cached --shortstat
 3 files changed, 70 insertions(+), 128 deletions(-)
```

### 状态码含义

| 状态码 | 含义 |
|---|---|
| `A` | Added（新增） |
| `M` | Modified（修改） |
| `D` | Deleted（删除） |
| `R` | Renamed（重命名） |
| `C` | Copied（复制） |
| `T` | Type changed（类型变更，如文件→符号链接） |
| `U` | Unmerged（合并冲突未解决） |

---

## §工作区模式（working）

**适用场景**：已改但未 `git add`，开发中自检。

### 核心命令

```bash
# 改动文件清单（含状态，含未跟踪文件）
git status --porcelain

# 已跟踪文件的改动详情
git diff -U10

# 已跟踪文件的改动统计
git diff --stat

# 未跟踪文件清单
git ls-files --others --exclude-standard
```

### 输出示例

```
$ git status --porcelain
 M src/auth/login.ts         # 工作区已改，未暂存
?? src/new/file.ts           # 未跟踪文件
```

### 状态码含义（双字符）

| 第一字符（暂存区） | 第二字符（工作区） | 含义 |
|---|---|---|
| ` ` `M` | 工作区修改，未暂存 |
| `M` ` ` | 暂存区修改，工作区无额外改动 |
| `M` `M` | 暂存区与工作区均有修改 |
| `A` ` ` | 暂存区新增 |
| `D` ` ` | 暂存区删除 |
| `?` `?` | 未跟踪文件 |
| `U` `U` | 合并冲突 |

### 工作区模式注意事项

- `git diff` 只显示**已跟踪文件**的工作区改动，**不含未跟踪文件**
- 未跟踪文件需用 `git ls-files --others --exclude-standard` 单独列出
- parse_git_diff.py 在工作区模式会合并 `git diff` + `git ls-files` 结果

---

## §commit id 模式（commit）

**适用场景**：审查特定 commit 范围，如审查 `abc1234..HEAD` 的所有改动。

### 核心命令

```bash
# 改动文件清单（commit 范围）
git diff <commit>..HEAD --name-status

# 改动详情（commit 范围）
git diff <commit>..HEAD -U10

# 改动统计（commit 范围）
git diff <commit>..HEAD --stat

# commit 列表（commit 范围）
git log <commit>..HEAD --oneline

# 单个 commit 的改动
git show <commit> --name-status
```

### commit 范围语法

| 语法 | 含义 |
|---|---|
| `<commit>..HEAD` | 从 commit（不含）到 HEAD（含）的所有改动 |
| `<commit1>..<commit2>` | 从 commit1（不含）到 commit2（含） |
| `<commit>...HEAD` | 三点形式，比较 merge-base（用于分支比较） |
| `<commit>^!` | 单个 commit（不含其父） |
| `<commit>` | 单个 commit（含其父，等价于 `<commit>^!` 用 `git show`） |

### 输出示例

```
$ git diff abc1234..HEAD --name-status
M       src/auth/login.ts
A       src/utils/helper.ts
D       src/old/deprecated.ts

$ git log abc1234..HEAD --oneline
def5678 feat: add login validation
ghi9012 fix: token refresh bug
jkl3456 refactor: extract date formatter
```

### commit id 模式注意事项

- `<commit>` 可以是完整 SHA-1、短 SHA-1、分支名、标签名或 `HEAD~N`
- 建议使用短 SHA-1（前 7-8 位），完整 SHA-1 太长
- 若 commit 不存在，git 会报错 `fatal: bad revision`

---

## 通用辅助命令

### 敏感文件检测

```bash
# 检测改动中是否含敏感文件
git diff --cached --name-only | grep -iE "\.env|secret|key|credential|password|token"
git diff --name-only | grep -iE "\.env|secret|key|credential|password|token"
git diff <commit>..HEAD --name-only | grep -iE "\.env|secret|key|credential|password|token"

# 检测改动中是否含密钥模式
git diff --cached | grep -iE "(api[_-]?key|secret|password|token)\s*[=:]\s*['\"]"
```

### 大改动文件检测

```bash
# 改动行数最多的 5 个文件
git diff --cached --stat | sort -t'|' -k2 -rn | head -5
git diff --stat | sort -t'|' -k2 -rn | head -5
git diff <commit>..HEAD --stat | sort -t'|' -k2 -rn | head -5
```

### 测试文件检测

```bash
# 改动中的测试文件
git diff --cached --name-only | grep -iE "test|spec|__tests__"
git diff --name-only | grep -iE "test|spec|__tests__"
git diff <commit>..HEAD --name-only | grep -iE "test|spec|__tests__"
```

---

## parse_git_diff.py 调用示例

```bash
# 暂存区模式
python scripts/parse_git_diff.py --mode staged --out diff.json

# 工作区模式
python scripts/parse_git_diff.py --mode working --out diff.json

# commit id 模式
python scripts/parse_git_diff.py --mode commit --commit abc1234 --out diff.json

# 仅解析不输出（dry-run）
python scripts/parse_git_diff.py --mode staged --out diff.json --dry-run
```

输出 diff.json 格式：

```json
{
  "mode": "staged",
  "commit": null,
  "stats": {"files_changed": 3, "insertions": 70, "deletions": 128},
  "files": [
    {"path": "src/auth/login.ts", "status": "M", "insertions": 25, "deletions": 8, "functions": ["login", "validateToken"]},
    {"path": "src/utils/helper.ts", "status": "A", "insertions": 45, "deletions": 0, "functions": ["formatDate", "parseQuery"]}
  ],
  "sensitive_files": [],
  "test_files": []
}
```
