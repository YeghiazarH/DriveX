"""A pursuing police cruiser that gains on the player over time."""

import pygame

from car_drawing import draw_car
from settings import (
    PLAYER_HEIGHT,
    PLAYER_Y,
    LOGICAL_WIDTH,
    TRAFFIC_HEIGHT,
    TRAFFIC_WIDTH,
    vehicle_scale_at,
)


class PoliceChase:
    def __init__(self):
        self.reset()

    def reset(self):
        self.gap = TRAFFIC_HEIGHT * 0.18
        self.elapsed = 0.0
        self.x = LOGICAL_WIDTH / 2
        self.target_lane = 1

    @property
    def y(self):
        return PLAYER_Y + PLAYER_HEIGHT + self.gap

    @property
    def rect(self):
        scale = vehicle_scale_at(self.y)
        return pygame.Rect(
            round(self.x - TRAFFIC_WIDTH * scale * 0.39),
            round(self.y + TRAFFIC_HEIGHT * scale * 0.05),
            round(TRAFFIC_WIDTH * scale * 0.78),
            round(TRAFFIC_HEIGHT * scale * 0.9),
        )

    def update(self, delta_time, player, boosting=False):
        self.elapsed += delta_time
        self.target_lane = player.lane
        target_x = player.x
        self.x += (target_x - self.x) * min(1.0, delta_time * 2.8)
        closing_speed = TRAFFIC_HEIGHT * (0.0045 + min(self.elapsed / 120, 0.003))
        if boosting:
            self.gap = min(
                TRAFFIC_HEIGHT * 1.8,
                self.gap + closing_speed * 1.7 * delta_time,
            )
        else:
            self.gap = max(0.0, self.gap - closing_speed * delta_time)

    def caught_player(self):
        return self.gap <= 0

    def draw(self, surface):
        # Alternate emergency lights independently from the game frame rate.
        phase = int(self.elapsed * 8) % 2
        scale = vehicle_scale_at(self.y)
        draw_car(
            surface,
            self.x,
            self.y,
            TRAFFIC_WIDTH * scale,
            TRAFFIC_HEIGHT * scale,
            (219, 225, 228),
            police=True,
            police_phase=phase,
        )
