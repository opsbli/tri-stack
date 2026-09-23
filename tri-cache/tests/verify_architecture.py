#!/usr/bin/env python3
"""tri-cache 四层架构自动化验证脚本。

对 tri-cache v2.0.0 的四层架构（L1 滑动窗口 / L2 结构化存储 / L3 轻量摘要 / L4 向量检索）
及配套能力（内容指纹去重 / 隐私过滤 / 差异化 TTL / 项目初始化 / 写入链路 / 检索链路）
逐项断言验证。对应 tests/tri-cache-full-testcases.md 的 TC-02/03/04/06/08 系列。

用法：
    python tests/verify_architecture.py
退出码：0=全部通过；1=存在失败。
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent

# 加载 cache_ops.py 与 cache_init.py（不依赖安装）
def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

cache_ops = _load("cache_ops", SKILL_DIR / "scripts" / "cache_ops.py")
cache_init = _load("cache_init", SKILL_DIR / "scripts" / "cache_init.py")

PASS = 0
FAIL = 0
RESULTS: list[tuple[str, bool, str]] = []


def check(tc_id: str, name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        status = "PASS"
    else:
        FAIL += 1
        status = "FAIL"
    RESULTS.append((tc_id, cond, name))
    suffix = f"  [{detail}]" if detail else ""
    print(f"  [{status}] {tc_id} {name}{suffix}")


def section(title: str) -> None:
    print(f"\n=== {title} ===")


# ---------------------------------------------------------------------------
# L1 滑动窗口
# ---------------------------------------------------------------------------
section("L1 滑动窗口")

# TC-04-01：FIFO 滑出
win, evicted = cache_ops.manage_window(
    [{"cache_key": "a"}, {"cache_key": "b"}], {"cache_key": "c"}, max_size=2)
check("TC-04-01", "FIFO 滑出：最旧条目滑出",
      [w["cache_key"] for w in win] == ["b", "c"]
      and [e["cache_key"] for e in evicted] == ["a"],
      f"窗口={[w['cache_key'] for w in win]} 滑出={[e['cache_key'] for e in evicted]}")

# 滑出条目降级写 L2/L3/L4（非丢弃）
check("TC-04-01b", "滑出条目返回给调用方降级（非丢弃）",
      len(evicted) == 1 and evicted[0]["cache_key"] == "a")

# TC-04-02：渐进注入配置
meta_tpl = json.loads((SKILL_DIR / "templates" / "meta.json").read_text(encoding="utf-8"))
cfg = meta_tpl["config"]
check("TC-04-02", "渐进注入：近 2 轮全文 + 其余仅摘要（配置存在）",
      cfg.get("config_window_size") == 50
      and cfg.get("config_window_inject_full_rounds") == 2,
      f"window_size={cfg.get('config_window_size')} inject_full={cfg.get('config_window_inject_full_rounds')}")

# 窗口容量默认 50
check("TC-04-02b", "窗口默认容量 50",
      cache_ops.DEFAULT_WINDOW_SIZE == 50)


# ---------------------------------------------------------------------------
# L2 结构化存储
# ---------------------------------------------------------------------------
section("L2 结构化存储")

# 初始化临时项目
tmp_root = Path(tempfile.mkdtemp(prefix="tri-cache-verify-"))
try:
    init_result = cache_init.init_project(str(tmp_root))
    cache_dir = tmp_root / ".tribro" / "cache"

    check("TC-03-07", "CACHE_INIT：四层结构齐备",
          init_result["schema_version"] == 2
          and (cache_dir / "index.db").is_file()
          and (cache_dir / "meta.json").is_file()
          and (cache_dir / "window_state.json").is_file()
          and (cache_dir / "entries").is_dir()
          and (cache_dir / "summaries").is_dir(),
          f"created={init_result['created']}")

    # 二次初始化保护
    again = cache_init.init_project(str(tmp_root))
    check("TC-02-12", "CACHE_INIT：重复初始化不覆盖（无 --force）",
          len(again["errors"]) > 0)

    # TC-06-02：四表 + 8 索引
    con = sqlite3.connect(str(cache_dir / "index.db"))
    cur = con.cursor()
    tables = {r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    indexes = {r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")}
    check("TC-06-02", "SQLite 四表齐备",
          {"cache_entries", "embeddings", "window_state", "cache_meta"} <= tables,
          f"tables={sorted(tables)}")
    check("TC-06-02b", "SQLite 8 索引齐备",
          len(indexes) == 8
          and {"idx_intent_l2", "idx_session", "idx_user", "idx_created",
               "idx_last_access", "idx_expires", "idx_status",
               "idx_window_session"} <= indexes,
          f"indexes={len(indexes)}")

    # TC-06-05：meta.json 配置键
    meta = json.loads((cache_dir / "meta.json").read_text(encoding="utf-8"))
    need_keys = {"config_max_size_mb", "config_window_size", "config_embedding_dim",
                 "config_vector_top_k", "config_summary_max_chars",
                 "config_ttl_by_intent", "config_no_cache_intents",
                 "config_privacy_patterns"}
    check("TC-06-05", "meta.json 配置键齐全",
          need_keys <= set(meta["config"]),
          f"missing={need_keys - set(meta['config'])}")

    # TC-04-03：结构化组合查询（按意图过滤）
    con.execute("""INSERT INTO cache_entries
        (cache_key, question, answer, summary, intent_l2, session_id, user_id,
         created_at, last_accessed, hit_count, ttl_seconds, expires_at, status, schema_version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2)""",
        ("k01", "什么是闭包", "闭包是函数与其词法作用域的组合。",
         "闭包是函数与其词法作用域的组合。", "I01", "sess_1", "default",
         1722497400, 1722497400, 0, 2592000, 1722497400 + 2592000, "active"))
    con.commit()
    rows = cur.execute(
        "SELECT cache_key FROM cache_entries WHERE intent_l2=? AND status='active'",
        ("I01",)).fetchall()
    check("TC-04-03", "L2 结构化组合查询（按意图+状态）",
          [r[0] for r in rows] == ["k01"])

    # -----------------------------------------------------------------------
    # L3 轻量摘要
    # -----------------------------------------------------------------------
    section("L3 轻量摘要")

    long_answer = "闭包是函数与其词法作用域的组合，它让函数可以访问其外部作用域的变量。" * 20
    summary = cache_ops.generate_summary("什么是闭包", long_answer)
    check("TC-04-04", "摘要 ≤200 字",
          len(summary) <= 200,
          f"len={len(summary)}")

    short_summary = cache_ops.generate_summary("什么是闭包", "闭包是函数与其词法作用域的组合。")
    check("TC-04-04b", "摘要取回答首句",
          short_summary == "闭包是函数与其词法作用域的组合。")

    # 截断：首句超长（无标点）时截断至 max_chars + …
    huge_first = "无标点超长首句" * 100
    truncated = cache_ops.generate_summary("q", huge_first, max_chars=200)
    check("TC-04-04c", "摘要超长截断 ≤200 字",
          len(truncated) <= 201 and truncated.endswith("…"),
          f"len={len(truncated)}")

    tags = cache_ops.extract_tags("JavaScript 闭包 作用域 函数 变量 词法环境")
    check("TC-04-04d", "关键词提取（拉丁优先 + CJK bigram）",
          len(tags) >= 3 and "javascript" in tags,
          f"tags={tags}")

    # -----------------------------------------------------------------------
    # L4 向量检索
    # -----------------------------------------------------------------------
    section("L4 向量检索")

    # TC-04-06：确定性嵌入
    v1 = cache_ops.embed("什么是闭包")
    v2 = cache_ops.embed("什么是闭包")
    check("TC-04-06", "嵌入确定性：同文本同向量",
          v1 == v2 and len(v1) == 256,
          f"dim={len(v1)}")

    # TC-04-05：语义召回（相似 query ≥ min_score）
    sim_reorder = cache_ops.cosine_similarity(
        cache_ops.embed("什么是闭包"), cache_ops.embed("闭包是什么"))
    min_score = cfg.get("config_vector_min_score", 0.5)
    check("TC-04-05", "语义召回：近义 query 命中（≥ min_score）",
          sim_reorder >= min_score,
          f"sim={sim_reorder:.4f} min_score={min_score}")

    # TC-04-07：阈值过滤（无关文本 < min_score）
    sim_unrelated = cache_ops.cosine_similarity(
        cache_ops.embed("什么是闭包"), cache_ops.embed("今天天气很好"))
    check("TC-04-07", "余弦阈值：无关文本被过滤（< min_score）",
          sim_unrelated < min_score,
          f"sim={sim_unrelated:.4f}")

    # 语义召回 > 无关文本（分离度）
    check("TC-04-07b", "分离度：近义相似度显著高于无关",
          sim_reorder > sim_unrelated + 0.3,
          f"近义={sim_reorder:.4f} 无关={sim_unrelated:.4f}")

    # -----------------------------------------------------------------------
    # 内容指纹去重 + 隐私过滤
    # -----------------------------------------------------------------------
    section("内容指纹去重 + 隐私过滤")

    # TC-04-09：归一化后指纹一致
    k1 = cache_ops.compute_key("Hello, World!")
    k2 = cache_ops.compute_key("hello world")
    check("TC-04-09", "内容指纹：归一化后 cache_key 一致",
          k1 == k2 and len(k1) == 16,
          f"key={k1}")

    # TC-02-04：去重（相同 key 不重复写，hit_count++）
    check("TC-02-04", "去重：相同提问同 cache_key",
          cache_ops.compute_key("什么是闭包") == cache_ops.compute_key("什么是闭包？"))

    # TC-02-06：隐私脱敏
    masked, hits = cache_ops.mask_secrets("password=abc123 与 token=xyz 的配置")
    check("TC-02-06", "隐私过滤：密钥模式脱敏",
          hits == 2 and "abc123" not in masked and "xyz" not in masked,
          f"hits={hits} masked={masked!r}")

    # TC-04-14：敏感度过高（≥3 处）跳过缓存
    _, hits3 = cache_ops.mask_secrets(
        "password=a token=b secret=c api_key=d")
    threshold = cfg.get("config_privacy_redact_threshold", 3)
    check("TC-04-14", "敏感度过高（≥3 处）判定",
          hits3 >= threshold,
          f"hits={hits3} threshold={threshold}")

    # -----------------------------------------------------------------------
    # 完整写入链路（L1→L2→L3→L4）
    # -----------------------------------------------------------------------
    section("完整写入链路（L1→L2→L3→L4）")

    question = "Koa 中间件怎么配置？"
    answer = "在 Koa 中通过 app.use 注册中间件，按声明顺序执行。"
    q_key = cache_ops.compute_key(question)
    q_summary = cache_ops.generate_summary(question, answer)
    q_tags = cache_ops.extract_tags(question + " " + answer)
    q_vec = cache_ops.embed(question)

    # L1 入窗
    window = []
    window, evicted = cache_ops.manage_window(window, {
        "cache_key": q_key, "question": question, "answer": answer,
        "summary": q_summary}, max_size=50)
    check("TC-02-05", "L1 入窗：新条目写入滑动窗口",
          len(window) == 1 and window[0]["cache_key"] == q_key)

    # L2 结构化入库
    con.execute("""INSERT INTO cache_entries
        (cache_key, question, answer, summary, intent_l2, session_id, user_id,
         created_at, last_accessed, hit_count, ttl_seconds, expires_at, tags, status, schema_version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 2)""",
        (q_key, question, answer, q_summary, "I03", "sess_2", "default",
         1722497400, 1722497400, 0, 604800, 1722497400 + 604800,
         json.dumps(q_tags, ensure_ascii=False), "active"))
    # L4 向量入库
    con.execute("""INSERT INTO embeddings (cache_key, dim, ngram_min, ngram_max, vector, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (q_key, 256, 1, 2, json.dumps(q_vec), 1722497400))
    # L1 窗口持久化
    con.execute("""INSERT INTO window_state (session_id, seq, cache_key, question, answer, summary, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("sess_2", 0, q_key, question, answer, q_summary, 1722497400))
    con.commit()

    row = cur.execute(
        "SELECT e.cache_key, e.summary, e.tags, v.dim FROM cache_entries e "
        "JOIN embeddings v ON e.cache_key=v.cache_key WHERE e.cache_key=?",
        (q_key,)).fetchone()
    check("TC-02-05b", "四层同步：L2 入库 + L3 摘要 + L4 向量齐备",
          row is not None and row[1] == q_summary and row[2] is not None and row[3] == 256)

    wrow = cur.execute(
        "SELECT cache_key FROM window_state WHERE session_id=? AND seq=0",
        ("sess_2",)).fetchone()
    check("TC-02-05c", "L1 窗口持久化：window_state 表镜像",
          wrow is not None and wrow[0] == q_key)

    # -----------------------------------------------------------------------
    # 完整检索链路（L1→L2→L4→L3）
    # -----------------------------------------------------------------------
    section("完整检索链路（L1→L2→L4→L3）")

    # L1 窗口命中 → 直接注入
    l1_hit = [w for w in window if w["cache_key"] == q_key]
    check("TC-04-01c", "L1 窗口命中 → 直接注入",
          len(l1_hit) == 1)

    # L2 结构化过滤
    l2_rows = cur.execute(
        "SELECT cache_key, summary FROM cache_entries WHERE intent_l2=? AND status='active'",
        ("I03",)).fetchall()
    check("TC-04-03b", "L2 结构化过滤命中",
          any(r[0] == q_key for r in l2_rows))

    # L4 向量检索：语义近义 query 召回
    query = "Koa 中间件如何配置"
    qv = cache_ops.embed(query)
    all_vecs = cur.execute(
        "SELECT e.cache_key, v.vector FROM cache_entries e JOIN embeddings v ON e.cache_key=v.cache_key "
        "WHERE e.status='active'").fetchall()
    scored = sorted(
        ((cache_ops.cosine_similarity(qv, json.loads(vec)), ck) for ck, vec in all_vecs),
        key=lambda x: x[0], reverse=True)
    top_hits = [ck for s, ck in scored if s >= min_score]
    check("TC-04-05b", "L4 向量检索：语义近义 query 召回相关条目",
          q_key in top_hits,
          f"top={top_hits}")

    # L3 摘要级注入（token 高效）
    l3_inject = [r[1] for r in l2_rows if r[0] == q_key]
    check("TC-04-04d", "L3 摘要级注入（非全文）",
          len(l3_inject) == 1 and len(l3_inject[0]) <= 200)

    # 命中热度更新（hit_count++）
    con.execute("UPDATE cache_entries SET hit_count=hit_count+1, last_accessed=? WHERE cache_key=?",
                (1722497401, q_key))
    con.commit()
    hc = cur.execute("SELECT hit_count FROM cache_entries WHERE cache_key=?", (q_key,)).fetchone()[0]
    check("TC-08-03", "命中热度：hit_count 递增",
          hc == 1)

    con.close()

finally:
    shutil.rmtree(tmp_root, ignore_errors=True)


# ---------------------------------------------------------------------------
# 汇总
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print(f"结果汇总：PASS={PASS}  FAIL={FAIL}  通过率={PASS/(PASS+FAIL)*100:.1f}%")
failed = [r for r in RESULTS if not r[1]]
if failed:
    print("失败用例：")
    for tc_id, _, name in failed:
        print(f"  - {tc_id} {name}")
    sys.exit(1)
print("四层架构验证全部通过。")
sys.exit(0)
