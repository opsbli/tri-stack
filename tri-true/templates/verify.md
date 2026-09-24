---
verify_id: <UUID>
task_name: <VERIFY_YYYYMMDD_HHMMSS_sessionid8>
source_skill: <tri-coding|tri-code-analyzer|user_direct|hook>
risk_level: <low|medium|high|critical>
domain: <medical|financial|legal|technical|general>
upstream_mode: <A_snapshot|B_install_prompt|C_degraded>
hallucination_type: <factuality|faithfulness|mixed>
final_confidence: <0-1>
knowledge_type: <known|computed|inferred|iframe|common|guess>
final_status: <verified|rejected|uncertain|human_review>
防线触发: <1|2|3|4>
修订次数: <0-3>
created_at: <ISO8601>
schema_version: 1
---

# 验证报告

> 本报告由 tri-true 四道防线产出。final_status=verified 仅代表通过验证流程，不代表绝对正确；final_status=human_review 须人工复核后方可交付。

## 一、验证结论

**最终状态**：<verified | rejected | uncertain | human_review>

**最终置信度**：<0-1>（阈值 <按 risk_level 的阈值>）

**知识类型**：<known | computed | inferred | iframe | common | guess>

**风险标注**：<low | medium | high | critical>

**兜底说明**（若有）：
<若触发兜底，说明：拒答原因 / 多答案列表 / 人审要求>

## 二、待验证原文

<段落切分后的原文，每段标 [P0] [P1] [P2]...>

## 三、防线执行总结

### 防线一·置信度评估 + 知识类型分类

| 段落 | VC | SC | CC | 综合 | 知识类型 | 阈值 | 判定 |
|------|----|----|----|------|----------|------|------|
| [P0] | 0.x | 0.x | 0.x | 0.x | known | 0.x | pass/fail |
| [P1] | 0.x | 0.x | 0.x | 0.x | inferred | 0.x | pass/fail |

**防线一结论**：<高置信+common/known 直接 verified / 中低置信或 inferred/iframe/guess/computed 按知识类型路由后续防线>

### 防线二·事实源验证

| 段落 | 主张 | 引用 | 信源 | Tier | 加权得分 | 状态 |
|------|------|------|------|------|----------|------|
| [P1] | <claim> | [1] | <url> | T1 | 0.x | supported |

**防线二结论**：<T1/T2 支撑 verified / T3/T4 或无源进入防线三>

### 防线三·多模型交叉验证

| 段落 | 主张 | 模型 | 回答摘要 | 自评置信 | UAF 权重 | 共识 |
|------|------|------|----------|----------|----------|------|
| [P2] | <claim> | gpt-4o | <answer> | 0.x | 0.x | 弱共识 |

**防线三结论**：<强/弱共识 verified / 分歧进入防线四>

### 防线四·自我反思修正

| 轮次 | 方法 | 原始置信 | 修订后置信 | 判定 |
|------|------|----------|------------|------|
| 1 | CoVe | 0.x | 0.x | pass/fail |
| 2 | Reflexion | 0.x | 0.x | pass/fail |
| 3 | Critique-Refine | 0.x | 0.x | pass/fail |

**防线四结论**：<修订后置信达标 verified / 仍不达标进入兜底>

## 四、修订记录摘要

<若触发防线四，列出关键修订：原回答 → 修订后回答，及修订原因>

## 五、风险标注与建议

- **风险等级**：<low | medium | high | critical>
- **是否需人审**：<否 | 是（critical + 置信 < 0.8）>
- **是否高风险操作**：<否 | 是（删除/发布/资金，需双人审）>
- **交付建议**：<可直接交付 | 需人审后交付 | 拒答并说明 / 列多答案>
