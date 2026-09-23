# 版本检查与更新规范

> 本文件是**本 skill 自带**的版本检查执行规范，随 skill 包分发，不依赖仓库内其他 skill 的文件。
> 家族级设计总纲（设计原则、端点配置真源、四处版本同步点、junction 单源例外、P1–P4 阻断定义）见
> `tri-intent/references/version-gate.md`。
> 所有 tri-* 家族 skill 的版本检查与更新操作均须遵循本规范。

> ⚠️ **本文为本地校正版**（见 `.workbuddy/patches/README.md`）。校正依据：与各 skill 实际搭载的
> `scripts/check_update.py` 行为逐条比对，修掉上游版本中不存在于实现的参数与退出码。

---

## 一、执行方式

```bash
python scripts/check_update.py --slug <slug> [--skill-dir <路径>] [--json]
                               [--force] [--dry-run] [--cache-dir <路径>] [--ttl-min <分钟>]
```

- `<slug>`：skill 标识，如 `tri-coding`；省略时读 SKILL.md frontmatter 的 `slug` 字段
- `--skill-dir`：skill 根目录，默认取脚本上级目录
- `--json`：输出 JSON 供 Agent 解析
- `--force`：强制重查，忽略节流缓存
- `--dry-run`：只判定不真正执行升级
- `--cache-dir`：缓存与备份目录覆盖（默认 `~/.cache/<slug>`），仅用于测试隔离
- `--ttl-min`：节流阈值（分钟），默认 1440

**退出码语义**（与 `check_update.py` 的 `EXIT_CODE` / `STATE_*` 严格对齐）：

| 退出码 | 状态 | 含义 |
|--------|------|------|
| 0 | A · 校验通过 | 响应有效且 current >= latest，放行 |
| 10 | B · 离线降级 | 网络不可达（DNS/连接失败/超时），重试 1 次仍失败，放行 |
| 11 | C · 通道降级 | 可达但响应无效（非 200 / 非 JSON / 无版本字段 / 读不到配置），放行 |
| 12 | D · 升级降级 | 确实陈旧且已真实尝试升级但未完成，放行 |
| 20 | BLOCK | 阻断，按 `block_code` 输出结构化恢复指引 |
| 64 | 参数或环境错误 | 脚本入参错误，或 SKILL.md 不存在 |

> 退出码 `<20` 一律放行（含 A/B/C/D 四态）；`>=20`（BLOCK）绝对禁止执行，并按 `block_code` 输出恢复指引：
> **P2** 签名明确不一致 / **P3** 回滚失败 / **P4** 通道此前正常但现在 5xx 且重试仍失败。
> 脚本自身异常时兜底降级放行（退出码 11），NEVER 因版本门自身故障阻断 skill 启动。

---

## 二、执行要点

1. **先读本地**：从 SKILL.md frontmatter 读取当前版本（`version:`）与自身 slug（`slug:`）
2. **节流缓存**：默认 1440 分钟（24h）内已查过且缓存有效 → 复用缓存结果
3. **端点解析**：API 主机读自 `~/.skillhub/metadata.json`（取 `skills_search_url` 与
   `skills_primary_download_url_template` 中先可解析者的 **origin**）；NEVER 硬编码域名。
   营销官网 `skillhub.cn` 对任意路径返回 200 + text/html 兜底页，**绝不可作校验端点**；
   实测 API 主机为 `api.skillhub.cn`
4. **网络查询**：`GET {api_host}/api/v1/skills/{slug}`，超时 ≤5s，失败重试 1 次（间隔 0.4s）
5. **响应有效性（三条件同时成立）**：HTTP 200 **且** `Content-Type` 含 `application/json`
   **且** 能解析出版本字段。仅看状态码会被 SPA 兜底页击穿
6. **最新版取值**：`latestVersion.version`，缺失时回退 `skill.tags.latest`
7. **归属校验**：响应中的 `slug` 与请求 slug 不一致 → 判响应无效（防串包）
8. **版本比较**：逐段整数比较（避免 `1.10.0 < 1.9.0` 的字典序陷阱）
9. **四态判定**（与脚本 `STATE_*` 对齐）：
   - **A 态（校验通过）**：响应有效且 current >= latest → 直接放行（退出码 0）
   - **B 态（离线降级）**：网络不可达 → 标注「版本校验未完成（离线）」后继续（退出码 10）
   - **C 态（通道降级）**：可达但响应无效 / 404 / 405 / 读不到配置 → 标注
     「版本校验未完成（通道不可用）」+ 输出通道异常告警后继续（退出码 11）
   - **D 态（升级降级）**：陈旧且已真实尝试自动升级但未完成 → 标注「版本陈旧·自动升级失败」
     + 输出手动升级指引后继续（退出码 12）
   - 四态 NEVER 用于绕过「已检出陈旧却不尝试升级」——MUST 先真实执行一次自动升级，失败方落 D 态
10. **升级流程**（仅 D 态触发，且 `skip_auto_upgrade` 为假）：
    - 权限探测 → 备份整树 → `skillhub upgrade <slug>` → `skillhub verify <slug>` → 必要时回滚
    - 签名明确不一致(P2) 或 回滚失败(P3) → 阻断（退出码 20）；其余降级场景 → 放行（退出码 12）
    - CLI 定位顺序：`PATH` 中的 `skillhub` → `~/.skillhub/skills_store_cli.py`；两者皆无 → 落 D 态
    - **junction / `source: local` 单源安装 → 跳过自动升级**，提示维护者在源码树手动同步
11. **兜底容错**：脚本自身异常 → 降级放行（退出码 11），NEVER 因版本门自身故障阻断 skill 启动

---

## 三、测试注入

通过 `--simulate-*` 参数注入模拟场景，验证四态判定逻辑（**仅用于自检，不改变真实环境**）：

| 注入参数 | 取值 | 模拟场景 |
|----------|------|----------|
| `--simulate-net` | `offline` / `http500` / `http404` / `html` / `badjson` | 网络与响应故障（`html` 模拟 SPA 兜底页） |
| `--simulate-latest` | 版本号 | 注入平台最新版本号用于比较 |
| `--simulate-fetch-ok` | 版本号 | 注入一次有效响应并指定其 latest（跳过真实网络） |
| `--simulate-upgrade` | `success` / `fail` / `interrupt` / `perm` / `none` | 注入升级结果 |

---

## 四、版本比较算法

```python
SEMVER_RE = re.compile(r"^\d+(\.\d+)*$")

def compare_versions(v1: str, v2: str):
    """比较两个 SemVer 版本号。返回 -1/0/1；任一不合格式则返回 None。"""
    if not v1 or not v2:
        return None
    if not SEMVER_RE.match(v1) or not SEMVER_RE.match(v2):
        return None
    parts1 = [int(x) for x in v1.split('.')]
    parts2 = [int(x) for x in v2.split('.')]
    while len(parts1) < len(parts2):
        parts1.append(0)
    while len(parts2) < len(parts1):
        parts2.append(0)
    for a, b in zip(parts1, parts2):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0
```

---

## 五、节流缓存机制

- 缓存文件：`~/.cache/<slug>/update-state.json`（可由 `--cache-dir` 覆盖）
- 缓存内容：按 slug 记录 `checked_at` / `state` / `current` / `latest` / `compare` / `last_valid_at`
- 节流窗口：`--ttl-min`，默认 1440 分钟（24 小时）
- `--force` 参数可强制绕过节流
- 备份目录：`~/.cache/<slug>/backup/`，升级前整树备份
- 缓存或备份写入失败 NEVER 影响主流程

---

## 六、生成物版本检查章节规范

所有 tri-* 家族 skill 的 SKILL.md 中，版本检查章节必须为**瘦指针 STUB**：

- **行数上限**：≤30 行
- **必须内容**：执行方式 + 指向本文件（`references/version-check-spec.md`）的指针
- **禁止内容**：内联四态判定细则、内联升级流程、内联版本比较算法
- **原因**：避免散文描述算法让模型复现导致漂移；所有版本检查逻辑集中在本规范文件中

---

## 七、与家族总纲的关系

| 文件 | 角色 | 范围 |
|---|---|---|
| **`references/version-check-spec.md`**（本文件） | **执行规范**，随每个 skill 包分发 | 该 skill 如何执行版本检查：入参、退出码、四态处置、兜底 |
| **`tri-intent/references/version-gate.md`** | **家族设计总纲** | 家族级设计原则、端点配置真源、四处版本同步点、junction 单源例外、P1–P4 阻断定义 |

- 每个 skill **自带**本文件，是为了满足「支持独立安装」——单独安装一个 skill 时不应依赖其他 skill 的文件
- **`scripts/check_update.py` 是可执行真源**：本文件与脚本冲突时，以脚本实际行为为准
- `tri-intent/references/version-gate.md` 与本文冲突时，*执行细节*以本文为准，*家族级设计约束*以总纲为准
