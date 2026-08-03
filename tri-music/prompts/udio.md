# Udio 指令模板 · udio.md

> Udio 是发烧友首选 AI 音乐工具，**Hi-Fi 级音质**、**专业编辑功能**（乐段修复/续写）、**国风还原度较高**。
> 本模板聚焦**专业创作**与**国风纯器乐**场景。

## 0. 工具特性速查

| 维度 | 评分 | 说明 |
|---|---|---|
| 生成速度 | ⭐⭐ | 平均 2 分钟 |
| 中文支持 | ⭐⭐⭐ | 良好但需英文关键词辅助 |
| 国风还原 | ⭐⭐⭐⭐ | 二胡/古筝较优、还原度高于 Suno |
| 抖音适配 | ⭐⭐ | 偏发烧友、爆款倾向弱 |
| 个性化 | ⭐⭐⭐⭐⭐ | 创作自由度极高 |
| 免费额度 | ⭐⭐⭐⭐ | 较少但音质更高 |
| 综合推荐 | ⭐⭐⭐⭐ | 专业创作者/国风纯器乐首选 |

---

## 1. Udio 中文创作最佳实践

### 核心优势
- **Hi-Fi 级音质**（24-bit/48kHz）
- **专业编辑功能**（乐段修复、续写、混音）
- **国风乐器还原度高**（古筝/二胡/箫）

### 核心挑战
- **生成速度慢**（平均 2 分钟）
- **操作复杂**（需音乐结构知识）
- **国内访问需特殊网络**

---

## 2. 完整指令模板

```markdown
【Style Tags】（必填 · 英文）
[填写示例：Chinese traditional folk, pentatonic scale, guzheng, erhu, xiao, atmospheric, 90 BPM, emotional, cinematic, slow build]

【Title】
[填写示例：独弦之歌]

【Lyrics】
[粘贴歌词 · 与 Suno 模板相同]

【Advanced Settings】
- Audio Quality: High (Studio)
- Generation Length: 2-4 minutes
- Creativity: 0.6-0.8 (避免太天马行空)
- Style Influence: 0.5-0.7

【Negative Tags】
- generic pop progression
- auto-tune
- modern trap beats
- rap elements

【国风乐器专项】
- Guzheng tremolo and arpeggios
- Erhu slides and vibrato
- Xiao atmospheric melody
- Dizi bamboo flute countermelody

【反 AI 罐头指令 · 必加】
（自动追加 prompts/anti-can.md 全文）
```

---

## 3. 完整示例（独弦琴 · 国风纯音乐）

```markdown
【Style Tags】
Chinese traditional folk, pentatonic scale, 90 BPM, atmospheric and cinematic, emotional and melancholic, featuring guzheng tremolo, erhu slides, xiao melody, slow build with dynamic emotional climax

【Title】
独弦之歌（无歌词纯音乐版）

【Lyrics】
[Instrumental - 无歌词]

【Advanced Settings】
- Audio Quality: High (Studio)
- Generation Length: 3 minutes
- Creativity: 0.6
- Style Influence: 0.7

【Negative Tags】
- vocal
- rap
- electronic dance music
- modern pop

【国风乐器专项】
- 主旋律：古筝（带摇指与划音）
- 副旋律：二胡（带滑音与揉弦）
- 装饰：箫（带气声）
- 鼓点：中国大鼓+手碟（弱化）
- 环境音：海浪声（侧链）

【反 AI 罐头指令】
- 主题必须围绕"独弦琴"展开
- 副歌金句使用"独弦"重复
- 编曲必须有独弦琴或箫的标志性独奏段落（≥30 秒）
- 不要使用 1645 标准 POP 和弦进行
- 加入海浪声环境音作为情绪衬底
```

---

## 4. Udio 3 套差异化指令

### 场景 ① · 国风纯器乐

```markdown
【Style Tags】
Chinese traditional instrumental, 80-100 BPM, atmospheric, featuring guzheng, erhu, pipa, xiao, cinematic, emotional

【Advanced Settings】
- Audio Quality: High (Studio)
- Generation Length: 3-5 minutes
- Creativity: 0.5-0.6
- Style Influence: 0.7-0.8
```

### 场景 ② · 国风跨界融合

```markdown
【Style Tags】
Chinese traditional folk with R&B, jazz, or lo-fi elements, 90-110 BPM, featuring guzheng, erhu, modern beats, atmospheric, soulful

【Advanced Settings】
- Creativity: 0.7-0.8（保留更多创意）
- Style Influence: 0.5
```

### 场景 ③ · 古风纯人声（vocal）

```markdown
【Style Tags】
Chinese ancient-style vocal, 70-90 BPM, female or male vocal with traditional singing technique, atmospheric, cinematic, emotional

【Advanced Settings】
- Vocal style: operatic, narrative
- Audio Quality: High
```

---

## 5. Udio 专业编辑技巧

### 技巧 ① · Inpainting（乐段修复）
对生成结果中不满意的某 10-30 秒，用 Inpainting 重新生成，其余保留。

### 技巧 ② · Extend（续写）
对生成结果满意但不完整，用 Extend 续写后续段落，**保持风格一致性**。

### 技巧 ③ · Style Influence 控制
- **高（0.8-1.0）**：强风格控制、输出稳定但创意受限
- **中（0.5-0.7）**：平衡风格与创意（推荐）
- **低（0.0-0.4）**：高创意但风格不可控

### 技巧 ④ · Creativity 控制
- **高（0.8-1.0）**：高创意但输出不稳定
- **中（0.5-0.7）**：平衡（推荐）
- **低（0.0-0.4）**：稳定但缺乏变化

### 技巧 ⑤ · 多次生成选最优
Udio 一次出 2 首，**生成 3-5 次**挑选后用 Inpainting 精修，比"一次性完美"更现实。

---

## 6. 常见错误与避坑

| 错误 | 后果 | 解决方案 |
|---|---|---|
| ❌ 期望"一次性完美" | 浪费积分 | 分次生成+ Inpainting 精修 |
| ❌ Style Influence 拉满 | 创意受限 | 保持 0.5-0.7 中等值 |
| ❌ 国风创作用现代 POP 关键词 | 输出违和 | 显式指定 guzheng/erhu/xiao |
| ❌ 不指定 BPM | 节奏不可控 | 显式指定 |
| ❌ 期望免费版商用 | 版权风险 | 确认订阅条款 |
