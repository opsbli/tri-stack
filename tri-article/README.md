# 去AI化文章生成（tri-article）

通用「去 AI 化」技术文章生成 skill：把任意技术主题写成**读起来像真人随手写**的文章，而非教科书 / ChatGPT 范文。作者人设、要植入的产品、保存路径等「具体数据」全部由用户一次填写、长期复用，不写死在 skill 内。

## 特性

- **通用引擎**：去 AI 化写作规则（禁用词、口语感、视角库、结构模式、质量门禁）与具体领域/人设解耦，换主题零改 skill。
- **去 AI 化引擎委派（tri-humanize）**：草稿完成后委派家族横向 skill `tri-humanize`（HUMANIZE-EMBED）做 35 种 AI 写作模式改写；缺失时回退内置 `de-ai-rules` 并声明降级，保证独立运行。
- **占位符 + profile 机制**：所有具体数据走 `{{占位符}}`，首次运行反问用户后落盘 `.tribro/article/profile.md`，每次生成先替换再执行。
- **去 AI 化质量门禁**：13 项一票否决自查（完整清单见 `references/de-ai-rules.md`），命中即重写。
- **可选产品自然植入**：配置开启后按「润物细无声」三层约束植入，绝不写成广告。
- **独立运行 / 下游接入 tri-intent**：默认独立工作；经 tri-intent 路由时读取快照直接执行，绝不重识别意图。

## 目录结构

```
tri-article/
├── SKILL.md                       主入口
├── README.md                      本文件
├── CHANGELOG.md                   变更记录
├── hooks/                         辅助脚本（纯标准库）
│   └── index.py                   文章索引与去重（dedup/add/search/list）
├── references/                    静态参考资料
│   └── de-ai-rules.md             去 AI 化引擎完整参考（禁用词/视角库/结构模式/门禁清单；tri-humanize 缺失时的降级回退引擎）
├── templates/
│   └── profile-skeleton.md        首次初始化复制填写的占位符骨架
└── tests/
    └── tri-article-full-testcases.md  全场景测试用例
```

## 安装

作为 tri-xxx 家族成员，可独立安装使用；若希望 tri-intent 自动路由到此，额外安装上游：

```
skillhub install tri-article
# 可选：skillhub install tri-intent
```

## 使用

1. **首次使用**：直接说「帮我写一篇去 AI 化的技术文章」，skill 会反问你人设、保存路径、选题领域、是否植入产品，并保存为 profile。
2. **常规生成**：再次说「写篇文章」，skill 自动读取 profile 替换占位符并生成，无需重复填表。
3. **修改配置**：编辑 `.tribro/article/profile.md`，或说「重新配置 tri-article」。

## 测试

见 `tests/tri-article-full-testcases.md`，覆盖占位符替换、去 AI 化门禁、产品植入开关、独立/接入两种模式等全场景。

## 设计原则

- **具体数据不写死**：skill 本体只放通用写作引擎，所有可变信息参数化。
- **首问即存、后续复用**：用户只需填一次，长期复用，符合「反问 → 保存 → 替换」闭环。
- **家族一致性**：遵循《tri-skill-规范与生成指南》全部硬约束，无 LICENSE/.gitignore。
