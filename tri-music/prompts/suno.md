# Suno AI 指令模板 · suno.md

> Suno AI 是全球龙头 AI 音乐工具，**几十秒出 2 首**、**支持 50+ 语言**、V5 模型人声自然度达新高。
> 本模板聚焦**中文爆款**创作，规避国内访问问题与积分限制。

## 0. 工具特性速查

| 维度 | 评分 | 说明 |
|---|---|---|
| 生成速度 | ⭐⭐⭐⭐⭐ | 几十秒出 2 首 |
| 中文支持 | ⭐⭐⭐⭐ | 优秀（无口音）但需用英文关键词辅助 |
| 国风还原 | ⭐⭐ | 古筝接近钢琴加混响、二胡常被小提琴替代 |
| 抖音适配 | ⭐⭐⭐ | 非中国本土训练数据、爆款倾向较弱 |
| 个性化 | ⭐⭐⭐⭐ | 风格控制能力强 |
| 免费额度 | ⭐⭐⭐ | 每日 50 积分（约 10 首），月底清零 |
| 综合推荐 | ⭐⭐⭐⭐ | 音质兜底首选、需配合代理 |

---

## 1. Suno 中文创作最佳实践

### 核心挑战
Suno 训练数据以**英文**为主，中文支持虽好但**国风元素还原弱**——古筝听起来像"钢琴加混响"，二胡常被"小提琴音色"替代。

### 解决策略
1. **英文 Style + 中文 Lyrics** 双轨制
2. 显式指定 "Chinese traditional instruments" 关键词
3. 多次生成 + 手动挑选

---

## 2. 完整指令模板

```markdown
【Style of Music】（必填 · 英文）
[填写示例：Chinese traditional folk with modern electronic, slow build to powerful chorus, 100 BPM, male vocal, emotional, cinematic]

【Title】
[填写示例：独弦之歌 (One String of Solitude)]

【Lyrics】（粘贴第一部分生成的歌词）
[Verse 1]
[粘贴歌词]
[Pre-Chorus]
[粘贴歌词]
[Chorus]
[粘贴歌词]
...

【Negative Tags】（避免项）
- generic pop chord progression
- auto-tune heavy
- rap verse
- english lyrics

【Style 关键词 · 中文国风专项】
- Chinese traditional instruments: guzheng, erhu, xiao, pipa
- Pentatonic scale
- Modern electronic production
- Atmospheric reverb
- Slow build, dynamic chorus
- Emotional, cinematic, melancholic

【反 AI 罐头指令 · 必加】
（自动追加 prompts/anti-can.md 全文）
```

---

## 3. 完整示例（独弦琴 · 国风电子）

```markdown
【Style of Music】
Chinese traditional folk with modern electronic fusion, 100 BPM, male vocal with raspy narrative tone, slow build to powerful chorus with electronic drums, pentatonic scale with Future Bass elements, atmospheric and cinematic, melancholic yet proud

【Title】
独弦之歌 (Song of the One-String)

【Lyrics】
[Verse 1]
潮水退去留下贝壳在沙滩
渔火渐远只剩桅杆的孤单
一根弦 挂满海风与咸
弹了千年 还没弹完

[Pre-Chorus]
人们说一弦只能弹一曲
可你听过海的声音吗

[Chorus]
独弦啊独弦 一弦弹尽千帆
独弦啊独弦 一根牵住两岸
独弦啊独弦 大海是琴盘
你听 风在合唱

[Verse 2]
[补充歌词]

[Bridge]
潮起是歌 潮落是叹
不解释的人 最是浪漫

[Chorus]
独弦啊独弦 一弦弹尽千帆
独弦啊独弦 一根牵住两岸
独弦啊独弦 大海是琴盘
你听 风在合唱 千年未散

【Negative Tags】
- generic pop chord progression
- auto-tune heavy
- english lyrics
- standard 4-chord progression

【Style 关键词】
Chinese traditional instruments (guzheng, xiao), pentatonic scale, modern electronic production, atmospheric ocean reverb, male vocal with narrative storytelling tone

【反 AI 罐头指令】
- 副歌"独弦啊独弦"重复 ≥ 2 次
- 避免主歌+8 度直入副歌的最常见 POP 套路
- 编曲必须有独弦琴或箫的标志性独奏段落
- 加入海浪声环境音作为情绪衬底
- 不要使用 1645 标准 POP 和弦进行
```

---

## 4. Suno 3 套差异化指令

### 场景 ① · 国风/古风

```markdown
【Style of Music】
Chinese traditional folk, 80-100 BPM, male or female vocal, pentatonic scale, featuring guzheng, erhu, xiao, pipa, atmospheric and cinematic, emotional

【Style 关键词】
traditional Chinese instruments, pentatonic, guzheng arpeggios, erhu slides, xiao atmospheric melody, traditional Chinese cultural elements
```

### 场景 ② · 国风电子融合

```markdown
【Style of Music】
Chinese traditional folk with Future Bass and Chill Electronica, 100-120 BPM, male or female vocal, pentatonic scale with modern electronic beats, featuring guzheng tremolo, erhu slides, atmospheric ocean or nature sounds

【Style 关键词】
Chinese traditional + Future Bass fusion, Chill Electronica, guzheng with reverb, atmospheric, dreamy, melancholic, 2025 hit-style
```

### 场景 ③ · 都市情感/治愈

```markdown
【Style of Music】
Chinese pop ballad, 60-90 BPM, gentle male or female vocal, piano-driven with string arrangement, emotional and introspective, cinematic

【Style 关键词】
Chinese pop, piano ballad, emotional storytelling, atmospheric, urban night mood, late-night vibes
```

---

## 5. Suno 使用技巧

### 技巧 ① · 多次生成选最优
Suno 一次出 2 首，**生成 5-10 次**挑选最优，比"反复要求重做"更高效。

### 技巧 ② · 善用 Negative Tags
显式排除不想要的元素："auto-tune heavy" "english lyrics" "standard 4-chord progression"。

### 技巧 ③ · Custom Mode 必用
不要用 Simple Mode，**Custom Mode** 才能精细控制歌词与风格。

### 技巧 ④ · Extend 功能做迭代
对生成结果满意但不完美时，用 Extend 续写/改写特定段落。

### 技巧 ⑤ · 国内访问需代理
免费版国内访问需特殊网络环境，建议 Pro 用户（$8/月）以稳定性。

### 技巧 ⑥ · 商用版权问题
免费作品带水印、商用需 Pro 订阅且**不能用于模仿真人歌手**（参考 2023《Heart on My Sleeve》下架案）。

---

## 6. 常见错误与避坑

| 错误 | 后果 | 解决方案 |
|---|---|---|
| ❌ Style 全用中文 | 识别率低 | Style 用英文、Lyrics 用中文 |
| ❌ 不指定 BPM | 节奏不匹配 | 显式指定 BPM |
| ❌ 不加 Negative Tags | 输出包含不想要元素 | 显式排除 |
| ❌ 一次性要求所有元素 | 输出混乱 | 分次生成 + Extend 迭代 |
| ❌ 国风创作不指定具体乐器 | 输出"假国风" | 显式列出 guzheng/erhu/xiao 等 |
| ❌ 商用免费版 | 法律风险 | Pro 订阅+确认授权 |

---

## 7. Suno vs 海绵音乐 vs 网易天音 vs 音潮 · 决策表

| 场景 | 推荐工具 | 理由 |
|---|---|---|
| 中文爆款快速验证 | **海绵音乐** | 中文押韵自然、抖音同源数据 |
| 音质兜底/国际化 | **Suno** | 全球行业标准、音质优 |
| 国风纯器乐/专业编曲 | **Udio** | 还原度优（但生成慢） |
| 零门槛生活记录 | **Melo** | 聊天式交互、零门槛 |
| 专业级控制/跨模态 | **音潮** | 全链路自研、跨模态 |
| 抖音爆款神曲 | **海绵音乐 + Suno** | 海绵出初稿、Suno 兜底音质 |
