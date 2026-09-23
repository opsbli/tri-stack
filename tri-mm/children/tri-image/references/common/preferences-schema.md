# 扩展偏好键空间（公共层 · 合并后单一命名空间）

> 合并前，各子场景各自维护一份偏好文件与各自的命名空间，导致同一用户可能被重复追问同一件事。合并后**全 skill 单一命名空间**：一次配置，七场景通用。

## 查找顺序（最先命中即生效）

| 优先级 | 路径 | 作用域 |
|---|---|---|
| 1 | `.tri-image/tri-image/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/tri-image/EXTEND.md` | XDG |
| 3 | `$HOME/.tri-image/EXTEND.md` | 用户级 |

未命中 → **⛔ 阻断**：MUST 先跑首次配置流程（见 SKILL.md §步骤 0），再进入任何其它步骤。

> 兼容旧路径：若存在历史 `.tri-image/image-engine-legacy/EXTEND.md` 且新路径不存在，运行时将其迁移到新路径；两者同时存在时以新路径为准。

## 引擎键（Track-R · T2）

| 键 | 说明 | 默认 |
|---|---|---|
| `default_provider` | google / openai / azure / openrouter / dashscope / zai / minimax / jimeng / seedream / replicate / agnes / codex-cli | 自動 |
| `default_quality` | `normal` / `2k` | `2k` |
| `default_aspect_ratio` | `1:1` / `16:9` / `9:16` / `4:3` / `3:4` / `2.35:1` | `1:1` |
| `default_image_size` | `1K` / `2K` / `4K`（Google / OpenRouter） | 由 quality 推导 |
| `default_image_api_dialect` | `openai-native` / `ratio-metadata` | `openai-native` |
| `default_model.<provider>` | 各 provider 默认模型 | 内置默认 |
| `max_workers` | 批处理并发上限 | 10 |
| `provider_limits.<provider>.concurrency` | 单 provider 并发 | 内置调优值 |
| `provider_limits.<provider>.start_interval_ms` | 起调间隔 | 内置调优值 |

## 生图公共键

| 键 | 说明 |
|---|---|
| `preferred_image_backend` | `auto`（默认）/ `ask` / 具体后端标识 |
| `generation_batch_size` | 并行派发批量，默认 `4` |
| `language` | 图上文本语言（en / zh / ja 等） |
| `default_output_dir` | `inline`（默认）/ `subdir` / `independent`，见 `output-contract.md` |
| `quick_mode` | 长期跳过确认门（等价每次 `--quick`） |
| `watermark` | 见 `watermark-guide.md` |

## 场景专属键

| 场景 | 键 |
|---|---|
| 封面图 | `preferred_type`、`preferred_palette`、`preferred_rendering`、`preferred_text`、`preferred_mood`、`preferred_font`、`default_aspect` |
| 信息图 | `preferred_layout`、`preferred_style`、`preferred_aspect`、`custom_styles` |
| 文章配图 | `preferred_style`、`preferred_palette`、`preferred_density` |
| 社媒卡片 | `preferred_style`、`preferred_layout`、`preferred_palette`、`preferred_count` |
| 幻灯片 | `style`、`texture`、`mood`、`typography`、`density`、`audience`、`review` |
| 漫画 | `preferred_art`、`preferred_tone`、`preferred_layout`、`preferred_aspect`、`character_presets` |
| 结构图 | `theme`（固定暗色，可扩展）、`default_scale`（@2x 默认 2） |

## 修改方式

- 直接编辑 EXTEND.md（本文件即 schema）；
- 或删除 EXTEND.md（/ 说「重新配置」），下次运行重新触发首次配置；
- 常用单行改动：`preferred_image_backend: ask`（每次都问后端）、`quick_mode: true`（免确认）、`watermark.enabled: true`。
