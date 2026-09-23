---
name: release-notes
description: 从工单/PRD/变更日志生成面向用户的发布说明，按类别（新功能/改进/修复）组织。
source: pm-skills-main/pm-execution/skills/release-notes/SKILL.md
domain: 执行
---

# 发布说明生成（release-notes）

> 蒸馏自 `release-notes`｜域：执行｜源词数：≈420

## 必含章节清单（MUST-SECTIONS）

- [ ] New Features — 全新能力
- [ ] Improvements — 现有功能增强
- [ ] Bug Fixes — 已解决问题
- [ ] Breaking Changes — 需用户操作（迁移/API 变更，若有）

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Deprecations —  sunset 的功能

## 逐段引导问题

- **Gather**：从工单/变更日志/PRD 提取「改了什么、影响谁、为何重要」。
- **Categorize**：New Features / Improvements / Bug Fixes / Breaking Changes / Deprecations。
- **Write**：每条以用户收益开头（非技术改动）；用平实语言；1-3 句；提供截图（若有）。
- **Tone**：B2B 专业、消费级友好、API 开发者向。

## 输出模板

```markdown
# [Product Name] — [Version / Date]
## New Features
- **[Feature]**: [1-2 sentence user benefit]
## Improvements
- **[Area]**: [what got better]
## Bug Fixes
- Fixed [issue in user terms]
## Breaking Changes (if any)
- **Action required**: [what users need to do]
```

## 输出命名规则

源文件未规定（save as markdown；可转 HTML 等）

## 关键规则

- 技术→用户语言：如「实现 Redis 缓存」→「仪表盘加载快至 3×」。
- 每条 1-3 句，避免内部代号/工单号。
- 先讲最具影响力变更。

## Checkpoint

> （源未设 checkpoint）

## Further Reading

- （源未提供 Further Reading 或全部不合规，已丢弃）
