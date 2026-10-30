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
        collision_width = PLAYER_WIDTH * 0.78
        collision_height = PLAYER_HEIGHT * 0.9
        return pygame.Rect(
            round(self.x - collision_width / 2),
            round(PLAYER_Y + (PLAYER_HEIGHT - collision_height) / 2),
            round(collision_width),
            round(collision_height),
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

    def draw(self, surface, boosted=False, animation_time=0.0):
        if boosted:
            flicker = 0.85 + (int(animation_time * 24) % 4) * 0.05
            tip_y = PLAYER_Y + PLAYER_HEIGHT * flicker
            for offset, color in (
                (-PLAYER_WIDTH * 0.22, (48, 205, 255)),
                (PLAYER_WIDTH * 0.22, (48, 205, 255)),
                (0, (210, 249, 255)),
            ):
                tip = (round(self.x + offset), round(tip_y + PLAYER_HEIGHT * 0.11))
                base_y = round(PLAYER_Y + PLAYER_HEIGHT * 0.93)
                base_x = round(self.x + offset)
                half_width = round(PLAYER_WIDTH * (0.055 if offset else 0.07))
                pygame.draw.polygon(
                    surface,
                    color,
                    [
                        (base_x - half_width, base_y),
                        (base_x + half_width, base_y),
                        tip,
                    ],
                )
        draw_car(
            surface,
            self.x,
            PLAYER_Y,
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
            PLAYER_GREEN,
            player=True,
        )
