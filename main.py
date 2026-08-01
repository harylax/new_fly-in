from terminal import Menu
from utils import MSGError


class Main:
    def __init__(self) -> None:
        self.menu: Menu = Menu()

    def run(self) -> None:
        try:
            self.menu.run_terminal()
        except KeyboardInterrupt:
            print()
            self.menu.quit()


if __name__ == "__main__":
    # try:
    #     Main().run()
    # except Exception as err:
    #     MSGError.print_error(f"Unexpected Error: {err}")
    Main().run()