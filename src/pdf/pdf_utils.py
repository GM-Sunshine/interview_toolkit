"""
PDF utility functions
"""


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    # Handle reportlab Color objects
    if hasattr(hex_color, 'red') and hasattr(hex_color, 'green') and hasattr(hex_color, 'blue'):
        return (hex_color.red, hex_color.green, hex_color.blue)
        
    # Handle string hex colors
    if isinstance(hex_color, str):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        
    # If neither, return a default color
    return (0, 0, 0)


def draw_smooth_gradient(
    canvas, x, y, width, height, start_color, end_color, direction="horizontal"
):
    """Draw a smooth gradient between two colors"""
    steps = 100
    if direction == "horizontal":
        for i in range(steps):
            r = start_color[0] + (end_color[0] - start_color[0]) * i / steps
            g = start_color[1] + (end_color[1] - start_color[1]) * i / steps
            b = start_color[2] + (end_color[2] - start_color[2]) * i / steps
            canvas.setFillColorRGB(r, g, b)
            canvas.rect(
                x + width * i / steps,
                y,
                width / steps + 1,
                height,
                fill=True,
                stroke=False,
            )
    else:  # vertical
        for i in range(steps):
            r = start_color[0] + (end_color[0] - start_color[0]) * i / steps
            g = start_color[1] + (end_color[1] - start_color[1]) * i / steps
            b = start_color[2] + (end_color[2] - start_color[2]) * i / steps
            canvas.setFillColorRGB(r, g, b)
            canvas.rect(
                x,
                y + height * i / steps,
                width,
                height / steps + 1,
                fill=True,
                stroke=False,
            )


def add_subtle_pattern(
    canvas, x, y, width, height, color, pattern_size=20, opacity=0.1
):
    """Add a subtle pattern to the background"""
    canvas.saveState()
    canvas.setFillColorRGB(*hex_to_rgb(color))
    canvas.setFillAlpha(opacity)

    for i in range(0, int(width), pattern_size):
        for j in range(0, int(height), pattern_size):
            if (i + j) % (pattern_size * 2) == 0:
                canvas.rect(
                    x + i,
                    y + j,
                    pattern_size / 2,
                    pattern_size / 2,
                    fill=True,
                    stroke=False,
                )

    canvas.restoreState()
