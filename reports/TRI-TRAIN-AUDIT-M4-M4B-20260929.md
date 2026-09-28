# tri-stack-train 训练复盘（二）· M4a/M4b 补证与结构性发现

- **日期**：2026-09-29
- **范围**：`tri-stack-train` 仓库 **M0 → M4b** 全 6 个里程碑的交付复盘，接续
  [`TRI-TRAIN-USAGE-AUDIT-20260928.md`](./TRI-TRAIN-USAGE-AUDIT-20260928.md)（该文只覆盖 M0–M3a）。
- **数据源**：
  1. Proma 会话 `821db134-ae57-4f7d-ae8a-0e6747ab5d5f`（tri-stack-train，24 轮）
  2. pi-agent 会话导出 `01a0e250-fbd1-7310-9e1c-f58b6c489ce1`（cwd `C:\Users\sam\Documents\codes\tri-stack-train`）
  3. 从上述会话 tool_use 参数重建的 `.tribro` 文件（`requirements` / `design` / `tasks` / `implements` / `verdict`）
- **落地批次**：[tt2 批](../ops/patches/README.md)（5 条内容 + 3 条 CHANGELOG + 1 条清单登记，9 个 op）
  + tt3 批（反同源假设，2 条内容 + 2 条 CHANGELOG + 1 条清单登记，7 个 op）。

> **为什么需要这份补证**：前批审计结论已在 `7740c18` 落地，但落地后紧接着执行的 M4a/M4b
> **仍然 3 轮回炉**。因此本文的三条结构性发现不重复前批结论，而是解释
> 「补丁已生效、为什么还在失败」。

---

## 一、冒烟缺陷台账

| 里程碑 | 自动化门禁 | 本机冒烟暴露的缺陷 | 回炉 commit |
|---|---|---|---|
| M0 骨架 | typecheck ✓ / 24→28/28 ✓ / build ✓ | ① `Error: Electron uninstall`——沙箱为提速 `export ELECTRON_SKIP_BINARY_DOWNLOAD=1`，`npm install` 判 up-to-date 不重跑 postinstall，二进制缺失传导到真机 ② 无 `.env` 加载路径，Key 需手工写 `process.env`（附带补 DeepSeek 默认配置） | — |
| M1 会话核心 | typecheck ✓ / 36/36 ✓ / build ✓ | ③ **重命名无效**——编辑态门控 `editingTitle === s.id` 与存值 `s.title` 永不相等，输入框永不进编辑态 | — |
| M2 项目与记忆 | typecheck ✓ / 49/49 ✓ / build ✓ | ④ Attach 项目后指示仍显示「AGENTS —」——`refreshCtx` 只在选项目/挂载时跑，attach 成功不触发 | — |
| M3a 工具与技能 | typecheck ✓ / 57/57 ✓ / build ✓ | 无（联网查天气闭环冒烟通过） | — |
| M4a 内嵌终端 | typecheck ✓ / 81→83/83 ✓ / build ✓ | ⑤ **Windows shell 探测全失败**——`existsSync('cmd.exe')` 只查 CWD，不命中 PATH | `b949298` |
| M4b 内嵌浏览器 | typecheck ✓ / 109→112/112 ✓ / build ✓ | ⑥ 弹出**独立窗口** ≠ 需求说的「内嵌」（架构错） ⑦ 面板无法拖动调整宽度 ⑧ 拖拽区 1px 过窄 + 图标干扰 | `fdd8cda` / `103fc94`+`2f5c60f` / `c6d40ef` |

**核心指标**：测试规模 24 → 112（×4.7）；自动化门禁失败 **0** 次；7 个缺陷 **100%** 由人工本机冒烟发现。
6 个里程碑全部交付，其中 5 个被冒烟暴露缺陷（M3a 干净）。

> 前批审计已记录的「tri-verify 全程缺席」「renderer/UI 层测试空转」「零 commit 纪律」三项不再重复，
> 后两项已由 `7740c18` 的 tt 批处理。本文只记**补丁生效之后**仍然失败的部分。

---

## 二、根因：三层，最外层是需求

### 2.1 需求层——失败模式不是问得少，而是问的层次错

`tri-intent` clarify-gate 的门控判定是「需求模糊/矛盾/缺关键信息」，它正确地工作于**参数层**。
但它从不拷问**自然语言词的语义**——因为定性词在语法上不是"模糊"的。

**M4b 的对照（决定性证据）**：

- `requirements.md §6` 的验收标准把「期望结果」列直接写成 **「本机冒烟通过」**（M4b-AC4/AC5/AC6 三条）：

  | ID | 需求 | 期望结果 |
  |---|---|---|
  | M4b-AC4 | 浏览器标签生命周期：create/list/switch/close 正常工作 | 本机冒烟通过 |
  | M4b-AC5 | Agent 端到端：`browser_navigate` → `browser_observe` 能读到目标页面标题与文本 | 本机冒烟通过 |
  | M4b-AC6 | 用户交互：BrowserPanel 手动导航 + 切标签 + 关闭 | 本机冒烟通过 |

- `design.md` R1 风险缓解写的是：「webContentsView 与主窗口布局冲突 → **独立容器挂载**」。
  这是**风险缓解方案本身违背需求语义**（需求要「内嵌」，缓解方案给「独立」），却被当常规决策记录。
- 门① 澄清 3 项：UI 位置 / User-Agent / 存储——**0 个架构语义**。
- M4c-1 门① 澄清 8 项（Shiki / react-markdown / jsdiff / 路径识别 / file_diff / 面板位置 / 宽度 / 快捷键）
  ——**仍是 0 个架构语义**。问题形态复现，说明是机制缺陷而非偶发。

→ agent 于是按「独立窗口」交付，把分歧写进「已知限制 #1」+ 门④「⚠️ 部分通过」，
而冒烟清单第 2 步甚至把「出现一个 Proma Browser 独立窗口加载 example.com」写成**预期行为**——
三重风险转嫁给用户。用户按清单执行也发现不了，只能说「这个不是我要的」。

**定性词的完整链条**：`内嵌`（需求）→ `独立容器挂载`（设计缓解）→ `独立窗口`（实现）→ `已知限制 #1`（承认）
→ `⚠️ 部分通过`（裁定）→ `预期行为`（冒烟清单）→ 用户否决（2 次回炉）。
链条每一环都「合规」，但语义在第一步就丢了。

### 2.2 用例层——三个病灶

**病灶 A · 断言对象错位。** M1 的重命名 bug 在 `App.tsx` 的 UI 状态机里
（`editingTitle === s.id` 永假），而测试全写在 `session-service.renameSession`（存储层）。
穷举存储层永远不会抓住 UI 状态机——测的对象和 bug 不在同一层。

**病灶 B · 测试与实现共享同一个错误前提（最阴险）。** `shell-probe` 的缺陷是
`existsSync('cmd.exe')` 在 Windows 上只检查 CWD、不命中 PATH，所以探测永远返回 false。
但 `shell-probe.test.ts` 的 `describe('shell-probe · UT09（存在性检查分支）')` 里，
**几乎每条用例都把 `mockExistsSync` 设成 `false`**：

```ts
vi.mock('node:fs', async () => {
  const actual = await vi.importActual<typeof import('node:fs')>('node:fs')
  return { ...actual, existsSync: vi.fn() }
})
// ...
it('不存在的 shell 路径直接返回 false（不发 spawn）', async () => {
  mockExistsSync.mockReturnValue(false)   // ← 把 bug 的症状固化为期望行为
// ...
it('_probeShell: Windows 分支对 cmd.exe 走特殊探测参数', async () => {
  mockExistsSync.mockReturnValue(false)
```

测试断言的**正是 bug 的症状**——「shell 探测返回 false」被当成一个需要覆盖的分支。
于是 83/83、112/112 全绿，真机探测全失败。**这是「测试越严谨越掩盖 bug」的最锋利形式**：
不是 mock 掉了被测逻辑，而是测试与实现共享了同一个错误前提。
修复后 `shell-probe.ts` 自己写了注释印证：
`// Windows 下 existsSync('cmd.exe') 仅检查 CWD，无法命中 PATH；必须自己展开。`

**病灶 C · AC 与 AT 同一抽象层。** AC 用自然语言（「内嵌」「可交互」「优雅降级」），
AT 直接抄成「本机冒烟（用户）」，中间没有一次「翻译成可判定断言」的动作。
`templates/requirements.md §6` 的原模板本身给了正确示范（「可编译、含单测、覆盖率 ≥80%」），
但没有任何条文禁止写「本机冒烟通过」——所以 agent 每轮都能合规地抄。

### 2.3 家族流程层——四个环节的 skill 具体缺陷

| 环节 | 缺陷 | 证据 |
|---|---|---|
| **clarify-gate** | 只拷问参数、从不拷问语义；定性词不是它的触发条件 | 见 2.1；M4b 3 问 / M4c-1 8 问全部落在选型层，0 架构语义 |
| **tri-verify 门④** | 四态判据被掏空 | `m4a-verdict.md`：`## 裁定：✅ 通过（附本机冒烟待用户确认）` + `## 门④ 最终裁定：✅ 完全通过`；`m4b-verdict.md`：`### 门④ 最终裁定：✅ 完全通过` |
| **tri-review** | M4a/M4b 完全未运行 | 全程未读取 `SKILL.md` / `review-checklists.md`（比 M1–M3a 的 3 条 grep 更彻底） |
| **tri-coding templates** | 约束写在 `templates/` 里会在实例化时被静默丢弃 | 见 §三 A |

---

## 三、三个结构性发现（超出前批审计）

### A. 约束写在哪一层，决定它会不会被执行

同一个 tt 批（`7740c18`，2026-09-28 16:44）落地了两个修补，M4a/M4b 在 17:29–20:15 执行，
**patch 已生效期**。对照结果极其干净：

| 修补 | 写在 | 结果 |
|---|---|---|
| #4 commit 硬门 | `tri-coding/SKILL.md` | **生效**——M4a/M4b 均有 commit（`325a251` / `fdd8cda` / `103fc94` / `c6d40ef` …） |
| #5 AT 硬化规则 | `tri-coding/templates/tasks.md §3.3` | **失效**——M4a/M4b 的 `tasks.md` 中该规则出现 **0 次**；AT 项仍写成「本机冒烟（用户）」，正是该规则明令禁止的写法 |

M4a 的 `tasks.md §3` 连「三层测试覆盖」前导段都丢了。

**判据**：写在 `SKILL.md` 的约束会被执行，只写在 `templates/*.md` 的约束会在实例化时被静默丢弃。
根因是**没有任何校验兜底**——实例化后谁也不检查模板里的硬约束有没有被带过来。

### B. 门④ 判据形态失真，四态形同虚设

`tri-verify` §二 定义四态封闭判据：`通过（engine=<id>）` / `修复后通过（轮次 n，归因 A/B/C）` /
`已升级人审` / `未执行（原因）`。实测两份 verdict：

- **M4a**：`✅ 完全通过` —— 该标签**不在四态内**；实际经历 1 次回炉（`b949298`），
  应为「修复后通过（轮次 1，归因 C 环境）」；「完全通过」+「附本机冒烟待用户确认」自相矛盾。
- **M4b**：`✅ 完全通过` —— 实际 2 次回炉；同表内 `M4b-AC5` 标「⚠️ 部分」（仅 UT19 tool 分发层，
  无完整 Agent 循环驱动）——**「完全通过」+ 一个 AC「部分」并存，自相矛盾**。
- **证据锚定条款被绕过**：四态要求「通过」必须引用 runId / 输出粘贴 / 截图路径。
  实测证据是「2026-09-28 20:14 用户确认冒烟通过」——一句话盖章。

四态定义**没有校验器**，所以写什么都能通过。这是设计缺口，不是执行不认真。

### C. 门控存在性无人负责

tri-review 在 M4a/M4b 读取次数 **0**（前批审计记录的 M1–M3a 至少有 3 条 grep）。
tt 批的 #7 checklist 硬门没有拦住——因为该硬门只约束 **review 内部行为**
（"跑了 review 就必须读 checklist"），**没有第二个 skill 负责检查 review 有没有被调用**。
门控内部有牙，但门的触发条件本身没有牙。

---

## 四、落地映射

| 建议 | 落点 | op id |
|---|---|---|
| #1 需求语义拷问（定性词 → 可判定断言，作 G2 反问必答项） | `tri-intent/clarify-gate/SKILL.md` | `tt2-intent-clarify-semantic` |
| #2 AC 期望结果禁词硬红线 + 每条 MUST 附可观测断言 | `tri-coding/templates/requirements.md §6` | `tt2-coding-ac-decidable` |
| #3 AT 硬化上移 SKILL.md + 实例化后自检（治 §三 A） | `tri-coding/SKILL.md` §质量标准 | `tt2-coding-at-uplift` |
| #8 verdict 标签封闭校验 + 回炉轮次/commit 链（治 §三 B） | `tri-verify/SKILL.md` §二 | `tt2-verify-verdict-tag-gate` |
| #10 tri-review 存在性检查（治 §三 C） | `tri-coding/SKILL.md` 功能验证门强制规则 | `tt2-coding-review-existence-gate` |
| #5 反同源假设（测试夹具与实现共享错误前提） | `tri-coding/SKILL.md` §质量标准 + `tri-sdlc/children/tri-test/SKILL.md` 维度 3 | `tt3-*` |

**版本线**：`tri-intent` 1.14.5→1.15.0、`tri-coding` 1.9.1→1.10.0→1.11.0、
`tri-verify` 1.1.1→1.2.0、`tri-test` 1.1.9→1.2.0。

> #5 单独开批的原因：它是**测试编写**规范而非交付门控，落点需要双重论证——
> 单放 `tri-test`（SDLC P6）会重犯 §三 A 的错，因为 tri-stack-train 走的是 tri-coding I11 直调路径，
> 根本不经过 tri-sdlc。所以两处都落：`tri-coding`（实际写测试的地方）+ `tri-test`（SDLC 流程的家）。

---

## 五、仍未覆盖（诚实边界）

1. **tri-coding I11 链路本身无 tri-verify 集成测试**：M4a/M4b 的 verdict 均由 agent 手写，
   没有任何脚本校验四态标签。#8 已把校验要求写成条文，但**校验器仍未实现**。
2. **门④ 的自动化程度仍为 0**：`verdict.md` 的标签校验目前是 prompt 层约束，
   不像 `tri-verify/scripts/verify_gate.py` 有可执行实现。下一步应把「标签 ∈ 封闭集」
   做成 `verify_gate.py` 的一条断言（`--self-test` 反例夹具已存在，成本很低）。
3. **前批遗留的 P2 未处理项**：tri-coding 测试门禁的「系统层」在 train 项目始终为 0 条
   （13 个测试文件 12 个在 main/shared 层），本轮未改——它是覆盖策略问题而非合规问题。
4. **本文不覆盖 tri-stack-train 项目的代码层修补**（M4c-1 未启动）：
   M4c-1 门① 的 8 个澄清点同样 0 个架构语义，**建议开新需求前先补一问**——
   「文件预览面板 = 主窗口右侧并列面板，还是替代会话区？Diff 显示 = 新标签还是覆盖当前预览？」
   照 M4b 的教训，这两个词不问清楚又是一轮回炉。另外 M4c-1 的 Q6 默认写「右侧第 8 个组件」，
   这是第三次复用同一个未经验证的假设（M4b Q1 同款，然后炸了）——同一个默认值第三次出现就该被质疑。
