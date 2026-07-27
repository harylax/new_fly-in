import sys
from network import Network
from utils import Img, Color, MSGError
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
from typing import Any


class StaticMap:
    def __init__(self, network: Network) -> None:
        self.network: Network = network
        self.width: int = 1200
        self.height: int = 600
        self.hub_positions: dict[str, tuple[int, int]] = {
            hub.name: self.to_screen(hub.x, hub.y) for hub in network.hubs
        }
        self.background: Any = pygame.transform.smoothscale(
            Img.BACKGROUND.value, (self.width, self.height)
            )
        self.screen: Any = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont(None, 22)

    def draw_static(self) -> None:
        self.screen.blit(self.background, (0, 0))

        for link in self.network.connections:
            if link.origin and link.destination:
                pos1: tuple[int, int] = self.hub_positions[link.origin.name]
                pos2: tuple[int, int] = \
                    self.hub_positions[link.destination.name]
                pygame.draw.line(self.screen, Color.WHITE.rgb, pos1, pos2, 3)

        for hub in self.network.hubs:
            x, y = self.hub_positions[hub.name]
            pygame.draw.circle(self.screen, hub.color.rgb, (x, y), 20)
            label: Any = self.font.render(hub.name, True, Color.WHITE.rgb)
            self.screen.blit(label, (x - label.get_width() // 2, y - 40))

    def to_screen(self, x: int, y: int) -> tuple[int, int]:
        margin: int = 150

        xs: list[int] = [hub.x for hub in self.network.hubs]
        ys: list[int] = [hub.y for hub in self.network.hubs]

        min_x: int = min(xs)
        max_x: int = max(xs)
        min_y: int = min(ys)
        max_y: int = max(ys)

        range_x: int = (max_x - min_x) or 1
        range_y: int = (max_y - min_y) or 1

        pos_x_ratio: float = (x - min_x) / range_x
        pos_y_ratio: float = (y - min_y) / range_y

        ratio_x_on_screen: float = pos_x_ratio * (self.width - 2 * margin)
        ratio_y_on_screen: float = pos_y_ratio * (self.height - 2 * margin)

        sx: int = int(ratio_x_on_screen + margin)
        sy: int = int(ratio_y_on_screen + margin)

        return (sx, sy)


class Animation:
    def __init__(self, static: StaticMap) -> None:
        self.network: Network = static.network
        self.hub_positions: dict[str, tuple[int, int]] = static.hub_positions
        self.screen = static.screen
        self.font = static.font
        ...


class GameMap:
    def __init__(self, static: StaticMap) -> None:
        self.static: StaticMap = static
        self.running: bool = True
        self.paused: bool = True
        self.clock: Any = pygame.time.Clock()

    def run_game(self) -> None:
        while self.running:
            _: Any = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused

            self.static.draw_static()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    from parser import RawParser
    raw = RawParser('test.txt')
    from model import MapModel
    model = MapModel(raw)
    net = Network(model)
    static = StaticMap(net)
    # for name, pos in static.hub_positions.items():
    #     print(f"{name}: {pos}")

    game = GameMap(static)
    game.run_game()
