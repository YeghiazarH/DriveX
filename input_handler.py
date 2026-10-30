"""Mouse and touch swipe gestures mapped to game actions."""

from dataclasses import dataclass

import pygame

from settings import ACTION_BUTTON_RECT, LOGICAL_HEIGHT, LOGICAL_WIDTH


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

    @classmethod
    def fill(cls, window_size):
        window_width, window_height = window_size
        return cls(0, 0, window_width, window_height, window_width, window_height)

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
    SWIPE_THRESHOLD = LOGICAL_WIDTH * 0.04

    def __init__(self):
        self._start = None
        self._finger_id = None

    def reset(self):
        self._start = None
        self._finger_id = None

    def handle_event(self, event, viewport, game_state="playing"):
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
            return self._action(start, viewport.to_logical(event.pos), game_state)

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
            return self._action(start, viewport.to_logical(window_position), game_state)

        return None

    def _action(self, start, end, game_state):
        if start is None or end is None:
            return None

        delta_x = end[0] - start[0]
        delta_y = end[1] - start[1]
        if max(abs(delta_x), abs(delta_y)) < self.SWIPE_THRESHOLD:
            if (
                start[0] > LOGICAL_WIDTH * 0.79
                and start[1] < LOGICAL_HEIGHT * 0.13
            ):
                return "toggle_sound"
            if game_state in ("ready", "game_over"):
                button = pygame.Rect(
                    round(ACTION_BUTTON_RECT[0]),
                    round(ACTION_BUTTON_RECT[1]),
                    round(ACTION_BUTTON_RECT[2]),
                    round(ACTION_BUTTON_RECT[3]),
                )
                if button.collidepoint(start):
                    return "play" if game_state == "ready" else "restart"
                return None
            return None
        if game_state != "playing":
            return None
        if abs(delta_x) > abs(delta_y):
            return "left" if delta_x < 0 else "right"
        return "accelerate" if delta_y < 0 else "brake"
