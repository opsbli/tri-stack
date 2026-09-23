---
name: security-audit-static-part3
description: security-audit-static 续篇（part3）——高漏检检查清单 10 项、输出格式与强制 Evidence 行、四级严重性锚点、发现数量控制、报告收尾三项、保存指令与关键规则。
source: pm-skills-main/pm-ai-shipping/commands/security-audit-static.md
domain: AI 交付
---

# /security-audit-static → 审计你手上已有的代码（part3）

> 蒸馏自命令 `security-audit-static`｜域：AI 交付｜源词数：1293
> 本文件是 `security-audit-static.md` 的续篇（三部分之三），因单文件超 900 词上限而拆出。审计引擎五步见 part1；fan-out 翻译与自我反驳判据见 part2。
> **拆分只切分了说明性散文的落点：下面的 10 项检查清单、Evidence 强制格式与四级严重性锚点逐条完整保留。**

## 高漏检检查清单（High-miss checklist · 按技术形态而非具体栈组织）

**必须逐条应用——这些是 AI 生成应用最常失手的地方。**

1. **Service-role / 关闭了 RLS 的边界** — 若 DB client 绕过行级安全，那么**每一个授权决策都必须在代码里**；标出**缺少 org/owner 过滤条件**的查询。
2. **Auth-provider 漂移（Auth-provider drift）** — 来自外部身份提供方（例：Clerk）的 claims 被信任，**却没有验证它们如何映射到数据作用域**。
3. **闸门/动作字段错配（Gate/action field mismatch）** — 权限校验的是一个 ID，**动作却执行在另一个从未被证明属于它的独立 ID 上**。
4. **可伪造的请求信号（Forgeable request signals）** — 端点靠 `?source=cron`、`?bot=1`、可猜的 header，或未签名的类 webhook 载荷把关，**而不是真正的鉴权**。**当该端点会改数据、发邮件或触发付费用量时，提升严重性。**
5. **输出编码 vs. 输入校验** — 用户数据被插值进 HTML、`<title>`、属性、JSON-LD、SQL 或 Markdown 时，**必须针对那个 sink 做编码；输入校验不算**。（XSS、CSP 缺口。）
6. **SSRF / 渲染器滥用** — 受攻击者影响的 URL、HTML、SVG 或 Markdown 抵达对外 fetch 或某个渲染器（headless browser、PDF/OG-image 生成器）。
7. **解析器 / 校验器差异（Parser / validator differentials）** — 校验器接受了一个消费方以不同方式解释的值：未加锚点的正则、`startsWith`/子串白名单、URL 解析器不一致、编码/大小写/斜杠/路径规范化不匹配，或**在一种表示上校验、在另一种表示上执行**。
8. **fail-open 路径** — error、`catch`、timeout、cancellation、cache-miss、stale-cache、feature-flag 或边界值分支**默认走了 allow**。**AI 代码特别爱写宽容的 fallback。**
9. **密钥 / PII 流入可观测系统** — 凭据、token、邮箱或敏感数据抵达日志、traces、分析或错误响应体；**尤其要检查 error 分支**。
10. **public-data-only 违规** — SPA/SEO 的 bot 路由或「public」端点**过度取了私有字段**。

## 输出模板

按文件分组存活下来的发现，**按严重性排序**，使用标准格式：

```markdown
Security Audit: [scope]

<file>:
  N. [SEVERITY] [Category] <location>
     Evidence: <file:line — verbatim code snippet>
     Risk Level: Critical | High | Medium | Low
     Attack Scenario: <attacker -> sink -> impact, step by step>
     Impact: <what data or functionality is compromised>
     Solution: <concrete code change>
```

**Evidence 行是强制项——一条无法引用它所指控的代码的发现，不许发布（doesn't ship）。**

## 严重性锚点（Severity anchors，四级，照抄）

- **Critical** — 未经认证的、或跨租户的访问，触及**数据、金钱或执行**。
- **High** — 一个**已认证用户**跨越了权限或租户边界，或**密钥/PII 泄露**。
- **Medium** — 一条**只是碰巧还成立**的边界（fail-open 路径、可伪造信号），或需要一个不太可能的前置条件。
- **Low** — 纵深防御缺口，**没有直接可利用路径**。

**发现数量控制**：若存活下来的发现超过约 **12** 条，**以最高严重性的条目开头，并把尾部按根因主题合并**——一份人类真会读的报告，胜过一份没人签核的详尽报告。

## 报告收尾（必含三项）

1. 跨发现的**根因主题（root-cause theme）**；
2. **哪些地方建得好——要明确说出来（say it explicitly）**；
3. **哪些是你无法验证、需要用户自行复核的**。

## 保存指令

完整报告写到 `reports/security_audit_{timestamp}.md`，并**把路径给用户**。

## 关键规则（源 Notes）

- **不要上报**没有具体影响的泛化加固建议、没有可达路径的过期依赖，以及不会随代码上线的 test/mock 代码。**但没有经典 sink 的逻辑与授权 bug 仍然算。**
- 本审计**设计上只读**：预批准的工具面覆盖读取、搜索、扇出与写 `reports/`，**它绝不编辑它审计的代码**。
- 本流程**只管安全**。过度取数、索引与缓存走 `performance-audit-static` 流程。
- 需要「先文档化、最后出交付包」的端到端一遍，走 `ship-check` 流程。

## 下一步建议

先处理 Critical/High；把每条被确认的发现交给 `derive-tests` 流程转成回归测试锚定它，避免同一缺口在下一次 AI 编辑时重开。

## Further Reading

（源未提供 Further Reading）
