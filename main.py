"""Entry point of the Fly-in 42 drone simulation application.

This module launches the interactive terminal menu that allows the user
to select a map, run the simulation and optionally display a graphical
animation of the drones' movements.
"""
from terminal import Menu
from utils import MSGError


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


if __name__ == "__main__":
    try:
        Main().run()
    except Exception as err:
        MSGError.print_error(f"Unexpected Error: {err}")
