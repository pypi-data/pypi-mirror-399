"""Animated loading spinner widget."""

import random
import time
from typing import Any

from rich.text import Text
from textual.app import RenderResult
from textual.reactive import reactive
from textual.timer import Timer
from textual.widget import Widget

from miu_code.tui.theme import VIBE_COLORS, get_gradient_color

# Braille spinner frames
SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

# Fun loading messages (easter eggs)
LOADING_MESSAGES = [
    "Thinking",
    "Processing",
    "Analyzing",
    "Generating",
    "Computing",
    "Reasoning",
    "Pondering",
    "Crafting response",
    "Working on it",
    "Almost there",
]


class LoadingSpinner(Widget):
    """Animated loading spinner with color wave effect."""

    DEFAULT_CSS = """
    LoadingSpinner {
        height: 1;
        padding: 0 1;
    }
    """

    is_loading = reactive(False)
    _frame_index = reactive(0)
    _color_offset = reactive(0.0)
    _start_time: float = 0.0
    _message: str = "Thinking"
    _timer: Timer | None = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._message = random.choice(LOADING_MESSAGES)

    def start(self, message: str | None = None) -> None:
        """Start the loading animation."""
        self._message = message or random.choice(LOADING_MESSAGES)
        self._start_time = time.time()
        self.is_loading = True
        self._timer = self.set_interval(0.1, self._tick_animation)

    def stop(self) -> None:
        """Stop the loading animation."""
        self.is_loading = False
        if self._timer:
            self._timer.stop()
            self._timer = None

    def on_resize(self) -> None:
        """Refresh on resize to ensure proper layout."""
        self.refresh()

    def _tick_animation(self) -> None:
        """Animation tick."""
        if not self.is_loading:
            return
        self._frame_index = (self._frame_index + 1) % len(SPINNER_FRAMES)
        self._color_offset += 0.15

    def render(self) -> RenderResult:
        """Render the spinner with animated colors."""
        if not self.is_loading:
            return Text("")

        text = Text()

        # Spinner character
        spinner_char = SPINNER_FRAMES[self._frame_index]
        spinner_color = get_gradient_color(self._color_offset % 1.0)
        text.append(f" {spinner_char} ", style=f"bold {spinner_color}")

        # Loading message with color wave
        message = self._message + "..."
        for i, char in enumerate(message):
            char_offset = (self._color_offset + i * 0.1) % 1.0
            color = get_gradient_color(char_offset)
            text.append(char, style=color)

        # Elapsed time
        elapsed = time.time() - self._start_time
        elapsed_str = f" ({elapsed:.1f}s)"
        text.append(elapsed_str, style=f"dim {VIBE_COLORS['orange_gold']}")

        return text
