"""
Icon Generator Script

Generates icon.ico from icon.svg for use in the application and executable.
Run this script once before building the executable.

Requirements:
    pip install cairosvg pillow

Usage:
    python generate_icon.py
"""

import os
import sys

def generate_icon():
    """Generate ICO file from SVG"""
    try:
        from cairosvg import svg2png
        from PIL import Image
        from io import BytesIO
    except ImportError as e:
        print("Missing dependencies. Please install them with:")
        print("    pip install cairosvg pillow")
        print(f"\nError: {e}")
        return False

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    svg_path = os.path.join(script_dir, "assets", "icon.svg")
    ico_path = os.path.join(script_dir, "assets", "icon.ico")

    if not os.path.exists(svg_path):
        print(f"Error: SVG file not found at {svg_path}")
        return False

    print(f"Reading SVG from: {svg_path}")

    # Icon sizes for ICO file (Windows standard sizes)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        print(f"  Generating {size}x{size} icon...")
        # Convert SVG to PNG at specified size
        png_data = svg2png(url=svg_path, output_width=size, output_height=size)
        # Open as PIL Image
        img = Image.open(BytesIO(png_data))
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        images.append(img)

    # Save as ICO with all sizes
    print(f"\nSaving ICO to: {ico_path}")
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )

    print("\nIcon generated successfully!")
    print(f"  File: {ico_path}")
    print(f"  Sizes: {', '.join(f'{s}x{s}' for s in sizes)}")

    return True


def generate_icon_fallback():
    """
    Fallback icon generator using only Pillow (no SVG support).
    Creates a simple programmatic icon if cairosvg is not available.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow is required. Install with: pip install pillow")
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    ico_path = os.path.join(script_dir, "assets", "icon.ico")

    print("Using fallback icon generator (no SVG support)...")
    print("For best results, install cairosvg: pip install cairosvg")

    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        print(f"  Generating {size}x{size} icon...")
        # Create image with gradient-like background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Background rounded rectangle (approximated with ellipses at corners)
        padding = max(1, size // 16)
        bg_color = (33, 150, 243, 255)  # #2196F3

        # Draw rounded rectangle background
        radius = size // 8
        draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=radius,
            fill=bg_color
        )

        # Draw two document shapes
        doc_width = size // 4
        doc_height = size // 3
        doc_color = (255, 255, 255, 230)

        # Left document
        left_x = size // 4 - doc_width // 2
        doc_y = size // 4
        draw.rounded_rectangle(
            [left_x, doc_y, left_x + doc_width, doc_y + doc_height],
            radius=max(1, size // 32),
            fill=doc_color
        )

        # Right document
        right_x = 3 * size // 4 - doc_width // 2
        draw.rounded_rectangle(
            [right_x, doc_y, right_x + doc_width, doc_y + doc_height],
            radius=max(1, size // 32),
            fill=doc_color
        )

        # Plus sign in the middle (for merge concept)
        plus_color = (255, 213, 79, 255)  # #FFD54F
        plus_size = max(2, size // 8)
        plus_thickness = max(1, size // 24)
        center_x, center_y = size // 2, size // 3

        # Horizontal bar
        draw.rectangle(
            [center_x - plus_size, center_y - plus_thickness // 2,
             center_x + plus_size, center_y + plus_thickness // 2],
            fill=plus_color
        )
        # Vertical bar
        draw.rectangle(
            [center_x - plus_thickness // 2, center_y - plus_size,
             center_x + plus_thickness // 2, center_y + plus_size],
            fill=plus_color
        )

        # Stitch pattern at bottom
        stitch_y = 2 * size // 3
        stitch_color = (255, 255, 255, 200)
        line_width = max(1, size // 32)

        for i in range(-2, 3):
            x1 = size // 2 + i * (size // 8) - size // 16
            x2 = x1 + size // 8
            y1 = stitch_y if i % 2 == 0 else stitch_y + size // 12
            y2 = stitch_y + size // 12 if i % 2 == 0 else stitch_y
            if 0 < x1 < size and 0 < x2 < size:
                draw.line([(x1, y1), (x2, y2)], fill=stitch_color, width=line_width)

        images.append(img)

    # Save as ICO
    print(f"\nSaving ICO to: {ico_path}")
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )

    print("\nFallback icon generated successfully!")
    return True


if __name__ == "__main__":
    # Ensure assets directory exists
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Try SVG-based generation first, fall back to programmatic
    success = generate_icon()
    if not success:
        print("\n" + "="*50)
        print("Falling back to programmatic icon generation...")
        print("="*50 + "\n")
        success = generate_icon_fallback()

    sys.exit(0 if success else 1)
