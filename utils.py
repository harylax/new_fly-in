from enum import Enum


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
    green = "green"
    blue = "blue"
    yellow = "yellow"
    orange = "orange"
    red = "red"
    purple = "purple"
    cyan = "cyan"
    none = "none"
    brown = "brown"
    lime = "lime"
    magenta = "magenta"
    gold = "gold"
    white = "white"

    @property
    def rgb(self) -> tuple[int, int, int]:
        color_dict: dict[
            Color, tuple[int, int, int]
            ] = {
            Color.green: (30, 140, 30),
            Color.blue: (30, 60, 150),
            Color.yellow: (180, 160, 40),
            Color.orange: (200, 100, 20),
            Color.red: (170, 40, 40),
            Color.purple: (100, 40, 150),
            Color.cyan: (30, 130, 130),
            Color.none: (80, 80, 80),
            Color.brown: (100, 60, 30),
            Color.lime: (90, 150, 40),
            Color.magenta: (140, 40, 140),
            Color.gold: (170, 140, 20),
            Color.white: (200, 200, 200)
        }
        return color_dict[self]
