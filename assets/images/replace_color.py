#!/usr/bin/env python3
"""
replace_color_range.py

Replace pixels whose RGB values are within a given delta of an old color.

Works with PNG, JPG, JPEG, WEBP, etc.
Output is always written as PNG.

Usage:
    python replace_color_range.py input.jpg output.png "#f3f4f7" "#d7e9ff" --delta 8

Color formats:
    "#f3f4f7"
    "243,244,247"
    "243,244,247,255"

Delta means per-channel RGB tolerance.

Example:
    old = 243,244,247
    delta = 8

A pixel matches if:

    abs(R - 243) <= 8
    abs(G - 244) <= 8
    abs(B - 247) <= 8
"""

import argparse
from pathlib import Path

from PIL import Image


def parse_color(s: str) -> tuple[int, ...]:
    s = s.strip()

    if s.startswith("#"):
        h = s[1:]

        if len(h) == 6:
            return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))

        if len(h) == 8:
            return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4, 6))

        raise ValueError("Hex colors must be #RRGGBB or #RRGGBBAA")

    parts = tuple(int(x.strip()) for x in s.split(","))

    if len(parts) not in (3, 4):
        raise ValueError("Colors must be R,G,B or R,G,B,A")

    if any(p < 0 or p > 255 for p in parts):
        raise ValueError("Color channel values must be between 0 and 255")

    return parts


def to_rgba(color: tuple[int, ...]) -> tuple[int, int, int, int]:
    if len(color) == 3:
        r, g, b = color
        return r, g, b, 255

    r, g, b, a = color
    return r, g, b, a


def rgb_within_delta(
    pixel: tuple[int, int, int, int],
    target: tuple[int, int, int, int],
    delta: int,
) -> bool:
    return (
        abs(pixel[0] - target[0]) <= delta
        and abs(pixel[1] - target[1]) <= delta
        and abs(pixel[2] - target[2]) <= delta
    )


def ensure_png_output_path(output_path: str) -> Path:
    path = Path(output_path)

    if path.suffix.lower() != ".png":
        path = path.with_suffix(".png")

    return path


def replace_color_range(
    input_path: str,
    output_path: str,
    old_color: tuple[int, ...],
    new_color: tuple[int, ...],
    delta: int,
) -> None:
    if delta < 0 or delta > 255:
        raise ValueError("--delta must be between 0 and 255")

    old_rgba = to_rgba(old_color)
    new_rgba = to_rgba(new_color)

    output_png_path = ensure_png_output_path(output_path)

    img = Image.open(input_path).convert("RGBA")
    pixels = img.load()

    width, height = img.size
    replaced = 0

    for y in range(height):
        for x in range(width):
            current = pixels[x, y]

            if rgb_within_delta(current, old_rgba, delta):
                # Preserve original alpha unless the replacement explicitly included alpha.
                if len(new_color) == 3:
                    pixels[x, y] = (new_rgba[0], new_rgba[1], new_rgba[2], current[3])
                else:
                    pixels[x, y] = new_rgba

                replaced += 1

    img.save(output_png_path, format="PNG")

    print(f"Saved: {output_png_path}")
    print(f"Replaced pixels: {replaced}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace pixels within an RGB delta range and save as PNG."
    )

    parser.add_argument("input", help="Input image path, e.g. input.png or input.jpg")
    parser.add_argument("output", help="Output PNG path, e.g. output.png")
    parser.add_argument("old_color", help='Color to replace, e.g. "#f3f4f7" or "243,244,247"')
    parser.add_argument("new_color", help='Replacement color, e.g. "#d7e9ff" or "215,233,255"')
    parser.add_argument(
        "--delta",
        type=int,
        default=0,
        help="Per-channel RGB tolerance. Default: 0",
    )

    args = parser.parse_args()

    old_color = parse_color(args.old_color)
    new_color = parse_color(args.new_color)

    replace_color_range(
        input_path=args.input,
        output_path=args.output,
        old_color=old_color,
        new_color=new_color,
        delta=args.delta,
    )


if __name__ == "__main__":
    main()
