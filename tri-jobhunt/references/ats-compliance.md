# ATS 兼容与排版（ats-compliance）· 共享资源层

> 由 ResumeSkills-main 的 resume-ats-optimizer / resume-formatter / resume-tailor 蒸馏，供
> tri-resume-core / tri-jd 等子 skill 复用。**ATS 铁律是底线规则，任何简历类产出 MUST 过此层。**
> grep 模式：`ATS` / `格式参数` / `章节顺序` / `关键词`

## 一、ATS 兼容铁律（底线规则 · 不可违反）

- **禁** 表格 / 多列 / 文本框 / 页眉页脚 / 图片 / 图形 / 特殊符号。
- **禁** 非常规章节名（ATS 靠标准锚文本识别区块）。
- **禁** 关键词堆砌（keyword stuffing）——应自然嵌入。
- **必** 单列布局、标准字体、标准章节名、联系方式（电话/邮箱/城市）放正文首部。
- **两套交付**：在线申请用 `.docx` / `.pdf`，且均可被解析。

## 二、排版格式参数（可落地为默认值）

| 参数 | 默认 |
|---|---|
| 页长 | Entry 1 页 / Mid 1-2 / Senior 2（Exec ≤3） |
| 边距 | 0.5"–1" |
| 字体 | Arial / Calibri / Times 等标准体 |
| Name 字号 | 16–20pt |
| 标题字号 | 12–14pt |
| 正文/最小 | 10–12pt / 最小 10pt |
| 行距 | 1.0–1.15 |

## 三、标准章节顺序

`Contact → Summary → Skills → Experience → Education → Certifications → Additional`

## 四、匹配分计算（tri-jd 决策上游）

- `Match Score = (匹配关键词数 / 必需关键词总数) × 100%`，目标 **≥80%**。
- 综合匹配：`Overall = (Required% × 0.7) + (Preferred% × 0.3)`。
- 关键词三分类：Hard Skills（语言/工具/认证/方法论）、Soft Skills、Industry Terms。
- 摆放优先级：Summary（5-8 个关键词）> Skills 区 > Experience bullets。
- 密度目标：Critical 关键词 2-4 次、Important 1-2 次；**禁堆砌**。

## 五、ATS 失败常见模式

创意排版 / 非常规章节名 / 缺关键词 / 关键词堆砌 / 表格图片 / 多列 / 页眉页脚。

## 六、真实性边界（resume-tailor 铁律）

- **HIGHLIGHT 而非 FABRICATE**：把完整经历当「成就图书馆」按岗位选书。
- 可接受：重排真实信息 / 用行业术语 / 添上下文。
- **NEVER**：加没掌握的技能 / 改数字 / 虚构经历 / 编造荣誉。
- 版本契约：master 单源 + `[LastName]_[Role]_[Company]_[Date]` 命名，定向版从副本编辑。