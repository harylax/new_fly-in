"""Shared utilities, enumerations and constants for Fly-in 42.

Provides colored terminal output helpers, RGB color definitions used
by the graphical view, map-file path tables and pre-loaded pygame images.
"""

from enum import Enum
import sys
try:
    import pygame  # type: ignore
except ImportError as err:
    print(
        "\033[91m"
        f"Import Error: {err}\n"
        "Please, install pygame before any run.\n"
        "Usage:\npython3 -m venv .venv"
        "\nsource venv/bin/activate"
        "\npython3 -m pip install pygame"
        "\033[0m"
    )
    sys.exit(1)


class MSGError:
    """Static helper that prints error messages to stderr in red."""

    @staticmethod
    def print_error(msg: str) -> None:
        """Print an error message to stderr using ANSI red coloring.

        Args:
            msg: Error text.
        """
        print(
            f"{Ansi.RED.value}"
            f"{msg}"
            f"{Ansi.RESET.value}",
            file=sys.stderr
        )


class Ansi(Enum):
    """ANSI escape sequences for colored terminal output."""

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
    """Named colors used both for map metadata and for pygame rendering.

    Each member exposes an 'rgb' property that returns the corresponding
    '(R, G, B)' tuple suitable for pygame drawing calls.
    """

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
        """Return the RGB triple associated with this color.

        Returns:
            Tuple '(R, G, B)' with integer components in '[0, 255]'.
        """
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


class MapFile:
    """Catalogue of pre-defined map file paths organised by difficulty.

    Attributes:
        default: Single default map.
        easy: Easy difficulty maps.
        medium: Medium difficulty maps.
        hard: Hard difficulty maps.
        challenger: Extremely difficult challenger maps.
    """

    def __init__(self) -> None:
        """Populate the path dictionaries for every difficulty level."""
        self.default: dict[int, str] = {
            1: "maps/default/01_default_map.txt"
        }
        self.easy: dict[int, str] = {
            1: "maps/easy/01_linear_path.txt",
            2: "maps/easy/02_simple_fork.txt",
            3: "maps/easy/03_basic_capacity.txt"
        }
        self.medium: dict[int, str] = {
            1: "maps/medium/01_dead_end_trap.txt",
            2: "maps/medium/02_circular_loop.txt",
            3: "maps/medium/03_priority_puzzle.txt"
        }
        self.hard: dict[int, str] = {
            1: "maps/hard/01_maze_nightmare.txt",
            2: "maps/hard/02_capacity_hell.txt",
            3: "maps/hard/03_ultimate_challenge.txt"
        }
        self.challenger: dict[int, str] = {
            1: "maps/challenger/01_the_impossible_dream.txt"
        }


class Img(Enum):
    """Pre-loaded pygame Surfaces used by the graphical visualiser."""

    BACKGROUND = pygame.image.load('night_city_skyline_3600x800.png')
    DRONE = pygame.image.load('drone-isometric-facing-right.png')
