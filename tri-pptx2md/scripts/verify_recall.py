#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""门D 召回率口径回归自检（tri-pptx2md v1.4.4）。

零第三方依赖：用 zipfile 现场拼最小 .pptx + 构造 MD，直接调用 quality_check 的
compute_metrics() / grade_confidence()，断言 v1.4.4 修复的四条口径问题不再回归：

  1. 跨页粘连：所有页拼成一个串再切 bigram 会造出伪 bigram，使完美转换 <100%
     → 现改为逐页切 bigram 求并集，完美转换 MUST 为 1.0 / A
  2. 全角数字不进分母：normalize 先 NFKC 折叠后，全角数字计入源侧
     → MD 丢掉全角数字 MUST 拉低召回（修复前恒为 1.0）
  3. 页覆盖达标但召回 <85%：fidelity-spec §三 C 行条件 MUST 可达（判 C，非 B）
  4. 多写 Slide 块：页覆盖 min() 截断到 100%，多出的块 MUST 进异常清单

用法：
    python scripts/verify_recall.py            # 退出码 0 全过 / 1 存在 FAIL
"""
from __future__ import annotations

import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_check import compute_metrics, grade_confidence  # noqa: E402

NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

SLIDE_TPL = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="{NS_A}" xmlns:r="{NS_R}" xmlns:p="{NS_P}"><p:cSld><p:spTree>
<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>
<p:sp><p:nvSpPr><p:cNvPr id="2" name="tb"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr/>
<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="zh-CN"/><a:t>{{text}}</a:t></a:r></a:p></p:txBody></p:sp>
</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'''


def build_pptx(pages: list[str], dest: Path) -> Path:
    """拼一个仅含文本的最小 .pptx（够 zipfile 与 python-pptx 两条提取路径使用）。"""
    n = len(pages)
    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>',
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>']
    sld_ids, rels = [], []
    for i in range(1, n + 1):
        ct.append(f'<Override PartName="/ppt/slides/slide{i}.xml" '
                  f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        sld_ids.append(f'<p:sldId id="{255 + i}" r:id="rId{i}"/>')
        rels.append(f'<Relationship Id="rId{i}" '
                    f'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" '
                    f'Target="slides/slide{i}.xml"/>')
    ct.append("</Types>")
    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                 'relationships/officeDocument" Target="ppt/presentation.xml"/></Relationships>')
    pres = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<p:presentation xmlns:p="{NS_P}" xmlns:r="{NS_R}"><p:sldIdLst>'
            + "".join(sld_ids) + "</p:sldIdLst></p:presentation>")
    pres_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 + "".join(rels) + "</Relationships>")
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels", root_rels)
        z.writestr("ppt/presentation.xml", pres)
        z.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        for i, text in enumerate(pages, 1):
            z.writestr(f"ppt/slides/slide{i}.xml", SLIDE_TPL.format(text=text))
    return dest


def check(name: str, ok: bool, detail: str, results: list) -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} —— {detail}")


def main() -> int:
    results: list[tuple[str, bool, str]] = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)

        # ① 跨页粘连：完美转换 MUST 100% / A（页数越少越能暴露）
        for n in (3, 5, 20):
            pages = [f"第{i}页标题第{i}页正文要点" for i in range(1, n + 1)]
            ppt = build_pptx(pages, td / f"perfect{n}.pptx")
            md = td / f"perfect{n}.md"
            md.write_text("\n".join(f"## Slide {i}\n\n### 第{i}页标题\n\n第{i}页正文要点\n"
                                    for i in range(1, n + 1)), encoding="utf-8")
            m = compute_metrics(ppt, md)
            g = grade_confidence(m)
            check(f"①完美转换 {n} 页 recall=1.0 且 A",
                  m["recall"] == 1.0 and g["confidence"] == "A",
                  f"recall={m['recall']} pc={m['page_coverage']} conf={g['confidence']}（修复前 3 页为 0.9286/B）",
                  results)

        # ② 全角数字进分母：源字符数含全角折叠后的 4 位数字；MD 丢掉全角数字 MUST 拉低召回
        ppt = build_pptx(["年度目标２０２６年营收目标"], td / "fw.pptx")
        md_keep = td / "fw_keep.md"
        md_keep.write_text("## Slide 1\n\n### 年度目标\n\n年度目标２０２６年营收目标\n", encoding="utf-8")
        md_drop = td / "fw_drop.md"
        md_drop.write_text("## Slide 1\n\n### 年度目标\n\n年度目标年营收目标\n", encoding="utf-8")
        mk, md_ = compute_metrics(ppt, md_keep), compute_metrics(ppt, md_drop)
        check("②全角数字计入统计（丢掉即掉分）",
              mk["source_total_chars"] == 13 and md_["recall"] < 1.0,
              f"源字符={mk['source_total_chars']}（NFKC 折叠后含 2026，修复前剔除全角为 9）；"
              f"全保留 recall={mk['recall']}，丢全角 recall={md_['recall']}（修复前丢全角恒为 1.0）",
              results)

        # ③ 页覆盖 100% 但召回 <85% → C（fidelity-spec §三 C 行可达）
        pages = [f"模块{i}标题模块{i}的一段真实正文内容用于测试召回" for i in range(1, 11)]
        ppt = build_pptx(pages, td / "bodygone.pptx")
        md = td / "bodygone.md"
        md.write_text("\n".join(f"## Slide {i}\n\n### 模块{i}标题\n" for i in range(1, 11)), encoding="utf-8")
        m = compute_metrics(ppt, md)
        g = grade_confidence(m)
        check("③页全在而正文大面积缺失 → C",
              m["page_coverage"] == 1.0 and m["recall"] < 0.85 and g["confidence"] == "C",
              f"pc={m['page_coverage']} recall={m['recall']} conf={g['confidence']}；"
              f"理由={g['reasons'][0]}",
              results)

        # ④ 多写 Slide 块 → 异常清单可见
        pages = [f"页{i}正文{i}" for i in range(1, 6)]
        ppt = build_pptx(pages, td / "extra.pptx")
        md = td / "extra.md"
        md.write_text("\n".join(f"## Slide {i}\n\n### 页{min(i, 5)}\n\n正文{min(i, 5)}\n"
                                for i in range(1, 13)), encoding="utf-8")
        m = compute_metrics(ppt, md)
        g = grade_confidence(m)
        check("④多写的 Slide 块进异常清单",
              m["md_extra_blocks"] == 7 and any("超过源" in a for a in m["anomalies"]),
              f"md_extra_blocks={m['md_extra_blocks']} 异常={m['anomalies']} conf={g['confidence']}"
              f"（修复前 pc=1.0、零告警、A）",
              results)

    failed = [r for r in results if not r[1]]
    print(f"\n[{'PASS' if not failed else 'FAIL'}] 召回率口径回归：{len(results) - len(failed)}/{len(results)} 通过")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
