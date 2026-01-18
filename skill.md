---
name: Watermark Remover
description: Remove visible Gemini AI watermarks from images using reverse alpha blending. Use when user mentions "remove watermark", "Gemini watermark", "去水印", or wants to clean AI-generated images.
---

# Watermark Remover

## Instructions

This skill removes visible Gemini AI watermarks from images using mathematically accurate reverse alpha blending. It is based on [GeminiWatermarkTool](https://github.com/allenk/GeminiWatermarkTool) by Allen Kuo.

### Important Notes

- This tool removes **VISIBLE watermarks only** (the semi-transparent logo in bottom-right corner)
- It does **NOT** remove **SynthID invisible watermarks** - those are embedded during image generation and cannot be separated from the image
- Best results on: slides, documents, UI screenshots, diagrams, logos, text-heavy images
- Always backup original images before processing

### How It Works

Gemini adds watermarks using alpha blending:
```
watermarked = alpha × logo + (1 - alpha) × original
```

This tool reverses the equation:
```
original = (watermarked - alpha × logo) / (1 - alpha)
```

### Watermark Size Detection

The tool automatically detects watermark size based on image dimensions:

| Image Size | Watermark | Position |
|------------|-----------|----------|
| W ≤ 1024 OR H ≤ 1024 | 48×48 | Bottom-right, 32px margin |
| W > 1024 AND H > 1024 | 96×96 | Bottom-right, 64px margin |

### Usage

#### Remove watermark from a single image (in-place):

```bash
uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg
```

#### Remove watermark and save to new file:

```bash
uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove input.jpg output.jpg
```

#### Batch process a directory:

```bash
uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove ./input_folder/ ./output_folder/
```

#### Force specific watermark size:

```bash
# Force small (48x48) watermark
uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg --force-small

# Force large (96x96) watermark
uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg --force-large
```

#### Verbose output:

```bash
uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove image.jpg -v
```

#### Show tool information:

```bash
uv run .claude/skills/watermark-remover/scripts/watermark_remover.py info
```

### Supported Formats

- Input: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`
- Output: Same as input format (preserves quality settings)

## Examples

### Example 1: Quick Watermark Removal

User request:
```
I have a Gemini-generated image with a watermark. Can you remove it?
```

You would:
1. Ask for the image path
2. Run the removal command:
   ```bash
   uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove /path/to/image.jpg -v
   ```
3. Confirm the watermark was removed

### Example 2: Batch Processing

User request:
```
I have a folder of AI-generated images that all have watermarks. Can you clean them?
```

You would:
1. Process the entire directory:
   ```bash
   uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove ./gemini_images/ ./cleaned_images/ -v
   ```
2. Report how many images were processed

### Example 3: Preserve Original

User request:
```
Remove the watermark but keep my original file intact.
```

You would:
1. Specify a different output path:
   ```bash
   uv run .claude/skills/watermark-remover/scripts/watermark_remover.py remove original.png cleaned.png -v
   ```

## Troubleshooting

### "The image doesn't look different after processing"

The watermark is semi-transparent. If the original background was similar to the watermark color (white), the difference may be subtle. Try viewing at 100% zoom in the watermark area (bottom-right corner).

### "Wrong watermark size detected"

Use `--force-small` or `--force-large` to manually specify the watermark size.

### "Alpha map not found"

The skill requires alpha mask files in the `assets/` directory. If missing, run:
```bash
python3 .claude/skills/watermark-remover/scripts/extract_masks.py /path/to/GeminiWatermarkTool/assets/embedded_assets.hpp
```

## Credits

- Original algorithm and masks by [Allen Kuo](https://github.com/allenk)
- Based on [GeminiWatermarkTool](https://github.com/allenk/GeminiWatermarkTool) (MIT License)
- Technical write-up: [Removing Gemini AI Watermarks: A Deep Dive into Reverse Alpha Blending](https://allenkuo.medium.com/removing-gemini-ai-watermarks-a-deep-dive-into-reverse-alpha-blending-bbbd83af2a3f)
