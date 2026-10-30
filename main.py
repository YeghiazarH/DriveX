"""Pygame CE entry point; compatible with pygbag's asyncio event loop."""

import asyncio

import pygame

from game import Game
from input_handler import InputHandler, Viewport
from settings import FPS, LOGICAL_HEIGHT, LOGICAL_WIDTH


async def main():
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
    pygame.init()
    pygame.display.set_caption("DriveX - Infinite Highway")
    window = pygame.display.set_mode(
        (402, 874),
        pygame.RESIZABLE,
    )
    logical_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    clock = pygame.time.Clock()
    game = Game()
    controls = InputHandler()
    running = True

    while running:
        delta_time = min(clock.tick(FPS) / 1000.0, 0.05)
        viewport = Viewport.fill(window.get_size())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue
            if event.type == pygame.VIDEORESIZE:
                window = pygame.display.set_mode(
                    (max(1, event.w), max(1, event.h)),
                    pygame.RESIZABLE,
                )
                viewport = Viewport.fill(window.get_size())
            action = controls.handle_event(event, viewport, game.state)
            if action in ("play", "restart"):
                game.start()
            elif action:
                game.handle_action(action)

        game.update(delta_time)
        game.draw(logical_surface)

        scaled_size = (max(1, round(viewport.width)), max(1, round(viewport.height)))
        scaled_game = pygame.transform.smoothscale(logical_surface, scaled_size)
        window.blit(scaled_game, (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
