"""Perspective highway, gameplay state, and heads-up display."""

import pygame

from player import Player
from police import PoliceChase
from settings import (
    ACTION_BUTTON_RECT,
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
        self.font = pygame.font.Font(None, round(LOGICAL_WIDTH * 0.052))
        self.small_font = pygame.font.Font(None, round(LOGICAL_WIDTH * 0.032))
        self.large_font = pygame.font.Font(None, round(LOGICAL_WIDTH * 0.12))
        self.title_font = pygame.font.Font(None, round(LOGICAL_WIDTH * 0.19))
        self.sounds = SoundEffects()
        self.reset()

    def reset(self):
        self.sounds.stop_siren()
        self.player = Player()
        self.traffic = Traffic()
        self.police = PoliceChase()
        self.distance = 0.0
        self.road_offset = 0.0
        self.state = "ready"
        self.game_over_reason = "traffic"

    @property
    def game_over(self):
        return self.state == "game_over"

    def start(self):
        self.reset()
        self.state = "playing"
        self.sounds.play("restart")
        self.sounds.start_siren()

    @property
    def score(self):
        return int(self.distance / 10)

    def handle_action(self, action):
        if action == "toggle_sound":
            enabled = self.sounds.toggle()
            if enabled:
                self.sounds.play("restart")
                if self.state == "playing":
                    self.sounds.start_siren()
            return
        if self.state != "playing":
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
        if self.state != "playing":
            return
        self.player.update(delta_time)
        self.traffic.update(delta_time, self.player.speed)
        self.police.update(delta_time, self.player)
        self.distance += self.player.speed * delta_time
        self.road_offset = (
            self.road_offset + self.player.speed * delta_time
        ) % (LANE_DASH_LENGTH + LANE_DASH_GAP)
        if self.traffic.collided_with(self.player.rect):
            self.game_over_reason = "traffic"
            self.state = "game_over"
            self.sounds.stop_siren()
            self.sounds.play("crash")
        elif self.police.caught_player():
            self.game_over_reason = "police"
            self.state = "game_over"
            self.sounds.stop_siren()
            self.sounds.play("crash")

    def draw(self, surface):
        self._draw_road(surface)
        self.traffic.draw(surface)
        self.police.draw(surface)
        self.player.draw(surface)
        if self.state == "playing":
            self._draw_dashboard(surface)
        elif self.state == "ready":
            self._draw_ready(surface)
        elif self.game_over:
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
        panel = pygame.Rect(
            round(margin),
            round(LOGICAL_HEIGHT * 0.025),
            LOGICAL_WIDTH - round(margin * 2),
            round(LOGICAL_HEIGHT * 0.15),
        )
        self._draw_glass_panel(surface, panel, radius=round(LOGICAL_WIDTH * 0.035))

        title = self.small_font.render("DRIVEX  /  HIGHWAY PATROL", True, (153, 212, 186))
        surface.blit(title, (panel.x + round(margin * 0.45), panel.y + round(LOGICAL_HEIGHT * 0.022)))
        score = self.font.render(f"{self.score:06d}", True, WHITE)
        score_label = self.small_font.render("DISTANCE", True, (191, 207, 202))
        speed = self.font.render(f"{int(self.player.speed)}", True, (170, 239, 191))
        speed_label = self.small_font.render("KM/H", True, (191, 207, 202))
        surface.blit(score, (panel.x + round(margin * 0.45), panel.y + round(LOGICAL_HEIGHT * 0.05)))
        surface.blit(
            score_label,
            (panel.x + round(margin * 0.45), panel.y + round(LOGICAL_HEIGHT * 0.102)),
        )
        speed_x = round(LOGICAL_WIDTH * 0.65)
        surface.blit(speed, (speed_x, panel.y + round(LOGICAL_HEIGHT * 0.05)))
        surface.blit(speed_label, (speed_x, panel.y + round(LOGICAL_HEIGHT * 0.102)))
        hint = self.small_font.render(
            "SWIPE TO STEER  ·  UP TO ACCELERATE  ·  DOWN TO BRAKE",
            True,
            (220, 229, 218),
        )
        hint_panel = pygame.Rect(
            round(margin),
            round(LOGICAL_HEIGHT * 0.186),
            LOGICAL_WIDTH - round(margin * 2),
            round(LOGICAL_HEIGHT * 0.053),
        )
        pygame.draw.rect(surface, (13, 24, 22), hint_panel, border_radius=round(LOGICAL_WIDTH * 0.018))
        surface.blit(hint, hint.get_rect(center=hint_panel.center))
        self._draw_sound_button(surface)

    def _draw_sound_button(self, surface):
        center = (round(LOGICAL_WIDTH * 0.87), round(LOGICAL_HEIGHT * 0.105))
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

    def _draw_ready(self, surface):
        self._draw_title_card(surface)
        self._draw_action_button(surface, "PLAY")

    def _draw_game_over(self, surface):
        self._draw_title_card(surface, game_over=True)
        self._draw_action_button(surface, "TRY AGAIN")

    def _draw_title_card(self, surface, game_over=False):
        shade = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
        shade.fill((7, 15, 17, 162))
        surface.blit(shade, (0, 0))
        center_x = LOGICAL_WIDTH // 2
        card = pygame.Rect(
            round(LOGICAL_WIDTH * 0.075),
            round(LOGICAL_HEIGHT * 0.31),
            round(LOGICAL_WIDTH * 0.85),
            round(LOGICAL_HEIGHT * 0.43),
        )
        self._draw_glass_panel(surface, card, radius=round(LOGICAL_WIDTH * 0.045))
        eyebrow = self.small_font.render(
            "PURSUIT ENDED" if game_over else "ENDLESS HIGHWAY RUN",
            True,
            (126, 223, 176),
        )
        title = self.title_font.render(
            ("CAUGHT" if self.game_over_reason == "police" else "CRASHED")
            if game_over else "DRIVEX",
            True,
            WHITE,
        )
        subtitle_text = (
            "The highway patrol caught up."
            if game_over and self.game_over_reason == "police"
            else "You hit traffic. Take another run."
            if game_over
            else "DODGE TRAFFIC. OUTRUN THE PATROL."
        )
        subtitle = self.small_font.render(subtitle_text, True, (196, 214, 208))
        center_y = card.y + round(card.height * 0.2)
        surface.blit(eyebrow, eyebrow.get_rect(center=(center_x, center_y)))
        surface.blit(title, title.get_rect(center=(center_x, center_y + LOGICAL_HEIGHT * 0.075)))
        surface.blit(
            subtitle,
            subtitle.get_rect(center=(center_x, center_y + LOGICAL_HEIGHT * 0.15)),
        )
        if game_over:
            result = self.font.render(f"DISTANCE  {self.score:06d}", True, (174, 237, 193))
            surface.blit(
                result,
                result.get_rect(center=(center_x, center_y + LOGICAL_HEIGHT * 0.2)),
            )
        else:
            self._draw_control_chips(surface, center_x, center_y + LOGICAL_HEIGHT * 0.18)
        self._draw_sound_button(surface)

    def _draw_control_chips(self, surface, center_x, y):
        labels = ("←  LANE", "↑  GAS", "↓  BRAKE")
        chip_width = round(LOGICAL_WIDTH * 0.24)
        gap = round(LOGICAL_WIDTH * 0.025)
        total_width = chip_width * len(labels) + gap * (len(labels) - 1)
        start_x = center_x - total_width // 2
        for index, label in enumerate(labels):
            rect = pygame.Rect(
                start_x + index * (chip_width + gap),
                round(y),
                chip_width,
                round(LOGICAL_HEIGHT * 0.055),
            )
            pygame.draw.rect(surface, (27, 46, 45), rect, border_radius=round(chip_width * 0.18))
            text = self.small_font.render(label, True, (215, 232, 223))
            surface.blit(text, text.get_rect(center=rect.center))

    def _draw_action_button(self, surface, label):
        rect = pygame.Rect(
            round(ACTION_BUTTON_RECT[0]),
            round(ACTION_BUTTON_RECT[1]),
            round(ACTION_BUTTON_RECT[2]),
            round(ACTION_BUTTON_RECT[3]),
        )
        pygame.draw.rect(
            surface,
            (14, 73, 52),
            rect.move(0, round(LOGICAL_HEIGHT * 0.012)),
            border_radius=round(LOGICAL_WIDTH * 0.04),
        )
        pygame.draw.rect(surface, (54, 211, 132), rect, border_radius=round(LOGICAL_WIDTH * 0.04))
        pygame.draw.rect(
            surface,
            (149, 255, 196),
            rect,
            width=max(2, round(LOGICAL_WIDTH * 0.004)),
            border_radius=round(LOGICAL_WIDTH * 0.04),
        )
        text = self.font.render(label, True, (8, 35, 25))
        surface.blit(text, text.get_rect(center=rect.center))

    @staticmethod
    def _draw_glass_panel(surface, rect, radius):
        pygame.draw.rect(surface, (8, 18, 19), rect, border_radius=radius)
        inner = rect.inflate(-6, -6)
        pygame.draw.rect(
            surface,
            (20, 34, 34),
            inner,
            width=max(1, radius // 8),
            border_radius=max(2, radius - 4),
        )
        pygame.draw.line(
            surface,
            (71, 109, 91),
            (inner.left + radius, inner.top),
            (inner.right - radius, inner.top),
            max(2, radius // 10),
        )
