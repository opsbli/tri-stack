# 四维审计检查项模板

> 本文件是 tri-checklist SKILL.md §方法论 四维审计框架的展开模板。每维度给出：核心问题 / 检查项清单（含复选框 + 严重程度标签）/ 数据采集方式 / 产出格式。SKILL.md 仅留概览，详细检查项在此检索。

> **grep 检索模式**：`grep -n "§<维度号>" references/audit-checklist-template.md`（如 `grep -n "§2" ` 定位审查点维度）

> **严重程度标签**：`[BLOCKER]`（阻塞提交）/ `[MAJOR]`（应修复）/ `[MINOR]`（建议修复），与 tri-review 审查报告对齐。

---

## §1 改动点维度（Changes）

**核心问题**：改了什么？哪些文件/函数/逻辑？改动类型是什么？

### 检查项清单

- [ ] `[BLOCKER]` **改动文件清单已列出** — 所有受影响文件（新增/修改/删除）均已记录
- [ ] `[BLOCKER]` **改动函数清单已列出** — 所有改动的函数/方法均已记录（含函数名 + 文件路径）
- [ ] `[MAJOR]` **改动类型已标注** — 每个改动标注类型（新增 / 修改 / 删除 / 重构）
- [ ] `[MAJOR]` **改动行数统计已列出** — 每个文件的增删行数已统计
- [ ] `[MINOR]` **改动 commit 信息已记录** — 若为 commit id 模式，commit message 已记录

### 数据采集

```bash
# 改动文件清单（按模式选择命令，见 git-diff-commands.md）
git diff --cached --name-status          # 暂存区
git diff --name-status                    # 工作区
git diff <commit>..HEAD --name-status     # commit id

# 改动函数清单（需 parse_git_diff.py 解析 hunk）
python scripts/parse_git_diff.py --mode <staged|working|commit> --commit <hash> --out diff.json
```

### 产出格式

```markdown
## 1. 改动点

### 1.1 改动文件清单

| 文件 | 类型 | 增行 | 删行 |
|---|---|---|---|
| src/auth/login.ts | 修改 | +25 | -8 |
| src/utils/helper.ts | 新增 | +45 | -0 |
| src/old/deprecated.ts | 删除 | +0 | -120 |

### 1.2 改动函数清单

- `src/auth/login.ts` → `login()` / `validateToken()` / `refreshSession()`
- `src/utils/helper.ts` → `formatDate()` / `parseQuery()`（新增）
```

---

## §2 审查点维度（Review）

**核心问题**：改动是否正确？质量如何？安全吗？性能如何？

> 本维度与 tri-review Phase 1（规格合规）+ Phase 2（代码质量）对齐，开发者自检时参照同样标准。

### 检查项清单

#### 2.1 功能正确性（与 tri-review Phase 1 对齐）

- [ ] `[BLOCKER]` **改动实现了预期功能** — 改动是否完整实现需求规格
- [ ] `[BLOCKER]` **无回归问题** — 改动未破坏既有功能
- [ ] `[MAJOR]` **边界条件已处理** — 空值/边界值/异常输入有显式处理
- [ ] `[MAJOR]` **错误处理完整** — 异常捕获 + 错误信息有意义 + 不吞异常

#### 2.2 代码质量（与 tri-review Phase 2 对齐）

- [ ] `[MAJOR]` **命名准确** — 变量/函数/类名表达意图
- [ ] `[MINOR]` **函数长度合理** — 建议 ≤50 行，超出须有正当理由
- [ ] `[MINOR]` **嵌套深度可控** — 建议 ≤3 层
- [ ] `[MINOR]` **无魔法数字** — 硬编码数字已提取为命名常量
- [ ] `[MINOR]` **复杂逻辑有注释** — 非显而易见的逻辑有说明

#### 2.3 安全性

- [ ] `[BLOCKER]` **无硬编码密钥/凭证** — 密钥从环境变量或密钥管理服务读取
- [ ] `[BLOCKER]` **SQL 注入防护** — 使用参数化查询，无字符串拼接 SQL
- [ ] `[BLOCKER]` **XSS 防护** — 用户输入输出时有编码/转义
- [ ] `[MAJOR]` **敏感数据日志脱敏** — 日志中不出现密码/Token/身份证
- [ ] `[MAJOR]` **权限检查在业务逻辑前** — 鉴权在业务逻辑入口处完成

#### 2.4 性能

- [ ] `[MAJOR]` **无 N+1 查询** — 循环内无数据库查询，或已用批量查询
- [ ] `[MAJOR]` **无不必要的循环嵌套** — O(n²) 及以上须有正当理由
- [ ] `[MINOR]` **大对象内存使用合理** — 流式处理或分页已考虑
- [ ] `[MINOR]` **关键路径无同步阻塞** — I/O 密集操作使用异步

### 数据采集

```bash
# 改动详情（查看具体代码变更）
git diff --cached -U10                    # 暂存区，显示 10 行上下文
git diff -U10                              # 工作区
git diff <commit>..HEAD -U10               # commit id

# 识别敏感文件改动
git diff --cached --name-only | grep -iE "\.env|secret|key|credential|password"
```

### 产出格式

```markdown
## 2. 审查点

### 2.1 功能正确性

- [ ] `[BLOCKER]` 改动实现了预期功能
- [ ] `[BLOCKER]` 无回归问题
- [ ] `[MAJOR]` 边界条件已处理
- [ ] `[MAJOR]` 错误处理完整

### 2.2 代码质量
...

### 2.3 安全性
...

### 2.4 性能
...
```

---

## §3 测试点维度（Test）

**核心问题**：测试覆盖够吗？边界条件测了吗？回归测试了吗？

### 检查项清单

#### 3.1 单元测试

- [ ] `[BLOCKER]` **核心逻辑有单元测试** — 改动的核心业务逻辑有对应单元测试
- [ ] `[MAJOR]` **新增函数有测试** — 本次新增的函数均有测试覆盖
- [ ] `[MAJOR]` **修改函数测试已更新** — 修改的函数对应的测试已同步更新
- [ ] `[MINOR]` **测试用例可读且独立** — 测试间无依赖，可独立运行

#### 3.2 边界测试

- [ ] `[MAJOR]` **空值/边界值有测试** — 空输入/边界值/异常输入有专门测试
- [ ] `[MAJOR]` **并发场景有测试** — 涉及并发的改动有并发测试
- [ ] `[MINOR]` **超时/重试有测试** — 外部调用的超时/重试有测试

#### 3.3 集成测试

- [ ] `[MAJOR]` **接口契约有集成测试** — 改动的 API 有集成测试
- [ ] `[MAJOR]` **数据流有集成测试** — 端到端数据流有测试
- [ ] `[MINOR]` **第三方依赖有 Mock/Stub** — 第三方依赖用 Mock 隔离

#### 3.4 回归测试

- [ ] `[BLOCKER]` **既有测试全部通过** — 既有测试套件运行无失败
- [ ] `[MAJOR]` **受影响模块回归测试** — 改动可能影响的模块已回归测试
- [ ] `[MINOR]` **性能回归测试** — 关键路径性能无回归

### 数据采集

```bash
# 识别测试文件改动
git diff --cached --name-only | grep -iE "test|spec|__tests__"

# 识别测试覆盖工具
ls jest.config.* vitest.config.* pytest.ini pyproject.toml pom.xml build.gradle .mocharc.* 2>/dev/null

# 运行测试套件（按技术栈）
npm test 2>/dev/null || pnpm test 2>/dev/null || pytest 2>/dev/null || go test ./... 2>/dev/null
```

### 产出格式

```markdown
## 3. 测试点

### 3.1 单元测试

- [ ] `[BLOCKER]` 核心逻辑有单元测试
- [ ] `[MAJOR]` 新增函数有测试
- [ ] `[MAJOR]` 修改函数测试已更新
- [ ] `[MINOR]` 测试用例可读且独立

### 3.2 边界测试
...

### 3.3 集成测试
...

### 3.4 回归测试
...
```

---

## §4 测试步骤维度（Test Steps）

**核心问题**：手动测试怎么走？关键场景验证步骤是什么？

### 检查项清单

> 本维度按场景分组，每个场景列出手动测试步骤。开发者按步骤执行并勾选复选框。

#### 4.1 核心功能场景

- [ ] `[BLOCKER]` **场景 1: <场景名>** — 步骤: ① <步骤1> → ② <步骤2> → ③ <步骤3> | 预期: <预期结果>
- [ ] `[BLOCKER]` **场景 2: <场景名>** — 步骤: ① <步骤1> → ② <步骤2> | 预期: <预期结果>
- [ ] `[MAJOR]` **场景 3: <场景名>** — 步骤: ① <步骤1> → ② <步骤2> | 预期: <预期结果>

#### 4.2 异常路径场景

- [ ] `[MAJOR]` **异常场景 1: <场景名>** — 步骤: ① <触发异常> → ② <验证错误处理> | 预期: <错误提示/日志>
- [ ] `[MAJOR]` **异常场景 2: <场景名>** — 步骤: ① <边界输入> → ② <验证边界处理> | 预期: <兜底结果>

#### 4.3 兼容性场景（按需）

- [ ] `[MINOR]` **浏览器兼容** — Chrome/Firefox/Safari/Edge 主流浏览器验证
- [ ] `[MINOR]` **移动端兼容** — iOS/Android 主流设备验证（若适用）
- [ ] `[MINOR]` **响应式布局** — 不同屏幕尺寸验证（若适用）

#### 4.4 部署验证（按需）

- [ ] `[MAJOR]` **构建成功** — `npm run build` / `pnpm build` 等构建命令成功
- [ ] `[MAJOR]` **启动成功** — 应用正常启动，无启动错误
- [ ] `[MINOR]` **健康检查通过** — 健康检查端点返回 200（若适用）

### 数据采集

```bash
# 识别功能场景（从 README/路由/控制器推断）
cat README.md 2>/dev/null | head -100
grep -rn "router\.\(get\|post\|put\|delete\)\|@Get\|@Post\|@Controller" --include="*.{ts,js,py,java,go}" . 2>/dev/null | head -30

# 识别构建命令
cat package.json 2>/dev/null | python -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d.get('scripts',{}), indent=2))" 2>/dev/null
```

### 产出格式

```markdown
## 4. 测试步骤

### 4.1 核心功能场景

- [ ] `[BLOCKER]` **场景 1: 用户登录**
  - 步骤: ① 访问 /login → ② 输入有效凭证 → ③ 点击登录
  - 预期: 跳转到 /dashboard，显示用户信息

- [ ] `[BLOCKER]` **场景 2: 用户注册**
  - 步骤: ① 访问 /register → ② 填写表单 → ③ 提交
  - 预期: 注册成功，发送验证邮件

### 4.2 异常路径场景
...

### 4.3 兼容性场景（按需）
...

### 4.4 部署验证（按需）
...
```

---

## 维度间关联

四维并非孤立，审计时须识别关联：

| 关联 | 说明 |
|---|---|
| 改动点 → 审查点 | 改动函数清单决定审查点检查范围 |
| 改动点 → 测试点 | 改动函数清单决定测试点覆盖范围 |
| 审查点 → 测试步骤 | 审查发现的功能场景决定测试步骤场景 |
| 测试点 → 测试步骤 | 测试点边界条件决定测试步骤异常场景 |

checklist 报告末尾须有「维度关联」章节，点明关键关联。
