# Gemini Watermark Remover Skill

[中文版](README_CN.md)

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that removes visible Gemini AI watermarks from images using reverse alpha blending.

## What is a Claude Code Skill?

Skills are reusable prompts and tools that extend Claude Code's capabilities. This skill enables Claude Code to automatically remove Gemini watermarks from your images through simple natural language commands.

## Features

- **Automatic Detection**: Detects watermark size based on image dimensions
- **Batch Processing**: Process entire directories at once
- **Multiple Formats**: Supports JPG, PNG, WebP, BMP
- **Non-destructive**: Option to save to new files while preserving originals

## Installation

1. Clone this repository to your Claude Code skills directory:

```bash
git clone https://github.com/mervinyx/agent-skill-gemini-watermark-remover.git ~/.claude/skills/watermark-remover
```

2. The skill will be automatically available in Claude Code.

## Usage

Simply ask Claude Code in natural language:

```
Remove the watermark from this image: /path/to/image.jpg
```

```
I have a folder of Gemini images with watermarks, please clean them all.
```

```
去掉这张图片的水印
```

### Command Line Usage

You can also use the script directly:

```bash
# Single image (in-place)
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg

# Single image (save to new file)
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove input.jpg output.jpg

# Batch process directory
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove ./input_folder/ ./output_folder/

# Force specific watermark size
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg --force-small
uv run ~/.claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg --force-large
```

## How It Works

Gemini adds watermarks using alpha blending:

```
watermarked = alpha × logo + (1 - alpha) × original
```

This tool reverses the equation to recover the original:

```
original = (watermarked - alpha × logo) / (1 - alpha)
```

### Watermark Size Detection

| Image Size | Watermark | Position |
|------------|-----------|----------|
| W ≤ 1024 OR H ≤ 1024 | 48×48 | Bottom-right, 32px margin |
| W > 1024 AND H > 1024 | 96×96 | Bottom-right, 64px margin |

## Limitations

- **Gemini Only**: This tool is specifically designed for Gemini AI watermarks. It will not work with watermarks from other AI platforms (MidJourney, DALL-E, etc.)
- **Visible Watermarks Only**: Does NOT remove SynthID invisible watermarks embedded during image generation
- **Fixed Position**: Only removes watermarks in the bottom-right corner

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Dependencies: click, pillow, numpy

## Credits

- Original algorithm and masks by [Allen Kuo](https://github.com/allenk)
- Based on [GeminiWatermarkTool](https://github.com/allenk/GeminiWatermarkTool) (MIT License)
- Technical write-up: [Removing Gemini AI Watermarks: A Deep Dive into Reverse Alpha Blending](https://allenkuo.medium.com/removing-gemini-ai-watermarks-a-deep-dive-into-reverse-alpha-blending-bbbd83af2a3f)

## License

MIT License
