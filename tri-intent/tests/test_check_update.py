#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tri-intent 版本门 check_update.py 测试套件 —— 冒烟 / 单元 / 功能 三档。

运行（从 tri-intent 目录）：
    python tests/test_check_update.py -v
    PYTHONDONTWRITEBYTECODE=1 python tests/test_check_update.py

设计要点：
  * 全自包含、零网络依赖、零真实缓存污染（--cache-dir 指向临时目录）。
  * 功能测试对 decide() 做端点 monkeypatch，使 B/C/U/D 各态确定性可复现，
    不依赖机器上是否存在 ~/.skillhub/metadata.json。
  * 路径全部相对（基于 __file__ 推导），无任何硬编码绝对路径，可直接随 skill 发布。
"""

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # tri-intent 源码根
SCRIPT = ROOT / "scripts" / "check_update.py"

spec = importlib.util.spec_from_file_location("check_update", str(SCRIPT))
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)

FAKE_HOST = "https://api.example.test"   # 功能测试用的确定性端点替身
SANDBOX_BASE_VERSION = "1.0.0"


def make_sandbox(version: str) -> Path:
    """复制真实 tri-intent 源码到临时沙箱，并把 frontmatter 版本改成指定值。"""
    d = Path(tempfile.mkdtemp(prefix="ti-test-"))
    shutil.copytree(ROOT, d, symlinks=True, dirs_exist_ok=True)
    md = d / "SKILL.md"
    txt = md.read_text(encoding="utf-8")
    txt = cu.VERSION_RE.sub(f"version: {version}", txt, count=1)
    md.write_text(txt, encoding="utf-8")
    return d


# ===========================================================================
# 冒烟测试：脚本能加载、能跑、语法正确
# ===========================================================================
class SmokeTest(unittest.TestCase):
    def test_module_loaded_with_core_api(self):
        for name in ("decide", "version_compare", "fetch_latest",
                     "detect_install_mode", "perform_upgrade", "main"):
            self.assertTrue(hasattr(cu, name), f"缺失核心函数 {name}")

    def test_cli_help_exits_zero(self):
        with self.assertRaises(SystemExit) as ctx:
            cu.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_cli_version_section_present(self):
        # 直接调用 main（返回 int 退出码，而非走 __main__ 的 sys.exit）
        cache = Path(tempfile.mkdtemp(prefix="ti-smoke-"))
        try:
            code = cu.main([
                "--slug", "tri-intent",
                "--skill-dir", str(make_sandbox("1.0.0")),
                "--cache-dir", str(cache),
                "--force", "--simulate-fetch-ok", "0.9.0",
            ])
            self.assertIn(code, (0, 10, 11, 12))
        finally:
            shutil.rmtree(cache, ignore_errors=True)


# ===========================================================================
# 单元测试：纯函数
# ===========================================================================
class UnitVersionCompare(unittest.TestCase):
    def test_segment_not_string_order(self):
        # 经典缺陷：'1.10.0' < '1.9.0' 字典序为真，但按段比较应为 1.10.0 更新
        self.assertEqual(cu.version_compare("1.10.0", "1.9.0"), 1)
        self.assertEqual(cu.version_compare("1.9.0", "1.10.0"), -1)

    def test_equal(self):
        self.assertEqual(cu.version_compare("1.0.0", "1.0.0"), 0)

    def test_missing_segment_pads_zero(self):
        self.assertEqual(cu.version_compare("1.2", "1.2.0"), 0)
        self.assertEqual(cu.version_compare("1.2.0", "1.2"), 0)

    def test_major_bump(self):
        self.assertEqual(cu.version_compare("2.0.0", "1.9.9"), 1)

    def test_invalid_inputs_return_none(self):
        self.assertIsNone(cu.version_compare("", "1.0.0"))
        self.assertIsNone(cu.version_compare(None, "1.0.0"))
        self.assertIsNone(cu.version_compare("abc", "1.0.0"))
        self.assertIsNone(cu.version_compare("1.0.0", "v2"))


class UnitFetchLatest(unittest.TestCase):
    def test_offline(self):
        r = cu.fetch_latest(FAKE_HOST, "x", simulate_net="offline")
        self.assertEqual(r["kind"], "offline")

    def test_html_spa_fallback(self):
        r = cu.fetch_latest(FAKE_HOST, "x", simulate_net="html")
        self.assertEqual(r["kind"], "invalid")
        self.assertEqual(r["http_status"], 200)
        self.assertIn("html", (r["content_type"] or "").lower())

    def test_404(self):
        r = cu.fetch_latest(FAKE_HOST, "x", simulate_net="http404")
        self.assertEqual(r["kind"], "invalid")

    def test_badjson_missing_field(self):
        r = cu.fetch_latest(FAKE_HOST, "x", simulate_net="badjson")
        self.assertEqual(r["kind"], "invalid")

    def test_simulate_fetch_ok(self):
        r = cu.fetch_latest(FAKE_HOST, "x", simulate_fetch_ok="9.9.9")
        self.assertEqual(r["kind"], "ok")
        self.assertEqual(r["latest"], "9.9.9")


class UnitInstallMode(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ti-mode-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_real_dir_no_registry(self):
        m = cu.detect_install_mode(self.tmp, None)
        self.assertFalse(m["skip_auto_upgrade"])
        self.assertFalse(m["source_local"])

    def test_source_local_registry_skips_upgrade(self):
        m = cu.detect_install_mode(self.tmp, {"source": "local"})
        self.assertTrue(m["source_local"])
        self.assertTrue(m["skip_auto_upgrade"])

    def test_symlink_detected(self):
        link = self.tmp / "link"
        target = self.tmp / "tgt"
        target.mkdir()
        try:
            link.symlink_to(target, target_is_directory=True)
        except (OSError, NotImplementedError, AttributeError):
            self.skipTest("当前平台不支持创建 symlink")
        m = cu.detect_install_mode(link, None)
        self.assertTrue(m["is_link"])
        self.assertTrue(m["skip_auto_upgrade"])


class UnitMisc(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ti-misc-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_read_frontmatter(self):
        md = self.tmp / "SKILL.md"
        md.write_text("---\nname: x\nslug: tri-x\nversion: 1.2.3\n---\nbody\n",
                      encoding="utf-8")
        v, s = cu.read_frontmatter(md)
        self.assertEqual(v, "1.2.3")
        self.assertEqual(s, "tri-x")

    def test_resolve_api_host_missing_config(self):
        orig = cu.METADATA_JSON
        cu.METADATA_JSON = Path("/nonexistent/metadata.json")
        try:
            host, err = cu.resolve_api_host()
            self.assertIsNone(host)
            self.assertIsNotNone(err)
        finally:
            cu.METADATA_JSON = orig

    def test_no_hardcoded_absolute_paths(self):
        """发布到 skillhub 的硬性约束：脚本不得含本机绝对路径。"""
        raw = SCRIPT.read_text(encoding="utf-8")
        low = raw.lower()
        forbidden = ["d:/demo", "c:/users/bingo", "c:\\users\\bingo",
                     "/d/demo", "tribro-agent", "/c/users/bingo"]
        for f in forbidden:
            self.assertNotIn(f, low, f"脚本含禁止的绝对/环境路径片段：{f}")
        # 反向确认路径来自 home / __file__，而非硬编码
        self.assertIn("Path.home()", raw)
        self.assertIn("__file__", raw)


# ===========================================================================
# 功能测试：走完整 decide() 管线（端点已 monkeypatch 为确定性替身）
# ===========================================================================
class Functional(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache = Path(tempfile.mkdtemp(prefix="ti-cache-"))
        cls._orig_resolve = cu.resolve_api_host
        # 用确定性替身替换端点解析，使各态可复现、不依赖真实 metadata.json/网络
        cu.resolve_api_host = lambda: (FAKE_HOST, None)

    @classmethod
    def tearDownClass(cls):
        cu.resolve_api_host = cls._orig_resolve
        shutil.rmtree(cls.cache, ignore_errors=True)

    def run_decide(self, version, extra=None):
        sb = make_sandbox(version)
        base = dict(
            slug="tri-intent", skill_dir=str(sb), ttl_min=1440,
            force=True, dry_run=False, cache_dir=str(self.cache),
            allow_junction_upgrade=True, json=True,
            simulate_latest=None, simulate_net="ok",
            simulate_fetch_ok=None, simulate_upgrade="real",
        )
        base.update(extra or {})
        args = SimpleNamespace(**base)
        r = cu.decide(args)
        exit_code = cu.EXIT_CODE.get(r["state"], 64)
        return r, exit_code, sb

    def test_A_already_latest(self):
        r, code, _ = self.run_decide("1.0.0", {"simulate_fetch_ok": "1.0.0"})
        self.assertEqual(r["state"], "A")
        self.assertEqual(code, 0)

    def test_A_local_ahead(self):
        r, code, _ = self.run_decide("1.0.0", {"simulate_fetch_ok": "0.9.0"})
        self.assertEqual(r["state"], "A")
        self.assertEqual(code, 0)

    def test_B_offline(self):
        r, code, _ = self.run_decide("1.0.0", {"simulate_net": "offline"})
        self.assertEqual(r["state"], "B")
        self.assertEqual(code, 10)

    def test_C_channel_invalid_html(self):
        r, code, _ = self.run_decide("1.0.0", {"simulate_net": "html"})
        self.assertEqual(r["state"], "C")
        self.assertEqual(code, 11)

    def test_U_update_success_rewrites_and_preserves(self):
        r, code, sb = self.run_decide(
            "1.0.0", {"simulate_fetch_ok": "1.9.0", "simulate_upgrade": "success"})
        self.assertEqual(code, 0)
        v, _ = cu.read_frontmatter(sb / "SKILL.md")
        self.assertEqual(v, "1.9.0", "升级后 frontmatter 版本应被改写")
        self.assertTrue((sb / "scripts" / "check_update.py").is_file(),
                        "升级后文件结构应保全")

    def test_D_fail_rollback_preserves_version(self):
        r, code, sb = self.run_decide(
            "1.0.0", {"simulate_fetch_ok": "1.9.0", "simulate_upgrade": "fail"})
        self.assertEqual(r["state"], "D")
        self.assertEqual(code, 12)
        v, _ = cu.read_frontmatter(sb / "SKILL.md")
        self.assertEqual(v, "1.0.0", "升级失败应回滚保留原版本")

    def test_D_perm_skips_upgrade(self):
        r, code, sb = self.run_decide(
            "1.0.0", {"simulate_fetch_ok": "1.9.0", "simulate_upgrade": "perm"})
        self.assertEqual(r["state"], "D")
        self.assertEqual(code, 12)

    def test_D_none_cli_missing(self):
        r, code, sb = self.run_decide(
            "1.0.0", {"simulate_fetch_ok": "1.9.0", "simulate_upgrade": "none"})
        self.assertEqual(r["state"], "D")
        self.assertEqual(code, 12)

    def test_junction_single_source_skips_auto_upgrade(self):
        # 链接/source:local 安装应跳过自动升级，落 D 态而非真升级
        r, code, sb = self.run_decide(
            "1.0.0",
            {"simulate_fetch_ok": "1.9.0", "simulate_upgrade": "real",
             "allow_junction_upgrade": False})
        # 即使未开 allow_junction_upgrade，沙箱本身是真实目录，
        # 这里额外验证 registry source:local 路径（通过 args 无法直达，改测 detect）
        mode = cu.detect_install_mode(sb, {"source": "local"})
        self.assertTrue(mode["skip_auto_upgrade"])


# ===========================================================================
# 回归测试：tri-intent 原有功能与修复集成点不被破坏
# ===========================================================================
class RegressionTest(unittest.TestCase):
    def test_skill_md_references_spec_and_script(self):
        md = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("version-check-spec.md", md,
                      "SKILL.md 应引用细则真源 version-check-spec.md（非已废弃的 version-gate.md）")
        self.assertNotIn("version-gate.md", md,
                         "SKILL.md 不得再引用已废弃的 version-gate.md")
        self.assertIn("check_update.py", md, "SKILL.md 应新增对可执行脚本 check_update.py 的引用")

    def test_check_downstream_help(self):
        code = _run([str(ROOT / "scripts" / "check_downstream.py"), "--help"])
        self.assertEqual(code, 0)

    def test_intent_gate_help(self):
        code = _run([str(ROOT / "hooks" / "intent-gate.py"), "--help"])
        self.assertEqual(code, 0)


def _run(argv):
    import subprocess
    try:
        p = subprocess.run([sys.executable] + argv, capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=60)
        return p.returncode
    except Exception:
        return 1


if __name__ == "__main__":
    unittest.main(verbosity=2)
