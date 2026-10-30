"""Player car state, movement, collision bounds, and primitive drawing."""

import pygame

from settings import (
    ACCELERATION_STEP,
    BRAKE_STEP,
    LANE_CENTERS,
    MAX_SPEED,
    MIN_SPEED,
    PLAYER_GREEN,
    PLAYER_HEIGHT,
    PLAYER_WIDTH,
    PLAYER_Y,
    START_SPEED,
)


class Player:
    def __init__(self):
        self.reset()

    def reset(self):
        self.lane = 1
        self.x = LANE_CENTERS[self.lane]
        self.speed = START_SPEED

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x - PLAYER_WIDTH / 2),
            PLAYER_Y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )

    def change_lane(self, direction):
        self.lane = max(0, min(len(LANE_CENTERS) - 1, self.lane + direction))

    def accelerate(self):
        self.speed = min(MAX_SPEED, self.speed + ACCELERATION_STEP)

    def brake(self):
        self.speed = max(MIN_SPEED, self.speed - BRAKE_STEP)

    def update(self, delta_time):
        target_x = LANE_CENTERS[self.lane]
        # Smoothly move to the selected lane rather than teleporting sideways.
        blend = min(1.0, delta_time * 12.0)
        self.x += (target_x - self.x) * blend

    def draw(self, surface):
        body = self.rect
        pygame.draw.rect(surface, PLAYER_GREEN, body, border_radius=9)
        pygame.draw.rect(surface, (20, 110, 58), body, width=2, border_radius=9)
        pygame.draw.rect(
            surface,
            (180, 226, 232),
            (body.x + 7, body.y + 13, body.width - 14, 17),
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            (32, 127, 79),
            (body.x + 8, body.y + 39, body.width - 16, 15),
            border_radius=4,
        )
        for wheel_y in (body.y + 12, body.bottom - 20):
            pygame.draw.rect(
                surface,
                (25, 28, 31),
                (body.left - 3, wheel_y, 6, 14),
                border_radius=2,
            )
            pygame.draw.rect(
                surface,
                (25, 28, 31),
                (body.right - 3, wheel_y, 6, 14),
                border_radius=2,
            )
        pygame.draw.rect(
            surface,
            (255, 235, 153),
            (body.x + 5, body.y + 3, 9, 4),
            border_radius=2,
        )
        pygame.draw.rect(
            surface,
            (255, 235, 153),
            (body.right - 14, body.y + 3, 9, 4),
            border_radius=2,
        )
