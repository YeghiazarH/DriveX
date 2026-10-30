"""Reusable top-down car illustration drawn entirely with Pygame primitives."""

import pygame


def _shade(color, amount):
    return tuple(max(0, min(255, channel + amount)) for channel in color)


def draw_car(surface, center_x, top, width, height, color, player=False):
    x = round(center_x - width / 2)
    y = round(top)
    w, h = round(width), round(height)

    pygame.draw.ellipse(
        surface,
        (26, 29, 30),
        (x - w * 0.13, y + h * 0.08, w * 1.26, h * 0.91),
    )
    tire_color = (18, 20, 22)
    for wheel_y in (y + h * 0.22, y + h * 0.69):
        pygame.draw.rect(
            surface, tire_color,
            (round(x - w * 0.1), round(wheel_y), round(w * 0.18), round(h * 0.2)),
            border_radius=max(2, round(w * 0.05)),
        )
        pygame.draw.rect(
            surface, tire_color,
            (x + w * 0.92, round(wheel_y), w * 0.18, h * 0.2),
            border_radius=max(2, round(w * 0.05)),
        )

    shell = [
        (x + w * 0.28, y + h * 0.02),
        (x + w * 0.72, y + h * 0.02),
        (x + w * 0.86, y + h * 0.09),
        (x + w * 0.96, y + h * 0.30),
        (x + w * 0.94, y + h * 0.83),
        (x + w * 0.81, y + h * 0.97),
        (x + w * 0.19, y + h * 0.97),
        (x + w * 0.06, y + h * 0.83),
        (x + w * 0.04, y + h * 0.30),
        (x + w * 0.14, y + h * 0.09),
    ]
    pygame.draw.polygon(surface, _shade(color, -38), shell)
    inner = [(x + w * 0.2, y + h * 0.06), (x + w * 0.8, y + h * 0.06),
             (x + w * 0.89, y + h * 0.22), (x + w * 0.88, y + h * 0.82),
             (x + w * 0.77, y + h * 0.93), (x + w * 0.23, y + h * 0.93),
             (x + w * 0.12, y + h * 0.82), (x + w * 0.11, y + h * 0.22)]
    pygame.draw.polygon(surface, color, inner)

    hood = [(x + w * 0.2, y + h * 0.1), (x + w * 0.8, y + h * 0.1),
            (x + w * 0.85, y + h * 0.27), (x + w * 0.15, y + h * 0.27)]
    pygame.draw.polygon(surface, _shade(color, 24), hood)
    windshield = [(x + w * 0.2, y + h * 0.31), (x + w * 0.8, y + h * 0.31),
                  (x + w * 0.72, y + h * 0.48), (x + w * 0.28, y + h * 0.48)]
    pygame.draw.polygon(surface, (78, 118, 132), windshield)
    pygame.draw.line(
        surface, (164, 196, 199), windshield[0], windshield[1], max(2, round(w * 0.025))
    )
    pygame.draw.polygon(
        surface, (55, 75, 83),
        [(x + w * 0.27, y + h * 0.54), (x + w * 0.73, y + h * 0.54),
         (x + w * 0.8, y + h * 0.7), (x + w * 0.2, y + h * 0.7)],
    )
    pygame.draw.polygon(
        surface, _shade(color, 17),
        [(x + w * 0.2, y + h * 0.74), (x + w * 0.8, y + h * 0.74),
         (x + w * 0.75, y + h * 0.88), (x + w * 0.25, y + h * 0.88)],
    )
    if player:
        pygame.draw.line(
            surface, (213, 242, 226),
            (x + w * 0.5, y + h * 0.12), (x + w * 0.5, y + h * 0.25),
            max(2, round(w * 0.025)),
        )

    lamp = (255, 242, 190)
    for lamp_x in (x + w * 0.19, x + w * 0.71):
        pygame.draw.rect(
            surface, lamp,
            (round(lamp_x), round(y + h * 0.055), round(w * 0.1), round(h * 0.035)),
            border_radius=max(2, round(w * 0.025)),
        )
    tail_lamp = (251, 73, 63)
    for lamp_x in (x + w * 0.17, x + w * 0.73):
        pygame.draw.rect(
            surface, tail_lamp,
            (round(lamp_x), round(y + h * 0.9), round(w * 0.1), round(h * 0.035)),
            border_radius=max(2, round(w * 0.025)),
        )
