---
name: glossary-schema
description: tri-translate 术语表数据模型 schema。定义三层优先级（A 不可译/B 已批准/C 推荐）+ 字段语义 + JSON 格式，供实现与校验对齐。
---

# tri-translate 术语表 Schema

> 本文件定义 tri-translate 术语表的数据模型，是 glossary.json 的唯一权威定义。
> 实现时 MUST 严格对齐本 schema，NEVER 私自增删字段；扩展须经 SKILL.md §可扩展性 声明。

## 一、JSON 整体结构

```json
{
  "schema_version": 1,
  "terms": [
    {
      "source": "<源词，必填>",
      "target": "<目标译法，必填>",
      "priority": "<A|B|C，必填>",
      "context": "<术语所在上下文，可选>",
      "block_synonyms": ["<屏蔽的错误译法数组，可选>"],
      "status": "<approved|pending|forbidden，默认 approved>",
      "example": "<示例用法，可选>",
      "notes": "<备注，可选>"
    }
  ]
}
```

## 二、字段语义规约

### 2.1 必填字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `source` | string | 非空，唯一 | 源词原文（如 "OpenAI"） |
| `target` | string | 非空 | 目标译法（Priority A 时 = source，即不译） |
| `priority` | enum | "A" \| "B" \| "C" | 优先级（详见 §三） |

### 2.2 可选字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `context` | string | "" | 术语所在上下文（消歧义，如 "company name"） |
| `block_synonyms` | string[] | [] | 屏蔽的错误译法（如 ["开放AI", "开放人工智能"]） |
| `status` | enum | "approved" | approved（已批准）/ pending（待审）/ forbidden（禁用） |
| `example` | string | "" | 示例用法 |
| `notes` | string | "" | 备注 |

## 三、三层优先级语义

| 优先级 | 含义 | 处理方式 | 示例 |
|--------|------|----------|------|
| **A · 不可译** | 永远保留原文，不进入翻译流程 | 隔离区占位符替换 + 译后还原 | OpenAI / ChatGPT / GPT-4 / GitHub / npm |
| **B · 已批准** | MUST 用批准译法，屏蔽 block_synonyms | 翻译时强制替换为 target，若出现 block_synonyms 中的译法 MUST 替换 | "agreement" → "协议"（屏蔽"合约"） |
| **C · 推荐** | 推荐使用，可上下文调整 | 优先用 target，但允许上下文调整 | "deployment" → "部署"（可调整为"上线"） |

## 四、状态机

```
pending ──批准──> approved ──禁用──> forbidden
                       ↑                  │
                       └──恢复────────────┘
```

| 状态 | 含义 | 处理 |
|------|------|------|
| pending | 待审 | 不强制应用，仅参考 |
| approved | 已批准 | 强制应用 |
| forbidden | 禁用 | 永不应用（屏蔽） |

## 五、校验规则

1. **必填字段不可缺**：source / target / priority 三字段缺一不可，校验失败 NEVER 入表。
2. **priority 取值受限**：仅 "A" / "B" / "C"，其它取值校验失败。
3. **source 唯一性**：同一 source 在 terms 数组中 MUST 唯一，重复入表校验失败。
4. **Priority A 的 target = source**：Priority A 不可译，target MUST 与 source 相同。
5. **block_synonyms 不能含 target**：屏蔽列表 NEVER 含批准译法本身。
6. **status 取值受限**：仅 "approved" / "pending" / "forbidden"，其它取值校验失败。

## 六、命名规范

文件名固定为 `glossary.json`，存放于：
- 安装目录：`tri-translate/templates/glossary.json`（默认术语表）
- 运行时：`.tribro/translate/glossary.json`（用户自定义术语表，可覆盖默认）

加载顺序：用户自定义优先 > 默认。

## 七、扩展规则

新增术语条目须经 `TRANSLATE_ADMIN glossary add` 命令，自动校验 schema 后入表。直接编辑 JSON 文件也允许，但下次加载时 MUST 重新校验。
