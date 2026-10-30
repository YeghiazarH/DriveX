"""Perspective highway, gameplay state, and heads-up display."""

import pygame

from player import Player
from settings import (
    GRASS,
    GRASS_DARK,
    HORIZON_Y,
    LANE_DASH_GAP,
    LANE_DASH_LENGTH,
    LANE_MARKER,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
    ROAD,
    ROAD_EDGE,
    ROAD_LEFT,
    ROAD_RIGHT,
    WHITE,
)
from sound_effects import SoundEffects
from traffic import Traffic


def road_bounds_at(y):
    progress = max(0.0, min(1.0, (y - HORIZON_Y) / (LOGICAL_HEIGHT - HORIZON_Y)))
    width = (ROAD_RIGHT - ROAD_LEFT) * (0.66 + progress * 0.34)
    center = LOGICAL_WIDTH / 2
    return center - width / 2, center + width / 2, progress


class Game:
    def __init__(self):
        self.font = pygame.font.Font(None, round(LOGICAL_WIDTH * 0.058))
        self.small_font = pygame.font.Font(None, round(LOGICAL_WIDTH * 0.034))
        self.large_font = pygame.font.Font(None, round(LOGICAL_WIDTH * 0.13))
        self.sounds = SoundEffects()
        self.reset()

    def reset(self):
        self.player = Player()
        self.traffic = Traffic()
        self.distance = 0.0
        self.road_offset = 0.0
        self.game_over = False

    @property
    def score(self):
        return int(self.distance / 10)

    def handle_action(self, action):
        if action == "toggle_sound":
            enabled = self.sounds.toggle()
            if enabled:
                self.sounds.play("restart")
            return
        if self.game_over:
            return
        if action == "left":
            previous_lane = self.player.lane
            self.player.change_lane(-1)
            if previous_lane != self.player.lane:
                self.sounds.play("lane")
        elif action == "right":
            previous_lane = self.player.lane
            self.player.change_lane(1)
            if previous_lane != self.player.lane:
                self.sounds.play("lane")
        elif action == "accelerate":
            self.player.accelerate()
            self.sounds.play("accelerate")
        elif action == "brake":
            self.player.brake()
            self.sounds.play("brake")

    def update(self, delta_time):
        if self.game_over:
            return
        self.player.update(delta_time)
        self.traffic.update(delta_time, self.player.speed)
        self.distance += self.player.speed * delta_time
        self.road_offset = (
            self.road_offset + self.player.speed * delta_time
        ) % (LANE_DASH_LENGTH + LANE_DASH_GAP)
        if self.traffic.collided_with(self.player.rect):
            self.game_over = True
            self.sounds.play("crash")

    def draw(self, surface):
        self._draw_road(surface)
        self.traffic.draw(surface)
        self.player.draw(surface)
        self._draw_dashboard(surface)
        if self.game_over:
            self._draw_game_over(surface)

    def _draw_road(self, surface):
        surface.fill(GRASS)
        for y in range(round(HORIZON_Y), LOGICAL_HEIGHT, round(LOGICAL_HEIGHT * 0.045)):
            left, right, perspective = road_bounds_at(y)
            texture_color = GRASS_DARK if (y // 170) % 2 else GRASS
            pygame.draw.line(
                surface,
                texture_color,
                (0, y),
                (round(left - 12 * perspective), y),
                max(1, round(2 * perspective)),
            )
            pygame.draw.line(
                surface,
                texture_color,
                (round(right + 12 * perspective), y),
                (LOGICAL_WIDTH, y),
                max(1, round(2 * perspective)),
            )

        top_left, top_right, _ = road_bounds_at(HORIZON_Y)
        bottom_left, bottom_right, _ = road_bounds_at(LOGICAL_HEIGHT)
        shoulder = LOGICAL_WIDTH * 0.025
        road_points = [
            (top_left, HORIZON_Y),
            (top_right, HORIZON_Y),
            (bottom_right, LOGICAL_HEIGHT),
            (bottom_left, LOGICAL_HEIGHT),
        ]
        shoulder_points = [
            (top_left - shoulder, HORIZON_Y),
            (top_right + shoulder, HORIZON_Y),
            (bottom_right + shoulder, LOGICAL_HEIGHT),
            (bottom_left - shoulder, LOGICAL_HEIGHT),
        ]
        pygame.draw.polygon(surface, (164, 157, 137), shoulder_points)
        pygame.draw.polygon(surface, ROAD, road_points)

        for side in (-1, 1):
            for y in range(round(HORIZON_Y), LOGICAL_HEIGHT, round(LOGICAL_HEIGHT * 0.032)):
                left, right, perspective = road_bounds_at(y)
                edge_x = left if side < 0 else right
                mark_width = max(2, round(LOGICAL_WIDTH * (0.006 + 0.004 * perspective)))
                pygame.draw.line(
                    surface,
                    ROAD_EDGE,
                    (round(edge_x), y),
                    (round(edge_x), y + round(10 + 12 * perspective)),
                    mark_width,
                )
                rail_x = edge_x + side * (LOGICAL_WIDTH * (0.027 + 0.012 * perspective))
                pygame.draw.circle(
                    surface, (194, 191, 176),
                    (round(rail_x), y), max(1, round(3 * perspective)),
                )

        boundary_count = 2
        dash_y = HORIZON_Y - self.road_offset
        while dash_y < LOGICAL_HEIGHT:
            draw_y = max(HORIZON_Y, dash_y)
            _, _, perspective = road_bounds_at(draw_y)
            dash_length = LANE_DASH_LENGTH * (0.35 + perspective * 0.85)
            for boundary in range(1, boundary_count + 1):
                left, right, _ = road_bounds_at(draw_y)
                x = left + (right - left) * boundary / 3
                mark_width = max(2, round(LOGICAL_WIDTH * (0.004 + perspective * 0.004)))
                pygame.draw.line(
                    surface, LANE_MARKER,
                    (round(x), round(draw_y)),
                    (round(x), round(min(LOGICAL_HEIGHT, draw_y + dash_length))),
                    mark_width,
                )
            dash_y += LANE_DASH_LENGTH + LANE_DASH_GAP

        for post_y in range(round(HORIZON_Y), LOGICAL_HEIGHT, round(LOGICAL_HEIGHT * 0.12)):
            left, right, perspective = road_bounds_at(post_y)
            size = max(2, round(LOGICAL_WIDTH * (0.004 + perspective * 0.006)))
            for x in (left - shoulder * 1.7, right + shoulder * 1.7):
                pygame.draw.rect(
                    surface, (235, 230, 207),
                    (round(x - size / 2), post_y, size, size * 4),
                    border_radius=size // 2,
                )

    def _draw_dashboard(self, surface):
        margin = LOGICAL_WIDTH * 0.055
        top = LOGICAL_HEIGHT * 0.035
        panel = pygame.Surface((LOGICAL_WIDTH, round(LOGICAL_HEIGHT * 0.18)), pygame.SRCALPHA)
        panel.fill((11, 19, 18, 174))
        surface.blit(panel, (0, 0))

        score = self.font.render(f"DISTANCE   {self.score:06d}", True, WHITE)
        speed = self.font.render(f"{int(self.player.speed)} km/h", True, (170, 239, 191))
        surface.blit(score, (round(margin), round(top)))
        surface.blit(speed, (round(margin), round(top + LOGICAL_HEIGHT * 0.048)))
        hint = self.small_font.render(
            "SWIPE   LANE  ·  UP  ACCELERATE  ·  DOWN  BRAKE", True, (220, 229, 218)
        )
        surface.blit(hint, (round(margin), round(top + LOGICAL_HEIGHT * 0.096)))
        self._draw_sound_button(surface)

    def _draw_sound_button(self, surface):
        center = (round(LOGICAL_WIDTH * 0.91), round(LOGICAL_HEIGHT * 0.105))
        radius = round(LOGICAL_WIDTH * 0.045)
        color = (54, 151, 100) if self.sounds.enabled else (87, 94, 94)
        pygame.draw.circle(surface, color, center, radius)
        x, y = center
        speaker = round(radius * 0.36)
        pygame.draw.polygon(
            surface, WHITE,
            [(x - speaker, y - speaker * 0.65), (x, y - speaker * 0.65),
             (x + speaker * 0.72, y - speaker), (x + speaker * 0.72, y + speaker),
             (x, y + speaker * 0.65), (x - speaker, y + speaker * 0.65)],
        )
        if self.sounds.enabled:
            pygame.draw.arc(
                surface, WHITE,
                (x - radius * 0.05, y - radius * 0.52, radius * 0.88, radius * 1.04),
                -0.95, 0.95, max(2, radius // 10),
            )
        else:
            pygame.draw.line(
                surface, (255, 112, 98),
                (x - radius * 0.18, y - radius * 0.68),
                (x + radius * 0.65, y + radius * 0.68),
                max(2, radius // 9),
            )

    def _draw_game_over(self, surface):
        shade = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        shade.fill((8, 13, 14, 190))
        surface.blit(shade, (0, 0))
        center_x = LOGICAL_WIDTH // 2
        center_y = round(LOGICAL_HEIGHT * 0.48)
        title = self.large_font.render("CRASH", True, WHITE)
        result = self.font.render(f"DISTANCE   {self.score}", True, WHITE)
        restart = self.small_font.render("TAP ANYWHERE TO DRIVE AGAIN", True, (190, 237, 204))
        surface.blit(title, title.get_rect(center=(center_x, center_y)))
        surface.blit(result, result.get_rect(center=(center_x, center_y + LOGICAL_HEIGHT * 0.07)))
        surface.blit(
            restart,
            restart.get_rect(center=(center_x, center_y + LOGICAL_HEIGHT * 0.14)),
        )
