#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pptx.py —— tri-ppt 确定性 PPTX 生成器（python-pptx）

读取 design.json（大纲 + 逐页动效方案）与 materials.json（素材引用），
生成设计精美、可直接下载的 PPTX 源文件。

用法：
    python build_pptx.py --spec design.json --materials materials.json --out deck.pptx

依赖：python-pptx（缺失时脚本会给出安装提示并退出）。
设计理念：所有版式/配色/字体/转场均为确定性算法，MUST 由此脚本落地，
SKILL.md 不内联算法细节（满足家族约束：确定性算法下沉 scripts/）。
"""

import argparse
import json
import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml

EMU_PER_IN = 914400
SLIDE_W = 13.333
SLIDE_H = 7.5

DEFAULT_THEME = {
    "aspect": "16:9",
    "colors": {
        "primary": "#1F4E79",
        "secondary": "#2E75B6",
        "accent": "#ED7D31",
        "bg": "#FFFFFF",
        "text": "#222222",
        "muted": "#666666",
    },
    "fonts": {"title": "Microsoft YaHei", "body": "Microsoft YaHei"},
}

TRANSITION_MAP = {
    "fade": "p:fade",
    "wipe": "p:wipe",
    "push": "p:push",
    "split": "p:split",
    "none": None,
}

CHART_MAP = {
    "bar": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "pie": XL_CHART_TYPE.PIE,
    "line": XL_CHART_TYPE.LINE_MARKERS,
}


def hex2rgb(value):
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def load_spec(spec_path, materials_path):
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
    materials = {}
    if materials_path and os.path.exists(materials_path):
        with open(materials_path, "r", encoding="utf-8") as f:
            materials = json.load(f)
    return spec, materials


def add_transition(slide, kind):
    """注入幻灯片切换效果（python-pptx 无原生 API，走 oxml）。"""
    if not kind or kind not in TRANSITION_MAP or TRANSITION_MAP[kind] is None:
        return
    sld = slide._element
    existing = sld.find(qn("p:transition"))
    if existing is not None:
        sld.remove(existing)
    tr = parse_xml('<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"/>')
    el = parse_xml(
        '<p:{kind} xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
        '<p:cTn spd="med" accel="0.05" decel="0.05"/></p:{kind}>'.format(kind=TRANSITION_MAP[kind].split(":")[1])
    )
    tr.append(el)
    sld.append(tr)


def add_bg(slide, color_hex):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = hex2rgb(color_hex)


def add_rect(slide, l, t, w, h, color_hex, line=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = hex2rgb(color_hex)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = hex2rgb(line)
        shp.line.width = Pt(1)
    shp.shadow.inherit = False
    return shp


def add_text(slide, l, t, w, h, text, size, color_hex, bold=False, align=PP_ALIGN.LEFT,
             font="Microsoft YaHei", anchor=MSO_ANCHOR.TOP, italic=False):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Pt(4)
    tf.margin_right = Pt(4)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    run.font.color.rgb = hex2rgb(color_hex)
    return tb


def add_bullets(slide, l, t, w, h, items, size, color_hex, font, accent_hex):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(8)
        marker = p.add_run()
        marker.text = "▪  "
        marker.font.size = Pt(size)
        marker.font.color.rgb = hex2rgb(accent_hex)
        marker.font.name = font
        run = p.add_run()
        run.text = item
        run.font.size = Pt(size)
        run.font.name = font
        run.font.color.rgb = hex2rgb(color_hex)
    return tb


def add_image_fit(slide, path, l, t, w, h):
    if not path or not os.path.exists(path):
        # 占位灰块
        add_rect(slide, l, t, w, h, "#EEEEEE", line="#CCCCCC")
        add_text(slide, l, t + h / 2 - 0.3, w, 0.6, "（图片缺失）", 12, "#999999",
                 align=PP_ALIGN.CENTER, font="Microsoft YaHei", anchor=MSO_ANCHOR.MIDDLE)
        return
    # 按比例缩放贴合框
    try:
        from PIL import Image
        with Image.open(path) as im:
            iw, ih = im.size
        box_ratio = w / h
        img_ratio = iw / ih
        if img_ratio > box_ratio:
            nw = w
            nh = w / img_ratio
        else:
            nh = h
            nw = h * img_ratio
        nl = l + (w - nw) / 2
        nt = t + (h - nh) / 2
        slide.shapes.add_picture(path, Inches(nl), Inches(nt), Inches(nw), Inches(nh))
    except Exception:
        slide.shapes.add_picture(path, Inches(l), Inches(t), Inches(w))


def render_cover(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["primary"])
    add_rect(slide, 0, SLIDE_H - 0.18, SLIDE_W, 0.18, c["accent"])
    add_text(slide, 0.9, SLIDE_H / 2 - 1.6, SLIDE_W - 1.8, 1.6, s.get("title", ""), 40,
             "#FFFFFF", bold=True, align=PP_ALIGN.LEFT, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    if s.get("subtitle"):
        add_text(slide, 0.95, SLIDE_H / 2 + 0.1, SLIDE_W - 1.9, 1.0, s["subtitle"], 20,
                 "#DCE6F1", align=PP_ALIGN.LEFT, font=ft["body"])
    meta = "  ·  ".join([x for x in [s.get("author"), s.get("date")] if x])
    if meta:
        add_text(slide, 0.95, SLIDE_H - 1.2, SLIDE_W - 1.9, 0.5, meta, 12, "#A9C4E0", font=ft["body"])


def render_section(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["bg"])
    add_rect(slide, 0, 0, 0.25, SLIDE_H, c["accent"])
    num = s.get("section_no", "")
    if num:
        add_text(slide, 0.9, 1.4, 3, 1.5, str(num), 72, c["secondary"], bold=True, font=ft["title"])
    add_text(slide, 0.9, 3.0, SLIDE_W - 1.8, 1.6, s.get("title", ""), 36, c["text"],
             bold=True, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    if s.get("subtitle"):
        add_text(slide, 0.95, 4.6, SLIDE_W - 1.9, 1.0, s["subtitle"], 18, c["muted"], font=ft["body"])


def render_bullets(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["bg"])
    add_rect(slide, 0, 0, SLIDE_W, 1.1, c["primary"])
    add_text(slide, 0.6, 0, SLIDE_W - 1.2, 1.1, s.get("title", ""), 26, "#FFFFFF",
             bold=True, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    items = s.get("bullets", [])
    if s.get("image"):
        add_bullets(slide, 0.7, 1.5, 7.0, SLIDE_H - 2.0, items, 18, c["text"], ft["body"], c["accent"])
        add_image_fit(slide, s["image"], 8.0, 1.5, 4.9, SLIDE_H - 2.2)
    else:
        add_bullets(slide, 0.7, 1.5, SLIDE_W - 1.4, SLIDE_H - 2.0, items, 18, c["text"], ft["body"], c["accent"])


def render_two_column(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["bg"])
    add_rect(slide, 0, 0, SLIDE_W, 1.1, c["primary"])
    add_text(slide, 0.6, 0, SLIDE_W - 1.2, 1.1, s.get("title", ""), 26, "#FFFFFF",
             bold=True, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    left = s.get("left", {})
    right = s.get("right", {})
    add_text(slide, 0.7, 1.4, 5.8, 0.5, left.get("heading", ""), 18, c["secondary"], bold=True, font=ft["title"])
    add_bullets(slide, 0.7, 2.0, 5.8, SLIDE_H - 2.4, left.get("bullets", []), 16, c["text"], ft["body"], c["accent"])
    add_rect(slide, 6.7, 1.4, 0.03, SLIDE_H - 2.0, "#DDDDDD")
    add_text(slide, 7.0, 1.4, 5.6, 0.5, right.get("heading", ""), 18, c["secondary"], bold=True, font=ft["title"])
    if right.get("image"):
        add_image_fit(slide, right["image"], 7.0, 2.0, 5.6, 3.4)
    add_bullets(slide, 7.0, 5.6, 5.6, SLIDE_H - 5.9, right.get("bullets", []), 16, c["text"], ft["body"], c["accent"])


def render_image_focus(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["bg"])
    add_text(slide, 0.6, 0.5, SLIDE_W - 1.2, 0.9, s.get("title", ""), 26, c["primary"],
             bold=True, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    add_image_fit(slide, s.get("image"), 0.8, 1.6, SLIDE_W - 1.6, SLIDE_H - 3.0)
    if s.get("caption"):
        add_text(slide, 0.8, SLIDE_H - 1.2, SLIDE_W - 1.6, 0.9, s["caption"], 14, c["muted"],
                 align=PP_ALIGN.CENTER, font=ft["body"], anchor=MSO_ANCHOR.MIDDLE)


def render_data_chart(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["bg"])
    add_rect(slide, 0, 0, SLIDE_W, 1.1, c["primary"])
    add_text(slide, 0.6, 0, SLIDE_W - 1.2, 1.1, s.get("title", ""), 26, "#FFFFFF",
             bold=True, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    chart = s.get("chart")
    if not chart:
        add_text(slide, 1, 2, SLIDE_W - 2, 1, "（无图表数据）", 16, c["muted"], font=ft["body"])
        return
    cd = CategoryChartData()
    cd.categories = chart.get("categories", [])
    for ser in chart.get("series", []):
        cd.add_series(ser.get("name", "Series"), ser.get("values", []))
    gf = slide.shapes.add_chart(CHART_MAP.get(chart.get("type", "bar"), XL_CHART_TYPE.COLUMN_CLUSTERED),
                                Inches(0.8), Inches(1.5), Inches(SLIDE_W - 1.6), Inches(SLIDE_H - 2.2), cd)
    chart_frame = gf.chart
    chart_frame.has_title = True
    chart_frame.chart_title.text_frame.text = chart.get("title", "")
    chart_frame.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
    chart_frame.has_legend = len(chart.get("series", [])) > 1
    if chart_frame.has_legend:
        chart_frame.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart_frame.legend.include_in_layout = False
        chart_frame.legend.font.size = Pt(11)
    plot = chart_frame.plots[0]
    plot.has_data_labels = True
    plot.data_labels.font.size = Pt(11)
    # 主题色填充系列
    series_colors = [c["primary"], c["secondary"], c["accent"]]
    for i, ser in enumerate(chart_frame.series):
        try:
            ser.format.fill.solid()
            ser.format.fill.fore_color.rgb = hex2rgb(series_colors[i % len(series_colors)])
        except Exception:
            pass


def render_comparison(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["bg"])
    add_rect(slide, 0, 0, SLIDE_W, 1.1, c["primary"])
    add_text(slide, 0.6, 0, SLIDE_W - 1.2, 1.1, s.get("title", ""), 26, "#FFFFFF",
             bold=True, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    cols = s.get("compare", [{}, {}])
    half = (SLIDE_W - 1.4) / 2
    for idx, col in enumerate(cols[:2]):
        x = 0.7 + idx * (half + 0.1)
        add_rect(slide, x, 1.5, half, 0.7, c["secondary"] if idx == 0 else c["accent"])
        add_text(slide, x, 1.5, half, 0.7, col.get("heading", ""), 18, "#FFFFFF", bold=True,
                 align=PP_ALIGN.CENTER, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
        add_bullets(slide, x + 0.2, 2.4, half - 0.4, SLIDE_H - 2.8, col.get("bullets", []), 16,
                    c["text"], ft["body"], c["accent"])


def render_quote(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["primary"])
    add_rect(slide, 0.8, SLIDE_H / 2 - 1.6, 0.12, 3.2, c["accent"])
    add_text(slide, 1.2, SLIDE_H / 2 - 1.6, SLIDE_W - 2.4, 3.2, "“" + s.get("quote", "") + "”", 30,
             "#FFFFFF", bold=True, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    if s.get("author"):
        add_text(slide, 1.3, SLIDE_H / 2 + 1.9, SLIDE_W - 2.6, 0.6, "— " + s["author"], 16,
                 "#DCE6F1", font=ft["body"])


def render_closing(slide, s, th, ft):
    c = th["colors"]
    add_bg(slide, c["primary"])
    add_rect(slide, 0, SLIDE_H - 0.18, SLIDE_W, 0.18, c["accent"])
    add_text(slide, 0, SLIDE_H / 2 - 1.0, SLIDE_W, 1.2, s.get("title", "谢谢观看"), 40, "#FFFFFF",
             bold=True, align=PP_ALIGN.CENTER, font=ft["title"], anchor=MSO_ANCHOR.MIDDLE)
    if s.get("subtitle"):
        add_text(slide, 0, SLIDE_H / 2 + 0.3, SLIDE_W, 0.8, s["subtitle"], 18, "#DCE6F1",
                 align=PP_ALIGN.CENTER, font=ft["body"])


RENDERERS = {
    "cover": render_cover,
    "section": render_section,
    "bullets": render_bullets,
    "two_column": render_two_column,
    "image_focus": render_image_focus,
    "data_chart": render_data_chart,
    "comparison": render_comparison,
    "quote": render_quote,
    "closing": render_closing,
}


def build(spec, materials, out_path):
    theme = dict(DEFAULT_THEME)
    if "theme" in spec:
        theme.update(spec["theme"])
        if "colors" in spec["theme"]:
            theme["colors"] = {**DEFAULT_THEME["colors"], **spec["theme"]["colors"]}
        if "fonts" in spec["theme"]:
            theme["fonts"] = {**DEFAULT_THEME["fonts"], **spec["theme"]["fonts"]}

    prs = Presentation()
    prs.slide_width = Emu(int(SLIDE_W * EMU_PER_IN))
    prs.slide_height = Emu(int(SLIDE_H * EMU_PER_IN))
    blank = prs.slide_layouts[6]

    # 资源目录：图片相对 spec 文件所在目录解析
    spec_dir = os.path.dirname(os.path.abspath(spec.get("_spec_path", "")))
    mat_images = {m.get("use"): m.get("path") for m in materials.get("images", [])}

    meta = spec.get("meta", {})
    slides = spec.get("slides", [])
    for idx, s in enumerate(slides):
        layout = s.get("layout", "bullets")
        slide = prs.slides.add_slide(blank)
        # 解析图片路径：slide.image 优先，否则按 use 从素材库匹配
        img = s.get("image")
        if not img and s.get("image_use"):
            img = mat_images.get(s["image_use"])
        if img and not os.path.isabs(img) and spec_dir:
            img = os.path.join(spec_dir, img)
        if img:
            s["image"] = img
        # 注入 meta 到 cover/closing
        if layout in ("cover", "closing") and meta:
            s.setdefault("author", meta.get("author"))
            s.setdefault("date", meta.get("date"))
            if layout == "cover":
                s.setdefault("title", meta.get("title"))
                s.setdefault("subtitle", meta.get("subtitle"))
        renderer = RENDERERS.get(layout, render_bullets)
        renderer(slide, s, theme, theme["fonts"])
        add_transition(slide, s.get("transition", "fade"))
        if s.get("notes"):
            slide.notes_slide.notes_text_frame.text = s["notes"]
    prs.save(out_path)


def main():
    ap = argparse.ArgumentParser(description="tri-ppt deterministic PPTX builder")
    ap.add_argument("--spec", required=True, help="design.json 路径")
    ap.add_argument("--materials", default=None, help="materials.json 路径")
    ap.add_argument("--out", required=True, help="输出 .pptx 路径")
    args = ap.parse_args()

    try:
        import pptx  # noqa
    except ImportError:
        sys.stderr.write("[ERROR] 缺少依赖 python-pptx。请先安装：\n"
                         "  pip install python-pptx\n"
                         "（隔离环境建议：python -m venv venv && venv/bin/pip install python-pptx）\n")
        sys.exit(2)

    spec, materials = load_spec(args.spec, args.materials)
    spec["_spec_path"] = args.spec
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    build(spec, materials, args.out)
    print("[OK] 已生成 PPTX：%s（共 %d 页）" % (args.out, len(spec.get("slides", []))))


if __name__ == "__main__":
    main()
