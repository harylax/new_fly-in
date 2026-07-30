from argparse import ArgumentParser
from terminal import Menu


class Main:
    def __init__(self) -> None:
        self.parser: ArgumentParser = ArgumentParser()
        self.parser.add_argument('--map')
        self.args = self.parser.parse_args()
        print(self.args)
        print(self.args)

    def run(self) -> None:
        menu: Menu = Menu()
        try:
            if self.args.map:
                menu.launch(self.args.map)
            else:
                menu.run_terminal()
        except KeyboardInterrupt:
            print()
            menu.quit()


if __name__ == "__main__":
    Main().run()
