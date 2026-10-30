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
    WHITE,
    road_bounds_at,
)
from sound_effects import SoundEffects
from traffic import Traffic


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
        self.roadside_offset = 0.0
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
        if self.state == "game_over":
            return
        world_speed = self.player.speed if self.state == "playing" else 92.0
        self.road_offset = (
            self.road_offset + world_speed * delta_time
        ) % (LANE_DASH_LENGTH + LANE_DASH_GAP)
        self.roadside_offset += world_speed * delta_time
        if self.state != "playing":
            return

        self.player.update(delta_time)
        self.traffic.update(delta_time, self.player.speed)
        self.police.update(delta_time, self.player)
        self.distance += self.player.speed * delta_time
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
        self._draw_horizon(surface)
        self._draw_verge(surface)
        top_left, top_right, _ = road_bounds_at(HORIZON_Y)
        bottom_left, bottom_right, _ = road_bounds_at(LOGICAL_HEIGHT)
        shoulder = LOGICAL_WIDTH * 0.028
        shoulder_points = [
            (top_left - shoulder, HORIZON_Y),
            (top_right + shoulder, HORIZON_Y),
            (bottom_right + shoulder, LOGICAL_HEIGHT),
            (bottom_left - shoulder, LOGICAL_HEIGHT),
        ]
        pygame.draw.polygon(surface, (89, 91, 83), shoulder_points)
        road_points = [
            (top_left, HORIZON_Y),
            (top_right, HORIZON_Y),
            (bottom_right, LOGICAL_HEIGHT),
            (bottom_left, LOGICAL_HEIGHT),
        ]
        pygame.draw.polygon(surface, ROAD, road_points)

        pygame.draw.line(
            surface, ROAD_EDGE,
            (round(top_left), round(HORIZON_Y)),
            (round(bottom_left), LOGICAL_HEIGHT),
            round(LOGICAL_WIDTH * 0.006),
        )
        pygame.draw.line(
            surface, ROAD_EDGE,
            (round(top_right), round(HORIZON_Y)),
            (round(bottom_right), LOGICAL_HEIGHT),
            round(LOGICAL_WIDTH * 0.006),
        )

        boundary_count = 2
        dash_y = HORIZON_Y + self.road_offset
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

        rumble_spacing = LOGICAL_HEIGHT * 0.06
        rumble_y = HORIZON_Y + (self.roadside_offset % rumble_spacing)
        rumble_index = int(self.roadside_offset / rumble_spacing)
        while rumble_y < LOGICAL_HEIGHT:
            if rumble_y >= HORIZON_Y:
                left, right, perspective = road_bounds_at(rumble_y)
                stripe_length = LOGICAL_WIDTH * (0.012 + perspective * 0.025)
                stripe_width = max(2, round(LOGICAL_WIDTH * (0.004 + perspective * 0.004)))
                for side, edge_x in ((-1, left), (1, right)):
                    color = (218, 210, 183) if rumble_index % 2 else (177, 80, 66)
                    pygame.draw.line(
                        surface,
                        color,
                        (round(edge_x + side * shoulder * 0.08), round(rumble_y)),
                        (round(edge_x + side * stripe_length), round(rumble_y)),
                        stripe_width,
                    )
            rumble_index -= 1
            rumble_y += rumble_spacing

    def _draw_horizon(self, surface):
        sky_colors = ((94, 157, 181), (126, 181, 190), (177, 201, 185))
        band_height = HORIZON_Y / len(sky_colors)
        for index, color in enumerate(sky_colors):
            pygame.draw.rect(
                surface,
                color,
                (0, round(index * band_height), LOGICAL_WIDTH, round(band_height + 1)),
            )
        hills_back = [
            (0, HORIZON_Y * 0.82),
            (LOGICAL_WIDTH * 0.18, HORIZON_Y * 0.63),
            (LOGICAL_WIDTH * 0.36, HORIZON_Y * 0.78),
            (LOGICAL_WIDTH * 0.58, HORIZON_Y * 0.58),
            (LOGICAL_WIDTH * 0.78, HORIZON_Y * 0.76),
            (LOGICAL_WIDTH, HORIZON_Y * 0.62),
            (LOGICAL_WIDTH, HORIZON_Y),
            (0, HORIZON_Y),
        ]
        pygame.draw.polygon(surface, (106, 143, 125), hills_back)
        hills_front = [
            (0, HORIZON_Y * 0.89),
            (LOGICAL_WIDTH * 0.25, HORIZON_Y * 0.75),
            (LOGICAL_WIDTH * 0.49, HORIZON_Y * 0.85),
            (LOGICAL_WIDTH * 0.73, HORIZON_Y * 0.71),
            (LOGICAL_WIDTH, HORIZON_Y * 0.84),
            (LOGICAL_WIDTH, HORIZON_Y),
            (0, HORIZON_Y),
        ]
        pygame.draw.polygon(surface, (71, 116, 87), hills_front)

        # A low skyline makes the vanishing point feel anchored in a real place.
        buildings = (
            (0.04, 0.12, 0.09), (0.13, 0.07, 0.12), (0.21, 0.1, 0.08),
            (0.68, 0.09, 0.1), (0.77, 0.07, 0.14), (0.85, 0.11, 0.09),
            (0.95, 0.06, 0.12),
        )
        for index, (x, width, height) in enumerate(buildings):
            rect = pygame.Rect(
                round(LOGICAL_WIDTH * x),
                round(HORIZON_Y * (0.78 - height)),
                round(LOGICAL_WIDTH * width),
                round(HORIZON_Y * height),
            )
            pygame.draw.rect(surface, (92, 123, 123), rect)
            for window_y in range(rect.y + 5, rect.bottom - 3, 10):
                for window_x in range(rect.x + 5, rect.right - 3, 9):
                    if (window_x + window_y + index) % 3:
                        pygame.draw.rect(
                            surface, (175, 190, 166),
                            (window_x, window_y, 2, 3),
                        )

    def _draw_verge(self, surface):
        texture_spacing = LOGICAL_HEIGHT * 0.045
        y = HORIZON_Y + (self.roadside_offset % texture_spacing)
        row = int(self.roadside_offset / texture_spacing)
        while y < LOGICAL_HEIGHT:
            if y >= HORIZON_Y:
                left, right, perspective = road_bounds_at(y)
                for side, edge in ((-1, left), (1, right)):
                    verge_width = max(1, round(edge if side < 0 else LOGICAL_WIDTH - edge))
                    streak_x = ((row * 157 + (0 if side < 0 else 83)) % max(1, verge_width))
                    streak_length = 18 + round(42 * perspective)
                    color = GRASS_DARK if row % 2 else (65, 108, 70)
                    start_x = streak_x if side < 0 else edge + streak_x
                    pygame.draw.line(
                        surface,
                        color,
                        (round(start_x), round(y)),
                        (round(start_x + side * streak_length), round(y - 3 * perspective)),
                        max(1, round(2 + 2 * perspective)),
                    )
            row -= 1
            y += texture_spacing

        tree_spacing = texture_spacing * 3
        tree_y = HORIZON_Y + (self.roadside_offset % tree_spacing)
        tree_index = int(self.roadside_offset / tree_spacing)
        while tree_y < LOGICAL_HEIGHT:
            if tree_y >= HORIZON_Y:
                    left, right, perspective = road_bounds_at(tree_y)
                    tree_size = (24 + 70 * perspective) * (0.88 + tree_index % 4 * 0.06)
                    for side, edge in ((-1, left), (1, right)):
                        center_x = edge + side * (tree_size * 0.78 + 12 * perspective)
                        trunk_width = max(3, round(tree_size * 0.17))
                        pygame.draw.rect(
                            surface, (91, 72, 49),
                            (
                                round(center_x - trunk_width / 2),
                                round(tree_y - tree_size * 0.08),
                                trunk_width,
                                round(tree_size * 0.52),
                            ),
                        )
                        pygame.draw.ellipse(
                            surface, (37, 76, 51),
                            (
                                round(center_x - tree_size * 0.57),
                                round(tree_y - tree_size * 0.55),
                                round(tree_size * 1.14),
                                round(tree_size * 0.78),
                            ),
                        )
                        pygame.draw.ellipse(
                            surface, (58, 105, 63),
                            (
                                round(center_x - tree_size * 0.43),
                                round(tree_y - tree_size * 0.64),
                                round(tree_size * 0.86),
                                round(tree_size * 0.64),
                            ),
                        )
                        pygame.draw.ellipse(
                            surface, (92, 136, 74),
                            (
                                round(center_x - tree_size * 0.16),
                                round(tree_y - tree_size * 0.58),
                                round(tree_size * 0.34),
                                round(tree_size * 0.28),
                            ),
                        )
            tree_index -= 1
            tree_y += tree_spacing

        post_spacing = texture_spacing * 2
        post_y = HORIZON_Y + (self.roadside_offset % post_spacing)
        while post_y < LOGICAL_HEIGHT:
            if post_y >= HORIZON_Y:
                    left, right, perspective = road_bounds_at(post_y)
                    post_height = 8 + round(17 * perspective)
                    for side, edge in ((-1, left), (1, right)):
                        post_x = edge + side * (LOGICAL_WIDTH * (0.055 + 0.02 * perspective))
                        pygame.draw.rect(
                            surface, (221, 218, 196),
                            (
                                round(post_x - max(2, 3 * perspective) / 2),
                                round(post_y - post_height),
                                max(2, round(3 * perspective)),
                                post_height,
                            ),
                            border_radius=2,
                        )
                        pygame.draw.line(
                            surface, (174, 66, 56),
                            (round(post_x - 2 * perspective), round(post_y - post_height * 0.68)),
                            (round(post_x + 2 * perspective), round(post_y - post_height * 0.68)),
                            max(1, round(2 * perspective)),
                        )
            post_y += post_spacing

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
        labels = ("LEFT  LANE", "UP  GAS", "DOWN  BRAKE")
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
