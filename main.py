import multiprocessing as mp
import random
import sys

from hx711 import HX711  # import the class HX711
import RPi.GPIO as GPIO  # import GPIO
import pygame
from pygame.rect import Rect
from pygame.surface import Surface
import numpy as np

from settings import *

import os
# os.environ["SDL_VIDEODRIVER"] = "dummy"

class Background(pygame.sprite.Sprite):
    def __init__(self, size: tuple[int, int]):
        super().__init__()
        self.origin = pygame.image.load(BACKGROUND_PATH).convert()
        self.image: Surface
        self.rect: Rect
        self.init_size = size
        self.size = size

    def update(self):
        self.image = pygame.transform.smoothscale(
            self.origin, self.size
        )
        self.size = (self.size[1] + 10, self.size[1] + 10)
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
    def __init__(self, image_path: str, size: tuple):
        super().__init__()
        self.image: pygame.surface.Surface = pygame.transform.scale(
            pygame.image.load(image_path), size
        ).convert_alpha()
        self.rect: pygame.rect.Rect = self.image.get_rect(center=CENTER)

        self.alpha = 0
        self.time = 0

    def update(self):
        self.time += 1
        if self.time < (FADE_SPEED / 255) * FPS:
            self.alpha += FADE_SPEED
        elif self.time > OBJECT_TIME * FPS:
            self.alpha -= FADE_SPEED
        else:
            self.alpha = 255

        if self.alpha < 0:
            self.kill()
        self.image.set_alpha(self.alpha)


class Glowing(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.origin: pygame.surface.Surface = pygame.transform.scale(
            pygame.image.load("./assets/glow.bmp"), (550, 550)
        ).convert_alpha()
        self.image: Surface = self.origin
        self.rect: Rect = self.image.get_rect(center=CENTER)

        self.alpha = 0
        self.angle = 0
        self.time = 0

    def update(self) -> None:
        self.time += 1
        if self.time < (FADE_SPEED / 255) * FPS:
            self.alpha += FADE_SPEED
        elif self.time > OBJECT_TIME * FPS:
            self.alpha -= FADE_SPEED
        else:
            self.alpha = 255

        if self.alpha < 0:
            self.kill()

        self.angle += 20
        self.image = pygame.transform.rotate(self.origin, self.angle)
        self.image.set_alpha(self.alpha)
        self.rect = self.image.get_rect(center=CENTER)


class TreviFountainGame:
    def __init__(self) -> None:
        PYGAME_BLEND_ALPHA_SDL2 = 1
        pygame.mixer.init()
        pygame.init()
        self.window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()

        self.bg = Background(SCREEN_SIZE)
        self.objects = pygame.sprite.Group()

        # TODO: test mp.Queue
        self.queue = mp.Queue()
        self.sensor = Worker(self.queue)

        self.prev_data = 0
        self.frame = 0

        pygame.mixer.music.load("./music/water.ogg")
        pygame.mixer.music.play(loops=-1)
        self.music_group = [pygame.mixer.Sound(p) for p in MUSIC_PATHS]

    def run(self):
        while True:
            self.window.fill(BLACK)
            self.clock.tick(FPS)
            self.frame += 1
            # TODO: test mp.Queue
            if not self.queue.empty():
                data = self.queue.get()
                gap = data - self.prev_data
                print(f"{data=} {self.prev_data=} {gap=}")
                # if gap > 700 and gap < 10000:
                if gap > 700 and gap < 30000:
                    self.music_play()
                    self.obj_appear()
                self.prev_data = data

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.music_play()
                    self.obj_appear()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.quit()
                     # elif event.key == pygame.K_m:
                     #     pygame.display.toggle_fullscreen()
                if event.type == pygame.QUIT:
                    self.quit()

            self.bg.update()
            bg_img, bg_rect = mask(self.bg.image, self.bg.rect)
            self.objects.update()

            self.window.blit(bg_img, bg_rect)
            for obj in self.objects:
                self.window.blit(obj.image, obj.rect)  # type: ignore
            pygame.display.update()

    def obj_appear(self) -> None:
        sel_idx = random.randint(0, len(OBJECT_PATHS) - 1)
        obj = Object(OBJECT_PATHS[sel_idx], (600, 600))
        # glow = Glowing()
        self.objects.empty()
        # self.objects.add(glow)
        self.objects.add(obj)

    def music_play(self) -> None:
        sel_idx = random.randint(0, len(self.music_group) - 1)
        print(sel_idx)
        self.music_group[sel_idx].play()

    def quit(self) -> None:
        self.sensor.kill()
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()
        GPIO.cleanup()
        sys.exit()


class Worker(mp.Process):
    def __init__(self, queue: mp.Queue) -> None:
        super().__init__()
        self.queue = queue
        print("Initialize HX711")
        self.hx = HX711(dout_pin=5, pd_sck_pin=6, gain=128, channel="A")
        self.hx.reset()
        print("Initialize HX711 Finished")
        self.start()

    def run(self) -> None:
        while True:
            self.queue.put(np.mean(self.hx.get_raw_data()))


if __name__ == "__main__":
    game = TreviFountainGame()
    game.run()
