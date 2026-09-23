#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tri-* 家族版本检查与强制自动更新脚本（check_update.py，按 --slug 适配各 skill）

职责：把 `references/version-check-spec.md` 中原本仅以文字约定存在的「第零步版本门」
落成确定性可执行逻辑。prompt 层只负责「调用本脚本 + 读取 JSON 结果 + 按态处置」，
NEVER 自行推断版本、NEVER 自行拼接升级命令。脚本自身不绑定 tri-intent——
它通过 --slug / --skill-dir（或自动从所在目录推导）适配任意 tri-* skill，
因此全家族共用同一份逻辑、同一套四态与退出码。

四态判定（与 version-check-spec.md §四 逐条对应）：
  A 校验通过   响应有效且 current >= latest
  B 离线降级   网络不可达（DNS/连接失败/超时），重试 1 次仍失败
  C 通道降级   可达但响应无效（非 200 / 非 JSON / 无版本字段 / 读不到配置）
  D 升级降级   确实陈旧且已真实尝试升级但未完成（CLI 缺失/升级失败/权限不足）

用法（脚本按 --slug 自动适配任意 tri-* skill，自身不绑定 tri-intent）：
    python check_update.py --json                                   # 自动定位所在 skill 目录
    python check_update.py --slug <slug> --skill-dir /path/to/<slug>
    python check_update.py --force --json          # 绕过节流强制检查
    python check_update.py --dry-run               # 只判定不真升级
    python check_update.py --cache-dir /tmp/test   # 测试隔离（避免污染真实缓存）

    # 测试注入（仅用于自检，不改变真实环境）
    python check_update.py --simulate-latest 9.9.9 --simulate-upgrade fail
    python check_update.py --simulate-net offline

退出码：
    0   A 校验通过（放行）
    10  B 离线降级（放行）
    11  C 通道降级（放行）
    12  D 升级降级（放行）
    20  阻断（P2 签名不一致 / P3 回滚失败 / P4 通道已证实正常却超时）
    64  参数或环境错误
  判定规则：0 <= code < 20 → 放行；code >= 20 → 阻断。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

DEFAULT_SLUG = "tri-intent"

# skillhub 客户端配置真源。NEVER 硬编码域名——营销官网 skillhub.cn 对任意路径
# 都返回 200+HTML 兜底页，误用会让校验永远"假通过"。
SKILLHUB_HOME = Path.home() / ".skillhub"
METADATA_JSON = SKILLHUB_HOME / "metadata.json"
STORE_CLI = SKILLHUB_HOME / "skills_store_cli.py"

LOCK_REL = Path(".workbuddy") / "skills" / ".skills_store_lock.json"

# 缓存根目录默认值；decide() 会按 slug（或 --cache-dir）重设为 ~/.cache/<slug>
CACHE_DIR = Path.home() / ".cache" / "tri-intent"
STATE_FILE = CACHE_DIR / "update-state.json"
BACKUP_ROOT = CACHE_DIR / "backup"

# 节流阈值，与 coding/scripts/check-updates.sh 的 STALE_MIN 一致
STALE_MIN = 1440

HTTP_TIMEOUT = 5          # §2.5 单次请求超时 MUST <= 5s
HTTP_RETRY = 1            # §2.5 失败重试 1 次

VERSION_RE = re.compile(r"^version:\s*([0-9]+(?:\.[0-9]+)*)", re.MULTILINE)
SLUG_RE = re.compile(r"^slug:\s*([A-Za-z0-9._-]+)", re.MULTILINE)

# 移植自 coding/scripts/log.js versionCompare 的格式白名单：
# 只允许数字和点号，且不能以点号开头或结尾
SEMVER_RE = re.compile(r"^\d+(\.\d+)*$")

STATE_PASS = "A"
STATE_OFFLINE = "B"
STATE_CHANNEL = "C"
STATE_STALE = "D"
STATE_BLOCK = "BLOCK"

EXIT_CODE = {
    STATE_PASS: 0,
    STATE_OFFLINE: 10,
    STATE_CHANNEL: 11,
    STATE_STALE: 12,
    STATE_BLOCK: 20,
}

SELF_CHECK_LABEL = {
    STATE_PASS: "已通过",
    STATE_OFFLINE: "离线降级",
    STATE_CHANNEL: "通道降级",
    STATE_STALE: "升级降级",
    STATE_BLOCK: "已阻断",
}


# ---------------------------------------------------------------------------
# 版本比较：移植自 coding/scripts/log.js 的 versionCompare()
# ---------------------------------------------------------------------------


def version_compare(a: Optional[str], b: Optional[str]) -> Optional[int]:
    """逐段整数比较两个版本号。

    与 coding/scripts/log.js versionCompare() 行为完全一致：
      - 任一为空 → None（原实现 console.warn 后 return null）
      - 任一不匹配 ^\\d+(\\.\\d+)*$ → None
      - 逐段 int 比较，短的一侧缺位补 0
      - a<b → -1；a>b → 1；相等 → 0

    这解决了字符串比较的经典缺陷：'1.10.0' < '1.9.0' 在字典序下成立，
    但按段比较 10 > 9，正确结果是 1.10.0 更新。
    """
    if not a or not b:
        return None
    if not SEMVER_RE.match(a) or not SEMVER_RE.match(b):
        return None
    sa = a.split(".")
    sb = b.split(".")
    for i in range(max(len(sa), len(sb))):
        x = int(sa[i]) if i < len(sa) else 0
        y = int(sb[i]) if i < len(sb) else 0
        if x < y:
            return -1
        if y < x:
            return 1
    return 0


# ---------------------------------------------------------------------------
# 本地信息读取
# ---------------------------------------------------------------------------


def read_frontmatter(skill_md: Path) -> Tuple[Optional[str], Optional[str]]:
    """从 SKILL.md frontmatter 读取 (version, slug)。"""
    try:
        head = skill_md.read_text(encoding="utf-8", errors="ignore")[:4000]
    except OSError:
        return None, None
    mv = VERSION_RE.search(head)
    ms = SLUG_RE.search(head)
    return (mv.group(1) if mv else None), (ms.group(1) if ms else None)


def load_registry_entry(slug: str) -> Optional[dict]:
    lock = Path.home() / LOCK_REL
    if not lock.is_file():
        return None
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    skills = data.get("skills")
    return skills.get(slug) if isinstance(skills, dict) else None


def is_link_like(p: Path) -> bool:
    """判定路径是否为 symlink 或 Windows directory junction。

    Windows 上 os.path.islink() 对 junction 返回 False，必须额外看 reparse tag。
    junction 安装意味着「运行态即源码态」，CLI 升级会覆盖链接破坏单源结构。
    """
    try:
        if p.is_symlink():
            return True
    except OSError:
        pass
    try:
        st = os.lstat(p)
    except OSError:
        return False
    return getattr(st, "st_reparse_tag", 0) != 0


def detect_install_mode(skill_dir: Path, registry: Optional[dict]) -> dict:
    """判定安装形态，决定是否跳过自动升级。"""
    user_level = Path.home() / ".workbuddy" / "skills" / skill_dir.name
    linked = is_link_like(skill_dir) or is_link_like(user_level)
    src_local = bool(registry and registry.get("source") == "local")
    dangling = user_level.exists() is False and is_link_like(user_level)
    return {
        "user_level_path": str(user_level),
        "is_link": linked,
        "source_local": src_local,
        "dangling_link": dangling,
        # junction 单源安装 → 跳过自动升级（version-check-spec.md §三 junction 例外）
        "skip_auto_upgrade": linked or src_local,
    }


def check_writable(target: Path) -> Tuple[bool, Optional[str]]:
    """探测目标目录可写性，用于提前识别「权限不足」。"""
    if not target.is_dir():
        return False, f"目录不存在：{target}"
    probe = target / f".wb_perm_probe_{os.getpid()}"
    try:
        probe.write_text("x", encoding="utf-8")
        probe.unlink()
        return True, None
    except OSError as e:
        return False, f"{type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# 端点解析与远端查询
# ---------------------------------------------------------------------------


def resolve_api_host() -> Tuple[Optional[str], Optional[str]]:
    """从 ~/.skillhub/metadata.json 推导 API 主机。返回 (host, error)。"""
    if not METADATA_JSON.is_file():
        return None, f"配置文件不存在：{METADATA_JSON}"
    try:
        meta = json.loads(METADATA_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return None, f"配置文件不可解析：{type(e).__name__}: {e}"
    for key in ("skills_search_url", "skills_primary_download_url_template"):
        url = meta.get(key)
        if not isinstance(url, str):
            continue
        m = re.match(r"^(https?://[^/]+)", url)
        if m:
            return m.group(1), None
    return None, "配置中未找到可推导 API 主机的字段"


def fetch_latest(api_host: str, slug: str,
                 simulate_net: str = "ok",
                 simulate_fetch_ok: Optional[str] = None) -> dict:
    """请求平台校验端点。返回结构化结果，NEVER 抛异常。

    分类原则：
      - 网络层不可达（DNS/拒连/超时）→ kind='offline' → B 态
      - 有响应但不满足 §2.4 三条件      → kind='invalid' → C 态
    """
    url = f"{api_host}/api/v1/skills/{slug}"
    out = {"url": url, "kind": None, "latest": None,
           "http_status": None, "content_type": None, "detail": None}

    # ---- 测试注入：有效响应（跳过真实请求，直接给 latest）----
    # 与 --simulate-net / --simulate-upgrade 对称，用于离线/未注册环境下
    # 确定性地验证 A 态（已最新）与 陈旧→升级 路径。
    if simulate_fetch_ok is not None:
        out["kind"] = "ok"
        out["latest"] = str(simulate_fetch_ok).strip()
        out["detail"] = f"模拟注入：有效响应 latest={out['latest']}"
        return out

    # ---- 测试注入通道：不发真实请求，直接构造对应故障 ----
    if simulate_net != "ok":
        out["detail"] = f"模拟注入：{simulate_net}"
        if simulate_net == "offline":
            out["kind"] = "offline"
            out["detail"] = "模拟注入：网络不可达（DNS 解析失败）"
        elif simulate_net == "http500":
            out["kind"] = "invalid"
            out["http_status"] = 500
            out["detail"] = "模拟注入：HTTP 500"
        elif simulate_net == "http404":
            out["kind"] = "invalid"
            out["http_status"] = 404
            out["detail"] = "模拟注入：HTTP 404 平台未收录"
        elif simulate_net == "html":
            out["kind"] = "invalid"
            out["http_status"] = 200
            out["content_type"] = "text/html"
            out["detail"] = "模拟注入：SPA 兜底页（200 + text/html）"
        elif simulate_net == "badjson":
            out["kind"] = "invalid"
            out["http_status"] = 200
            out["content_type"] = "application/json"
            out["detail"] = "模拟注入：JSON 中缺少版本字段"
        else:
            out["kind"] = "invalid"
            out["detail"] = f"未知模拟类型：{simulate_net}"
        return out

    last_err = None
    for attempt in range(HTTP_RETRY + 1):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json",
                              "User-Agent": "tri-skills-version-gate/1.0"})
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                out["http_status"] = resp.getcode()
                ctype = (resp.headers.get("Content-Type") or "").lower()
                out["content_type"] = ctype
                body = resp.read()
                # §2.4 有效性条件二：Content-Type 必须含 application/json
                if "application/json" not in ctype:
                    out["kind"] = "invalid"
                    out["detail"] = f"Content-Type 非 JSON：{ctype or '(空)'}"
                    return out
                try:
                    data = json.loads(body.decode("utf-8", errors="replace"))
                except json.JSONDecodeError as e:
                    out["kind"] = "invalid"
                    out["detail"] = f"响应体非合法 JSON：{e}"
                    return out
                # §2.3 取值优先级：latestVersion.version → skill.tags.latest
                latest = None
                lv = data.get("latestVersion")
                if isinstance(lv, dict):
                    latest = lv.get("version")
                if not latest:
                    sk = data.get("skill")
                    if isinstance(sk, dict):
                        tags = sk.get("tags")
                        if isinstance(tags, dict):
                            latest = tags.get("latest")
                if not latest:
                    out["kind"] = "invalid"
                    out["detail"] = "响应缺少 latestVersion.version / skill.tags.latest"
                    return out
                # §2.3 归属校验：防串包
                got_slug = data.get("slug") or (data.get("skill") or {}).get("slug")
                if got_slug and got_slug != slug:
                    out["kind"] = "invalid"
                    out["detail"] = f"slug 不匹配：请求 {slug}，返回 {got_slug}"
                    return out
                out["kind"] = "ok"
                out["latest"] = str(latest).strip()
                return out
        except urllib.error.HTTPError as e:
            # 有响应但状态码非 2xx → 通道问题，不是离线
            out["http_status"] = e.code
            out["kind"] = "invalid"
            out["detail"] = f"HTTP {e.code} {e.reason}"
            last_err = out["detail"]
            if e.code in (404, 405):
                return out          # 明确的"平台未收录"，无需重试
        except urllib.error.URLError as e:
            out["kind"] = "offline"
            out["detail"] = f"网络不可达：{e.reason}"
            last_err = out["detail"]
        except (TimeoutError, OSError) as e:
            out["kind"] = "offline"
            out["detail"] = f"网络异常/超时：{type(e).__name__}: {e}"
            last_err = out["detail"]
        if attempt < HTTP_RETRY:
            time.sleep(0.4)
    out["detail"] = last_err or "未知网络错误"
    return out


# ---------------------------------------------------------------------------
# 节流状态（移植 coding check-updates.sh 的时间戳门）
# ---------------------------------------------------------------------------


def load_state() -> dict:
    if not STATE_FILE.is_file():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(state: dict) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass          # 缓存写失败 NEVER 影响主流程


def is_fresh(state: dict, slug: str, ttl_min: int) -> bool:
    rec = (state.get("skills") or {}).get(slug)
    if not rec:
        return False
    ts = rec.get("checked_at")
    if not isinstance(ts, (int, float)):
        return False
    return (time.time() - ts) < ttl_min * 60


# ---------------------------------------------------------------------------
# 升级执行
# ---------------------------------------------------------------------------


def locate_cli() -> Tuple[Optional[List[str]], str]:
    """按 version-check-spec.md §3.2 顺序定位 CLI。返回 (argv 前缀, 描述)。"""
    exe = shutil.which("skillhub")
    if exe:
        return [exe], f"PATH: {exe}"
    if STORE_CLI.is_file():
        return [sys.executable, str(STORE_CLI)], f"CLI 本体: {STORE_CLI}"
    return None, "未找到 skillhub CLI（PATH 与 ~/.skillhub/skills_store_cli.py 均不可用）"


def run_cmd(argv: List[str], timeout: int = 180) -> Tuple[int, str]:
    try:
        p = subprocess.run(argv, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()
    except subprocess.TimeoutExpired:
        return 124, f"命令超时（>{timeout}s）：{' '.join(argv)}"
    except OSError as e:
        return 126, f"命令无法执行：{type(e).__name__}: {e}"


def backup_skill(skill_dir: Path, version: str) -> Tuple[Optional[Path], Optional[str]]:
    """升级前完整备份。返回 (备份路径, 错误)。"""
    try:
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        dest = BACKUP_ROOT / f"{skill_dir.name}-{version}-{int(time.time())}"
        # symlinks=True：junction/symlink 安装场景下不跟随链接复制整棵源码树
        shutil.copytree(skill_dir, dest, symlinks=True, dirs_exist_ok=False)
        return dest, None
    except OSError as e:
        return None, f"{type(e).__name__}: {e}"


def rollback_skill(backup: Path, skill_dir: Path) -> Tuple[bool, Optional[str]]:
    """从备份回滚，并清理半成品。"""
    try:
        if skill_dir.exists() and not is_link_like(skill_dir):
            shutil.rmtree(skill_dir, ignore_errors=True)
        shutil.copytree(backup, skill_dir, symlinks=True, dirs_exist_ok=True)
        return True, None
    except OSError as e:
        return False, f"{type(e).__name__}: {e}"


def perform_upgrade(slug: str, skill_dir: Path, current: str, latest: str,
                    dry_run: bool, simulate_upgrade: str) -> dict:
    """执行升级 → verify → 必要时回滚。返回结构化结果。"""
    r = {
        "attempted": True, "succeeded": False, "cli": None,
        "backup": None, "rolled_back": False, "verify": None,
        "block_code": None, "messages": [],
    }

    def log(m: str) -> None:
        r["messages"].append(m)

    # --- 前置：权限探测。权限不足直接落 D 态，NEVER 走到写坏一半 ---
    ok, why = check_writable(skill_dir)
    if not ok and simulate_upgrade != "success":
        log(f"权限不足，跳过升级：{why}")
        return r
    if simulate_upgrade == "perm":
        log("权限不足，跳过升级：模拟注入（目标目录只读）")
        return r

    cli, cli_desc = locate_cli()
    if simulate_upgrade == "none":
        cli, cli_desc = None, "模拟注入：未找到 skillhub CLI"
    r["cli"] = cli_desc
    if cli is None:
        log(cli_desc)
        return r

    if dry_run:
        log(f"dry-run：跳过实际升级。将执行 {cli_desc} upgrade {slug}")
        return r

    # --- 步骤 1：备份（§3.4 回滚保障） ---
    backup, err = backup_skill(skill_dir, current)
    if backup is None:
        log(f"备份失败，放弃升级以免不可回滚：{err}")
        return r
    r["backup"] = str(backup)
    log(f"已备份至 {backup}")

    # --- 步骤 2：升级 ---
    if simulate_upgrade == "fail":
        code, out = 1, "模拟注入：upgrade 非零退出（error: network unreachable）"
    elif simulate_upgrade == "interrupt":
        code, out = 130, "模拟注入：升级中断（KeyboardInterrupt / 进程被杀）"
        # 模拟半成品：删掉一个文件，验证回滚能恢复
        victim = skill_dir / "SKILL.md"
        try:
            if victim.is_file():
                victim.unlink()
                log("模拟注入：升级中断已损坏 SKILL.md（用于验证回滚）")
        except OSError:
            pass
    elif simulate_upgrade == "success":
        # 保真模拟：真实 upgrade 会改写 frontmatter 版本，这里同样落盘，
        # 以便后续「重新校验自证」（§3.7）能读到升级后的真实版本
        code, out = 0, "模拟注入：upgrade 成功"
        try:
            md = skill_dir / "SKILL.md"
            txt = md.read_text(encoding="utf-8")
            md.write_text(
                VERSION_RE.sub(f"version: {latest}", txt, count=1),
                encoding="utf-8")
            log(f"模拟注入：已将 frontmatter 版本写为 {latest}")
        except OSError as e:
            code, out = 1, f"模拟注入写版本失败：{e}"
    else:
        if cli is None:
            log(cli_desc)
            return r
        code, out = run_cmd(cli + ["upgrade", slug])
    log(f"upgrade 退出码={code}；输出：{out[:500]}")

    if code != 0:
        # §3.6 升级未完成 → 回滚半成品后落 D 态降级，NEVER 阻断
        ok_rb, rb_err = rollback_skill(backup, skill_dir)
        r["rolled_back"] = ok_rb
        if ok_rb:
            log("升级失败，已回滚至备份版本")
        else:
            log(f"升级失败且回滚失败：{rb_err}")
            r["block_code"] = "P3"      # §五 P3 回滚失败 MUST 阻断
        return r

    # --- 步骤 3：verify（§3.3 三态，NEVER 把"无法判定"当失败） ---
    if simulate_upgrade == "success":
        v_code, v_out = 0, "模拟注入：verify 通过"
    else:
        v_code, v_out = run_cmd(cli + ["verify", slug])
    r["verify"] = {"code": v_code, "output": v_out[:500]}

    mismatch = v_code != 0 and re.search(
        r"signature.*mismatch|签名.*不匹配|checksum.*mismatch|integrity.*fail",
        v_out, re.I)
    if mismatch:
        ok_rb, rb_err = rollback_skill(backup, skill_dir)
        r["rolled_back"] = ok_rb
        r["block_code"] = "P2" if ok_rb else "P3"
        log(f"verify 签名明确不一致，已{'回滚' if ok_rb else '回滚失败: ' + str(rb_err)}")
        return r
    if v_code != 0:
        log(f"verify 无法判定（未登录/网络异常/平台未收录），标注「完整性未校验」后继续：{v_out[:200]}")

    r["succeeded"] = True
    log("升级成功")
    return r


# ---------------------------------------------------------------------------
# 主判定
# ---------------------------------------------------------------------------


def decide(args) -> dict:
    result: dict = {
        "slug": None, "skill_dir": None, "current": None, "latest": None,
        "compare": None, "state": None, "self_check": None,
        "throttled": False, "install_mode": None, "endpoint": None,
        "upgrade": None, "block_code": None,
        "warnings": [], "actions": [], "notes": [],
    }

    # ---- 定位 skill 目录 ----
    skill_dir = Path(args.skill_dir).resolve() if args.skill_dir \
        else Path(__file__).resolve().parent.parent
    result["skill_dir"] = str(skill_dir)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        result["state"] = STATE_BLOCK
        result["block_code"] = "ENV"
        result["warnings"].append(f"SKILL.md 不存在：{skill_md}")
        return result

    current, fm_slug = read_frontmatter(skill_md)
    slug = args.slug or fm_slug or skill_dir.name or DEFAULT_SLUG
    result["slug"] = slug
    result["current"] = current

    # 缓存目录：默认 ~/.cache/<slug>，可用 --cache-dir 覆盖（测试隔离，避免污染真实缓存）
    global CACHE_DIR, STATE_FILE, BACKUP_ROOT
    CACHE_DIR = Path(args.cache_dir).expanduser() if args.cache_dir \
        else Path.home() / ".cache" / slug
    STATE_FILE = CACHE_DIR / "update-state.json"
    BACKUP_ROOT = CACHE_DIR / "backup"
    if not current:
        result["warnings"].append("SKILL.md frontmatter 未读到 version，无法比较版本")

    registry = load_registry_entry(slug)
    mode = detect_install_mode(skill_dir, registry)
    result["install_mode"] = mode
    if mode["dangling_link"]:
        result["warnings"].append(
            f"user-level 链接悬空（指向不存在的目标）：{mode['user_level_path']}"
            " —— 斜杠激活将失效，需重指当前源码树")

    # ---- 节流（对齐 coding STALE_MIN=1440） ----
    state = load_state()
    if not args.force and is_fresh(state, slug, args.ttl_min):
        rec = state["skills"][slug]
        result["throttled"] = True
        result["state"] = rec.get("state", STATE_PASS)
        result["latest"] = rec.get("latest")
        result["compare"] = rec.get("compare")
        result["self_check"] = SELF_CHECK_LABEL.get(result["state"], "已通过")
        result["notes"].append(
            f"距上次检查不足 {args.ttl_min} 分钟，复用缓存结果（--force 可强制重查）")
        return result

    # ---- 解析端点 ----
    api_host, cfg_err = resolve_api_host()
    result["endpoint"] = {"api_host": api_host, "error": cfg_err}
    if api_host is None:
        result["state"] = STATE_CHANNEL
        result["warnings"].append(f"读不到 API 主机：{cfg_err}")
        result["actions"].append("核查 ~/.skillhub/metadata.json 是否存在且含 skills_search_url")
        return result

    # ---- 请求平台 ----
    fetched = fetch_latest(api_host, slug, args.simulate_net, args.simulate_fetch_ok)
    result["endpoint"]["url"] = fetched["url"]
    result["endpoint"]["http_status"] = fetched["http_status"]
    result["endpoint"]["content_type"] = fetched["content_type"]
    result["endpoint"]["detail"] = fetched["detail"]

    if fetched["kind"] == "offline":
        result["state"] = STATE_OFFLINE
        result["warnings"].append(f"网络不可达（已重试 {HTTP_RETRY} 次）：{fetched['detail']}")
        result["actions"].append("恢复网络后重跑；离线期间以当前版本继续执行")
        return result

    if fetched["kind"] == "invalid":
        # §五 P4 收窄：仅当此前曾拿到过有效响应（通道被证实正常）才阻断
        prior_ok = bool(((state.get("skills") or {}).get(slug) or {}).get("last_valid_at"))
        is_5xx = (fetched["http_status"] or 0) >= 500
        if prior_ok and is_5xx:
            result["state"] = STATE_BLOCK
            result["block_code"] = "P4"
            result["warnings"].append(
                f"通道此前正常但现在返回 {fetched['http_status']}，重试后仍失败：{fetched['detail']}")
            result["actions"].append("检查 skillhub 连通性后重试")
            return result
        result["state"] = STATE_CHANNEL
        result["warnings"].append(f"响应无效：{fetched['detail']}")
        result["actions"].append(f"维护者核查端点配置：{fetched['url']}")
        return result

    latest = args.simulate_latest or fetched["latest"]
    result["latest"] = latest
    if args.simulate_latest:
        result["notes"].append(f"测试注入 latest={args.simulate_latest}（真实平台值 {fetched['latest']}）")

    cmp = version_compare(current, latest)
    result["compare"] = cmp
    if cmp is None:
        result["state"] = STATE_CHANNEL
        result["warnings"].append(
            f"版本号格式非法，无法比较：current={current!r} latest={latest!r}")
        return result

    # ---- A 态：已是最新或本地领先 ----
    if cmp >= 0:
        result["state"] = STATE_PASS
        result["notes"].append(
            "本地版本领先平台（未发布的新版），属放行区间" if cmp > 0 else "已是最新版本")
        _persist(state, slug, result, valid=True)
        return result

    # ---- current < latest：陈旧 ----
    if mode["skip_auto_upgrade"] and not args.allow_junction_upgrade:
        # junction 单源例外：CLI 升级会覆盖链接破坏单源结构
        result["state"] = STATE_STALE
        result["upgrade"] = {"attempted": False,
                             "reason": "junction/source:local 单源安装，跳过自动升级"}
        result["warnings"].append(
            f"版本陈旧（{current} < {latest}）；该 skill 以链接指向源码树，"
            "自动升级会破坏单源结构，已跳过")
        result["actions"].append("由维护者在源码树手动同步后重新发布")
        _persist(state, slug, result, valid=True)
        return result

    up = perform_upgrade(slug, skill_dir, current or "0", latest,
                         args.dry_run, args.simulate_upgrade)
    result["upgrade"] = up

    if up.get("block_code"):
        result["state"] = STATE_BLOCK
        result["block_code"] = up["block_code"]
        result["warnings"].append("；".join(up["messages"]))
        result["actions"].append(
            f"手动恢复：{_manual_cmd(slug)}；备份位于 {up.get('backup')}")
        _persist(state, slug, result, valid=True)
        return result

    if up.get("succeeded"):
        new_cur, _ = read_frontmatter(skill_md)
        result["current"] = new_cur or current
        recmp = version_compare(result["current"], latest)
        result["compare"] = recmp
        if recmp is not None and recmp >= 0:
            result["state"] = STATE_PASS
            result["notes"].append(f"已自动升级 {current} → {result['current']} 并复核通过")
        else:
            result["state"] = STATE_STALE
            result["warnings"].append(
                f"升级命令成功但版本仍为 {result['current']}，未达 {latest}")
            result["actions"].append(_manual_cmd(slug))
        _persist(state, slug, result, valid=True)
        return result

    # ---- D 态：真实尝试过但未完成 ----
    result["state"] = STATE_STALE
    result["warnings"].append(
        f"版本陈旧（{current} < {latest}），自动升级未完成：" + "；".join(up["messages"]))
    result["actions"].append(_manual_cmd(slug))
    _persist(state, slug, result, valid=True)
    return result


def _manual_cmd(slug: str) -> str:
    return (f"skillhub upgrade {slug} && skillhub verify {slug}"
            f"   # CLI 不在 PATH 时：python ~/.skillhub/skills_store_cli.py upgrade {slug}")


def _persist(state: dict, slug: str, result: dict, valid: bool) -> None:
    state.setdefault("skills", {})
    rec = state["skills"].setdefault(slug, {})
    rec.update({
        "checked_at": time.time(),
        "state": result["state"],
        "current": result["current"],
        "latest": result["latest"],
        "compare": result["compare"],
    })
    if valid:
        rec["last_valid_at"] = time.time()
    save_state(state)


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------


def render_human(r: dict) -> str:
    tag = {STATE_PASS: "A 校验通过", STATE_OFFLINE: "B 离线降级",
           STATE_CHANNEL: "C 通道降级", STATE_STALE: "D 升级降级",
           STATE_BLOCK: "阻断"}.get(r["state"], r["state"])
    lines = [
        f"[{r['slug']} 版本门] {tag}"
        + (f"（{r['block_code']}）" if r.get("block_code") else ""),
        f"  slug={r['slug']}  当前={r['current']}  最新={r['latest'] or '未知'}"
        + (f"  比较={r['compare']}" if r["compare"] is not None else ""),
    ]
    if r["throttled"]:
        lines.append("  节流命中：复用缓存结果")
    # 注意：dict.get(k, {}) 在「键存在但值为 None」时仍返回 None，
    # 必须用 (x or {}) 兜底——早期返回路径（如 SKILL.md 缺失）会留下 None。
    if (r.get("install_mode") or {}).get("skip_auto_upgrade"):
        lines.append("  安装形态：链接/source:local 单源（自动升级已跳过）")
    for w in r["warnings"]:
        lines.append(f"  ⚠ {w}")
    for n in r["notes"]:
        lines.append(f"  · {n}")
    for a in r["actions"]:
        lines.append(f"  → {a}")
    lines.append(f"  自检口径：版本检查={SELF_CHECK_LABEL.get(r['state'], r['state'])}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="tri-* 家族版本检查与强制自动更新（version-gate 第零步的可执行实现，按 --slug 适配各 skill）")
    ap.add_argument("--slug", default=None, help="skill slug，默认读 frontmatter")
    ap.add_argument("--skill-dir", default=None, help="skill 根目录，默认脚本上级目录")
    ap.add_argument("--ttl-min", type=int, default=STALE_MIN,
                    help=f"节流阈值（分钟），默认 {STALE_MIN}，对齐 coding 的 STALE_MIN")
    ap.add_argument("--force", action="store_true", help="绕过节流强制重查")
    ap.add_argument("--dry-run", action="store_true", help="只判定不真正执行升级")
    ap.add_argument("--cache-dir", default=None,
                    help="缓存/备份目录覆盖（默认 ~/.cache/<slug>），仅用于测试隔离")
    ap.add_argument("--allow-junction-upgrade", action="store_true",
                    help="允许对链接安装执行升级（仅测试用，正常 NEVER 开启）")
    ap.add_argument("--json", action="store_true", help="输出 JSON 供 Agent 解析")
    # 测试注入
    ap.add_argument("--simulate-latest", default=None,
                    help="[测试] 注入平台最新版本号")
    ap.add_argument("--simulate-net", default="ok",
                    choices=["ok", "offline", "http500", "http404", "html", "badjson"],
                    help="[测试] 注入网络/响应故障")
    ap.add_argument("--simulate-fetch-ok", default=None,
                    help="[测试] 注入一次有效响应并指定其 latest 版本（跳过真实网络）")
    ap.add_argument("--simulate-upgrade", default="real",
                    choices=["real", "success", "fail", "interrupt", "perm", "none"],
                    help="[测试] 注入升级结果")
    args = ap.parse_args(argv)

    r = decide(args)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(render_human(r))
    return EXIT_CODE.get(r["state"], 64)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("[tri-skills 版本门] 已中断；以当前版本继续执行", file=sys.stderr)
        sys.exit(EXIT_CODE[STATE_OFFLINE])
    except Exception as e:                          # noqa: BLE001
        # 兜底：版本门 NEVER 因自身异常导致 skill 完全无法启动
        print(f"[tri-skills 版本门] 脚本自身异常，降级放行：{type(e).__name__}: {e}",
              file=sys.stderr)
        sys.exit(EXIT_CODE[STATE_CHANNEL])
