"""A pursuing police cruiser that gains on the player over time."""

import math
import random

import pygame

from car_drawing import draw_car
from settings import (
    LANE_CENTERS,
    PLAYER_HEIGHT,
    PLAYER_Y,
    LOGICAL_WIDTH,
    START_SPEED,
    TRAFFIC_HEIGHT,
    TRAFFIC_WIDTH,
    vehicle_scale_at,
)


class PoliceChase:
    def __init__(self):
        self.reset()

    def reset(self):
        self.gap = TRAFFIC_HEIGHT * 0.32
        self.elapsed = 0.0
        self.x = LOGICAL_WIDTH / 2
        self.lane = 1
        self.target_lane = 1
        self.lane_change_timer = 0.8
        self.speed = START_SPEED

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
        self.lane_change_timer -= delta_time
        if self.lane_change_timer <= 0:
            if self.target_lane != player.lane:
                self.target_lane += 1 if player.lane > self.target_lane else -1
            elif random.random() < 0.42:
                options = [lane for lane in range(len(LANE_CENTERS)) if lane != self.target_lane]
                self.target_lane = random.choice(options)
            self.lane_change_timer = random.uniform(0.9, 1.7)

        gap_ratio = self.gap / TRAFFIC_HEIGHT
        chase_pressure = 0.18 if gap_ratio > 0.85 else -0.12 if gap_ratio < 0.4 else 0.0
        speed_wave = math.sin(self.elapsed * 1.35) * 0.09
        speed_factor = max(0.72, min(1.32, 1.0 + chase_pressure + speed_wave))
        if boosting:
            speed_factor = min(speed_factor, 0.86)
        target_speed = player.speed * speed_factor
        self.speed += (target_speed - self.speed) * min(1.0, delta_time * 2.2)

        target_x = LANE_CENTERS[self.target_lane]
        steering_rate = 2.8 + min(self.speed / max(player.speed, 1.0), 1.5)
        self.x += (target_x - self.x) * min(1.0, delta_time * steering_rate)
        if abs(target_x - self.x) < TRAFFIC_WIDTH * 0.08:
            self.lane = self.target_lane

        closing_speed = TRAFFIC_HEIGHT * (0.0075 + min(self.elapsed / 120, 0.004))
        if boosting:
            self.gap = min(
                TRAFFIC_HEIGHT * 1.8,
                self.gap + closing_speed * 1.6 * delta_time,
            )
        else:
            self.gap = max(
                0.0,
                self.gap - closing_speed * max(0.35, self.speed / max(player.speed, 1.0)) * delta_time,
            )

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
