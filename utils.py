from enum import Enum
import sys


class MSGError:
    @staticmethod
    def print_error(msg: str) -> None:
        print(
            f"{Ansi.RED.value}"
            f"{msg}"
            f"{Ansi.RESET.value}",
            file=sys.stderr
        )


class Ansi(Enum):
    CLEAR = "\033[2J\033[H"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    PURPLE = "\033[95m"
    WHITE = "\033[97m"


class Color(Enum):
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"
    PURPLE = "purple"
    CYAN = "cyan"
    NONE = "none"
    BROWN = "brown"
    LIME = "lime"
    MAGENTA = "magenta"
    GOLD = "gold"
    WHITE = "white"
    BLACK = "black"
    MAROON = "maroon"
    DARKRED = "darkred"
    CRIMSON = "crimson"
    VIOLET = "violet"
    RAINBOW = "rainbow"

    @property
    def rgb(self) -> tuple[int, int, int]:
        color_dict: dict[
            Color, tuple[int, int, int]
            ] = {
            Color.GREEN: (30, 140, 30),
            Color.BLUE: (30, 60, 150),
            Color.YELLOW: (180, 160, 40),
            Color.ORANGE: (200, 100, 20),
            Color.RED: (170, 40, 40),
            Color.PURPLE: (100, 40, 150),
            Color.CYAN: (30, 130, 130),
            Color.NONE: (80, 80, 80),
            Color.BROWN: (100, 60, 30),
            Color.LIME: (90, 150, 40),
            Color.MAGENTA: (140, 40, 140),
            Color.GOLD: (170, 140, 20),
            Color.WHITE: (200, 200, 200),
            Color.BLACK: (15, 15, 15),
            Color.MAROON: (90, 30, 30),
            Color.DARKRED: (110, 20, 20),
            Color.CRIMSON: (150, 20, 50),
            Color.RAINBOW: (180, 60, 180),
            Color.VIOLET: (140, 60, 190)
        }
        return color_dict[self]


class Img(Enum):
    try:
        import pygame  # type: ignore
    except ImportError as err:
        MSGError.print_error(
            f"Import Error: {err}\n"
            "Please, install pygame before any run.\n"
            "Usage:\npython3 -m venv venv"
            "\nsource venv/bin/activate"
            "\npython3 -m pip install pygame"
        )
        sys.exit(1)

    BACKGROUND = pygame.image.load('night_city_skyline_3600x800.png')
    DRONE = pygame.image.load('drone-isometric-facing-right.png')
