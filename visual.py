import sys
from network import Network
from simulation import Simulation
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
        self.hub_positions: dict[str, tuple[float, float]] = {
            hub.name: self.to_screen(hub.x, hub.y) for hub in network.hubs
        }
        self.background: Any = pygame.transform.smoothscale(
            Img.BACKGROUND.value, (self.width, self.height)
            )
        self.screen: Any = pygame.display.set_mode((self.width, self.height))
        self.font: dict[int, Any] = {
            22: pygame.font.SysFont(None, 22),
            36: pygame.font.SysFont(None, 36)
        }
        self.legends: dict[str, Color] = {
            hub.name.strip('0123456789'): hub.color for hub in network.hubs
        }

    def draw_static(self) -> None:
        self.screen.blit(self.background, (0, 0))

        spacing: int = 30
        pos: int = spacing
        for name in self.legends:
            pygame.draw.circle(
                self.screen, self.legends[name].rgb, (spacing, pos), 10
                )
            label: Any = self.font[22].render(name, True, Color.WHITE.rgb)
            self.screen.blit(label, (spacing + 15, pos - 8))
            pos += spacing

        for link in self.network.connections:
            if link.origin and link.destination:
                pos1: tuple[
                    float, float
                    ] = self.hub_positions[link.origin.name]
                pos2: tuple[
                    float, float
                    ] = self.hub_positions[link.destination.name]
                pygame.draw.line(self.screen, Color.WHITE.rgb, pos1, pos2, 3)

        for hub in self.network.hubs:
            x, y = self.hub_positions[hub.name]
            pygame.draw.circle(self.screen, hub.color.rgb, (x, y), 20)
            letter: str = (
                "S" if hub == self.network.start_hub
                else "G" if hub == self.network.end_hub
                else hub.zone.value[0].capitalize()
            )
            initial: Any = self.font[36].render(
                letter, True, Color.WHITE.rgb
                )
            self.screen.blit(initial, initial.get_rect(center=(x, y)))

    def to_screen(self, x: int, y: int) -> tuple[float, float]:
        margin: int = 150

        xs: list[int] = [hub.x for hub in self.network.hubs]
        ys: list[int] = [hub.y for hub in self.network.hubs]

        min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)

        range_x: int = (max_x - min_x) or 1
        range_y: int = (max_y - min_y) or 1

        pos_x_ratio: float = (x - min_x) / range_x
        pos_y_ratio: float = (y - min_y) / range_y

        width: int = self.width - 2 * margin
        height: int = self.height - 2 * margin

        ratio_x_on_screen: float = pos_x_ratio * width
        ratio_y_on_screen: float = pos_y_ratio * height

        sx: float = ratio_x_on_screen + margin + 50
        sy: float = ratio_y_on_screen + margin

        return (sx, sy)


class Animation:
    def __init__(self, static: StaticMap, simulation: Simulation) -> None:
        self.network: Network = static.network
        self.drone: Any = pygame.transform.smoothscale(
            Img.DRONE.value, (60, 60)
            )
        self.hub_positions: dict[
            str, tuple[float, float]
            ] = static.hub_positions
        self.screen = static.screen
        self.font = static.font
        self.drones_moves: list[
            list[tuple[int, str]]
            ] = simulation.drones_moves
        self.current_turn: int = 0
        self.max_turn: int = len(simulation.drones_moves) - 1

    def get_position(self, name: str) -> tuple[float, float]:
        for link in self.network.connections:
            if link.name == name and link.origin and link.destination:
                x1, y1 = self.hub_positions[link.origin.name]
                x2, y2 = self.hub_positions[link.destination.name]
                pos: tuple[float, float] = (
                    (x1 + x2) / 2,
                    (y1 + y2) / 2
                )
                return pos
        return self.hub_positions[name]

    def draw_drones(self) -> None:
        count_drawn: dict[str, int] = {}
        end_count: int = 0
        for drone_id, name in self.drones_moves[self.current_turn]:
            x, y = self.get_position(name)
            if name == self.network.end_hub.name:
                x += end_count * 20
                end_count += 1
            else:
                if name in count_drawn:
                    x += count_drawn[name]
                    count_drawn[name] -= 20
                else:
                    count_drawn[name] = -20
            self.screen.blit(self.drone, self.drone.get_rect(center=(x, y)))
            label: Any = self.font[22].render(
                f"D{drone_id}", True, Color.YELLOW.rgb
                )
            self.screen.blit(label, (x, y - 30))


class GameMap:
    def __init__(self, static: StaticMap, animation: Animation) -> None:
        self.static: StaticMap = static
        self.animation: Animation = animation
        self.running: bool = True
        self.paused: bool = True
        self.clock: Any = pygame.time.Clock()
        self.progress: int = 0
        self.turn_duration: int = 1000

    def display_turn_and_status(self) -> None:
        status: str = " [PAUSED]" if self.paused else ""
        text: str = (
            f"Turn {self.animation.current_turn}/"
            f"{self.animation.max_turn}{status}"
        )
        label: Any = self.static.font[36].render(text, True, Color.BLACK.rgb)
        x: int = self.static.width // 2 - 100
        y: int = 10
        padding: int = 10
        pygame.draw.rect(self.static.screen, Color.WHITE.rgb, (
            x - padding, y - padding,
            label.get_width() + padding * 2,
            label.get_height() + padding * 2
            )
        )
        self.static.screen.blit(label, (x, y))

    def run_game(self) -> None:
        while self.running:
            delta_time: Any = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key in [pygame.K_r]:
                        self.animation.current_turn = 0

            if (
                not self.paused
                and self.animation.current_turn < self.animation.max_turn
            ):
                self.progress += delta_time
                if self.progress > self.turn_duration:
                    self.progress = 0
                    self.animation.current_turn += 1

            self.static.draw_static()
            self.animation.draw_drones()
            self.display_turn_and_status()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    from parser import RawParser
    # raw = RawParser('test.txt')
    raw = RawParser('maps/challenger/01_the_impossible_dream.txt')
    from model import MapModel
    model = MapModel(raw)
    network = Network(model)
    from pathfinder import PathFinder
    pathfinder = PathFinder(network)
    simulation = Simulation(network, pathfinder)
    simulation.solver()
    static = StaticMap(network)
    animation = Animation(static, simulation)
    game = GameMap(static, animation)
    game.run_game()
