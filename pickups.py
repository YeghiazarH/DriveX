"""Roadside nitro pickups that reward lane changes."""

import random

import pygame

from settings import (
    HORIZON_Y,
    LANE_COUNT,
    LOGICAL_HEIGHT,
    LANE_WIDTH,
    lane_center_at,
    vehicle_scale_at,
)


class NitroPickup:
    def __init__(self, lane, y):
        self.lane = lane
        self.y = float(y)
        self.collected = False

    @property
    def rect(self):
        scale = vehicle_scale_at(self.y)
        size = max(18, round(LANE_WIDTH * 0.18 * scale))
        return pygame.Rect(
            round(lane_center_at(self.lane, self.y) - size / 2),
            round(self.y - size / 2),
            size,
            size,
        )

    def update(self, delta_time, world_speed):
        self.y += world_speed * delta_time * 0.82

    def draw(self, surface):
        center = (round(lane_center_at(self.lane, self.y)), round(self.y))
        scale = vehicle_scale_at(self.y)
        radius = max(8, round(LANE_WIDTH * 0.11 * scale))
        pygame.draw.circle(surface, (28, 94, 111), center, radius + max(2, radius // 4))
        pygame.draw.circle(surface, (49, 213, 230), center, radius)
        pygame.draw.circle(surface, (195, 255, 246), center, round(radius * 0.68), max(1, radius // 10))
        bolt = [
            (center[0] + round(radius * 0.12), center[1] - round(radius * 0.58)),
            (center[0] - round(radius * 0.32), center[1] + round(radius * 0.04)),
            (center[0] - round(radius * 0.02), center[1] + round(radius * 0.04)),
            (center[0] - round(radius * 0.18), center[1] + round(radius * 0.56)),
            (center[0] + round(radius * 0.34), center[1] - round(radius * 0.12)),
            (center[0] + round(radius * 0.04), center[1] - round(radius * 0.12)),
        ]
        pygame.draw.polygon(surface, (13, 69, 86), bolt)


class NitroPickups:
    def __init__(self):
        self.items = []
        self.spawn_timer = random.uniform(3.8, 5.2)

    def reset(self):
        self.items.clear()
        self.spawn_timer = random.uniform(3.8, 5.2)

    def update(self, delta_time, world_speed, traffic):
        self.spawn_timer -= delta_time
        if self.spawn_timer <= 0:
            spawn_y = HORIZON_Y + 18
            blocked_lanes = {
                car.lane
                for car in traffic.cars
                if abs(car.y - spawn_y) < 280
            }
            lanes = [
                lane for lane in range(LANE_COUNT)
                if lane not in blocked_lanes
                and all(pickup.lane != lane or pickup.y > spawn_y + 240 for pickup in self.items)
            ]
            if lanes:
                self.items.append(NitroPickup(random.choice(lanes), HORIZON_Y - 15))
            self.spawn_timer = random.uniform(5.5, 8.0)

        for pickup in self.items:
            pickup.update(delta_time, world_speed)
        self.items = [
            pickup for pickup in self.items
            if not pickup.collected and pickup.y < LOGICAL_HEIGHT + 60
        ]

    def collect(self, player_rect):
        collected = 0
        for pickup in self.items:
            if not pickup.collected and player_rect.colliderect(pickup.rect):
                pickup.collected = True
                collected += 1
        return collected

    def draw(self, surface):
        for pickup in self.items:
            pickup.draw(surface)
