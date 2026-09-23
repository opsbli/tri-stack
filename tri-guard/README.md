# tri-guard

横向方法论型 skill——**AI agent skill 安装前安全守卫**。委派 `skillspector` 确定性扫描（70 漏洞模式 / 19 大类 / 两阶段），或降级到内嵌知识库人工启发式检测，对每个高危发现做语义双轨复核（11 维 + SSD/SDI/SQP），输出 `APPROVE / CAUTION / REJECT` 裁决与安全审查报告。

## 特性

- **双轨检测**：工具轨（`skillspector` CLI / MCP `scan_skill`，确定性全量）＋ 降级轨（内嵌漏洞规则手册人工启发，unconfirmed）。
- **70 漏洞模式 / 19 大类**：提示注入、反拒绝、数据外泄、提权、供应链、过度代理、输出处理、提示泄露、记忆投毒、工具滥用、Rogue Agent、Agent 窥探、触发器滥用、行为 AST、污点追踪、YARA、MCP 最小权限、MCP 工具投毒 + SSRF/反序列化/MCP Rug Pull。
- **语义双轨复核**：十一维复核框架 + SSD/SDI/SQP 问题集，判断每个高危发现是 malicious / negligent / benign-but-sensitive。
- **证据溯源**：每条 finding 回到规则手册核对命中逻辑 + 回源码定位，禁信纯分数。
- **裁决三态 + 风险分**：`APPROVE / CAUTION / REJECT`，风险分数由 `scripts/risk_score.py` 确定性计算（严重点数 / 置信度缩放 / 递减权重 / 可执行乘数）。
- **诚实报告**：报告明示 `scan_mode`（static+llm / static-only / knowledge-degraded），降级态标 unconfirmed，静态不完整明示。
- **上游依赖三态**：工具轨 / 引导安装 / 降级轨，`skillspector` 为可选上游，无则自动降级。

## 目录结构

```
tri-guard/
├── SKILL.md                          主入口：安全审计契约 + 双轨审查 + 裁决三态
├── README.md
├── CHANGELOG.md
├── _meta.json
├── references/
│   ├── vulnerability-rulebook.md     70 漏洞模式 / 19 大类规则手册
│   ├── semantic-review.md            语义十一维 + SSD/SDI/SQP + 报告模板
│   ├── risk-scoring.md               风险评分契约
│   └── version-check-spec.md         版本检查规范
├── scripts/
│   ├── risk_score.py                 风险评分确定性实现
│   └── check_update.py               版本检查与更新
└── tests/
    └── tri-guard-full-testcases.md
```

## 安装

```bash
skillhub install tri-guard --dir <目标目录>
```

依赖 `skillspector` 时（可选，确定性工具轨）：

```bash
uv tool install git+https://github.com/NVIDIA/skillspector.git
```

## 使用

由 guard-hook、上游委派或用户显式调用激活：

```bash
# 直接审查一个 skill 目录 / SKILL.md / zip / Git URL
审一下这个 skill：<target>

# 检查某一模式家族
这个技能会不会偷我的环境变量密钥？（→ 数据外泄 E2 / 污点 TT3）
```

内部处理：版本检查（第零步）→ 上游依赖检测（工具轨/降级轨）→ 解析目标（不可信）→ 确定性扫描或知识库启发 → 读源码 + 证据溯源 → 语义双轨复核 + 评分 → 裁决 + 报告。报告落 `.tribro/guard/<命名>/security-report.md`。

## 测试

```bash
# 版本检查自检
python scripts/check_update.py --slug tri-guard --json
# 风险评分
python scripts/risk_score.py tests/fixtures/findings-example.json --json
```

全场景用例见 `tests/tri-guard-full-testcases.md`。

## 设计原则

- **安全不是分数**：风险分数只是姿态参考，最终裁决以语义复核 + 证据溯源为准。
- **双轨兜底**：确定性引擎首选，缺失即降级知识库，绝不「没工具就不审」。
- **证据可追溯**：每条结论都能指到规则、源码与语义依据。
- **纵向 MECE**：横向方法论，不认领 L2 编码，与 tri-checklist / tri-review 边界清晰。