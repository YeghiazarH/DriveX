"""Player car state, movement, collision bounds, and primitive drawing."""

import pygame

from car_drawing import draw_car
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
        draw_car(
            surface,
            self.x,
            PLAYER_Y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
            PLAYER_GREEN,
            player=True,
        )
