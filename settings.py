from pathlib import Path
import pygame

SCREEN_SIZE = (600, 600)
WIDTH, HEIGHT = SCREEN_SIZE
CENTER = int(WIDTH / 2), int(HEIGHT / 2)
FPS = 30
FADE_SPEED = 50  # 1 ~ 255
OBJECT_TIME = 1

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

BACKGROUND_PATH = "./assets/water.jpg"

files = list(Path("./assets/obj/").glob("*.png"))
OBJECTS = [pygame.image.load(str(file)).convert_alpha() for file in files]
GLOW_OBJ = pygame.image.load("./assets/glow.png").convert_alpha()
