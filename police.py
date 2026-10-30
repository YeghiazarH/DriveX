"""A pursuing police cruiser that gains on the player over time."""

import pygame

from car_drawing import draw_car
from settings import (
    PLAYER_HEIGHT,
    PLAYER_Y,
    ROAD_LEFT,
    ROAD_RIGHT,
    TRAFFIC_HEIGHT,
    TRAFFIC_WIDTH,
)


class PoliceChase:
    def __init__(self):
        self.reset()

    def reset(self):
        self.gap = TRAFFIC_HEIGHT * 0.62
        self.elapsed = 0.0
        self.x = (ROAD_LEFT + ROAD_RIGHT) / 2
        self.target_lane = 1

    @property
    def y(self):
        return PLAYER_Y + PLAYER_HEIGHT + self.gap

    @property
    def rect(self):
        return pygame.Rect(
            round(self.x - TRAFFIC_WIDTH / 2),
            round(self.y),
            round(TRAFFIC_WIDTH),
            round(TRAFFIC_HEIGHT),
        )

    def update(self, delta_time, player):
        self.elapsed += delta_time
        self.target_lane = player.lane
        target_x = player.x
        self.x += (target_x - self.x) * min(1.0, delta_time * 2.8)
        closing_speed = TRAFFIC_HEIGHT * (0.008 + min(self.elapsed / 120, 0.006))
        self.gap = max(0.0, self.gap - closing_speed * delta_time)

    def caught_player(self):
        return self.gap <= TRAFFIC_HEIGHT * 0.1

    def draw(self, surface):
        # Alternate emergency lights independently from the game frame rate.
        phase = int(self.elapsed * 8) % 2
        blue, red = (45, 122, 255), (255, 54, 53)
        draw_car(
            surface,
            self.x,
            self.y,
            TRAFFIC_WIDTH,
            TRAFFIC_HEIGHT,
            (219, 225, 228),
        )
        center_y = round(self.y + TRAFFIC_HEIGHT * 0.23)
        bar_width = TRAFFIC_WIDTH * 0.34
        bar_height = max(5, round(TRAFFIC_HEIGHT * 0.035))
        left_color, right_color = (blue, red) if phase == 0 else (red, blue)
        pygame.draw.rect(
            surface,
            left_color,
            (
                round(self.x - bar_width),
                center_y,
                round(bar_width),
                bar_height,
            ),
            border_radius=bar_height // 2,
        )
        pygame.draw.rect(
            surface,
            right_color,
            (
                round(self.x),
                center_y,
                round(bar_width),
                bar_height,
            ),
            border_radius=bar_height // 2,
        )
