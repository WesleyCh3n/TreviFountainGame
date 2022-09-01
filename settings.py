from pathlib import Path

SCREEN_SIZE = (600, 600)
WIDTH, HEIGHT = SCREEN_SIZE
CENTER = int(WIDTH / 2), int(HEIGHT / 2)
FPS = 30
FADE_SPEED = 15
OBJECT_TIME = 3

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

BACKGROUND_PATH = "./assets/water.jpg"

files = list(Path("./assets/obj/").glob("*.png"))
OBJECT_PATHS = [str(file) for file in files]
