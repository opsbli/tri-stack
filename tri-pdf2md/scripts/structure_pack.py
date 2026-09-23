#!/usr/bin/env python3
"""门E · 结构化交付（tri-pdf2md）

确定性结构化包装：类 Obsidian MD（YAML frontmatter 强制元数据 + 标题树 ToC + 页码锚点）
+ Small-to-Big 父子分块 chunks.json + 人工调优审阅页 review.html + 锚点覆盖率统计。
PDF 被视为「有时效、有坐标的数据源」——版本与页码/坐标锚点由框架硬编码写入，NEVER 依赖模型自觉。

用法：
    python scripts/structure_pack.py --pdf <路径> --md <转换产物> [--out-dir <目录>]
           [--doc-name <名>] [--doc-version <版本>]
           [--backend <slug>] [--grade <L0|L1|L2>] [--confidence <A|B|C>] [--fidelity-rate <0-1>]
           [--parent-granularity section|page] [--child-max-chars 800] --json

输出：<同名>.obsidian.md + chunks.json + review.html（落 --out-dir，缺省 MD 同目录）。
退出码：0 成功；2 参数/文件错误；3 frontmatter 强制字段校验失败。
规范唯一真源：references/obsidian-output-spec.md 与 references/chunking-spec.md。
"""
from _io_safe import safe_print
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

PARENT_CAPACITY = 3000            # 父块容量上限（chunking-spec §五）
FINGERPRINT_CHARS = 40            # 页码锚点指纹长度（obsidian-output-spec §四）
SENTENCE_END = "。！？；.!?"      # 子块二次切分的句末标点

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def normalize(text: str) -> str:
    """归一化：去全部空白（中文 PDF 文本层常带散布空格）。"""
    return re.sub(r"\s+", "", text or "")


# ---------------------------------------------------------------------------
# PDF 侧：页文本 + 字符坐标（坐标 = 空间锚点，用户硬要求）
# ---------------------------------------------------------------------------

def load_pdf_pages(pdf_path: Path):
    """返回 (pages, reader_kind)。pages: [{page, text, norm, chars}]；pdfplumber 才有 chars。"""
    try:
        import pdfplumber
    except ImportError:
        pdfplumber = None
    if pdfplumber is not None:
        pages = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for i, pg in enumerate(pdf.pages):
                text = pg.extract_text() or ""
                pages.append({
                    "page": i + 1,
                    "text": text,
                    "norm": normalize(text),
                    "chars": [
                        {"c": ch.get("text", ""), "x0": ch.get("x0"), "y0": ch.get("top"),
                         "x1": ch.get("x1"), "y1": ch.get("bottom")}
                        for ch in pg.chars
                    ],
                })
        return pages, "pdfplumber"
    try:
        import pypdf
    except ImportError:
        return None, None
    reader = pypdf.PdfReader(str(pdf_path))
    pages = []
    for i, pg in enumerate(reader.pages):
        try:
            text = pg.extract_text() or ""
        except Exception:
            text = ""
        pages.append({"page": i + 1, "text": text, "norm": normalize(text), "chars": []})
    return pages, "pypdf"


def fingerprint(text: str, n: int = FINGERPRINT_CHARS) -> str:
    return normalize(text)[:n]


def match_page(fp: str, pages):
    """指纹在页文本序列中 find。返回 (page_number, source)；source: exact|inherited|unavailable。"""
    if not fp:
        return None, "unavailable"
    for pg in pages:
        if fp in pg["norm"]:
            return pg["page"], "exact"
    return None, "inherited" if any(pg["norm"] for pg in pages) else "unavailable"


def char_bbox(fp: str, page):
    """在页 chars 拼接序列中定位指纹，取 bbox 并集。未命中返回 None。"""
    if not fp or not page["chars"]:
        return None
    seq = ""
    idx_map = []  # seq 中每个字符 → chars 下标
    for ci, ch in enumerate(page["chars"]):
        for c in normalize(ch["c"]):
            seq += c
            idx_map.append(ci)
    pos = seq.find(fp)
    if pos < 0:
        return None
    hit = idx_map[pos:pos + len(fp)]
    xs0 = [page["chars"][i]["x0"] for i in hit if page["chars"][i]["x0"] is not None]
    ys0 = [page["chars"][i]["y0"] for i in hit if page["chars"][i]["y0"] is not None]
    xs1 = [page["chars"][i]["x1"] for i in hit if page["chars"][i]["x1"] is not None]
    ys1 = [page["chars"][i]["y1"] for i in hit if page["chars"][i]["y1"] is not None]
    if not (xs0 and ys0 and xs1 and ys1):
        return None
    return [round(min(xs0), 1), round(min(ys0), 1), round(max(xs1), 1), round(max(ys1), 1)]


def page_text_bbox(page):
    """页面正文区近似 bbox（approx 级）。"""
    if not page["chars"]:
        return None
    xs0 = [c["x0"] for c in page["chars"] if c["x0"] is not None]
    ys0 = [c["y0"] for c in page["chars"] if c["y0"] is not None]
    xs1 = [c["x1"] for c in page["chars"] if c["x1"] is not None]
    ys1 = [c["y1"] for c in page["chars"] if c["y1"] is not None]
    if not (xs0 and ys0 and xs1 and ys1):
        return None
    return [round(min(xs0), 1), round(min(ys0), 1), round(max(xs1), 1), round(max(ys1), 1)]


# ---------------------------------------------------------------------------
# MD 侧：标题树分节 + 段落子块
# ---------------------------------------------------------------------------

def parse_sections(md_text: str):
    """按标题切节。返回 [{level, title, heading_path, lines}]；无标题时整文一节（level 0）。"""
    lines = md_text.splitlines()
    sections = []
    stack = []  # [(level, title)]
    cur = None
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            if cur is not None:
                sections.append(cur)
            level = len(m.group(1))
            title = m.group(2)
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            cur = {"level": level, "title": title,
                   "heading_path": [t for _, t in stack], "lines": [line]}
        else:
            if cur is None:
                cur = {"level": 0, "title": "", "heading_path": [], "lines": []}
            cur["lines"].append(line)
    if cur is not None:
        sections.append(cur)
    return sections


def split_children(section_lines, max_chars: int):
    """段落级子块切分：空行分段；表格/代码块整体；超长按句末标点二次切；标题行不产子块。"""
    blocks = []
    buf = []
    in_code = False
    for line in section_lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            buf.append(line)
            continue
        if not in_code and HEADING_RE.match(line):
            continue
        if not in_code and stripped == "":
            if buf:
                blocks.append("\n".join(buf).strip())
                buf = []
            continue
        buf.append(line)
    if buf:
        blocks.append("\n".join(buf).strip())

    children = []
    for blk in blocks:
        if len(blk) <= max_chars:
            children.append(blk)
            continue
        # 超长块按句末标点切
        parts, start = [], 0
        for i, ch in enumerate(blk):
            if ch in SENTENCE_END and i - start + 1 >= max_chars * 0.6:
                parts.append(blk[start:i + 1])
                start = i + 1
        if start < len(blk):
            parts.append(blk[start:])
        children.extend(p.strip() for p in parts if p.strip())
    return [c for c in children if c]


# ---------------------------------------------------------------------------
# 产物渲染
# ---------------------------------------------------------------------------

def yaml_escape(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_obsidian(doc_meta, sections, anchors):
    fm = [
        "---",
        f"title: {yaml_escape(doc_meta['title'])}",
        f"source_file: {yaml_escape(doc_meta['source_file'])}",
        f"source_path: {yaml_escape(doc_meta['source_path'])}",
        f"doc_version: {yaml_escape(doc_meta['doc_version'])}",
        f"pages: {doc_meta['pages']}",
        f"page_range: \"1-{doc_meta['pages']}\"",
        f"converted_at: {yaml_escape(doc_meta['converted_at'])}",
        f"backend: {yaml_escape(doc_meta['backend'])}",
        f"grade: {yaml_escape(doc_meta['grade'])}",
        f"confidence: {yaml_escape(doc_meta['confidence'])}",
        f"fidelity_rate: {doc_meta['fidelity_rate']}",
        "toc:",
    ]
    for sec in sections:
        if sec["level"] >= 1:
            fm.append(f"  - {yaml_escape(sec['title'])}")
    fm.append(f"tags: [pdf2md{', ' + doc_meta['extra_tags'] if doc_meta['extra_tags'] else ''}]")
    fm.append("---")

    toc = ["## 目录", ""]
    for sec in sections:
        if sec["level"] >= 1:
            indent = "  " * (sec["level"] - 1)
            toc.append(f"{indent}- {sec['title']}")
    if len(toc) > 2:
        toc.append("")

    body = []
    for si, sec in enumerate(sections):
        if sec["level"] >= 1:
            body.append("")
            body.append("#" * sec["level"] + " " + sec["title"])
        for line in sec["lines"]:
            if HEADING_RE.match(line):
                continue
            body.append(line)
        anchor = anchors[si]
        if anchor["page"] is not None:
            if anchor["page_end"] and anchor["page_end"] != anchor["page"]:
                body.append(f"%% p.{anchor['page']}-{anchor['page_end']} %%")
            else:
                body.append(f"%% p.{anchor['page']} %%")
        else:
            body.append("%% p.? %%")
    return "\n".join(fm) + "\n\n" + "\n".join(toc) + "\n" + "\n".join(body) + "\n"


REVIEW_HTML_TMPL = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>tri-pdf2md 分块人工调优 · {title}</title>
<style>
 body{{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;margin:0;background:#f6f7f9;color:#24292f}}
 header{{background:#1f2937;color:#fff;padding:12px 20px;position:sticky;top:0;z-index:9}}
 header h1{{font-size:16px;margin:0 0 4px}}
 header .meta{{font-size:12px;opacity:.85}}
 header button{{float:right;margin-left:8px;background:#2563eb;color:#fff;border:0;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:13px}}
 main{{display:flex;gap:0;height:calc(100vh - 74px)}}
 #list{{flex:1.4;overflow-y:auto;padding:12px}}
 #panel{{flex:1;overflow-y:auto;padding:16px;background:#fff;border-left:1px solid #e5e7eb}}
 .parent{{background:#fff;border:1px solid #e5e7eb;border-radius:8px;margin-bottom:12px}}
 .parent>h2{{font-size:14px;margin:0;padding:8px 12px;background:#f3f4f6;cursor:pointer;border-radius:8px 8px 0 0}}
 .child{{border-top:1px solid #f0f0f0;padding:8px 12px;cursor:pointer;font-size:13px}}
 .child:hover{{background:#eff6ff}}
 .child.sel{{background:#dbeafe}}
 .child .tag{{display:inline-block;font-size:11px;color:#6b7280;margin-left:6px}}
 .child .rev{{color:#059669;font-weight:600}}
 #panel label{{display:block;font-size:12px;color:#6b7280;margin-top:10px}}
 #panel input[type=text],#panel textarea{{width:100%;box-sizing:border-box;border:1px solid #d1d5db;border-radius:6px;padding:6px;font-size:13px}}
 #panel .orig{{background:#f9fafb;border-radius:6px;padding:8px;font-size:12px;white-space:pre-wrap;max-height:200px;overflow-y:auto}}
 #panel button{{margin-top:10px;margin-right:8px;border:0;border-radius:6px;padding:6px 12px;cursor:pointer;font-size:13px}}
 .b-blue{{background:#2563eb;color:#fff}} .b-gray{{background:#e5e7eb}} .b-red{{background:#dc2626;color:#fff}}
 .stat{{font-size:12px;margin-right:14px}}
</style>
</head>
<body>
<header>
 <h1>分块人工调优 · {title}</h1>
 <div class="meta">doc_id: {doc_id} ｜ doc_version: {doc_version} ｜ 页数: {pages}</div>
 <div style="margin-top:6px">
  <span class="stat">子块 <b id="st-child">0</b></span>
  <span class="stat">锚点覆盖 <b id="st-anchor">0%</b></span>
  <span class="stat">已核 <b id="st-rev">0</b></span>
  <button onclick="exportRevised()">导出修订版 chunks.json</button>
 </div>
</header>
<main>
 <div id="list"></div>
 <div id="panel"><p style="color:#6b7280">← 点击左侧子块：调整边界 / 补全元数据 / 标记已核。人工修订 NEVER 改写原文（保真红线），只作用于分块层。</p></div>
</main>
<script>
const DATA = {data};
let selId = null, mergeCount = 0, splitCount = 0;

function stats(){{
  const kids = DATA.chunks.filter(c=>c.type==="child");
  const anch = kids.filter(c=>c.anchor_source!=="unavailable");
  document.getElementById("st-child").textContent = kids.length;
  document.getElementById("st-anchor").textContent = kids.length? Math.round(100*anch.length/kids.length)+"%" : "0%";
  document.getElementById("st-rev").textContent = kids.filter(c=>c.metadata && c.metadata.reviewed).length;
}}
function render(){{
  const root = document.getElementById("list"); root.innerHTML="";
  DATA.chunks.filter(c=>c.type==="parent").forEach(p=>{{
    const box = document.createElement("div"); box.className="parent";
    const h = document.createElement("h2");
    h.textContent = p.chunk_id + " " + (p.heading_path[p.heading_path.length-1]||"(无标题)") + ` （p.${{p.page_start}}-${{p.page_end}}，${{p.children.length}} 子块）`;
    h.onclick = ()=> box.querySelector(".kids").classList.toggle("hide") || true;
    const kids = document.createElement("div"); kids.className="kids";
    p.children.forEach(cid=>{{
      const c = DATA.chunks.find(x=>x.chunk_id===cid); if(!c) return;
      const d = document.createElement("div");
      d.className = "child"+(c.chunk_id===selId?" sel":"");
      d.onclick = ()=>{{ selId=c.chunk_id; renderPanel(c); render(); }};
      let meta = c.metadata||{{}};
      d.innerHTML = `<b>${{c.chunk_id}}</b><span class="tag">p.${{c.page??'?'}}</span>` +
        (c.char_count?`<span class="tag">${{c.char_count}}字</span>`:"") +
        (meta.entity?`<span class="tag">🏷 ${{escHtml(meta.entity)}}</span>`:"") +
        (meta.reviewed?`<span class="rev">已核</span>`:"") +
        `<div style="color:#374151;margin-top:2px">${{escHtml(c.text.slice(0,80))}}…</div>`;
      kids.appendChild(d);
    }});
    box.appendChild(h); box.appendChild(kids); root.appendChild(box);
  }});
  stats();
}}
function escHtml(s){{return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}}
function renderPanel(c){{
  const p = document.getElementById("panel");
  const m = c.metadata = c.metadata || {{entity:"",entity_aliases:[],source_context:"",reviewed:false}};
  p.innerHTML = `
   <b>${{c.chunk_id}}</b> <span style="color:#6b7280">p.${{c.page??'?'}} ｜ ${{c.heading_path.join(" › ")||"-"}}</span>
   <div style="color:#6b7280;font-size:12px">bbox: ${{JSON.stringify(c.bbox)}} （${{c.bbox_confidence}}）</div>
   <label>原文（NEVER 改写）</label><div class="orig">${{escHtml(c.text)}}</div>
   <label>实体补全（例：「同比增长3%」→ 补公司名「腾讯控股」）</label>
   <input type="text" id="f-entity" value="${{escAttr(m.entity)}}" placeholder="实体/公司名">
   <label>实体别名（逗号分隔，例：0700.HK, Tencent）</label>
   <input type="text" id="f-aliases" value="${{escAttr((m.entity_aliases||[]).join(", "))}}">
   <label>场景上下文（例：2026Q2 财报）</label>
   <input type="text" id="f-ctx" value="${{escAttr(m.source_context)}}" placeholder="补全主语/时间/场景">
   <label>拆分：在下方文本中定位切点（点击「在此拆分」按光标位置）</label>
   <textarea id="f-split" rows="4">${{escHtml(c.text)}}</textarea>
   <div>
    <button class="b-blue" onclick="saveMeta('${{c.chunk_id}}')">保存元数据</button>
    <button class="b-gray" onclick="markRev('${{c.chunk_id}}')">${{m.reviewed?'取消已核':'标记已核'}}</button>
    <button class="b-gray" onclick="splitChunk('${{c.chunk_id}}')">在此拆分</button>
    <button class="b-red" onclick="mergeUp('${{c.chunk_id}}')">与上一子块合并</button>
   </div>`;
}}
function escAttr(s){{return escHtml(s).replace(/"/g,"&quot;");}}
function saveMeta(id){{
  const c = DATA.chunks.find(x=>x.chunk_id===id);
  c.metadata.entity = document.getElementById("f-entity").value.trim();
  c.metadata.entity_aliases = document.getElementById("f-aliases").value.split(/[,，]/).map(s=>s.trim()).filter(Boolean);
  c.metadata.source_context = document.getElementById("f-ctx").value.trim();
  render(); renderPanel(c);
}}
function markRev(id){{ const c=DATA.chunks.find(x=>x.chunk_id===id); c.metadata.reviewed=!c.metadata.reviewed; render(); renderPanel(c); }}
function splitChunk(id){{
  const pos = document.getElementById("f-split").selectionStart;
  const c = DATA.chunks.find(x=>x.chunk_id===id);
  if(!pos || pos>=c.text.length-1){{ alert("请先在文本框内点击定位切点位置"); return; }}
  const a = c.text.slice(0,pos).trim(), b = c.text.slice(pos).trim();
  if(!a||!b){{ alert("切点不能产生空块"); return; }}
  const nid = id+"-s"+(++splitCount);
  const nc = JSON.parse(JSON.stringify(c));
  nc.chunk_id=nid; nc.text=b; nc.char_count=b.length;
  c.text=a; c.char_count=a.length;
  const pi = DATA.chunks.findIndex(x=>x.chunk_id===c.parent_id);
  const p = DATA.chunks[pi];
  p.children.splice(p.children.indexOf(id)+1,0,nid);
  DATA.chunks.splice(DATA.chunks.indexOf(c)+1,0,nc);
  selId=nid; render(); renderPanel(nc);
}}
function mergeUp(id){{
  const ci = DATA.chunks.findIndex(x=>x.chunk_id===id);
  const c = DATA.chunks[ci];
  const p = DATA.chunks.find(x=>x.chunk_id===c.parent_id);
  const pos = p.children.indexOf(id);
  if(pos<=0){{ alert("已是该父块首个子块，无上邻"); return; }}
  const prev = DATA.chunks.find(x=>x.chunk_id===p.children[pos-1]);
  if(!confirm(`合并 ${{prev.chunk_id}} + ${{c.chunk_id}}？（锚点取并集）`)) return;
  prev.text = prev.text + "\\n\\n" + c.text;
  prev.char_count = prev.text.length;
  if(c.page && (prev.page===null||prev.page===undefined||c.page<prev.page)) prev.page=c.page;
  p.children.splice(pos,1); DATA.chunks.splice(ci,1);
  mergeCount++; selId=prev.chunk_id; render(); renderPanel(prev);
}}
function exportRevised(){{
  const out = Object.assign({{}}, DATA, {{revised_at: new Date().toISOString(), revision_stats: {{merged:mergeCount, split:splitCount}}}});
  const blob = new Blob([JSON.stringify(out,null,2)],{{type:"application/json"}});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "chunks.revised.json";
  a.click(); URL.revokeObjectURL(a.href);
}}
document.querySelectorAll(".kids").forEach(e=>e.classList.remove("hide"));
render();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def build_all(pdf_path: Path, md_path: Path, args) -> dict:
    md_text = md_path.read_text(encoding="utf-8", errors="ignore")
    pages, reader_kind = load_pdf_pages(pdf_path)
    if pages is None:
        return {"ok": False, "errors": ["本地无 pdfplumber/pypdf，无法结构化——请安装：pip install pdfplumber"]}

    page_count = len(pages)
    stat = pdf_path.stat()
    size_hash = hashlib.md5(f"{pdf_path.name}:{page_count}:{stat.st_size}".encode()).hexdigest()[:6]
    doc_id = f"{pdf_path.stem}_{size_hash}"
    mtime = time.strftime("%Y-%m-%d", time.localtime(stat.st_mtime))
    doc_version = args.doc_version or f"v{mtime}_{size_hash[:4]}"
    doc_name = args.doc_name or pdf_path.stem

    doc_meta = {
        "title": doc_name,
        "source_file": pdf_path.name,
        "source_path": str(pdf_path.resolve()),
        "doc_version": doc_version,
        "pages": page_count,
        "converted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "backend": args.backend or "",
        "grade": args.grade or "",
        "confidence": args.confidence or "",
        "fidelity_rate": args.fidelity_rate if args.fidelity_rate is not None else None,
        "extra_tags": "",
    }
    # frontmatter 强制字段校验（obsidian-output-spec §二）
    missing = [k for k in ("title", "source_file", "doc_version", "pages")
               if not doc_meta.get(k)]
    if missing:
        return {"ok": False, "errors": [f"frontmatter 强制字段缺失：{missing}"], "exit_code": 3}

    sections = parse_sections(md_text)
    any_text = any(pg["norm"] for pg in pages)

    # --- 节级页码锚点（精确匹配 → 后向继承优先 → 前向兜底）---
    raw = []
    for sec in sections:
        fp = fingerprint("\n".join(l for l in sec["lines"] if not HEADING_RE.match(l)))
        page, source = match_page(fp, pages)
        raw.append({"page": page if source == "exact" else None, "source": source})
    nxt_page = None
    for r in reversed(raw):  # 后向继承（空标题节与其后内容通常同页）
        if r["page"] is not None:
            nxt_page = r["page"]
        elif nxt_page is not None:
            r["page"] = nxt_page
    last_page = None
    for r in raw:  # 前向兜底（文末空节）
        if r["page"] is not None:
            last_page = r["page"]
        elif last_page is not None:
            r["page"] = last_page
    anchors = [{"page": r["page"], "source": r["source"], "page_end": None} for r in raw]
    # 跨页：节起始页与后继节起始页推算区间
    for i, a in enumerate(anchors):
        if a["page"] is None:
            continue
        nxt = None
        for j in range(i + 1, len(anchors)):
            if anchors[j]["page"] is not None:
                nxt = anchors[j]["page"]
                break
        if nxt is not None and nxt > a["page"]:
            a["page_end"] = nxt - 1 if nxt - 1 > a["page"] else None

    # --- Small-to-Big 父子分块 ---
    chunks = []
    parent_seq = 0
    for si, sec in enumerate(sections):
        parent_seq += 1
        pid = f"p{parent_seq:03d}"
        anchor = anchors[si]
        child_texts = split_children(sec["lines"], args.child_max_chars)
        children_ids = []
        child_entries = []
        for ci, text in enumerate(child_texts):
            cid = f"{pid}-c{ci + 1:02d}"
            cfp = fingerprint(text)
            cpage, csource = match_page(cfp, pages)
            if cpage is None:
                cpage, csource = anchor["page"], "inherited" if anchor["page"] is not None else "unavailable"
            bbox, bbox_conf = None, "unavailable"
            if cpage is not None:
                pg = pages[cpage - 1]
                bbox = char_bbox(cfp, pg)
                if bbox is not None:
                    bbox_conf = "exact"
                else:
                    bbox = page_text_bbox(pg)
                    bbox_conf = "approx" if bbox else "unavailable"
            entry = {
                "chunk_id": cid, "type": "child", "parent_id": pid,
                "heading_path": sec["heading_path"],
                "text": text, "page": cpage, "anchor_source": csource,
                "bbox": bbox, "bbox_confidence": bbox_conf,
                "char_count": len(text),
                "metadata": {"entity": "", "entity_aliases": [], "source_context": "", "reviewed": False},
            }
            child_entries.append(entry)
            children_ids.append(cid)
        body_text = "\n".join(l for l in sec["lines"] if not HEADING_RE.match(l)).strip()
        page_start = anchor["page"] or (child_entries[0]["page"] if child_entries else None)
        page_end = None
        cps = [c["page"] for c in child_entries if c["page"] is not None]
        if cps:
            page_end = max(cps)
        chunks.append({
            "chunk_id": pid, "type": "parent", "level": sec["level"] or None,
            "heading_path": sec["heading_path"], "text": body_text,
            "page_start": page_start, "page_end": page_end,
            "children": children_ids, "char_count": len(normalize(body_text)),
        })
        chunks.extend(child_entries)

    # 页级父块聚合（--parent-granularity page：按页重组父子关系由 review.html 与下游自行聚合；
    # 结构化缺省仍输出 section 父块，页级模式仅调整标记）
    kids = [c for c in chunks if c["type"] == "child"]
    anchored = [c for c in kids if c["anchor_source"] != "unavailable"]
    anchor_coverage = round(len(anchored) / len(kids), 4) if kids else 0.0

    chunks_doc = {
        "doc_id": doc_id,
        "doc_version": doc_version,
        "generated_at": doc_meta["converted_at"],
        "parent_granularity": args.parent_granularity,
        "child_max_chars": args.child_max_chars,
        "chunks": chunks,
    }

    obsidian_md = render_obsidian(doc_meta, sections, anchors)
    review_html = REVIEW_HTML_TMPL.format(
        title=doc_meta["title"], doc_id=doc_id, doc_version=doc_version,
        pages=doc_meta["pages"],
        data=json.dumps(chunks_doc, ensure_ascii=False),
    )

    out_dir = Path(args.out_dir) if args.out_dir else md_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    obs_path = out_dir / f"{md_path.stem}.obsidian.md"
    chunks_path = out_dir / f"{md_path.stem}.chunks.json"
    review_path = out_dir / f"{md_path.stem}.review.html"
    obs_path.write_text(obsidian_md, encoding="utf-8")
    chunks_path.write_text(json.dumps(chunks_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(review_html, encoding="utf-8")

    return {
        "ok": True,
        "doc_id": doc_id,
        "doc_version": doc_version,
        "reader_kind": reader_kind,
        "pages": page_count,
        "sections": len(sections),
        "parent_chunks": len([c for c in chunks if c["type"] == "parent"]),
        "child_chunks": len(kids),
        "anchor_coverage": anchor_coverage,
        "bbox_exact": len([c for c in kids if c["bbox_confidence"] == "exact"]),
        "bbox_approx": len([c for c in kids if c["bbox_confidence"] == "approx"]),
        "scan_mode": not any_text,
        "evaluation_supply": {
            "parse_completeness_source": "门D quality_check.py 保真率（本脚本不重复计算）",
            "citation_traceability": anchor_coverage,
            "note": "召回命中率/生成忠实度归下游 LLM-as-Judge（references/rag-handoff-spec.md §四）",
        },
        "products": {
            "obsidian_md": str(obs_path),
            "chunks_json": str(chunks_path),
            "review_html": str(review_path),
        },
        "warnings": ([] if any_text else ["无文本层（扫描件）——页码/坐标锚点不可计算，coverage=0 如实报告"])
        + ([f"非缺省分块参数：child_max_chars={args.child_max_chars}"] if args.child_max_chars != 800 else []),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="tri-pdf2md 门E 结构化交付")
    ap.add_argument("--pdf", required=True, help="源 PDF 路径")
    ap.add_argument("--md", required=True, help="门C 转换产物 MD 路径")
    ap.add_argument("--out-dir", help="输出目录（缺省 MD 同目录）")
    ap.add_argument("--doc-name", help="覆盖文档名（缺省 PDF 文件名去扩展名）")
    ap.add_argument("--doc-version", help="覆盖版本标识（缺省 PDF修改日期_指纹）")
    ap.add_argument("--backend", help="门C 后端 slug（frontmatter 元数据）")
    ap.add_argument("--grade", choices=["L0", "L1", "L2", "L3"], help="转换档位")
    ap.add_argument("--confidence", choices=["A", "B", "C"], help="门D 置信度")
    ap.add_argument("--fidelity-rate", type=float, help="门D 保真率（0-1）")
    ap.add_argument("--parent-granularity", choices=["section", "page"], default="section")
    ap.add_argument("--child-max-chars", type=int, default=800)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    pdf_path, md_path = Path(args.pdf), Path(args.md)
    errors = []
    if not pdf_path.is_file():
        errors.append(f"PDF 不存在：{pdf_path}")
    if not md_path.is_file():
        errors.append(f"MD 不存在：{md_path}")
    if errors:
        safe_print(json.dumps({"ok": False, "errors": errors}, ensure_ascii=False))
        return 2

    result = build_all(pdf_path, md_path, args)
    code = result.pop("exit_code", 0)
    safe_print(json.dumps(result, ensure_ascii=False, indent=2))
    return code if not result.get("ok") else 0


if __name__ == "__main__":
    sys.exit(main())
