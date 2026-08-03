---
name: tri-article-profile-skeleton
description: tri-article 首次初始化时复制填写的用户配置骨架。每一行 `键: 值` 对应 SKILL.md 中的一个 {{占位符}}；缺失的必填项会在生成时被反问补全。
---

# tri-article 用户配置（profile）

> 本文件填充 SKILL.md 中所有 `{{KEY}}` 占位符。由 agent 首次运行时反问用户后填写，并保存到 `.tribro/tri-article/profile.md`。
> 规则：多值项用「/」分隔或每行一个；未配置项留空，引擎回退内置默认值。

## 必填项

AUTHOR_PROFILE: <文末「个人介绍」使用的人设底稿，1–2 句可扩展；去掉手机号/邮箱/微信号等隐私。例：10+ 年软件开发经验，专注某领域，不定期在某某平台分享技术文章。>

ARTICLES_ROOT: <文章保存根目录，默认 .tribro/tri-article/articles，内部按「领域分桶 + index.json 索引」组织（见 SKILL.md §1.5）。例：.tribro/tri-article/articles>

DOMAIN_POOL: <选题领域池（同时作为领域分桶名），至少 3 项，每行一个或用「/」分隔。例：前端框架 / 后端服务 / 云原生>

## 产品自然植入（可选，默认关闭）

PRODUCT_ENABLED: <true 或 false；为 false 时文章不出现任何产品>

PRODUCT_NAME: <你的产品名，仅当 PRODUCT_ENABLED=true 需填>

PRODUCT_DESC: <产品一句话描述，仅当开启>

PRODUCT_TECH: <产品技术栈，仅当开启>

PRODUCT_RELATION: <产品与文章主题的天然关联说明，仅当开启>

## 可选项（留空回退内置默认）

LICENSE_STMT: <文末许可证声明；留空回退「本文遵循 MIT 协议，转载请注明出处。」>

DISABLED_WORDS: <禁用词表，用「/」分隔；留空回退内置默认禁用词>

---

### 反问示例（agent 首次初始化时参考，分批问，避免一次轰炸）

1. 「这篇文章文末的『个人介绍』想用谁的人设？给我 1–2 句底稿（别带隐私信息）。」
2. 「文章默认保存到 .tribro/tri-article/articles（按领域分桶 + 索引，便于搜索去重），要换路径吗？」
3. 「平时主要写哪几个技术领域？给我 3 个以上，我用来轮转选题。」
4. 「要不要顺带植入你正在做的产品？要的话把名字、一句话介绍、技术栈、和文章主题的关联发我。」
5. 「文末许可证声明用默认的 MIT 就行，还是你自定义一句？」
