"""Interactive terminal menu for the Fly-in 42 drone simulation.

Provides a text-based user interface that lets the player choose a map
by difficulty, launch the simulation, display textual turn-by-turn
output and optionally start the graphical animation.
"""

import sys
from utils import Ansi, MapFile, MSGError
from parser import RawParser
from model import MapModel
from network import Network
from pathfinder import PathFinder
from output import Output
from simulation import Simulation
from visual import StaticMap, Animation, GameMap


class Menu:
    """Text-based menu system driving the whole application.

    Displays ASCII art titles, difficulty selectors and map pickers.
    Once a map is chosen the simulation is run and the user is offered
    the option to watch a pygame animation.

    Attributes:
        title: Multi-line ASCII banner shown on every screen.
        main_menu: Text of the top-level choices.
        difficulty: Text of the difficulty selection screen.
        exit_message: Farewell banner displayed on quit.
        easy / medium / hard / challenger: Per-difficulty map lists.
    """

    def __init__(self) -> None:
        """Initialize all menu text strings and ASCII art."""
        self._title: str = (
            "╔════════════════════════════════════════════════════╗\n"
            "║                                                    ║\n"
            "║    ███████╗██╗     ██╗   ██╗      ██╗███╗   ██╗    ║\n"
            "║    ██╔════╝██║     ╚██╗ ██╔╝      ██║████╗  ██║    ║\n"
            "║    █████╗  ██║      ╚████╔╝ █████╗██║██╔██╗ ██║    ║\n"
            "║    ██╔══╝  ██║       ╚██╔╝  ╚════╝██║██║╚██╗██║    ║\n"
            "║    ██║     ███████╗   ██║         ██║██║ ╚████║    ║\n"
            "║    ╚═╝     ╚══════╝   ╚═╝         ╚═╝╚═╝  ╚═══╝    ║\n"
            "║                                                    ║\n"
            "║         42 Drone Simulation - by haryandr          ║\n"
            "╚════════════════════════════════════════════════════╝"
        )
        self._main_menu: str = (
            "[1] 🚀 Run default map\n\n"
            "[2] 🗺️ Choose map\n\n"
            "[3] 📂 Enter your existing map path\n\n"
            "[4] ❌ Quit\n\n"
            "──────────────────────────────────────────────────────\n"
        )
        self._difficulty: str = (
            "Choose difficulty\n\n"
            "\t[1] 🟢 Easy\n"
            "\t[2] 🟡 Medium\n"
            "\t[3] 🔴 Hard\n"
            "\t[4] 💀 Challenger\n"
            "\n\t[0] ← Back\n\n"
            "──────────────────────────────────────────────────────\n"
        )
        self._exit_message: str = (
            "══════════════════════════════════════════════════════\n\n"
            "\t   Thank you for using Fly-in 42\n\n"
            "\t\tHave a nice flight ✈\n\n"
            "\t\t      Bye bye!\n\n"
            "══════════════════════════════════════════════════════"
        )
        self._easy: str = (
            f"{Ansi.GREEN.value}"
            "Easy maps\n\n"
            "\t[1] Linear path\n"
            "\t[2] Simple fork\n"
            "\t[3] Basic capacity\n"
            f"{Ansi.RESET.value}"
            "\n\t[0] ← Back\n"
            "──────────────────────────────────────────────────────\n"
        )
        self._medium: str = (
            f"{Ansi.BLUE.value}"
            "Medium maps\n\n"
            "\t[1] Dead end trap\n"
            "\t[2] Circular loop\n"
            "\t[3] Priority puzzle\n"
            f"{Ansi.RESET.value}"
            "\n\t[0] ← Back\n"
            "──────────────────────────────────────────────────────\n"
        )
        self._hard: str = (
            f"{Ansi.YELLOW.value}"
            "Hard maps\n\n"
            "\t[1] Maze nightmare\n"
            "\t[2] Capacity Hell\n"
            "\t[3] Ultimate challenge\n"
            f"{Ansi.RESET.value}"
            "\n\t[0] ← Back\n"
            "──────────────────────────────────────────────────────\n"
        )
        self._challenger: str = (
            f"{Ansi.RED.value}"
            "Challenger\n\n"
            "\t[1] The impossible dream\n"
            f"{Ansi.RESET.value}"
            "\n\t[0] ← Back\n"
            "──────────────────────────────────────────────────────\n"
        )

    def _home(self) -> int:
        """Display the main menu and return the user's numeric choice.

        Returns:
            Integer option (1-4) or '-1' on invalid input.
        """
        print(Ansi.CLEAR.value, end="")
        print(f"{self._title}")
        print(self._main_menu)
        print("Choose an option [1-4] > ", end="")
        try:
            return int(input())
        except ValueError:
            return -1

    def quit(self) -> None:
        """Print the farewell message and terminate the process."""
        print(self._exit_message)
        sys.exit(0)

    def _default_map(self) -> None:
        """Launch the simulation with a pre-built default map."""
        self.launch(MapFile().default[1])

    def _custom_map(self) -> None:
        """Prompt the user for a custom map path and launch it."""
        print(Ansi.CLEAR.value, end="")
        print(f"{self._title}")
        print(self._main_menu)
        print("Enter your map.txt file path\n")
        path: str = input("Path > ")
        try:
            self.launch(path)
        except UnicodeDecodeError as err:
            MSGError.print_error(
                f"Unicode Decode Error: {err}"
            )
            sys.exit(1)

    def launch(self, path: str) -> None:
        """Parse, solve and display a map.

        Optionally start the Graphical Visualization.

        Args:
            path: Filesystem or archive-relative path of the map file.
        """
        raw: RawParser = RawParser(path)
        model: MapModel = MapModel(raw)
        network: Network = Network(model)
        pathfinder: PathFinder = PathFinder(network)
        simulation: Simulation = Simulation(network, pathfinder)
        simulation.solver()
        output: list[str] = Output(network, simulation).simulation_output()
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self._title}")
            print(
                "──────────────────────────────────────────────────────\n"
                "Do you want to enable graphical animation?"
                )
            choice: str = input("\nYour choice [Y/n] ").strip().lower()
            if choice in ['y', 'yes', 'n', 'no']:
                break

        print(Ansi.CLEAR.value, end="")

        for line in output:
            print(line)

        if choice in ['y', 'yes']:
            static: StaticMap = StaticMap(network)
            animation: Animation = Animation(static, simulation)
            game: GameMap = GameMap(static, animation)
            game.run_game()
        self.quit()

    def _choose_difficulty(self) -> None:
        """Display the difficulty selector, dispatch to the matching menu."""
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self._title}")
            print(self._difficulty)
            print("Choose [1-4][0] > ", end="")
            try:
                x = int(input())
            except ValueError:
                continue
            if x == 1:
                self._easy_menu()
            elif x == 2:
                self._medium_menu()
            elif x == 3:
                self._hard_menu()
            elif x == 4:
                self._challenger_menu()
            elif x == 0:
                return

    def _easy_menu(self) -> None:
        """Display the easy-map picker and launch the chosen map."""
        map: dict[int, str] = MapFile().easy
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self._title}")
            print(self._easy)
            print("Choose [1-3][0] > ", end="")
            try:
                x = int(input())
            except ValueError:
                continue
            if x == 1:
                self.launch(map[1])
            elif x == 2:
                self.launch(map[2])
            elif x == 3:
                self.launch(map[3])
            elif x == 0:
                return

    def _medium_menu(self) -> None:
        """Display the medium-map picker and launch the chosen map."""
        map: dict[int, str] = MapFile().medium
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self._title}")
            print(self._medium)
            print("Choose [1-3][0] > ", end="")
            try:
                x = int(input())
            except ValueError:
                continue
            if x == 1:
                self.launch(map[1])
            elif x == 2:
                self.launch(map[2])
            elif x == 3:
                self.launch(map[3])
            elif x == 0:
                return

    def _hard_menu(self) -> None:
        """Display the hard-map picker and launch the chosen map."""
        map: dict[int, str] = MapFile().hard
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self._title}")
            print(self._hard)
            print("Choose [1-3][0] > ", end="")
            try:
                x = int(input())
            except ValueError:
                continue
            if x == 1:
                self.launch(map[1])
            elif x == 2:
                self.launch(map[2])
            elif x == 3:
                self.launch(map[3])
            elif x == 0:
                return

    def _challenger_menu(self) -> None:
        """Display the challenger-map picker and launch the chosen map."""
        map: dict[int, str] = MapFile().challenger
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self._title}")
            print(self._challenger)
            print("Choose [1][0] > ", end="")
            try:
                x = int(input())
            except ValueError:
                continue
            if x == 1:
                self.launch(map[1])
            elif x == 0:
                return

    def run_terminal(self) -> None:
        """Run main interactive loop of the terminal interface."""
        while True:
            x: int = self._home()
            if x == 1:
                self._default_map()
            elif x == 2:
                self._choose_difficulty()
            elif x == 3:
                self._custom_map()
            elif x == 4:
                print(Ansi.CLEAR.value, end="")
                self.quit()
