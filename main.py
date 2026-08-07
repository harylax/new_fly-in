#!/usr/bin/env python3

"""Entry point of the Fly-in 42 drone simulation application.

This module launches the interactive terminal menu that allows the user
to select a map, run the simulation and optionally display a graphical
animation of the drones' movements.
"""
from parser import RawParser
from model import MapModel
from network import Network
from pathfinder import PathFinder
from simulation import Simulation
from output import Output
from terminal import Menu
from utils import MSGError
from visual import StaticMap, Animation, GameMap
import sys


class Main:
    """Application entry point.

    Instantiates the terminal menu and handles the main execution loop.
    """

    def __init__(self) -> None:
        """Initialize the Main controller with a Menu instance."""
        self.menu: Menu = Menu()

    def run(self) -> None:
        """Start the terminal interface and handle user interruption."""
        try:
            self.menu.run_terminal()
        except KeyboardInterrupt:
            print()
            self.menu.quit()

    def parse_args(self, argv: list[str]) -> tuple[str | None, bool]:
        """Parse command-line arguments for CLI mode.

        Accepted forms:
            []                       -> interactive menu
            [map_file.txt]           -> run the map without animation
            [--visual, map_file.txt] -> run the map with pygame animation

        Args:
            argv: Command-line arguments (sys.argv[1:]).

        Returns:
            A tuple '(map_path, with_visual)' where 'map_path' is the
            path to the map file or 'None', and 'with_visual' indicates
            whether the graphical animation was requested.
        """
        map_path: str | None = None
        with_visual: bool = False
        unknown: list[str] = []

        if not argv:
            return (map_path, with_visual)

        for arg in argv:
            if arg.endswith('.txt'):
                if map_path:
                    MSGError.print_error(
                        "CLI Error: only one map file is allowed.\n"
                        "Usage: python3 main.py --visual map_file.txt"
                        )
                    sys.exit(1)
                map_path = arg
            elif arg == '--visual':
                with_visual = True
            else:
                unknown.append(arg)

        if unknown:
            MSGError.print_error(
                f"CLI Error: unknown option(s): {', '.join(
                    opt for opt in unknown
                    )}\n"
                "Usage: python3 main.py --visual map_file.txt"
                )
            sys.exit(1)

        return (map_path, with_visual)

    def run_cli(self, map_path: str | None, with_visual: bool = False) -> None:
        """Run a map from the command line without the interactive menu.

        Args:
            map_path: Path to the map definition file.
            with_visual: If True, open the graphical viewer.
        """
        if not map_path:
            MSGError.print_error(
                "CLI Error: --visual requires a map file.\n"
                "Usage: python3 main.py --visual map_file.txt"
                )
            sys.exit(1)
        raw = RawParser(map_path)
        model: MapModel = MapModel(raw)
        network: Network = Network(model)
        pathfinder: PathFinder = PathFinder(network)
        simulation: Simulation = Simulation(network, pathfinder)
        simulation.solver()
        output: Output = Output(network, simulation)
        for line in output.simulation_output():
            print(line)
        if with_visual:
            static: StaticMap = StaticMap(network)
            animation: Animation = Animation(static, simulation)
            game: GameMap = GameMap(static, animation)
            try:
                game.run_game()
            except KeyboardInterrupt:
                print()
                self.menu.quit()
        self.menu.quit()


if __name__ == "__main__":
    main: Main = Main()
    try:
        map_path, with_visual = main.parse_args(sys.argv[1:])
        if not map_path and not with_visual:
            main.run()
        else:
            main.run_cli(map_path, with_visual)
    except Exception as err:
        MSGError.print_error(f"Unexpected Error: {err}")
