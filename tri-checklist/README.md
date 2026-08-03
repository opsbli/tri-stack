# tri-checklist · 审计清单生成

> tri-xxx 家族下游执行 skill · 认领 I10 audit-checklist 子类 · 对项目进行全面审计，生成 Markdown 复选框 checklist 供自检/CR/质量保障。

## 特性

- **四维审计**：改动点 / 审查点 / 测试点 / 测试步骤，与 tri-review Phase 1+2 对齐
- **三种 Git 输入模式**：暂存区（`git diff --cached`）/ 工作区（`git diff` + 未跟踪）/ commit id（`git diff <commit>..HEAD`）
- **Markdown 复选框产出**：标准 `- [ ]` 格式，IDE/GitHub 直接渲染勾选
- **严重程度标签**：`[BLOCKER]` / `[MAJOR]` / `[MINOR]` 三级，与 tri-review 审查报告对齐
- **双审批门**：门①审计范围确认 + 门②checklist 交付确认
- **三态上游检测**：快照模式 / 待识别 / 引导安装 / 降级模式
- **敏感文件检测**：自动识别 .env / secret / key / credential / password / token 文件改动
- **零第三方依赖**：脚本仅用 Python 标准库（subprocess/json/re）

## 目录结构

```
tri-checklist/
├── SKILL.md                          # 主入口
├── README.md                         # 本文件
├── CHANGELOG.md                      # 版本变更记录
├── references/
│   ├── audit-checklist-template.md   # 四维审计检查项模板
│   └── git-diff-commands.md          # Git diff 命令参考表（三种模式）
├── scripts/
│   ├── parse_git_diff.py             # Git diff 解析器
│   └── build_checklist.py            # Markdown checklist 组装器
└── tests/
    └── tri-checklist-full-testcases.md  # 全场景测试用例
```

## 安装

```bash
skillhub install tri-checklist --dir <目标目录>
```

## 使用

### 标准模式（经 tri-intent 路由）

用户说「生成审计 checklist」「项目自检清单」「改动审查测试清单」「质量保障 checklist」「commit 提交前检查清单」等，tri-intent 识别为 I10 audit-checklist 子类后路由到本 skill。

### 降级模式（独立使用）

未安装 tri-intent 时可直接调用，需自构造输入：

1. 识别 Git 输入模式（暂存区/工作区/commit id）
2. 运行 `python scripts/parse_git_diff.py --mode <staged|working|commit> --commit <hash> --out diff.json`
3. 准备 template.json（参考 `references/audit-checklist-template.md` 转换为 JSON）
4. 运行 `python scripts/build_checklist.py --diff diff.json --template template.json --out checklist.md`

### parse_git_diff.py 用法

```bash
# 暂存区模式
python scripts/parse_git_diff.py --mode staged --out diff.json

# 工作区模式
python scripts/parse_git_diff.py --mode working --out diff.json

# commit id 模式
python scripts/parse_git_diff.py --mode commit --commit abc1234 --out diff.json

# 仅解析不输出
python scripts/parse_git_diff.py --mode staged --out diff.json --dry-run
```

### build_checklist.py 用法

```bash
# 标准用法
python scripts/build_checklist.py --diff diff.json --template template.json --out checklist.md

# 仅校验不输出
python scripts/build_checklist.py --diff diff.json --template template.json --out dummy.md --dry-run
```

## diff.json 格式

```json
{
  "mode": "staged",
  "commit": null,
  "stats": {"files_changed": 3, "insertions": 70, "deletions": 128},
  "files": [
    {"path": "src/auth/login.ts", "status": "modified", "status_code": "M",
     "insertions": 25, "deletions": 8, "functions": ["login", "validateToken"]}
  ],
  "untracked_files": [],
  "sensitive_files": [],
  "test_files": []
}
```

## template.json 格式

```json
{
  "dimensions": {
    "review": {
      "sections": [
        {"title": "2.1 功能正确性", "items": [
          {"severity": "blocker", "text": "改动实现了预期功能"},
          {"severity": "blocker", "text": "无回归问题"}
        ]}
      ]
    },
    "test": {"sections": [...]},
    "test_steps": {"sections": [...]}
  }
}
```

> 改动点维度（changes）由 build_checklist.py 基于 diff.json 自动生成，无需在 template.json 中定义。

## 测试

```bash
# 全场景测试用例
cat tests/tri-checklist-full-testcases.md
```

## 设计原则

1. **规范是事实源**：四维检查项模板与 Git 命令参考均在 `references/` 单点维护，SKILL.md 仅留指针
2. **确定性算法下沉**：diff 解析与 checklist 组装逻辑在 `scripts/`，避免散文描述让模型自律复现
3. **单文件 Markdown**：产出 checklist 必须单文件，NEVER 多文件
4. **双审批门护栏**：门①范围确认防审计跑偏，门②交付确认防半成品落地
5. **只生成清单不执行审查**：清单供开发者自检或作为 tri-review 审查依据；执行审查由 tri-review 完成
6. **与 tri-review 对齐**：审查点检查项与 tri-review Phase 1+2 维度对齐，便于联动
