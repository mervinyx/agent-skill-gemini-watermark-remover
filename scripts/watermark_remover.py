#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "click>=8.0",
#     "pillow>=10.0",
#     "numpy>=1.24",
# ]
# ///
"""
Gemini Watermark Remover

Remove visible Gemini AI watermarks from images using reverse alpha blending.
Based on GeminiWatermarkTool by Allen Kuo (https://github.com/allenk/GeminiWatermarkTool)

Algorithm:
  Gemini adds watermark: watermarked = alpha * logo + (1 - alpha) * original
  To remove: original = (watermarked - alpha * logo) / (1 - alpha)
"""

import sys
from pathlib import Path
from typing import Literal

import click
import numpy as np
from PIL import Image

ASSETS_DIR = Path(__file__).parent.parent / "assets"
BG_48_PATH = ASSETS_DIR / "bg_48.png"
BG_96_PATH = ASSETS_DIR / "bg_96.png"


def load_alpha_map(path: Path) -> np.ndarray:
    """Load background capture and convert to alpha map (0.0-1.0)."""
    img = Image.open(path).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    # Use max of RGB channels for brightness
    gray = np.max(arr, axis=2)
    return gray / 255.0


def get_watermark_config(width: int, height: int) -> tuple[int, int, Literal["small", "large"]]:
    """
    Get watermark configuration based on image dimensions.

    Returns: (margin, logo_size, size_name)

    Rules from Gemini:
    - Large (96x96, 64px margin): BOTH width AND height > 1024
    - Small (48x48, 32px margin): Otherwise
    """
    if width > 1024 and height > 1024:
        return 64, 96, "large"
    return 32, 48, "small"


def remove_watermark(
    image: np.ndarray,
    alpha_map: np.ndarray,
    position: tuple[int, int],
    logo_value: float = 255.0,
) -> np.ndarray:
    """
    Remove watermark using reverse alpha blending.

    Formula: original = (watermarked - alpha * logo) / (1 - alpha)
    """
    result = image.copy().astype(np.float32)
    x, y = position
    h, w = alpha_map.shape

    # Clip to image bounds
    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(image.shape[1], x + w)
    y2 = min(image.shape[0], y + h)

    if x1 >= x2 or y1 >= y2:
        return image

    # Get ROIs
    alpha_roi = alpha_map[y1 - y:y2 - y, x1 - x:x2 - x]
    image_roi = result[y1:y2, x1:x2]

    # Thresholds
    alpha_threshold = 0.002
    max_alpha = 0.99

    # Apply reverse alpha blending
    for row in range(alpha_roi.shape[0]):
        for col in range(alpha_roi.shape[1]):
            alpha = alpha_roi[row, col]
            if alpha < alpha_threshold:
                continue
            alpha = min(alpha, max_alpha)
            one_minus_alpha = 1.0 - alpha
            for c in range(3):
                watermarked = image_roi[row, col, c]
                original = (watermarked - alpha * logo_value) / one_minus_alpha
                image_roi[row, col, c] = np.clip(original, 0, 255)

    return result.astype(np.uint8)


def process_image(
    input_path: Path,
    output_path: Path,
    force_size: str | None = None,
    verbose: bool = False,
) -> bool:
    """Process a single image to remove watermark."""
    try:
        img = Image.open(input_path).convert("RGB")
        width, height = img.size

        # Determine watermark size
        if force_size == "small":
            margin, logo_size, size_name = 32, 48, "small"
        elif force_size == "large":
            margin, logo_size, size_name = 64, 96, "large"
        else:
            margin, logo_size, size_name = get_watermark_config(width, height)

        # Load appropriate alpha map
        alpha_path = BG_48_PATH if size_name == "small" else BG_96_PATH
        if not alpha_path.exists():
            click.echo(f"Error: Alpha map not found: {alpha_path}", err=True)
            return False

        alpha_map = load_alpha_map(alpha_path)

        # Calculate watermark position (bottom-right corner)
        pos_x = width - margin - logo_size
        pos_y = height - margin - logo_size

        if verbose:
            click.echo(f"Processing: {input_path.name} ({width}x{height})")
            click.echo(f"  Watermark: {size_name} ({logo_size}x{logo_size}) at ({pos_x}, {pos_y})")

        # Remove watermark
        img_array = np.array(img)
        result = remove_watermark(img_array, alpha_map, (pos_x, pos_y))

        # Save result
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_img = Image.fromarray(result)

        # Determine quality settings based on format
        ext = output_path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            result_img.save(output_path, quality=100)
        elif ext == ".png":
            result_img.save(output_path, compress_level=6)
        elif ext == ".webp":
            result_img.save(output_path, lossless=True)
        else:
            result_img.save(output_path)

        if verbose:
            click.echo(f"  Saved: {output_path}")
        return True

    except Exception as e:
        click.echo(f"Error processing {input_path}: {e}", err=True)
        return False


@click.group()
def cli():
    """Gemini Watermark Remover - Remove visible AI watermarks from images."""
    pass


@cli.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_path", type=click.Path(path_type=Path), required=False)
@click.option("--force-small", is_flag=True, help="Force 48x48 watermark size")
@click.option("--force-large", is_flag=True, help="Force 96x96 watermark size")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
def remove(
    input_path: Path,
    output_path: Path | None,
    force_small: bool,
    force_large: bool,
    verbose: bool,
):
    """Remove watermark from an image or directory of images."""
    force_size = "small" if force_small else ("large" if force_large else None)

    if input_path.is_dir():
        # Batch processing
        if output_path is None:
            click.echo("Error: Output directory required for batch processing", err=True)
            sys.exit(1)

        output_path.mkdir(parents=True, exist_ok=True)
        extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
        files = [f for f in input_path.iterdir() if f.suffix.lower() in extensions]

        success = 0
        for f in files:
            out_file = output_path / f.name
            if process_image(f, out_file, force_size, verbose):
                success += 1

        click.echo(f"Processed {success}/{len(files)} images")
    else:
        # Single file
        if output_path is None:
            # In-place editing
            output_path = input_path

        if process_image(input_path, output_path, force_size, verbose):
            click.echo(f"Done: {output_path}")
        else:
            sys.exit(1)


@cli.command()
def info():
    """Show information about the tool."""
    click.echo("Gemini Watermark Remover")
    click.echo("========================")
    click.echo()
    click.echo("Based on GeminiWatermarkTool by Allen Kuo")
    click.echo("https://github.com/allenk/GeminiWatermarkTool")
    click.echo()
    click.echo("This tool removes VISIBLE Gemini watermarks only.")
    click.echo("It does NOT remove SynthID (invisible watermarks).")
    click.echo()
    click.echo("Watermark detection rules:")
    click.echo("  - Small (48x48): Image width OR height <= 1024")
    click.echo("  - Large (96x96): Image width AND height > 1024")
    click.echo()
    click.echo(f"Assets directory: {ASSETS_DIR}")
    click.echo(f"  bg_48.png: {'exists' if BG_48_PATH.exists() else 'MISSING'}")
    click.echo(f"  bg_96.png: {'exists' if BG_96_PATH.exists() else 'MISSING'}")


if __name__ == "__main__":
    cli()
