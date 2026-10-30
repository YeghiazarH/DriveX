"""Randomly generated traffic cars and collision checks."""

import random

import pygame

from settings import (
    LANE_CENTERS,
    LOGICAL_HEIGHT,
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
        return pygame.Rect(
            round(self.x - TRAFFIC_WIDTH / 2),
            round(self.y),
            TRAFFIC_WIDTH,
            TRAFFIC_HEIGHT,
        )

    def update(self, delta_time, player_speed):
        # Cars approach from ahead and move down the screen relative to the player.
        self.y += (115.0 + player_speed * 0.34) * delta_time

    def draw(self, surface):
        body = self.rect
        pygame.draw.rect(surface, self.color, body, border_radius=8)
        pygame.draw.rect(surface, (112, 37, 39), body, width=2, border_radius=8)
        pygame.draw.rect(
            surface,
            (177, 220, 226),
            (body.x + 7, body.y + 12, body.width - 14, 17),
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            (137, 45, 47),
            (body.x + 8, body.y + 42, body.width - 16, 14),
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


class Traffic:
    def __init__(self):
        self.cars = []
        self.spawn_timer = 0.6

    def reset(self):
        self.cars.clear()
        self.spawn_timer = 0.6

    def _spawn_car(self):
        open_lanes = [
            lane
            for lane in range(len(LANE_CENTERS))
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
