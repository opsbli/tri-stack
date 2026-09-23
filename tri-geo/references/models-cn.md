# 国内主流大模型引用偏好与适配规范（models-cn.md）

> 加载时机：M3+ 国内模型引用适配前（设计指南 §2.5）
> **最后验证日期：2026-09-16 ｜ 当前状态：`unverified`（框架版，待实测校准）**

## 一、使用原则（先读这一节）

1. 本文件是**待填充的核验框架**，不是已核验的事实库。任何标 `unverified` 的条目**不得**作为评分依据或对外结论输出（P3 红线）。
2. 条目升级为 `verified` 的唯一路径：`probe_runner.py plan` → Agent 实际提问 → `ingest` 回填原始回答 → `answer_judge.py` 判定 → 把实测来源分布与命中证据路径写入本表。
3. 引擎清单（8 个，编码与 `validate_input.py` 白名单一致）：`deepseek` `doubao` `kimi` `zhipu` `wenxin` `yuanbao` `tongyi` `baidu_ai`
4. 验收门 T6 要求的四引擎重点：**DeepSeek / 豆包 / Kimi / 智谱 GLM**。

## 二、逐引擎适配卡（按此结构填写与核验）

### DeepSeek（编码 `deepseek`）

| 字段 | 内容 | 状态 |
|------|------|------|
| 架构特征 | 报道称采用 MoE 架构、强调推理效率、擅长结构化任务 | unverified |
| 解析偏好 | 待实测：逻辑推理步骤可视化、分点/代码块是否更易被引用 | unverified |
| 信源生态 | 待实测：是否偏重开放社区与门户（知乎/搜狐） | unverified |
| 适配要点（假设） | 结论前置；推理步骤用有序列表呈现；参数与对比用表格 | unverified |
| 实测证据 | `.geo-snapshots/<品牌>/probe/deepseek/*.txt` | 待填充 |
| 验证日期 | — | — |

### 豆包（编码 `doubao`）

| 字段 | 内容 | 状态 |
|------|------|------|
| 抓取特征 | 公开可核验：字节系内容抓取 UA 为 Bytespider（`site_signal.py` 已纳入爬虫核验） | **verified(UA 公开)** |
| 信源生态 | 报道称优先字节系内容与 CSDN | unverified |
| 解析偏好 | 待实测：权威背书内容的引用占比 | unverified |
| 适配要点（假设） | 保证 Bytespider 未被 robots.txt 禁止；技术内容布局 CSDN；Schema 完整 | unverified |
| 验证日期 | — | — |

### Kimi（编码 `kimi`）

| 字段 | 内容 | 状态 |
|------|------|------|
| 架构特征 | 报道称具备长上下文能力、多模态 | unverified |
| 信源生态 | 待实测：长文知乎与开放社区的引用占比 | unverified |
| 适配要点（假设） | 长文连贯结构 + 图文表整合；小节自包含便于长上下文召回 | unverified |
| 验证日期 | — | — |

### 智谱 GLM（编码 `zhipu`）

| 字段 | 内容 | 状态 |
|------|------|------|
| 信源生态 | 未获取可靠公开数据 | unverified |
| 适配要点（假设） | 结构化事实密度优先；避免长铺垫 | unverified |
| 验证日期 | — | — |

### 文心一言 / 元宝 / 通义 / 百度 AI（编码 `wenxin` `yuanbao` `tongyi` `baidu_ai`）

| 字段 | 内容 | 状态 |
|------|------|------|
| 信源生态 | 报道称：文心/百度 AI 偏百家号与百科；元宝偏微信公众号；通义未见可靠数据 | unverified |
| 适配要点（假设） | 按目标引擎选择首发阵地，保证事实在多平台表述一致（交叉印证） | unverified |
| 验证日期 | — | — |

## 三、M3+ 适配执行流程（确定性部分由脚本承担）

1. `validate_input.py --mode cn_fit`：校验品牌/品类/引擎编码（默认收窄为四引擎重点）。
2. Agent 读取本文件对应引擎卡 → 生成适配版内容（写作规范受 `writing_rules.py` 约束）。
3. `writing_rules.py` 校验（不达标打回，≤2 轮）→ `citation_check.py` 来源核验（捏造硬阻断）。
4. `probe_runner.py plan --rounds 3` 生成 prompt 集 → Agent 实际提问 → `ingest` 回填。
5. `answer_judge.py` 规则判定：提及率、引用位次、情感；输出采样轮数与波动区间。
6. 判定结果 → 回写本文件对应行的「实测证据」与「验证日期」，状态改为 `verified`。

## 四、禁止事项

- 禁止用 LLM 自我推演（"虚拟收录查询"）替代真实提问（P3）。
- 禁止把 `unverified` 条目写成结论或评分。
- 禁止跨引擎混算数据：每个引擎的实测结果独立记录、独立呈现。
