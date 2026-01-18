# Gemini 水印去除工具 Skill

[English](README.md)

一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 技能插件，使用逆向 Alpha 混合算法去除 Gemini AI 生成图片的可见水印。

## 什么是 Claude Code Skill？

Skill（技能）是扩展 Claude Code 能力的可复用提示词和工具。安装此 Skill 后，你可以通过自然语言让 Claude Code 自动帮你去除图片中的 Gemini 水印。

## 功能特点

- **自动检测**：根据图片尺寸自动识别水印大小
- **批量处理**：支持一次性处理整个文件夹
- **多格式支持**：支持 JPG、PNG、WebP、BMP 格式
- **非破坏性**：可选择保存为新文件，保留原图

## 安装方法

1. 将此仓库克隆到 Claude Code 的 skills 目录：

```bash
git clone https://github.com/mervinyx/agent-skill-gemini-watermark-remover.git ~/.claude/skills/watermark-remover
```

2. 安装完成后，Skill 会自动在 Claude Code 中生效。

## 使用方法

直接用自然语言告诉 Claude Code：

```
去掉这张图片的水印：/path/to/image.jpg
```

```
我有一个文件夹的 Gemini 图片都有水印，帮我批量处理一下
```

```
Remove the watermark from this image
```

### 命令行使用

也可以直接使用脚本：

```bash
# 单张图片（原地修改）
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg

# 单张图片（保存为新文件）
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove input.jpg output.jpg

# 批量处理文件夹
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove ./input_folder/ ./output_folder/

# 强制指定水印大小
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg --force-small
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg --force-large
```

## 工作原理

Gemini 使用 Alpha 混合添加水印：

```
带水印图片 = alpha × 水印 + (1 - alpha) × 原图
```

本工具通过逆向公式还原原图：

```
原图 = (带水印图片 - alpha × 水印) / (1 - alpha)
```

### 水印尺寸检测规则

| 图片尺寸 | 水印大小 | 位置 |
|----------|----------|------|
| 宽 ≤ 1024 或 高 ≤ 1024 | 48×48 | 右下角，距边缘 32px |
| 宽 > 1024 且 高 > 1024 | 96×96 | 右下角，距边缘 64px |

## 使用限制

- **仅支持 Gemini**：本工具专为 Gemini AI 水印设计，无法去除其他 AI 平台的水印（如 MidJourney、DALL-E 等）
- **仅去除可见水印**：无法去除 SynthID 隐形水印（嵌入在图片生成过程中的数字水印）
- **固定位置**：只能去除右下角的水印

## 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip
- 依赖库：click、pillow、numpy

## 致谢

- 原始算法和掩码由 [Allen Kuo](https://github.com/allenk) 提供
- 基于 [GeminiWatermarkTool](https://github.com/allenk/GeminiWatermarkTool)（MIT 许可证）
- 技术文章：[Removing Gemini AI Watermarks: A Deep Dive into Reverse Alpha Blending](https://allenkuo.medium.com/removing-gemini-ai-watermarks-a-deep-dive-into-reverse-alpha-blending-bbbd83af2a3f)

## 许可证

MIT License
