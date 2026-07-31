import sys
from utils import Ansi, MapFile
from parser import RawParser
from model import MapModel
from network import Network, Hub, Connection
from pathfinder import PathFinder
from simulation import Simulation
from visual import StaticMap
from visual import Animation
from visual import GameMap


class Menu:
    def __init__(self) -> None:
        self.title: str = (
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
        self.main_menu: str = (
            "[1] 🚀 Run default map\n\n"
            "[2] 🗺️ Choose map\n\n"
            "[3] 📂 Enter your existing map path\n\n"
            "[4] ❌ Quit\n\n"
            "──────────────────────────────────────────────────────\n"
        )
        self.difficulty: str = (
            "Choose difficulty\n\n"
            "\t[1] 🟢 Easy\n"
            "\t[2] 🟡 Medium\n"
            "\t[3] 🔴 Hard\n"
            "\t[4] 💀 Challenger\n"
            "\n\t[0] ← Back\n\n"
            "──────────────────────────────────────────────────────\n"
        )
        self.exit_message: str = (
            "══════════════════════════════════════════════════════\n\n"
            "\t   Thank you for using Fly-in 42\n\n"
            "\t\tHave a nice flight ✈\n\n"
            "\t\t      Bye bye!\n\n"
            "══════════════════════════════════════════════════════"
        )
        self.easy: str = (
            f"{Ansi.GREEN.value}"
            "Easy maps\n\n"
            "\t[1] Linear path\n"
            "\t[2] Simple fork\n"
            "\t[3] Basic capacity\n"
            f"{Ansi.RESET.value}"
            "\n\t[0] ← Back\n"
            "──────────────────────────────────────────────────────\n"
        )
        self.medium: str = (
            f"{Ansi.BLUE.value}"
            "Medium maps\n\n"
            "\t[1] Dead end trap\n"
            "\t[2] Circular loop\n"
            "\t[3] Priority puzzle\n"
            f"{Ansi.RESET.value}"
            "\n\t[0] ← Back\n"
            "──────────────────────────────────────────────────────\n"
        )
        self.hard: str = (
            f"{Ansi.YELLOW.value}"
            "Hard maps\n\n"
            "\t[1] Maze nightmare\n"
            "\t[2] Capacity Hell\n"
            "\t[3] Ultimate challenge\n"
            f"{Ansi.RESET.value}"
            "\n\t[0] ← Back\n"
            "──────────────────────────────────────────────────────\n"
        )
        self.challenger: str = (
            f"{Ansi.RED.value}"
            "Challenger\n\n"
            "\t[1] The impossible dream\n"
            f"{Ansi.RESET.value}"
            "\n\t[0] ← Back\n"
            "──────────────────────────────────────────────────────\n"
        )

    def home(self) -> int:
        print(Ansi.CLEAR.value, end="")
        print(f"{self.title}")
        print(self.main_menu)
        print("Choose an option [1-4] > ", end="")
        try:
            return int(input())
        except ValueError:
            return -1

    def quit(self) -> None:
        print(self.exit_message)
        sys.exit(0)

    def default_map(self) -> None:
        self.launch(MapFile().default[1])

    def custom_map(self) -> None:
        print(Ansi.CLEAR.value, end="")
        print(f"{self.title}")
        print(self.main_menu)
        print("Enter your map path\n")
        path: str = input("Path > ")
        self.launch(path)

    def simulation_output(
            self,
            moves: list[list[tuple[int, str]]],
            hubs: list[Hub],
            connections: list[Connection]
            ) -> list[str]:
        result: list[str] = []
        last_track: list[tuple[int, str]] = []
        for i in range(1, len(moves[1:-1])):
            line = ''
            last_track.clear()
            if i > 1:
                last_track.extend(moves[i - 1])
            for drone_id, zone_name in moves[i]:
                if (drone_id, zone_name) in last_track:
                    continue

                for link in connections:
                    if zone_name == link.name:
                        line += f"D{drone_id}-{zone_name} [CONNECTION] "
                for hub in hubs:
                    if hub in [hubs[0], hubs[-1]]:
                        continue
                    if zone_name == hub.name:
                        try:
                            ansi: str = Ansi[hub.color.name].value
                        except KeyError:
                            ansi = Ansi.WHITE.value
                        line += (
                            f"{ansi}D{drone_id}-"
                            f"{zone_name}"
                            f" [{hub.zone.name}] "
                            f"{Ansi.RESET.value}"
                            )
            result.append(f"turn {i}: {line}")

        title: str = (
            f"{Ansi.CYAN.value}{Ansi.BOLD.value}"
            "──────────────────────────────────────────────────────\n"
            "\t\t>>>Simulation Output<<<\n"
            "──────────────────────────────────────────────────────\n"
            f"{Ansi.RESET.value}"
        )
        result.insert(0, title)
        return result

    def launch(self, path: str) -> None:
        raw: RawParser = RawParser(path)
        model: MapModel = MapModel(raw)
        network: Network = Network(model)
        pathfinder: PathFinder = PathFinder(network)
        simulation: Simulation = Simulation(network, pathfinder)
        simulation.solver()
        output: list[str] = self.simulation_output(
            simulation.drones_moves, network.hubs, network.connections
            )
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self.title}")
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

    def choose_difficulty(self) -> None:
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self.title}")
            print(self.difficulty)
            print("Choose [1-4][0] > ", end="")
            try:
                x = int(input())
            except ValueError:
                continue
            if x == 1:
                self.easy_menu()
            elif x == 2:
                self.medium_menu()
            elif x == 3:
                self.hard_menu()
            elif x == 4:
                self.challenger_menu()
            elif x == 0:
                return

    def easy_menu(self) -> None:
        map: dict[int, str] = MapFile().easy
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self.title}")
            print(self.easy)
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

    def medium_menu(self) -> None:
        map: dict[int, str] = MapFile().medium
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self.title}")
            print(self.medium)
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

    def hard_menu(self) -> None:
        map: dict[int, str] = MapFile().hard
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self.title}")
            print(self.hard)
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

    def challenger_menu(self) -> None:
        map: dict[int, str] = MapFile().challenger
        while True:
            print(Ansi.CLEAR.value, end="")
            print(f"{self.title}")
            print(self.challenger)
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
        while True:
            x: int = self.home()
            if x == 1:
                self.default_map()
            elif x == 2:
                self.choose_difficulty()
            elif x == 3:
                self.custom_map()
            elif x == 4:
                print(Ansi.CLEAR.value, end="")
                self.quit()


if __name__ == "__main__":
    menu: Menu = Menu()
    menu.run_terminal()
