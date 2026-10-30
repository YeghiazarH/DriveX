"""Game state and drawing for the infinite highway run."""

import pygame

from player import Player
from settings import (
    GRASS,
    LANE_DASH_GAP,
    LANE_DASH_LENGTH,
    LANE_MARKER,
    LANE_CENTERS,
    LANE_WIDTH,
    LOGICAL_HEIGHT,
    LOGICAL_WIDTH,
    ROAD,
    ROAD_EDGE,
    ROAD_LEFT,
    ROAD_RIGHT,
    WHITE,
)
from traffic import Traffic


class Game:
    def __init__(self):
        self.font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 58)
        self.small_font = pygame.font.Font(None, 22)
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
        if self.game_over:
            return
        if action == "left":
            self.player.change_lane(-1)
        elif action == "right":
            self.player.change_lane(1)
        elif action == "accelerate":
            self.player.accelerate()
        elif action == "brake":
            self.player.brake()

    def update(self, delta_time):
        if self.game_over:
            return
        self.player.update(delta_time)
        self.traffic.update(delta_time, self.player.speed)
        self.distance += self.player.speed * delta_time
        dash_cycle = LANE_DASH_LENGTH + LANE_DASH_GAP
        self.road_offset = (self.road_offset + self.player.speed * delta_time) % dash_cycle
        if self.traffic.collided_with(self.player.rect):
            self.game_over = True

    def draw(self, surface):
        self._draw_road(surface)
        self.traffic.draw(surface)
        self.player.draw(surface)
        self._draw_dashboard(surface)
        if self.game_over:
            self._draw_game_over(surface)

    def _draw_road(self, surface):
        surface.fill(GRASS)
        pygame.draw.rect(
            surface,
            ROAD,
            (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, LOGICAL_HEIGHT),
        )
        pygame.draw.rect(surface, ROAD_EDGE, (ROAD_LEFT, 0, 4, LOGICAL_HEIGHT))
        pygame.draw.rect(surface, ROAD_EDGE, (ROAD_RIGHT - 4, 0, 4, LOGICAL_HEIGHT))

        dash_cycle = LANE_DASH_LENGTH + LANE_DASH_GAP
        start_y = -dash_cycle + self.road_offset
        for lane_boundary in (ROAD_LEFT + LANE_WIDTH, ROAD_LEFT + 2 * LANE_WIDTH):
            y = start_y
            while y < LOGICAL_HEIGHT:
                pygame.draw.rect(
                    surface,
                    LANE_MARKER,
                    (round(lane_boundary) - 2, round(y), 4, LANE_DASH_LENGTH),
                    border_radius=2,
                )
                y += dash_cycle

        for y in range(35, LOGICAL_HEIGHT, 92):
            pygame.draw.circle(surface, (54, 114, 59), (21, y), 3)
            pygame.draw.circle(surface, (54, 114, 59), (379, y + 34), 3)

    def _draw_dashboard(self, surface):
        panel = pygame.Surface((LOGICAL_WIDTH, 62), pygame.SRCALPHA)
        panel.fill((18, 24, 28, 180))
        surface.blit(panel, (0, 0))

        score_text = self.font.render(f"SCORE  {self.score:06d}", True, WHITE)
        speed_text = self.font.render(
            f"{int(self.player.speed)} km/h", True, (157, 241, 183)
        )
        surface.blit(score_text, (16, 12))
        surface.blit(speed_text, (LOGICAL_WIDTH - speed_text.get_width() - 16, 12))
        hint = self.small_font.render(
            "Swipe: change lane  |  Up: accelerate  |  Down: brake",
            True,
            WHITE,
        )
        surface.blit(hint, hint.get_rect(center=(LOGICAL_WIDTH // 2, 48)))

    def _draw_game_over(self, surface):
        shade = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        shade.fill((10, 13, 16, 178))
        surface.blit(shade, (0, 0))

        title = self.large_font.render("GAME OVER", True, WHITE)
        result = self.font.render(f"Distance score: {self.score}", True, WHITE)
        restart = self.small_font.render(
            "Tap or click to restart", True, (190, 235, 202)
        )
        surface.blit(title, title.get_rect(center=(LOGICAL_WIDTH // 2, 250)))
        surface.blit(result, result.get_rect(center=(LOGICAL_WIDTH // 2, 300)))
        surface.blit(restart, restart.get_rect(center=(LOGICAL_WIDTH // 2, 348)))
