---
name: never-translate-schema
description: tri-translate 不译规则集数据模型 schema。定义 19 类不译要素 + 正则模式 + 占位符规则，供隔离区提取算法对齐。
---

# tri-translate 不译规则集 Schema

> 本文件定义 tri-translate 不译规则集的数据模型，是 never-translate.json 的唯一权威定义。
> 实现时 MUST 严格对齐本 schema，NEVER 私自增删 19 类预置规则；扩展须经 SKILL.md §可扩展性 声明。

## 一、JSON 整体结构

```json
{
  "schema_version": 1,
  "rules": [
    {
      "id": "<规则ID，如 PATH_ABS>",
      "name": "<规则名，如 绝对路径>",
      "pattern": "<正则模式>",
      "placeholder": "<占位符模板，含 {N} 占位，如 __PATH_{N}__>",
      "description": "<规则描述>",
      "preserve": true
    }
  ]
}
```

## 二、字段语义规约

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | string | 非空，唯一 | 规则 ID（大写+下划线，如 PATH_ABS） |
| `name` | string | 非空 | 规则中文名 |
| `pattern` | string | 非空，合法正则 | 识别模式（regex） |
| `placeholder` | string | 非空，含 `{N}` | 占位符模板，`{N}` 在执行时替换为序号 |
| `description` | string | 可选 | 规则描述 |
| `preserve` | boolean | 默认 true | 是否保留原文（false=删除，仅特殊场景） |

## 三、19 类预置规则

| # | id | name | pattern（简写） | placeholder |
|---|----|------|----------------|-------------|
| 1 | PATH_ABS | 绝对路径 | `/[a-zA-Z]?:?\\?[^/\s]+[/\][^/\s]+` | `__PATH_{N}__` |
| 2 | PATH_REL | 相对路径 | `(\.\./|\./)[^\s]+` | `__PATH_{N}__` |
| 3 | CODE_FENCED | 围栏代码块 | ` ```[\s\S]*?``` ` | `__CODEBLOCK_{N}__` |
| 4 | CODE_INLINE | 行内代码 | ` `[^`]+` ` | `__CODE_{N}__` |
| 5 | CMD_LINE | 命令行 | `^[$>]\s+\w+` 或行首 `$ ` | `__CMD_{N}__` |
| 6 | API_ENDPOINT | API 端点 | `(GET\|POST\|PUT\|DELETE\|PATCH)\s+/[^\s]+` | `__API_{N}__` |
| 7 | URL | URL | `https?://[^\s]+` | `__URL_{N}__` |
| 8 | DOMAIN | 域名 | `[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` | `__DOMAIN_{N}__` |
| 9 | EMAIL | 邮箱 | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+` | `__EMAIL_{N}__` |
| 10 | CONFIG_KEY | 配置键 | YAML `^\w+:` 或 JSON `"\w+":` 键名 | 保留键名 |
| 11 | ENV_VAR | 环境变量 | `\$[A-Z_][A-Z0-9_]*` 或 `\$\{[A-Z_]+\}` | `__ENV_{N}__` |
| 12 | VERSION | 版本号 | `v?\d+\.\d+(\.\d+)?` | 保留 |
| 13 | SHA_HASH | SHA/哈希 | `[0-9a-f]{7,40}` | 保留 |
| 14 | BRAND_NAME | 品牌名/产品名 | 术语表 Priority A | 保留 |
| 15 | TRADEMARK | 商标 | `™\|®` | 保留 |
| 16 | ACRONYM | 首字母缩写 | `[A-Z]{2,}` 且非全大写单词 | 保留（首现可附中文） |
| 17 | TECH_IDENTIFIER | 技术标识符 | 驼峰或下划线变量/函数/类名 | 保留 |
| 18 | NUMBER_UNIT | 数字与单位 | `\d+(\.\d+)?\s?[A-Za-z%]+` | 保留 |
| 19 | DATETIME | 日期时间 | ISO 8601 或文档约定格式 | 保留 |

## 四、占位符规则

### 4.1 占位符格式

`__<TYPE>_<N>__`

- `<TYPE>`：占位类型（大写），如 PATH / CODE / URL
- `<N>`：序号（从 1 递增），如 1, 2, 3

### 4.2 占位符示例

```
原文：See [documentation](https://example.com/docs) at /usr/local/bin.
占位后：See [documentation](__URL_1__) at __PATH_1__.
映射表：
  __URL_1__: https://example.com/docs
  __PATH_1__: /usr/local/bin
```

### 4.3 占位符还原

译后 MUST 还原所有占位符。验证：

```
残留检测：regex.search(final_text, r"__\w+_\d+__") == None
若残留：MUST 人工介入或重译，原文不可丢
```

## 五、规则优先级

19 类规则按以下顺序扫描（避免冲突）：

1. CODE_FENCED（先抓大块代码）
2. CODE_INLINE（再抓行内代码）
3. URL（先于域名识别，避免 URL 被切为域名）
4. API_ENDPOINT
5. EMAIL
6. PATH_ABS / PATH_REL
7. CMD_LINE
8. ENV_VAR
9. VERSION / SHA_HASH / NUMBER_UNIT / DATETIME
10. BRAND_NAME / TRADEMARK / ACRONYM / TECH_IDENTIFIER（结合术语表与上下文）
11. CONFIG_KEY / DOMAIN（最后识别，依赖上下文）

## 六、校验规则

1. **必填字段不可缺**：id / name / pattern / placeholder 四字段缺一不可。
2. **id 唯一性**：同一 id 在 rules 数组中 MUST 唯一。
3. **pattern 合法性**：MUST 是合法正则，编译失败 NEVER 入表。
4. **placeholder 含 {N}**：MUST 含 `{N}` 占位符，否则校验失败。
5. **preserve 默认 true**：删除类规则（preserve=false）MUST 显式声明并标注理由。

## 七、命名规范

文件名固定为 `never-translate.json`，存放于：
- 安装目录：`tri-translate/templates/never-translate.json`（默认规则集）
- 运行时：`.tribro/translate/never-translate.json`（用户自定义规则，与默认合并）

加载顺序：默认 + 用户自定义合并，用户自定义优先（同 id 时覆盖默认）。

## 八、扩展规则

新增不译规则须经 `TRANSLATE_ADMIN never-translate add` 命令，自动校验 schema 后入表。直接编辑 JSON 文件也允许，但下次加载时 MUST 重新校验。

扩展示例：项目内部 URL 域名（如 `internal.company.com`）可加规则强制不译。
