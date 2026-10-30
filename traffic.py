"""Randomly generated traffic cars and collision checks."""

import random

import pygame

from car_drawing import draw_car
from settings import (
    LANE_CENTERS,
    LANE_COUNT,
    HORIZON_Y,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
    ROAD_LEFT,
    ROAD_RIGHT,
    TRAFFIC_HEIGHT,
    TRAFFIC_RED,
    TRAFFIC_WIDTH,
)


class TrafficCar:
    def __init__(self, lane, y, color):
        self.lane = lane
        self.x = LANE_CENTERS[lane]
        self.y = float(y)
        self.color = color

    @property
    def rect(self):
        x = lane_center_at(self.lane, self.y)
        return pygame.Rect(
            round(x - TRAFFIC_WIDTH / 2),
            round(self.y),
            TRAFFIC_WIDTH,
            TRAFFIC_HEIGHT,
        )

    def update(self, delta_time, player_speed):
        # Cars approach from ahead and move down the screen relative to the player.
        self.y += (115.0 + player_speed * 0.34) * delta_time

    def draw(self, surface):
        draw_car(
            surface,
            lane_center_at(self.lane, self.y),
            self.y,
            TRAFFIC_WIDTH,
            TRAFFIC_HEIGHT,
            self.color,
        )


class Traffic:
    def __init__(self):
        self.cars = []
        self.spawn_timer = 0.6

    def reset(self):
        self.cars.clear()
        self.spawn_timer = 0.6

    def _spawn_car(self):
        open_lanes = [
            lane for lane in range(LANE_COUNT)
            if all(car.lane != lane or car.y > 150 for car in self.cars)
        ]
        if not open_lanes:
            return
        lane = random.choice(open_lanes)
        variations = (
            TRAFFIC_RED,
            (220, 91, 52),
            (190, 62, 79),
            (205, 72, 55),
        )
        self.cars.append(TrafficCar(lane, -TRAFFIC_HEIGHT, random.choice(variations)))

    def update(self, delta_time, player_speed):
        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0:
            self._spawn_car()
            self.spawn_timer = random.uniform(0.7, 1.15)

        for car in self.cars:
            car.update(delta_time, player_speed)
        self.cars = [car for car in self.cars if car.y < LOGICAL_HEIGHT + 10]

    def collided_with(self, player_rect):
        return any(player_rect.colliderect(car.rect) for car in self.cars)

    def draw(self, surface):
        for car in self.cars:
            car.draw(surface)


def lane_center_at(lane, y):
    road_progress = max(
        0.0, min(1.0, (y - HORIZON_Y) / (LOGICAL_HEIGHT - HORIZON_Y))
    )
    road_width = (ROAD_RIGHT - ROAD_LEFT) * (0.66 + road_progress * 0.34)
    left = LOGICAL_WIDTH / 2 - road_width / 2
    return left + road_width * (lane + 0.5) / LANE_COUNT
