import random
import sys

import pygame
from pygame.rect import Rect
from pygame.surface import Surface

from settings import *


class Background(pygame.sprite.Sprite):
    def __init__(self, size: tuple[int, int]):
        super().__init__()
        self.origin = pygame.image.load(BACKGROUND_PATH)
        self.image: Surface
        self.rect: Rect
        self.init_size = size
        self.size = size

    def update(self):
        self.image = pygame.transform.smoothscale(
            self.origin.convert_alpha(), self.size
        )
        self.size = (self.size[1] + 2, self.size[1] + 2)
        if self.size[0] == 1200:
            self.size = self.init_size
        self.rect = self.image.get_rect()
        self.rect.center = CENTER


def mask(image: Surface, rect: Rect) -> tuple[Surface, Rect]:
    crop_bg = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    pygame.draw.ellipse(crop_bg, (255, 255, 255, 255), (0, 0, *SCREEN_SIZE))
    crop_bg.blit(image, rect, special_flags=pygame.BLEND_RGBA_MIN)
    return crop_bg, crop_bg.get_rect()


class Object(pygame.sprite.Sprite):
    def __init__(self, image_path: str, size: tuple, center: tuple):
        super().__init__()
        self.image: pygame.surface.Surface = pygame.transform.scale(
            pygame.image.load(image_path), size
        ).convert_alpha()
        self.rect: pygame.rect.Rect = self.image.get_rect()
        self.rect.center = center

        self.size = size
        self.alpha = 1

        self.is_fade_in = False
        self.timeout = 0

    def update(self):
        self.timeout += 1
        if self.timeout > OBJECT_TIME * FPS:
            self.alpha -= FADE_SPEED
            if self.alpha < 0:
                self.kill()
            self.image.set_alpha(self.alpha)
        if self.is_fade_in:
            self.image.set_alpha(self.alpha)
            self.alpha += FADE_SPEED
            if self.alpha > 255:
                self.image.set_alpha(255)
                self.is_fade_in = False

    def start(self):
        self.is_fade_in = True


class Glowing(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.origin: pygame.surface.Surface = pygame.transform.scale(
            pygame.image.load("./assets/glow.png"), SCREEN_SIZE
        ).convert_alpha()
        self.image: Surface = self.origin
        self.rect: Rect

        self.alpha = 255
        self.angle = 0
        self.timeout = 0

    def update(self) -> None:
        self.timeout += 1
        if self.timeout > OBJECT_TIME * FPS:
            self.alpha -= FADE_SPEED
            if self.alpha < 0:
                self.kill()
        self.angle += 1
        self.image = pygame.transform.rotate(self.origin, self.angle)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(
            center=self.origin.get_rect(center=CENTER).center
        )


class TreviFountainGame:
    def __init__(self) -> None:
        pygame.init()
        self.window = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()

        self.bg = Background(SCREEN_SIZE)
        self.objects = pygame.sprite.Group()

    def run(self):
        while True:
            self.window.fill(BLACK)
            self.clock.tick(FPS)

            self.bg.update()
            bg_img, bg_rect = mask(self.bg.image, self.bg.rect)
            self.window.blit(bg_img, bg_rect)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    sel_idx = random.randint(0, len(OBJECT_PATHS) - 1)
                    obj = Object(OBJECT_PATHS[sel_idx], (250, 250), CENTER)
                    glow = Glowing()

                    self.objects.empty()
                    self.objects.add(glow)
                    self.objects.add(obj)
                    obj.start()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_m:
                        pygame.display.toggle_fullscreen()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.objects.update()
            for obj in self.objects:
                self.window.blit(obj.image, obj.rect)  # type: ignore
            pygame.display.update()


if __name__ == "__main__":
    game = TreviFountainGame()
    game.run()
