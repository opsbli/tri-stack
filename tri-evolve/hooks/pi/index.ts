// evolve-hook · 形态 B 适配器（pi / in-process TypeScript）
// 契约见 ../spec.md；家族规则见 tri-forge/references/family-spec.md §1.5
//
// 落点：pi.on("agent_settled") —— 官方定义为「final、notification-only，用于需要知道
//       Pi 不会再自动继续」时，已真机验证一轮交互恰好触发 1 次。
//
// 三条 pi 硬约束（官方文档）在本文件的落地：
//   ① 工厂里 NEVER 启动常驻资源 —— 本工厂只做事件注册，不建目录、不起定时器
//   ② ctx.reload() 会替换运行时、旧状态不可复用 —— 故去重状态**不放模块级变量**，
//      改为「session 内持久化载体（pi.appendEntry）+ session_start 时重建」
//   ③ 状态用 appendEntry 持久化，可跨 restart / compaction 存活
//
// 探测依据（pi 0.85.1 实测）：
//   agent_settled 的 payload 仅 { type } —— 无会话/消息标识，故标识一律取自 ctx
//   ctx.sessionManager.sessionId —— 会话标识；ctx.cwd —— .tribro/ 落点基准
//   助手消息带 responseId（message.id 为空）—— 用作 exchange_id
//   message_end 一轮触发 2 次：role=user 与 role=assistant 各一次 → 必须按 role 过滤

import { appendFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";

const PRODUCED_BY = "tri-evolve/hooks/pi";
const ENTRY_TYPE = "tri-evolve.signal";

function sha8(s: string): string {
  try { return createHash("sha1").update(String(s)).digest("hex").slice(0, 8); } catch { return "no-hash"; }
}

export default function (pi: any) {
  // ⚠️ 运行期状态：仅存活于本 factory 实例。reload 后会重建，
  //    因此它们只是「快查缓存」，唯一真相在 session 持久化条目里（见 rebuildSeen）。
  let seen = new Set<string>();
  let sessionId = "unknown";
  let lastAssistant: { responseId?: string; text?: string } | null = null;

  function rebuildSeen(ctx: any) {
    seen = new Set<string>();
    try {
      const sm = ctx?.sessionManager ?? {};
      const pools: any[] = [];
      if (Array.isArray(sm.fileEntries)) pools.push(...sm.fileEntries);
      if (sm.byId && typeof sm.byId === "object") pools.push(...Object.values(sm.byId));
      for (const e of pools) {
        const t = e?.type ?? e?.kind ?? e?.name;
        const d = e?.data ?? e;
        if (t === ENTRY_TYPE && d?.exchange_id) seen.add(String(d.session_id ?? sessionId) + "::" + String(d.exchange_id));
      }
    } catch { /* 降级：重建失败则退化为「本实例内去重」，不抛错 */ }
  }

  pi.on("session_start", async (_e: any, ctx: any) => {
    try {
      sessionId = String(ctx?.sessionManager?.sessionId ?? "unknown");
      rebuildSeen(ctx);
    } catch { /* 静默降级 */ }
  });

  // role 过滤是必需的：一轮里 message_end 会出现 user 与 assistant 各一次
  pi.on("message_end", async (e: any) => {
    try {
      const m = e?.message;
      if (m?.role === "assistant") {
        const text = typeof m.content === "string"
          ? m.content
          : Array.isArray(m.content)
            ? m.content.map((c: any) => c?.text ?? "").join("")
            : "";
        lastAssistant = { responseId: m.responseId, text };
      }
    } catch { /* 静默降级 */ }
  });

  pi.on("agent_settled", async (_e: any, ctx: any) => {
    try {
      const cwd = String(ctx?.cwd ?? process.cwd());
      const exchangeId = lastAssistant?.responseId
        || (lastAssistant?.text ? sha8(lastAssistant.text) : "")
        || ("t" + Date.now());
      const key = sessionId + "::" + exchangeId;

      if (seen.has(key)) return;          // 幂等：同一轮只采集一次
      seen.add(key);

      const answer = lastAssistant?.text ?? "";
      const rec = {
        ts: new Date().toISOString(),
        session_id: sessionId,
        exchange_id: exchangeId,
        answer_hash: sha8(answer),
        source_skill: "",                  // 探测阶段留空；后续可从快照补齐
        produced_by: PRODUCED_BY,
      };

      // ① 事件流落盘（追加式，永不覆盖）
      const dir = join(cwd, ".tribro", "evolve");
      mkdirSync(dir, { recursive: true });
      appendFileSync(join(dir, "signals.jsonl"), JSON.stringify(rec) + "\n", "utf8");

      // ② 去重键持久化进 session（跨 reload / restart 存活）
      try { pi.appendEntry(ENTRY_TYPE, { session_id: sessionId, exchange_id: exchangeId }); } catch { /* 不致命 */ }

      // ③ 有 UI 才提示（headless 模式下 ctx.hasUI=false）
      try { if (ctx?.hasUI) ctx.ui?.notify?.("evolve-hook: 已采集 1 条信号", "info"); } catch { /* 不致命 */ }
    } catch { /* 契约 §五：写盘失败静默降级，NEVER 中断代理循环 */ }
    finally {
      lastAssistant = null;                // 每轮清零，防止跨轮串用
    }
  });

  pi.on("session_shutdown", async () => {
    // 幂等清理：本适配器无常驻资源（硬约束 ①），仅清内存引用
    seen = new Set<string>();
    lastAssistant = null;
  });
}
