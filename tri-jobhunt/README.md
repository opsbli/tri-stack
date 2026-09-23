# tri-jobhunt · 求职全流程路由

覆盖求职/简历/面试/谈判完整生命周期的**单入口领域 skill**。把求职素材生成与策略决策收敛为一个入口
`/tri-jobhunt`，内部按请求类型分发到 6 个 children 子 skill，产出可投的简历、求职信、面试题库与谈判方案。

## 特性（Features）

- **单入口分发**：识别求职请求类型（R1-R11）→ 分发到对应子 skill，不产生第二个入口。
- **6 子 skill 覆盖**：`tri-jd`（JD 匹配/投否）、`tri-resume-core`（简历核心/ATS/量化/定制/版本）、
  `tri-docs`（求职信/申请表/冷邮件/LinkedIn/案例/推荐人）、`tri-interview`（面试 STAR 库）、
  `tri-negotiate`（谈判+Offer）、`tri-role`（技术/高管/学术/创意/转行）。
- **共享资源层**：ATS 铁律 / 量化方法论 / STAR 框架 / 角色差异统一放 `references/`，只蒸馏一次消除重复。
- **真实性底线**：HIGHLIGHT 不 Fabricate，量化诚实，敏感数据标注。

## 目录结构

```
tri-jobhunt/
├── SKILL.md  README.md  CHANGELOG.md  _meta.json(#安装元数据,由 install_skill.py 生成)
├── references/
│   ├── jobhunt-routes.md        # R1-R11 路由表 + 分发契约
│   ├── quantification.md        # 六类/五估算/四模板/动词库
│   ├── ats-compliance.md        # ATS 铁律/格式/章节/匹配
│   ├── star-framework.md        # STAR/XYZ/CAR + 故事库
│   ├── role-branches.md         # 五角色差异增量
│   └── version-check-spec.md    # 版本检查规范真源(自包含副本)
├── scripts/check_update.py      # 版本检查门可执行实现
├── children/                    # 6 个子 skill（随父包分发）
│   ├── tri-jd/SKILL.md          # JD 匹配 / 投否决策 (R3)
│   ├── tri-resume-core/SKILL.md # 简历优化核心 (R1/R2/R4/R10/R11)
│   ├── tri-docs/SKILL.md        # 求职产出文档 (R5)
│   ├── tri-interview/SKILL.md   # 面试 STAR 库 (R6)
│   ├── tri-negotiate/SKILL.md   # 谈判 + Offer (R7/R8)
│   └── tri-role/SKILL.md        # 专项角色 (R9)
└── tests/tri-jobhunt-full-testcases.md
```

## 安装（Installation）

- **上游依赖**：本 skill 不依赖 tri-intent（非其下游，用户显式调用激活）。
- 复制 `tri-jobhunt/` 到 skill 识别目录（或目录 junction），即可 `/tri-jobhunt` 斜杠激活。
- 6 个 children 子 skill 随父包分发、**不独立安装**；缺失时主 skill 降级提示补齐。

## 使用（Usage）

输入例：一份简历 + 一条 JD；或一句「帮我写 ATS 友好的简历要点」「这个岗位值不值得投」
「写封求职信/自荐邮件」「准备面试」「比较这两个 offer」「转行写简历」。

预期产物：ATS 报表 / 量化要点 / 求职信 / 面试题库 / 谈判方案 / 角色专属简历等。

## 测试（Testing）

见 `tests/tri-jobhunt-full-testcases.md`（零.能力清单 Reflect 全 SKILL 能力，用例覆盖 A-H 八组）。

## 设计原则 / 注意事项

- **单入口不暴露子 skill**；请求一次一环节推进。
- 真实性与量化诚实是底线（R11）；敏感薪资/法规只给方法与框架。
- 主 skill 本身是 tri-forge 生成的机器 skill，随包自带 `scripts/check_update.py` 版本门；
  children 子 skill 版本一致性由主 skill 统一巡检。
- 不含任何参考技能版权/作者信息，仅含通用方法论与可执行规则。