"""Reusable top-down vehicle illustrations drawn entirely with Pygame primitives."""

import pygame


def _shade(color, amount):
    return tuple(max(0, min(255, channel + amount)) for channel in color)


def _rounded(surface, color, x, y, width, height, radius):
    bounds = pygame.Rect(round(x), round(y), max(1, round(width)), max(1, round(height)))
    pygame.draw.rect(surface, color, bounds, border_radius=max(1, round(radius)))


def draw_car(
    surface,
    center_x,
    top,
    width,
    height,
    color,
    player=False,
    police=False,
    police_phase=0,
):
    x = center_x - width / 2
    y = top
    w, h = width, height
    radius = w * 0.19

    pygame.draw.ellipse(
        surface,
        (19, 25, 28),
        (round(x - w * 0.06), round(y + h * 0.07), round(w * 1.12), round(h * 0.91)),
    )

    tire_color = (20, 23, 26)
    for tire_y in (y + h * 0.2, y + h * 0.68):
        for tire_x in (x + w * 0.015, x + w * 0.805):
            _rounded(surface, tire_color, tire_x, tire_y, w * 0.18, h * 0.19, w * 0.065)
            pygame.draw.line(
                surface,
                (72, 78, 80),
                (round(tire_x + w * 0.035), round(tire_y + h * 0.055)),
                (round(tire_x + w * 0.16), round(tire_y + h * 0.055)),
                max(1, round(w * 0.012)),
            )

    body = (x + w * 0.075, y + h * 0.015, w * 0.85, h * 0.97)
    _rounded(surface, (13, 17, 19), *body, radius)
    _rounded(surface, _shade(color, -32), x + w * 0.09, y + h * 0.025, w * 0.82, h * 0.95, radius * 0.9)
    _rounded(surface, color, x + w * 0.115, y + h * 0.04, w * 0.77, h * 0.92, radius * 0.78)

    # Hood and trunk give the silhouette clear front and rear ends.
    _rounded(
        surface,
        _shade(color, 18),
        x + w * 0.19,
        y + h * 0.095,
        w * 0.62,
        h * 0.19,
        w * 0.1,
    )
    pygame.draw.line(
        surface,
        _shade(color, 38),
        (round(x + w * 0.23), round(y + h * 0.12)),
        (round(x + w * 0.77), round(y + h * 0.12)),
        max(1, round(w * 0.012)),
    )
    pygame.draw.line(
        surface,
        _shade(color, -28),
        (round(x + w * 0.22), round(y + h * 0.295)),
        (round(x + w * 0.78), round(y + h * 0.295)),
        max(1, round(w * 0.012)),
    )

    glass_edge = (28, 43, 49)
    glass = (73, 111, 124)
    pygame.draw.polygon(
        surface,
        glass_edge,
        [
            (round(x + w * 0.18), round(y + h * 0.32)),
            (round(x + w * 0.82), round(y + h * 0.32)),
            (round(x + w * 0.75), round(y + h * 0.48)),
            (round(x + w * 0.25), round(y + h * 0.48)),
        ],
    )
    pygame.draw.polygon(
        surface,
        glass,
        [
            (round(x + w * 0.215), round(y + h * 0.335)),
            (round(x + w * 0.785), round(y + h * 0.335)),
            (round(x + w * 0.73), round(y + h * 0.465)),
            (round(x + w * 0.27), round(y + h * 0.465)),
        ],
    )
    pygame.draw.line(
        surface,
        (174, 202, 205),
        (round(x + w * 0.25), round(y + h * 0.35)),
        (round(x + w * 0.75), round(y + h * 0.35)),
        max(1, round(w * 0.012)),
    )

    _rounded(surface, _shade(color, -9), x + w * 0.22, y + h * 0.48, w * 0.56, h * 0.23, w * 0.075)
    pygame.draw.line(
        surface,
        _shade(color, 32),
        (round(x + w * 0.5), round(y + h * 0.49)),
        (round(x + w * 0.5), round(y + h * 0.7)),
        max(1, round(w * 0.012)),
    )

    pygame.draw.polygon(
        surface,
        glass_edge,
        [
            (round(x + w * 0.27), round(y + h * 0.735)),
            (round(x + w * 0.73), round(y + h * 0.735)),
            (round(x + w * 0.79), round(y + h * 0.865)),
            (round(x + w * 0.21), round(y + h * 0.865)),
        ],
    )
    pygame.draw.polygon(
        surface,
        (54, 83, 94),
        [
            (round(x + w * 0.305), round(y + h * 0.75)),
            (round(x + w * 0.695), round(y + h * 0.75)),
            (round(x + w * 0.745), round(y + h * 0.85)),
            (round(x + w * 0.255), round(y + h * 0.85)),
        ],
    )
    pygame.draw.line(
        surface,
        _shade(color, -24),
        (round(x + w * 0.22), round(y + h * 0.88)),
        (round(x + w * 0.78), round(y + h * 0.88)),
        max(1, round(w * 0.014)),
    )

    # Door seams, mirrors, and side highlights give the body more definition.
    for seam_y in (y + h * 0.52, y + h * 0.69):
        pygame.draw.line(
            surface,
            _shade(color, -19),
            (round(x + w * 0.13), round(seam_y)),
            (round(x + w * 0.87), round(seam_y)),
            max(1, round(w * 0.009)),
        )
    for mirror_x in (x + w * 0.025, x + w * 0.865):
        _rounded(surface, _shade(color, -20), mirror_x, y + h * 0.34, w * 0.11, h * 0.075, w * 0.035)
    pygame.draw.line(
        surface,
        _shade(color, 45),
        (round(x + w * 0.145), round(y + h * 0.22)),
        (round(x + w * 0.145), round(y + h * 0.79)),
        max(1, round(w * 0.012)),
    )

    # Headlamps face the top of the screen; the red lamps face trailing traffic.
    lamp_width = w * 0.17
    lamp_height = h * 0.025
    for lamp_x in (x + w * 0.17, x + w * 0.66):
        _rounded(surface, (255, 246, 211), lamp_x, y + h * 0.045, lamp_width, lamp_height, lamp_height * 0.45)
    for lamp_x in (x + w * 0.17, x + w * 0.66):
        _rounded(surface, (247, 66, 60), lamp_x, y + h * 0.925, lamp_width, lamp_height, lamp_height * 0.45)
        pygame.draw.line(
            surface,
            (255, 153, 113),
            (round(lamp_x + w * 0.025), round(y + h * 0.936)),
            (round(lamp_x + w * 0.12), round(y + h * 0.936)),
            max(1, round(w * 0.01)),
        )

    if player:
        pygame.draw.line(
            surface,
            (221, 246, 232),
            (round(x + w * 0.5), round(y + h * 0.13)),
            (round(x + w * 0.5), round(y + h * 0.24)),
            max(1, round(w * 0.018)),
        )

    if police:
        stripe = (35, 83, 133)
        pygame.draw.line(
            surface,
            stripe,
            (round(x + w * 0.14), round(y + h * 0.53)),
            (round(x + w * 0.14), round(y + h * 0.86)),
            max(2, round(w * 0.055)),
        )
        pygame.draw.line(
            surface,
            stripe,
            (round(x + w * 0.86), round(y + h * 0.53)),
            (round(x + w * 0.86), round(y + h * 0.86)),
            max(2, round(w * 0.055)),
        )
        lightbar_y = y + h * 0.455
        lightbar_h = max(2, round(h * 0.035))
        left_light, right_light = (
            ((49, 126, 255), (255, 51, 56))
            if police_phase == 0
            else ((255, 51, 56), (49, 126, 255))
        )
        _rounded(surface, (19, 27, 35), x + w * 0.25, lightbar_y, w * 0.5, lightbar_h, lightbar_h / 2)
        _rounded(surface, left_light, x + w * 0.27, lightbar_y, w * 0.22, lightbar_h, lightbar_h / 2)
        _rounded(surface, right_light, x + w * 0.51, lightbar_y, w * 0.22, lightbar_h, lightbar_h / 2)
