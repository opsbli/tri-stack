---
name: ai-patterns
description: tri-humanize 的 35 种 AI 写作模式决策规则表（单一事实源）。每种模式含识别信号（Words to watch）/ IF-THEN 决策规则 / Before-After 示例 / 误报注意。grep 模式：模式 N1–N35、误报检查、语气规则。
---

# 35 种 AI 写作模式决策规则表

> 本文件是 tri-humanize 的模式识别单一事实源。改写时逐段对照本表标记模式，按 IF-THEN 规则处置。
> 模式编号沿用稳定的 N1–N35 序号，便于跨文档引用与回溯；编号只作索引，不承载来源含义。
> 每种模式同时给出英文与中文触发词，两种语言文本分别对照各自词表。

## 一、内容模式（N1–N6）

### 模式 N1 · 夸大重要性与遗产

**识别信号（Words to watch）**：stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance/significance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted

**中文触发词**：标志着、见证了、是……的体现/证明/提醒、极其重要的/重要的/至关重要的/核心的/关键性的作用/时刻、凸显/强调/彰显了其重要性/意义、反映了更广泛的、象征着其持续的/永恒的/持久的、为……做出贡献、为……奠定基础、塑造着、关键转折点、不断演变的格局、焦点、不可磨灭的印记、深深植根于

**IF-THEN 规则**：IF 观察到普通细节被描述为重大变化、证明遗产、或反映广泛趋势 THEN 删除夸大，保留事实。

**示例**：
- Before: The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics in Spain. This initiative was part of a broader movement across Spain to decentralize administrative functions and enhance regional governance.
- After: The Statistical Institute of Catalonia was established in 1989, part of a wider decentralization of administrative functions in Spain.

**误报注意**：若来源确实说明了历史意义，保留有用信息；只删除无来源的拔高。

### 模式 N2 · 点名炫耀重要性

**识别信号**：independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence

**中文触发词**：独立报道、地方/区域/国家媒体、由知名专家撰写、活跃的社交媒体账号、拥有超过 X 万粉丝

**IF-THEN 规则**：IF 观察到列出知名出版物或粉丝数来证明某人重要 THEN 只保留有实际上下文的有用引用。

**示例**：
- Before: Her views have been cited in The New York Times, BBC, Financial Times, and The Hindu. She maintains an active social media presence with over 500,000 followers.
- After: Her views have been cited in The New York Times and the BBC.

**误报注意**：若来源解释了某人说了什么、在哪里说的，保留该有用引用；不为缩短版本虚构上下文。

### 模式 N3 · 浅层 -ing 分析

**识别信号**：highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing...

**中文触发词**：突出了……、确保了……、反映了/象征着……、为……做出贡献、培养了/促进了……、涵盖了……、展示了……（句尾附加的现在分词短语）

**IF-THEN 规则**：IF 观察到 -ing 短语让简单事实显得更深 THEN 只保留来源支持的内容。

**示例**：
- Before: The temple's color palette of blue, green, and gold resonates with the region's natural beauty, symbolizing Texas bluebonnets, the Gulf of Mexico, and the diverse Texan landscapes, reflecting the community's deep connection to the land.
- After: The temple is painted blue, green, and gold, colors meant to evoke Texas bluebonnets and the Gulf of Mexico.

### 模式 N4 · 销售语言

**识别信号**：boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning

**中文触发词**：拥有（夸张用法）、充满活力的、丰富的（比喻）、深刻的、增强其、展示、体现、致力于、自然之美、坐落于、位于……的中心、开创性的（比喻）、著名的、令人叹为观止的、必游之地、迷人的

**IF-THEN 规则**：IF 观察到广告式语言描述地点/文化/产品/组织 THEN 删除销售腔，保留事实。

**示例**：
- Before: Nestled within the breathtaking region of Gonder in Ethiopia, Alamata Raya Kobo stands as a vibrant town with a rich cultural heritage and stunning natural beauty.
- After: Alamata Raya Kobo is a town in the Gonder region of Ethiopia.

### 模式 N5 · 模糊来源

**识别信号**：Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications (when few cited)

**中文触发词**：行业报告显示、观察者指出、专家认为、一些批评者认为、多个来源/出版物（实际引用却很少）

**IF-THEN 规则**：IF 观察到把主张归于未具名专家/批评者/报告/观察者 THEN 有真实来源则点名，否则删除无支持的主张。NEVER 虚构来源。

**示例**：
- Before: Due to its unique characteristics, the Haolai River is of interest to researchers and conservationists. Experts believe it plays a crucial role in the regional ecosystem.
- After: Researchers and conservationists study the Haolai River for its unusual characteristics.

### 模式 N6 · 公式化挑战与展望章节

**识别信号**：Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook

**中文触发词**：尽管其……面临若干挑战……、尽管存在这些挑战、挑战与遗产、未来展望

**IF-THEN 规则**：IF 观察到模板化的挑战/展望章节（重复模糊主张而非增加事实）THEN 保留事实，删除销售腔。

**示例**：
- Before: Despite its industrial prosperity, Korattur faces challenges typical of urban areas, including traffic congestion and water scarcity. Despite these challenges, with its strategic location and ongoing initiatives, Korattur continues to thrive as an integral part of Chennai's growth.
- After: Korattur has recurring traffic congestion and water shortages.

**误报注意**：日期或公开行动等细节只有来源或用户提供时才添加。

## 二、语言语法模式（N7–N13）

### 模式 N7 · 过度使用的 AI 词

**识别信号（高频 AI 词）**：Actually, additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, gate/gated/gating (figurative; preserve established technical usage), highlight (verb), interplay, intricate/intricacies, key (adjective), landscape (abstract noun), pivotal, quietly, showcase, tapestry (abstract noun), testament, underscore (verb), valuable, vibrant

**中文触发词**：此外、与……保持一致、至关重要、深入探讨、强调、持久的、增强、培养、获得、突出（动词）、相互作用、复杂/复杂性、关键（形容词）、格局（抽象名词）、关键性的、展示、织锦（抽象名词）、证明、强调（动词）、宝贵的、充满活力的

**IF-THEN 规则**：IF 观察到这些词成组出现（尤其堆叠时）THEN 用更自然的词替换。单个出现不处理。

**示例**：
- Before: Additionally, a distinctive feature of Somali cuisine is the incorporation of camel meat. An enduring testament to Italian colonial influence is the widespread adoption of pasta in the local culinary landscape, showcasing how these dishes have integrated into the traditional diet.
- After: Somali cuisine also includes camel meat, which is considered a delicacy. Pasta dishes, introduced during Italian colonization, remain common, especially in the south.

**误报注意**：`gate/gated/gating` 的既有技术用法（feature gating、CI quality gates）保留。

### 模式 N8 · 避免 is 和 are

**识别信号**：serves as/stands as/marks/represents [a], boasts/features/offers [a]

**中文触发词**：作为/代表/标志着/充当 [一个]、拥有/设有/提供 [一个]

**IF-THEN 规则**：IF 观察到用长短语替代简单动词 is/are/has THEN 用简单动词。

**示例**：
- Before: Gallery 825 serves as LAAA's exhibition space for contemporary art. The gallery features four separate spaces and boasts over 3,000 square feet.
- After: Gallery 825 is LAAA's exhibition space for contemporary art. The gallery has four rooms totaling 3,000 square feet.

### 模式 N9 · Not X but Y 与截断否定结尾

**识别信号**：Not only...but..., It's not just X, it's Y, 截断结尾（如 "no guessing"）

**中文触发词**：不仅……而且……、这不仅仅是关于……而是……、不是……而是……、截断否定结尾（如「无需猜测」）

**IF-THEN 规则**：IF 观察到 "Not only...but..." / "It's not just X, it's Y" 结构或截断否定结尾 THEN 直接陈述要点，补全为清晰从句。

**示例**：
- Before: It's not just about the beat riding under the vocals; it's part of the aggression and atmosphere. It's not merely a song, it's a statement.
- After: The heavy beat adds to the aggressive tone.
- Before (截断否定): The options come from the selected item, no guessing.
- After: The options come from the selected item without forcing the user to guess.

### 模式 N10 · 强行三连

**识别信号**：把想法强行凑成三组（innovation, inspiration, and industry insights）

**中文触发词**：强行凑成三组（创新、灵感和行业洞察）

**IF-THEN 规则**：IF 观察到强行把想法凑成三组以显得完整 THEN 用意思需要的数量。

**示例**：
- Before: The event features keynote sessions, panel discussions, and networking opportunities. Attendees can expect innovation, inspiration, and industry insights.
- After: The event includes talks and panels. There's also time for informal networking between sessions.

### 模式 N11 · 改名与重复句首

**识别信号**：同一主体反复改名（protagonist/main character/hero）；多句以同一主语开头（尤其 she/he）

**中文触发词**：同一主体反复改名（主人公/主要角色/中心人物/英雄）、多句以同一主语开头

**IF-THEN 规则**：IF 观察到同一主体反复改名 THEN 统一用一个清晰名称；IF 观察到重复句首 THEN 合并句子、必要时换主语、或以动作开头。NEVER 禁止重复词本身，只修重复句模式。

**示例**：
- Before (改名循环): The protagonist faces many challenges. The main character must overcome obstacles. The central figure eventually triumphs. The hero returns home.
- After: The protagonist faces many challenges but eventually triumphs and returns home.
- Before (重复句首): She noted the door. She noted the lock on it. She filed both away.
- After: She noted the door and its lock, then filed both away.

**误报注意**：刻意重复句首（如 "She came. She saw. She conquered."）用于构建节奏或压力时保留，仅当重复无增益时才改。

### 模式 N12 · 虚假 from X to Y 范围

**识别信号**：X 和 Y 不构成真实范围的 "from X to Y"

**中文触发词**：从 X 到 Y（X 与 Y 不构成真实范围）

**IF-THEN 规则**：IF 观察到 X 和 Y 不构成真实范围的 "from X to Y" THEN 直接列出主题。

**示例**：
- Before: Our journey through the universe has taken us from the singularity of the Big Bang to the grand cosmic web, from the birth and death of stars to the enigmatic dance of dark matter.
- After: The book covers the Big Bang, star formation, and current theories about dark matter.

### 模式 N13 · 被动语态与缺失主语

**识别信号**：隐藏行为者或省略主语（No configuration file needed. The results are preserved automatically.）

**中文触发词**：隐藏行为者或省略主语（无需配置文件、结果会被自动保留）

**IF-THEN 规则**：IF 观察到被动语态或缺失主语使行为者/动作不清晰 THEN 在有助于清晰时用主动语态。

**示例**：
- Before: No configuration file needed. The results are preserved automatically.
- After: You do not need a configuration file. The system preserves the results automatically.

## 三、风格模式（N14–N19）

### 模式 N14 · em/en 破折号（硬性规则）

**识别信号**：em dash（—）、en dash（–）、带空格破折号（ — ）、双连字符（ -- ）

**中文触发词**：em dash（—）、en dash（–）、中文全角破折号（——）、带空格破折号（ — ）、双连字符（ -- ）

**IF-THEN 规则（判定层）**：单个破折号 NEVER 视为 AI 腔证据。仅当破折号与公式化销售节奏、N27 假装揭示真相、N31 强行笑点等模式同现时才计入 AI 判定。

**IF-THEN 规则（处置层 · 强制）**：无论是否判定为 AI 腔，终稿 MUST 不含 em dash、en dash 与中文全角破折号（「——」在中文排版中虽属常见用法，本 skill 不做语言例外）。替换为句号/逗号/冒号/括号，或重写句子。返回前 MUST 搜索 —、–、—— 并逐个处理。

**处置例外（命中任一即保留）**：①写作样本使用该标点（按样本频率保留）；②第二手文本内部（引号、标题、专有名词、讨论该短语本身的示例）；③代码块、YAML 元数据、数据、链接目标内部。

**示例**：
- Before: The term is primarily promoted by Dutch institutions—not by the people themselves. You don't say "Netherlands, Europe" as an address—yet this mislabeling continues—even in official documents.
- After: The term is primarily promoted by Dutch institutions, not by the people themselves. You don't say "Netherlands, Europe" as an address, yet this mislabeling continues in official documents.

**误报注意**：编辑与记者常用 em dash；单个 em dash 不构成**判定** AI 腔的证据，只有与公式化销售节奏同现才判定。判定层与处置层互不覆盖——不判为 AI 腔的文本，其破折号仍按处置层规则移除（除非命中上述三条例外之一）。

### 模式 N15 · 过多加粗

**识别信号**：无明确理由的加粗词/短语

**中文触发词**：无明确理由的加粗词/短语

**IF-THEN 规则**：IF 观察到无明确理由的加粗 THEN 移除加粗。

**示例**：
- Before: It blends **OKRs (Objectives and Key Results)**, **KPIs (Key Performance Indicators)**, and visual strategy tools such as the **Business Model Canvas (BMC)** and **Balanced Scorecard (BSC)**.
- After: It blends OKRs, KPIs, and visual strategy tools like the Business Model Canvas and Balanced Scorecard.

### 模式 N16 · 加粗小标题列表

**识别信号**：每项以加粗标签+冒号开头的纵向列表

**中文触发词**：每项以加粗标签+冒号开头的纵向列表

**IF-THEN 规则**：IF 观察到每项以加粗标签+冒号开头的纵向列表且列表无额外价值 THEN 改用散文。

**示例**：
- Before: - **User Experience:** The user experience has been significantly improved with a new interface. / - **Performance:** Performance has been enhanced through optimized algorithms. / - **Security:** Security has been strengthened with end-to-end encryption.
- After: The update improves the interface, speeds up load times through optimized algorithms, and adds end-to-end encryption.

### 模式 N17 · 标题大写

**识别信号**：标题中每个主要词都大写

**中文触发词**：标题中每个主要词都大写（中文不适用；中文替代信号：中英混排标题的英文词首字母全大写）

**IF-THEN 规则**：IF 观察到标题中每个主要词都大写 THEN 改为句子式大小写。

**中文适配（不适用）**：中文标题无大小写概念，纯中文标题直接跳过本模式。仅当标题为中英混排时，对英文部分按本规则处置。

**示例**：
- Before: ## Strategic Negotiations And Global Partnerships
- After: ## Strategic negotiations and global partnerships

### 模式 N18 · 表情符号

**识别信号**：标题和列表项中的装饰性 emoji

**中文触发词**：标题和列表项中的装饰性 emoji（🚀 💡 ✅）

**IF-THEN 规则**：IF 观察到标题/列表项中的装饰性 emoji THEN 移除。

**示例**：
- Before: 🚀 **Launch Phase:** The product launches in Q3 / 💡 **Key Insight:** Users prefer simplicity / ✅ **Next Steps:** Schedule follow-up meeting
- After: The product launches in Q3. User research showed a preference for simplicity. Next step: schedule a follow-up meeting.

### 模式 N19 · 弯引号

**识别信号**：弯引号（“...”）而目标格式用直引号（"..."）

**中文触发词**：弯引号（中文不适用；中文替代信号：同一文本内中英引号混用、该用中文引号处用了英文直引号）

**IF-THEN 规则**：IF 观察到弯引号而目标格式用直引号 THEN 改为直引号。

**中文适配（不适用）**：中文文本以中文引号（「」或""）为规范，本模式不改写中文引号本身。中文场景只处理替代信号：同一文本内中英文引号混用、或该用中文引号处误用英文直引号时，统一为文本既定的引号风格。

**示例**：
- Before: He said “the project is on track” but others disagreed.
- After: He said "the project is on track" but others disagreed.

**误报注意**：macOS/Word/Google Docs 默认自动弯引号；弯引号单独出现不构成 AI 证据，只有与其他信号堆叠才判定。

## 四、聊天机器人模式（N20–N22）

### 模式 N20 · 答案中残留的聊天机器人文本

**识别信号**：I hope this helps, Of course!, Certainly!, You're absolutely right!, Would you like..., Want me to...?, Want me to give examples?, Should I continue?, let me know, here is a...

**中文触发词**：希望这对您有帮助、当然！、一定！、您说得完全正确！、您想要……吗、请告诉我、这是一个……

**IF-THEN 规则**：IF 观察到聊天机器人的问候/提议/结尾残留在应独立成文的文本中 THEN 移除。

**示例**：
- Before: Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand on any section.
- After: The French Revolution began in 1789 when financial crisis and food shortages led to widespread unrest.

### 模式 N21 · 知识截止声明与猜测

**识别信号**：as of [date], Up to my last training update, While specific details are limited/scarce..., based on available information, not publicly available, maintains a low profile, keeps personal details private, prefers to stay out of the spotlight, likely [grew up/studied/began], it is believed that

**中文触发词**：截至 [日期]、根据我最后的训练更新、虽然具体细节有限/稀缺……、基于可用信息……、尚未公开、可能/大概 [做过某事]

**IF-THEN 规则**：IF 观察到知识截止声明或「找不到来源后用合理猜测填补」THEN 陈述来源未显示的内容，或删除句子。NEVER 把猜测当事实呈现。

**示例**：
- Before (截止声明): While specific details about the company's founding are not extensively documented in readily available sources, it appears to have been established sometime in the 1990s.
- After: The company's founding date is not documented in the available sources. (或删除该句。只有来源提供时才陈述日期。)
- Before (猜测性补全): Information about her early life is not publicly available, suggesting she maintains a low profile and keeps personal details private. She likely grew up in a middle-class household, which shaped her later interest in education reform.
- After: Her early life is not documented in the available sources. (或省略该节。)

### 模式 N22 · 过度顺从语气

**识别信号**：先赞美用户或同意再回答（Great question! You're absolutely right! That's an excellent point!）

**中文触发词**：好问题！、您说得完全正确、这是一个很好的观点

**IF-THEN 规则**：IF 观察到先赞美用户或同意再回答 THEN 直接回答。

**示例**：
- Before: Great question! You're absolutely right that this is a complex topic. That's an excellent point about the economic factors.
- After: The economic factors you mentioned are relevant here.

## 五、填充、对冲与结构套路（N23–N35）

### 模式 N23 · 填充短语

**识别信号**：In order to, Due to the fact that, At this point in time, In the event that, The system has the ability to, It is important to note that

**中文触发词**：为了实现这一目标、由于……的事实、在这个时间点、在您需要……的情况下、系统具有……的能力、值得注意的是

**IF-THEN 规则**：IF 观察到填充短语 THEN 用简洁表达替换。

**替换对照**：
- "In order to achieve this goal" → "To achieve this"
- "Due to the fact that it was raining" → "Because it was raining"
- "At this point in time" → "Now"
- "In the event that you need help" → "If you need help"
- "The system has the ability to process" → "The system can process"
- "It is important to note that the data shows" → "The data shows"

### 模式 N24 · 过多限定词

**识别信号**：to be fair, it's also possible, could potentially, might arguably, in some cases it may, this is an inference

**中文触发词**：说实话、这也是有可能的、可能潜在地、在某些情况下可能、这是一种推断

**IF-THEN 规则**：IF 观察到限定词堆叠使每个主张都显得不确定 THEN 只保留来源支持且意思需要的限定词；移除只为修补先前过度陈述的保留条款。

**示例**：
- Before: It could potentially possibly be argued that the policy might have some effect on outcomes.
- After: The policy may affect outcomes.

### 模式 N25 · 泛泛的正面结尾

**识别信号**：以模糊乐观结尾（The future looks bright. Exciting times lie ahead. This represents a major step in the right direction.）

**中文触发词**：公司的未来看起来光明、激动人心的时代即将到来、这代表了向正确方向迈出的重要一步

**IF-THEN 规则**：IF 观察到以模糊乐观结尾 THEN 以最后一个具体事实结尾；来源陈述真实计划时用真实计划。

**示例**：
- Before: The future looks bright for the company. Exciting times lie ahead as they continue their journey toward excellence. This represents a major step in the right direction.
- After: (删除该段。以最后一个具体事实结尾，而非送别语。来源陈述真实计划时使用真实计划。)

### 模式 N26 · 过多连字符词对

**识别信号**：third-party, cross-functional, client-facing, data-driven, decision-making, well-known, high-quality, real-time, long-term, end-to-end

**中文触发词**：连字符词对到处出现；中文对应信号为同类复合修饰词堆叠（第三方、跨职能、面向客户、数据驱动、端到端、实时、长期、高质量）

**IF-THEN 规则**：IF 观察到连字符词对到处出现 THEN 名词前保留（a high-quality report），名词后去掉（the report is high quality）。

**示例**：
- Before: The cross-functional team delivered a high-quality, data-driven report. The team is cross-functional, the report is high-quality, and the methodology is data-driven.
- After: The cross-functional team delivered a high-quality, data-driven report. The team is cross functional, the report is high quality, and the methodology is data driven.

### 模式 N27 · 假装揭示更深真相

**识别信号**：The real question is, at its core, in reality, what really matters, fundamentally, the deeper issue, the heart of the matter

**中文触发词**：真正的问题是、归根结底、事实上、真正重要的是、从根本上说、更深层次的问题、问题的核心

**IF-THEN 规则**：IF 观察到用这些短语让普通观点显得像隐藏真相 THEN 直接陈述。

**示例**：
- Before: The real question is whether teams can adapt. At its core, what really matters is organizational readiness.
- After: The question is whether teams can adapt. That mostly depends on whether the organization is ready to change its habits.

### 模式 N28 · 宣布下一个要点

**识别信号**：Let's dive in, let's explore, let's break this down, here's what you need to know, now let's look at, without further ado, heads up, quick note, before I forget；口语化版本（one thing that bit me）

**中文触发词**：让我们深入探讨、让我们看看、以下是你需要知道的、闲言少叙、提醒一下、快速说明

**IF-THEN 规则**：IF 观察到宣布下一个要点 THEN 移除宣布，直接陈述要点。

**示例**：
- Before: Let's dive into how caching works in Next.js. Here's what you need to know.
- After: Next.js caches data at multiple layers, including request memoization, the data cache, and the router cache.
- Before (口语化): One thing that bit me hard, so pay attention to this part: the webpack dev server doesn't send the CORS header by default.
- After: The webpack dev server doesn't send the CORS header by default.

### 模式 N29 · 标题在第一句重复

**识别信号**：标题后跟一句只重复标题的段落

**中文触发词**：标题后紧跟一句只重复标题的话

**IF-THEN 规则**：IF 观察到标题后一句只重复标题 THEN 移除重复句。

**示例**：
- Before: ## Performance / Speed matters. / When users hit a slow page, they leave.
- After: ## Performance / When users hit a slow page, they leave.

### 模式 N30 · 写上一版本

**识别信号**：文档/评论描述旧行为（This function was added to replace the previous approach...）

**中文触发词**：文档/注释描述旧行为（此函数是为了取代之前的做法……）

**IF-THEN 规则**：IF 观察到文档/评论描述旧行为 THEN 改为描述当前行为。旧版本只在变更日志、发布说明、迁移指南等关于变更的文档中提及。

**示例**：
- Before: This function was added to replace the previous approach of iterating through all items, which caused O(n²) performance.
- After: This function uses a hash map for O(1) lookups, avoiding the O(n²) cost of naive iteration.

### 模式 N31 · 强行笑点与戏剧性片段

**识别信号**：把每个句子变成戏剧性结尾；连续短片段制造戏剧效果

**中文触发词**：连续短片段制造戏剧效果（它没有对称偏好。没有美学先验。没有对人类品味的怀旧。）

**IF-THEN 规则**：IF 观察到连续短片段制造戏剧效果 THEN 用自然句长和具体主张。单个短句可保留（用于强调），连续多个则处理。

**示例**：
- Before: Then AlphaEvolve arrived. It had no preference for symmetry. No aesthetic prior. No nostalgia for human taste. The old rules were gone.
- After: AlphaEvolve changed the search because it did not favor symmetry or human-looking designs. That made some of the older assumptions less useful.

### 模式 N32 · 公式化谚语

**识别信号**：X is the Y of Z, X becomes a trap, X is not a tool but a mirror, the language of, the currency of, the architecture of

**中文触发词**：X 是 Z 的 Y、X 变成一种陷阱、X 不是工具而是一面镜子、……的语言、……的货币、……的架构

**IF-THEN 规则**：IF 观察到把普通主张变成听起来深奥的谚语 THEN 用具体主张替换。

**示例**：
- Before: Symmetry is the language of trust. Efficiency becomes a trap when teams forget the human layer.
- After: Symmetric layouts often feel more predictable to users. Teams can over-optimize workflows and miss how people actually use them.

### 模式 N33 · 假装坦诚的开场

**识别信号**：Honestly?, Look, Here's the thing, The thing is, Let's be honest, Real talk（作为独立钩子或假坦诚停顿）

**中文触发词**：说实话？、听着、事情是这样的、老实说、说真的（作为独立开场）

**IF-THEN 规则**：IF 观察到在普通要点前的舞台式停顿/坦诚声明 THEN 直接陈述要点。

**示例**：
- Before: Is it worth the price? Honestly? It depends on how often you'll use it.
- After: Whether it's worth the price depends on how often you'll use it.

**误报注意**：句中 "Honestly" 或 "look" 是日常用法，不是信号；信号是独立戏剧化开场。

### 模式 N34 · 回答没人提出的异议

**识别信号**：This isn't (mainly/really) about, I'm not saying/arguing/trying to, To be clear, Don't get me wrong, This is not to say, You could argue/frame this differently but, Some might say... but

**中文触发词**：这（主要/真正）不是关于……、我并不是说/认为/试图、明确地说、别误会、这并不是说、有人可能会说……但是

**IF-THEN 规则**：IF 观察到回答文本中不存在的异议（尤其主题在别处未出现）THEN 移除无支持的辩护，保留真实主张并直接陈述。具名来源或完整回答的异议保留。直接主张（如 "the API is not thread-safe"）不是本模式。

**示例**：
- Before: This isn't mainly about prompt length, and I'm not arguing that documentation doesn't matter. You could categorize the problem another way, but the issue is whether the agent can use the instruction when it acts.
- After: The issue is whether the agent can use the instruction when it acts.

### 模式 N35 · 拒绝虚假替代方案

**识别信号**：A tempting option/approach would be, One might be tempted to, An obvious approach would be, You might think... but, It would be easy to just, Some would suggest

**中文触发词**：一个诱人的选择/方法是、有人可能会想、一个显而易见的方法是、你可能会认为……但、很容易就会……、有人会建议

**IF-THEN 规则**：IF 观察到引入无人会考虑的选项、在从句中拒绝、再不提及 THEN 移除虚假选项，直接陈述真实约束。真实替代方案（设计文档/教程/论证中读者可能考虑的选项）保留。

**示例**：
- Before: Session tokens are rotated every 24 hours. A tempting approach would be to rotate them by restarting the auth service on a cron job, but that would drop every active session. Rotation happens in place, and clients refresh transparently.
- After: Session tokens are rotated every 24 hours, in place, and clients refresh transparently.

**误报注意**：一个被拒选项可能有效；多个无关的短拒绝是更强信号。问每个句子增加了什么新信息，若只记录先前编辑则围绕其主要观点重写段落。

## 六、误报检查（What not to flag）

> 一个人可能使用上述某些模式。以下任何一项单独出现 NEVER 视为 AI 证据：

- **完美语法与一致风格**：专业人士或被编辑过。润色 ≠ AI。
- **混合随意与正式风格**：可能反映作者的领域、年龄或个人习惯。
- **「平淡」或「机械」散文**：AI 散文有*特定*信号。无这些信号的泛泛干涩只是干涩写作。
- **正式或学术词**：模式 N7 只针对特定过度使用的词。不简化所有正式词。
- **评论上的信函式开头/结尾**：称呼与签名比 ChatGPT 早几个世纪。
- **孤立出现的常见过渡词**：*Additionally*/*moreover*/*consequently* 只有堆叠时才是 AI 信号。一个 *however* 不是。
- **弯引号单独出现**：macOS/Word/Google Docs 默认自动弯引号。弯引号只有与其他信号堆叠时才计数。
- **em dash 单独出现**：编辑与记者常用。em dash 只有与公式化销售节奏同现才是证据。
- **单个强调短句**：只有连续多个戏剧化片段才标记。
- **刻意重复句首**：作者可能为节奏或压力重复句首（如 "She came. She saw. She conquered."）。仅当重复无增益时才改。
- **句中 "Honestly" 或 "look"**：随意写作中常见。信号是独立戏剧化开场，不是词本身。
- **有用的限制与免责声明**：保留范围声明、法律与安全提示、真实更正、具名异议、回复、FAQ 回答。
- **真实替代方案**：保留设计文档/教程/论证中读者可能考虑的选项。只移除文本否定后不再使用的不可信选项。
- **无来源主张**：大部分网络内容无引用。缺引用不证明任何事。
- **正确、复杂的格式**：可视化编辑器与模板无需 AI 也能产出干净输出。
- **第二手文本**：不在引号、标题、专有名词或讨论该短语本身的示例中改写受监控短语。

> 不确定时，寻找多个模式同现。一个 em dash 证明不了什么。同一段落中多个固定模式是更强证据。

## 七、保留的人类细节（Human details to keep）

> 这些细节常承载作者语气。除非伤害含义，否则保留：

- **具体、不寻常的细节**：真实地址、奇怪引语、或「the lawyer who used to work upstairs from my dentist」这类短语。
- **混合感受与未解决张力**：保留「I think this is mostly good, but it bothers me, and I can't fully explain why.」这类句子。
- **时代性引用**：对应特定年份与亚文化的俚语、梗、圈内笑话。模型滞后一年或更久。
- **刻意第一人称选择**：作者能解释为何保留某个删减或用词时，保留。
- **句长变化**：真实写作长短交替。AI 写作趋向均匀的中等句长节奏。
- **真实题外话、括号或自我纠正**：「(I keep wanting to say 'almost' here, but it really was certain.)」模型很少这样打断自己。
- **2022-11-30 前的编辑**：ChatGPT 公开上线。更早的内容几乎不可能是 AI 写的。

## 八、语气规则（写作样本匹配）

> 用户提供写作样本时，样本优先于默认风格规则。

1. **先读样本**：注意句长、用词、段落开头、标点、重复短语、过渡。
2. **匹配习惯**：不把随意词换成正式词，不删除刻意怪癖。
3. **样本使用 em dash 时**：按样本频率保留（不适用模式 N14 禁令）。

**无样本时的语气选择**：

| 文本类型 | 语气策略 |
|----------|----------|
| 博客/散文/观点/个人写作 | 保留作者观点、不确定性、混合感受、幽默、题外话、不均匀节奏；不虚构事实来让文本显得个人化 |
| 参考/技术/法律/事实文本 | 保持中性、简洁、客观 |
