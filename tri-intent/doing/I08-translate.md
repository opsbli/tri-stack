---
name: I08-translate
description: 【Doing·I08 翻译转换】用户要求跨语言翻译或跨格式转换时触发，如中英互译、代码语言互转、Markdown 转 HTML、JSON 转 YAML。核心是在不同语言/格式间等价转换。
---

# I08 翻译转换（Doing）

## 识别特征

- 动词为 **翻译 / 译成 / 转成 / 转换为**，涉及**源→目标**的形态迁移
- 语言翻译（中↔英↔日…）或格式转换（MD↔HTML、JSON↔YAML、SQL 方言互转）
- 典型语料：「翻译成英文」「把这段 Python 转成 Go」「JSON 转 CSV」

## 与邻近意图边界

- vs **I07 内容改写**：I08 跨语言/跨格式，I07 同语言内加工
- vs **I11 编码开发**：代码语言互转归 I08；写新功能归 I11
- vs **I15 多媒体生成**：I08 文本/代码转换，不产多媒体

## PDF 转换子类（pdf2md · 子类路由）

**触发语义**：任务要点含 PDF 转 Markdown 语义（PDF 转 MD / 转成 Markdown / pdf2md / PDF 无损转换 / 把这份 PDF 转成 md）。

**路由规则**：`L3_子意图` 标注为 `pdf2md`，`下游路由建议` **直接覆写为 tri-pdf2md**（一跳，无需中介 skill），L2 保持 I08 不变。

**MECE 依据**：「一个 L2 意图（I08）对应一个一跳下游」，仅由 `L3_子意图` 区分——语言翻译与其它格式转换仍归 tri-content（默认），PDF→MD 专用编排归 tri-pdf2md。与 I06 article→tri-article 同构。

**与 tri-pdf2md 上游依赖检测的对称关系**：tri-intent 的下游依赖检测在此场景仅需检测源码树 `tri-pdf2md/`，缺失即提示安装；tri-pdf2md 独立使用时反向检测 tri-intent 可用性（三态：快照模式/引导安装/降级模式）。任一端缺失都被发现。

**边界细则**：PDF 的合并/拆分/表单/水印等文档操作不属于 I08·pdf2md（归环境内置 pdf skill）；「把 PDF 内容翻译成英文」是翻译语义（归 tri-content·I08 默认，可委派 tri-translate），非 pdf2md 子类。

## 格式转换子类族（x2md 族 · 子类路由）

**触发语义**：任务要点含 Word/PPT/Excel/HTML 转 Markdown 语义（Word 转 MD / docx2md / 把这份 docx 转成 md；PPT 转 MD / pptx2md；Excel 转 MD / xlsx2md；HTML 转 MD / html2md；扩展名族：.docx/.docm/.doc、.pptx/.pptm/.pps/.pot/.ppsx/.ppsm/.ppt、.xlsx/.xlsm/.xls/.xlsb/.csv、.html/.htm；.wps 同格式兼容）。

**路由规则**：`L3_子意图` 按源格式分别标注为 `docx2md` / `pptx2md` / `xlsx2md` / `html2md`，`下游路由建议` **直接覆写为对应 tri-<fmt>2md**（一跳，无需中介 skill），L2 保持 I08 不变。

**MECE 依据**：与 pdf2md 子类同构——一个 L2 意图（I08）对应一个一跳下游，仅由 `L3_子意图` 区分源格式；tri-docx2md/tri-pptx2md/tri-xlsx2md/tri-html2md 各认领一种源格式族（docx2md=.docx/.docm/.doc、pptx2md=.pptx/.pptm/.pps/.pot/.ppsx/.ppsm/.ppt、xlsx2md=.xlsx/.xlsm/.xls/.xlsb/.csv、html2md=.html/.htm），族内扩展名归同一 skill（同族 MECE），彼此族间零交集。五格式（.odt/.ods/.odp/.rtf/.epub）家族统一不支持，命中即优雅跳过（SKIP）。

**对称双向检测**：tri-intent 的下游依赖检测在此场景仅需检测源码树对应的 `tri-<fmt>2md/`，缺失即提示安装；各 x2md skill 独立使用时反向检测 tri-intent 可用性（三态：快照模式/引导安装/降级模式）。

**边界细则**：Word/PPT/Excel 的编辑、批注、合并等文档操作不属于 I08·x2md 族（归环境内置对应 skill）；单一源格式转换走本族对应技能，**多格式文档集→知识库**走 tri-wiki（见下）。

## 知识库搭建子类（wiki · 子类路由）

**触发语义**：任务要点含知识库搭建语义（搭建知识库 / 建知识库 / 把文档整理成知识库 / 构建 wiki / 知识库生成 / 批量文档转知识库 / 建个人知识库）。

**路由规则**：`L3_子意图` 标注为 `wiki`，`下游路由建议` **直接覆写为 tri-wiki**（一跳，无需中介 skill），L2 保持 I08 不变。

**MECE 依据**：与 pdf2md 子类同构——仅由 `L3_子意图` 区分：**单文档格式转换走 x2md 族单技能（交付单份 MD + 质量报告），文档集→知识库走 tri-wiki（交付主题树 + MOC + 索引 + 覆盖率/链接密度分级质量报告）**。tri-wiki 是集合级编排层，其 C 阶段反向委派 x2md 族完成批量转换，两层职责正交不竞争。

**对称双向检测**：tri-intent 的下游依赖检测在此场景仅需检测源码树 `tri-wiki/`，缺失即提示安装；tri-wiki 独立使用时反向检测 tri-intent 可用性（三态：快照模式/引导安装/降级模式）。

**边界细则**：单篇文档「转成 MD」不含组织/索引诉求，归 x2md 族而非 wiki；「知识库 loop/domain 创建」（I14·loop，长期循环体）与「知识库搭建」（I08·wiki，一次性文档资产构建）以交付对象区分——前者归 tri-loop，后者归 tri-wiki。