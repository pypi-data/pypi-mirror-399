"""Miu brand theme colors and utilities."""

# Miu brand palette (teal -> cyan gradient)
MIU_COLORS = {
    "primary": "#1ABC9C",  # teal
    "primary_light": "#48C9B0",  # light teal
    "secondary": "#16A085",  # dark teal
    "accent": "#0E6655",  # deep teal
    "highlight": "#76D7C4",  # bright cyan
}

# Gradient sequence for animations
GRADIENT_SEQUENCE = [
    "#76D7C4",  # bright cyan
    "#48C9B0",  # light teal
    "#1ABC9C",  # teal
    "#16A085",  # dark teal
    "#0E6655",  # deep teal
]

# Semantic colors
SEMANTIC_COLORS = {
    "user": "#3498DB",  # blue for user
    "assistant": "#1ABC9C",  # teal for agent
    "system": "#7F8C8D",  # gray for system
    "error": "#E74C3C",  # red for errors
    "accent": "#1ABC9C",  # teal accent
    "thinking": "#48C9B0",  # light teal for thinking
}

# Alias for backward compatibility
VIBE_COLORS = {
    "gold": "#76D7C4",  # remapped to bright cyan
    "orange_gold": "#48C9B0",  # light teal
    "orange": "#1ABC9C",  # teal
    "orange_red": "#16A085",  # dark teal
    "red": "#0E6655",  # deep teal
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color."""
    return f"#{r:02x}{g:02x}{b:02x}"


def interpolate_color(color1: str, color2: str, t: float) -> str:
    """Interpolate between two hex colors. t: 0.0 to 1.0."""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)

    return rgb_to_hex(r, g, b)


def get_gradient_color(progress: float) -> str:
    """Get color from gradient based on progress (0.0 to 1.0)."""
    if progress <= 0:
        return GRADIENT_SEQUENCE[0]
    if progress >= 1:
        return GRADIENT_SEQUENCE[-1]

    # Calculate position in gradient
    segment_count = len(GRADIENT_SEQUENCE) - 1
    segment = int(progress * segment_count)
    segment = min(segment, segment_count - 1)

    local_progress = (progress * segment_count) - segment

    return interpolate_color(
        GRADIENT_SEQUENCE[segment], GRADIENT_SEQUENCE[segment + 1], local_progress
    )
