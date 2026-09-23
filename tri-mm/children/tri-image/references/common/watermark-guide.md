# 水印注入（公共层 · 可选能力）

> 水印在扩展偏好中默认关闭；启用后由提示词注入，各场景共用同一套模板与位置取值。

## 偏好结构

```yaml
watermark:
  enabled: false
  content: "品牌名"
  position: bottom-right   # bottom-right / bottom-left / bottom-center / top-right
  opacity: 0.6
```

## 注入方式

### Track-R · T1（原生后端）

原生生图工具提供 `footnote` 参数时优先用它——**硬上限 16 字符**，超出 MUST 截断并提示用户。

### Track-R · T2（引擎）与其它

追加以下段落到提示词正文：

```
Include a subtle watermark "[content]" positioned at [position].
The watermark should be legible but not distracting.
```

## 约束

- 水印 MUST 由模型在生成阶段绘制，**NEVER** 事后用图像处理叠加到已生成的位图上（违反 Track-R 红线 2 的同类禁令）。
- 水印内容由用户偏好提供；NEVER 自行编造品牌词。
- Track-V（结构图）不注水水印：矢量产物由用户在编辑器中后处理，若确需可用 `title`/`desc` 元素标注。
