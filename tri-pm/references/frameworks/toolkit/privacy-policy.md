---
name: privacy-policy
description: 隐私政策起草框架——覆盖数据类型、管辖区、GDPR/CCPA 合规与需法律审阅条款，含标准 14 段结构
source: pm-skills-main/pm-toolkit/skills/privacy-policy/SKILL.md
domain: 工具
---

# 隐私政策生成（privacy-policy · 技能态）

> 蒸馏自 `privacy-policy`｜域：工具｜源词数：1586
> 本文为**技能态**。同名命令态见 `workflows/toolkit/privacy-policy.md`。

## 必含章节清单（MUST-SECTIONS）

- [x] Purpose — 框架目的
- [x] Important Disclaimer — 重要免责声明（原样保留）
- [x] Input Arguments — 输入参数
- [x] Process — 起草流程（7 步）
- [x] Privacy Policy Template Structure — 模板结构（序言 + 14 段）
- [x] 14 Key Sections — 14 个必备条款（逐条，含 `[⚠️]` 标记）

### 可选补充段（OPTIONAL，不参与 BLOCK 判定）

- [ ] Content Guidelines — 内容准则（见正文）
- [ ] Output Format — 输出三段式（见 part2）
- [ ] Key Compliance Reminders — 合规提醒（见 part2）
- [ ] Before You Publish — 发布前清单（见 part2）

## 逐段引导问题

- **Purpose**：为产品/服务起草详细隐私政策，覆盖数据类型、适用辖区，并标注需法律审阅条款。
- **Disclaimer**：非法律意见，发布前须经数据隐私专业律师审阅。
- **Key Sections**：14 段是否齐备，每段必备内容是否覆盖， jurisdiction-specific 段是否标 `[⚠️]`。

## 输出模板

```markdown
## Privacy Policy: [Product]
[完整政策正文]

### Compliance Checklist
| Regulation | Status | Notes |
|-----------|--------|-------|

### Clauses Requiring Legal Review
| Clause | Why | Priority |
|--------|-----|----------|

### Implementation Checklist
- [ ] Cookie consent banner
- [ ] Data subject request process
- [ ] Data processing records
- [ ] DPA with processors
```

## 输出命名规则

源文件未规定（命令态默认保存为 markdown，可导出 DOCX）

## 重要免责声明（原样保留）

**This is for informational purposes only and does not constitute legal advice. Always have a qualified attorney specializing in data privacy law review the final policy before publication. Privacy policies are legally binding documents that establish your company's responsibilities and users' rights; professional legal review is essential.**

## 输入参数（源变量翻译为对话上下文）

- 产品名 / 产品 URL（可选，提供则研究）/ 公司法定名 / 公司地址 / 隐私联系邮箱
- 信息类型（如姓名、邮箱、使用行为、位置、支付、设备标识）
- 适用管辖区（如美国、欧盟 GDPR、加州 CCPA）

## 流程（7 步）

1. **Research**：若提供 URL，走访站点识别收集的数据与第三方集成。
2. **Clarify Data Collection**：直接收集 / 自动收集 / 第三方数据 / 特殊类别（健康、金融、儿童、生物识别）。
3. **Identify Applicable Laws**：GDPR、CCPA/CPRA、其他州法（VIPA、TDPSA）、行业法（HIPAA/GLBA/FERPA）。
4. **Structure**：按标准 14 段组织（见下）。
5. **Plain Language**：清晰易懂，首次用术语即定义。
6. **Highlight**：需管辖区专属语言/数据权利的段标 `[⚠️ LEGAL REVIEW REQUIRED]`。
7. **Provide Context**：说明每段重要性、公司待决事项、合规考量。

## 14 Key Sections（必备条款，逐条照抄）

**Preamble（序言）**：政策覆盖范围、最后更新日、用户联系渠道。

**1. Information We Collect（收集的信息）**：个人/使用/设备/位置/支付/通信；`[⚠️]` 敏感或特殊类别（健康、生物识别等）。

**2. How We Collect（收集方式）**：直接（表单/注册）、自动（cookie/分析/传感器）、第三方（伙伴/服务商/经纪）。

**3. How We Use（使用目的）**：提供服务与支持、改进个性化、分析、营销、安全防欺诈、法律合规；`[⚠️]` 其他目的须显式声明。

**4. Legal Basis for Processing（处理的法律依据）** `[⚠️]`（GDPR 尤重）：Consent / Contract / Legal obligation / Vital interests / Public task / Legitimate interests。

**5. Data Sharing and Third Parties（共享与第三方）**：服务商、商业伙伴、法律机关；`[⚠️]` 第三方所在地（尤其超出用户辖区）。

**6. International Data Transfer（跨境传输）** `[⚠️]`：传输方式、机制（SCC/充分性决定/用户同意）、存储处理地。

**7. Data Retention（留存）**：账户数据、使用日志、已删内容的保留期；`[⚠️]` 须具体，多法规强制要求。

**8. User Rights（用户权利）** `[⚠️]`：访问、删除（被遗忘权）、更正、限制处理、可携、opt-out、投诉监管；含行权方式与联系。

**9. Cookies and Tracking（Cookie 与追踪）** `[⚠️]`：所用工具、用途、如何管理、非必要 cookie 是否需显式同意（GDPR 要求）。

**10. Security（安全）**：传输与静态加密、访问控制、定期审计、事件响应、局限性声明。

**11. Children's Privacy（儿童隐私）** `[⚠️]`（若服务 13 岁以下）：家长同意、年龄门、合规 COPPA/UK Children's Code。

**12. Contact and Rights（联系与权利）**：隐私邮箱、邮寄地址、响应时限、DPO（如需）。

**13. Policy Changes（政策变更）**：通知期（如 30 天）、通知方式、重大变更的用户 opt-out 权。

**14. Additional Provisions（附加条款）**：是否售卖数据（否则显式声明）、第三方链接免责、准据法、生效日。

## 内容准则（Content Guidelines）

- 具体：不说"用于产品改进"，而说清具体分析了什么、优先改了什么。
- 平实语言：写给普通读者，解释收集了什么、为何。
- 透明：诚实列出所有收集（含分析、第三方、用途）。
- 用户控制：说明如何访问/删除/退出。
- 与实相符：政策须匹配产品真实行为，不符则改产品或改政策。
- 用具体信息类型让政策贴合实际收集。

## Checkpoint

（源未设显式 checkpoint 引句；以下为关键提醒）
> "Get legal review: Before publishing, have a data privacy attorney in your jurisdiction review the policy."
> 发布前请辖区数据隐私律师审阅。

（输出三段式、合规提醒、发布前清单见 `privacy-policy-part2.md`）
