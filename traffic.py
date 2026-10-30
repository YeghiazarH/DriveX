"""Randomly generated traffic cars and collision checks."""

import random

import pygame

from car_drawing import draw_car
from settings import (
    LANE_CENTERS,
    LANE_COUNT,
    HORIZON_Y,
    LOGICAL_HEIGHT,
    TRAFFIC_HEIGHT,
    TRAFFIC_RED,
    TRAFFIC_WIDTH,
    lane_center_at,
    vehicle_scale_at,
)


class TrafficCar:
    def __init__(self, lane, y, color):
        self.lane = lane
        self.x = LANE_CENTERS[lane]
        self.y = float(y)
        self.color = color
        self.near_miss_awarded = False
        self.width_scale, self.height_scale = random.choice(
            ((0.94, 0.88), (1.0, 1.0), (0.96, 1.1), (1.05, 0.96))
        )

    @property
    def rect(self):
        scale = vehicle_scale_at(self.y)
        car_width = TRAFFIC_WIDTH * scale * self.width_scale
        car_height = TRAFFIC_HEIGHT * scale * self.height_scale
        width = car_width * 0.78
        height = car_height * 0.9
        return pygame.Rect(
            round(lane_center_at(self.lane, self.y) - width / 2),
            round(self.y + (car_height - height) / 2),
            round(width),
            round(height),
        )

    def update(self, delta_time, player_speed):
        # Cars approach from ahead and move down the screen relative to the player.
        self.y += (145.0 + player_speed * 0.42) * delta_time

    def draw(self, surface):
        scale = vehicle_scale_at(self.y)
        draw_car(
            surface,
            lane_center_at(self.lane, self.y),
            self.y,
            TRAFFIC_WIDTH * scale * self.width_scale,
            TRAFFIC_HEIGHT * scale * self.height_scale,
            self.color,
        )


class Traffic:
    def __init__(self):
        self.cars = []
        self.spawn_timer = 0.9

    def reset(self):
        self.cars.clear()
        self.spawn_timer = 0.9

    def _spawn_car(self, lane):
        spawn_y = HORIZON_Y - TRAFFIC_HEIGHT * 0.05
        variations = (
            TRAFFIC_RED,
            (205, 93, 59),
            (57, 111, 157),
            (157, 174, 177),
            (194, 146, 57),
            (47, 126, 111),
            (122, 79, 104),
        )
        self.cars.append(TrafficCar(lane, spawn_y, random.choice(variations)))

    def _spawn_wave(self):
        spawn_y = HORIZON_Y - TRAFFIC_HEIGHT * 0.05
        occupied = {
            car.lane
            for car in self.cars
            if abs(car.y - spawn_y) < TRAFFIC_HEIGHT * 1.65
        }
        open_lanes = [lane for lane in range(LANE_COUNT) if lane not in occupied]
        if len(open_lanes) < 2:
            return

        car_count = 2 if len(open_lanes) == LANE_COUNT and random.random() < 0.78 else 1
        for lane in random.sample(open_lanes, car_count):
            self._spawn_car(lane)

    def update(self, delta_time, player_speed):
        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0:
            self._spawn_wave()
            relative_speed = 145.0 + player_speed * 0.42
            spacing = random.uniform(1.55, 1.85) * TRAFFIC_HEIGHT
            self.spawn_timer = spacing / relative_speed

        for car in self.cars:
            car.update(delta_time, player_speed)
        self.cars = [car for car in self.cars if car.y < LOGICAL_HEIGHT + 10]

    def collided_with(self, player_rect):
        return any(player_rect.colliderect(car.rect) for car in self.cars)

    def draw(self, surface):
        for car in self.cars:
            car.draw(surface)
