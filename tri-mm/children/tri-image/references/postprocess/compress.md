# 后处理：压缩与格式转换

> 生成产物交付前的可选收尾步骤。脚本：`scripts/compress_image.py`（零必需依赖，按需用系统工具或 Pillow 兜底）。

## 用法

```bash
python scripts/compress_image.py <图片或目录>
python scripts/compress_image.py dir/ -r                 # 递归处理目录
python scripts/compress_image.py a.png -f webp -q 80 -k  # 转 webp、质量 80、保留原文件
python scripts/compress_image.py a.png --json            # JSON 输出
```

| 参数 | 说明 | 默认 |
|---|---|---|
| `-f/--format` | `webp` / `png` / `jpeg` | `webp` |
| `-q/--quality` | 0–100 | 80 |
| `-k/--keep` | 保留原文件 | 关闭 |
| `-r/--recursive` | 目录递归 | 关闭 |
| `-o/--output` | 单文件模式输出路径 | 自动推导 |
| `--json` | 结构化输出 | 关闭 |

退出码：`0` 成功；`2` 输入/参数问题；`3` 本机无可用压缩后端。

## 后端探测（跨平台）

按序探测 `cwebp` → `magick` → `convert`，**并对 ImageMagick 家族做身份校验**：Windows 的 `C:\Windows\system32\convert.exe` 是磁盘格式转换工具，与 ImageMagick 的 `convert` 同名，未经校验直接调用后果不可逆。校验通过条件：可执行文件不在系统目录，且 `convert -version` 输出含 `imagemagick`。

二者皆无时降级到 Python `Pillow`（`compress_with_pillow`）；Pillow 也不存在 → 退出码 3 并给出安装建议，**NEVER 崩溃、NEVER 静默失败**。

## 数据安全（本次修复重点）

1. **NEVER 覆盖源文件**：输出路径若与输入路径相同，自动改写到 `<stem>-compressed<ext>`。
2. **输出冲突自动编号**：同一批内两个输入映射到同一输出时，自动追加 `-2`、`-3` 序号。
3. **tmp → rename 原子落盘**：先写 `<out>.tmp` 再 `os.replace`，避免中途失败留下半截文件。
4. 失败项单独记录到 `failures`，NEVER 中断整批处理。

## 支持格式

输入：`.png .jpg .jpeg .webp .gif .tiff`；输出：`webp`（默认）/ `png` / `jpeg`。

## 与交付流程的关系

后处理**仅限**裁剪、缩放、压缩、格式转换。NEVER 用任何程序在已生成的位图上补字、改字、擦字、盖字——文字错讹只能靠改提示词重出（见 `../common/image-backend-rules.md` 红线 2）。
