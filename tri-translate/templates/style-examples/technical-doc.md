---
style_example_id: technical-doc
doc_type: technical_doc
audience: developer
register: formal
description: 技术文档风格示例。直译为主，意译为辅；保留所有代码/路径/命令/版本号；术语按 glossary 强制一致。Few-shot 学习用。
---

# 风格示例 · 技术文档

> 本示例供 Few-shot 学习使用。展示技术文档场景下的三策略分层与不译要素保留。

## 示例 1：API 文档

### 原文

```text
Install the SDK by running `npm install @scope/sdk` in your terminal. Add the following line to your `config.json`:

```json
{
  "apiKey": "your-api-key-here",
  "endpoint": "https://api.example.com/v1"
}
```

The SDK requires Node.js v18.0.0 or later. See https://nodejs.org for downloads.
```

### 译文

```text
在终端中运行 `npm install @scope/sdk` 安装该 SDK。在 `config.json` 中添加以下内容：

```json
{
  "apiKey": "your-api-key-here",
  "endpoint": "https://api.example.com/v1"
}
```

该 SDK 需要 Node.js v18.0.0 或更高版本。下载地址见 https://nodejs.org。
```

### 策略标注

| 段 | 策略 | 不译要素 |
|----|------|----------|
| 1 | 直译 | `npm install @scope/sdk` / `config.json` |
| 2 | 不译 | 整段 JSON 配置块 |
| 3 | 直译 | Node.js / v18.0.0 / https://nodejs.org |

---

## 示例 2：命令行参考

### 原文

```text
To deploy, run `deploy --prod --region us-east-1`. The deploy command reads from `$DEPLOY_TOKEN` environment variable. Make sure the token has `write` permission on the target bucket at `s3://my-bucket/`.
```

### 译文

```text
部署时运行 `deploy --prod --region us-east-1`。deploy 命令从 `$DEPLOY_TOKEN` 环境变量读取凭据。请确保该 token 对目标桶 `s3://my-bucket/` 具有 `write` 权限。
```

### 策略标注

| 段 | 策略 | 不译要素 |
|----|------|----------|
| 1 | 直译 | `deploy --prod --region us-east-1` / `$DEPLOY_TOKEN` / `s3://my-bucket/` / `write` |

---

## 风格要点

- 命令行、路径、配置键、环境变量、版本号 100% 保留原文
- API 名词（如 deploy 命令）首次出现可保留英文，后续沿用
- 直译时仍保持中文语序与表达习惯，避免欧化
- 代码块整体进入隔离区不译
