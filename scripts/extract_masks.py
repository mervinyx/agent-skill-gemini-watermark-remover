#!/usr/bin/env python3
"""Extract embedded PNG masks from GeminiWatermarkTool C++ header file."""

import re
import sys
from pathlib import Path


def extract_png_data(hpp_content: str, var_name: str) -> bytes:
    """Extract PNG byte array from C++ header content."""
    pattern = rf'{var_name}\[\]\s*=\s*\{{\s*([\s\S]*?)\}};'
    match = re.search(pattern, hpp_content)
    if not match:
        raise ValueError(f"Could not find {var_name} in header file")

    hex_str = match.group(1)
    hex_values = re.findall(r'0x([0-9a-fA-F]{2})', hex_str)
    return bytes(int(h, 16) for h in hex_values)


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_masks.py <path/to/embedded_assets.hpp>")
        print("Download from: https://github.com/allenk/GeminiWatermarkTool")
        sys.exit(1)
    hpp_path = Path(sys.argv[1])
    output_dir = Path(__file__).parent.parent / "assets"
    output_dir.mkdir(exist_ok=True)

    content = hpp_path.read_text()

    # Extract 48x48 mask
    bg_48_data = extract_png_data(content, "bg_48_png")
    (output_dir / "bg_48.png").write_bytes(bg_48_data)
    print(f"Extracted bg_48.png ({len(bg_48_data)} bytes)")

    # Extract 96x96 mask
    bg_96_data = extract_png_data(content, "bg_96_png")
    (output_dir / "bg_96.png").write_bytes(bg_96_data)
    print(f"Extracted bg_96.png ({len(bg_96_data)} bytes)")


if __name__ == "__main__":
    main()
