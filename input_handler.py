"""Mouse and touch swipe gestures mapped to game actions."""

from dataclasses import dataclass

import pygame

from settings import LOGICAL_HEIGHT, LOGICAL_WIDTH


@dataclass(frozen=True)
class Viewport:
    """The centered, aspect-preserving area where the logical game is drawn."""

    x: float
    y: float
    width: float
    height: float
    window_width: int
    window_height: int

    @classmethod
    def fit(cls, window_size):
        window_width, window_height = window_size
        scale = min(
            window_width / LOGICAL_WIDTH,
            window_height / LOGICAL_HEIGHT,
        )
        width = LOGICAL_WIDTH * scale
        height = LOGICAL_HEIGHT * scale
        return cls(
            (window_width - width) / 2,
            (window_height - height) / 2,
            width,
            height,
            window_width,
            window_height,
        )

    def to_logical(self, position):
        x, y = position
        if (
            self.width <= 0
            or self.height <= 0
            or x < self.x
            or y < self.y
            or x > self.x + self.width
            or y > self.y + self.height
        ):
            return None
        return (
            (x - self.x) * LOGICAL_WIDTH / self.width,
            (y - self.y) * LOGICAL_HEIGHT / self.height,
        )


class InputHandler:
    SWIPE_THRESHOLD = 28

    def __init__(self):
        self._start = None
        self._finger_id = None

    def reset(self):
        self._start = None
        self._finger_id = None

    def handle_event(self, event, viewport, game_over=False):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # SDL may emit both finger and synthetic mouse events for one touch.
            if getattr(event, "touch", False):
                return None
            self._start = viewport.to_logical(event.pos)
            self._finger_id = None
            return None

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if getattr(event, "touch", False):
                return None
            start = self._start
            self.reset()
            return self._action(start, viewport.to_logical(event.pos), game_over)

        if event.type == pygame.FINGERDOWN:
            self._start = viewport.to_logical(
                (event.x * viewport.window_width, event.y * viewport.window_height)
            )
            self._finger_id = event.finger_id
            return None

        if event.type == pygame.FINGERUP:
            if self._finger_id != event.finger_id:
                return None
            start = self._start
            self.reset()
            window_position = (
                event.x * viewport.window_width,
                event.y * viewport.window_height,
            )
            return self._action(start, viewport.to_logical(window_position), game_over)

        return None

    def _action(self, start, end, game_over):
        if start is None or end is None:
            return None
        if game_over:
            return "restart"

        delta_x = end[0] - start[0]
        delta_y = end[1] - start[1]
        if max(abs(delta_x), abs(delta_y)) < self.SWIPE_THRESHOLD:
            return None
        if abs(delta_x) > abs(delta_y):
            return "left" if delta_x < 0 else "right"
        return "accelerate" if delta_y < 0 else "brake"
