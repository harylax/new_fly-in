import sys
from network import Network, Zone
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
        pygame.init()
        self.network: Network = network
        self.width: int = 1200
        self.height: int = 600
        self.horizontal_scroll: int = 0
        self.vertical_scroll: int = 0

        self.hub_positions: dict[str, tuple[float, float]] = {
            hub.name: (
                hub.x * 150 + 150,
                hub.y * 100 + self.height * 0.65
                ) for hub in network.hubs
        }
        self.background: Any = Img.BACKGROUND.value
        self.screen: Any = pygame.display.set_mode((self.width, self.height))
        self.font: dict[int, Any] = {
            22: pygame.font.SysFont("Arial", 22),
            36: pygame.font.SysFont("Arial", 36)
        }

    def draw_static(self) -> None:
        self.screen.blit(self.background, (
            self.horizontal_scroll,
            self.vertical_scroll
            ))

        for link in self.network.connections:
            if link.origin and link.destination:
                x1, y1 = self.hub_positions[link.origin.name]
                x2, y2 = self.hub_positions[link.destination.name]
                x1 += self.horizontal_scroll
                x2 += self.horizontal_scroll
                y1 += self.vertical_scroll
                y2 += self.vertical_scroll
                pygame.draw.line(
                    self.screen, Color.NONE.rgb,
                    (x1, y1), (x2, y2), 3
                    )

        for hub in self.network.hubs:
            x, y = self.hub_positions[hub.name]
            x += self.horizontal_scroll
            y += self.vertical_scroll
            if hub.color == Color.NONE:
                pygame.draw.circle(self.screen, hub.color.rgb, (x, y), 20, 2)
            else:
                pygame.draw.circle(self.screen, hub.color.rgb, (x, y), 20)
            letter: str = (
                "S" if hub == self.network.start_hub
                else "G" if hub == self.network.end_hub
                else "B" if hub.zone == Zone.BLOCKED
                else hub.zone.value[0].capitalize()
            )
            initial: Any = self.font[36].render(
                letter, True, Color.WHITE.rgb
                )
            self.screen.blit(initial, initial.get_rect(center=(x, y)))
            label: Any = self.font[22].render(hub.name, True, Color.WHITE.rgb)
            self.screen.blit(label, (x - 35, y - 40))


class Animation:
    def __init__(self, static: StaticMap, simulation: Simulation) -> None:
        self.static: StaticMap = static
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
        self.progress: int = 0
        self.turn_duration: int = 1000

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

        progress_ratio: float = min(
            self.progress / self.turn_duration, 1.0
            ) if self.current_turn < self.max_turn else 0.0

        prev_state: list[
            tuple[int, str]
        ] = self.drones_moves[self.current_turn]
        next_turn: int = min(self.current_turn + 1, self.max_turn)
        next_state: list[
            tuple[int, str]
        ] = self.drones_moves[next_turn]

        for (drone_id, prev_name), (_, next_name) in zip(
            prev_state, next_state
        ):
            px, py = self.get_position(prev_name)
            nx, ny = self.get_position(next_name)
            x: float = px + (nx - px) * progress_ratio
            y: float = py + (ny - py) * progress_ratio
            x += self.static.horizontal_scroll
            y += self.static.vertical_scroll
            if prev_name == self.network.end_hub.name:
                x += end_count * 25
                end_count += 1
            else:
                if prev_name in count_drawn:
                    x += count_drawn[prev_name]
                    count_drawn[prev_name] -= 25
                else:
                    count_drawn[prev_name] = -25
            self.screen.blit(self.drone, self.drone.get_rect(center=(x, y)))
            label: Any = self.font[22].render(
                f"D{drone_id}", True, Color.YELLOW.rgb
                )
            self.screen.blit(label, (x, y - 30))


class GameMap:
    def __init__(self, static: StaticMap, animation: Animation) -> None:
        self.static: StaticMap = static
        self.animation: Animation = animation
        self.max_scroll: dict[str, int] = {
            'x': -self.static.background.get_width() + self.static.width,
            'y': -self.static.background.get_height() + self.static.height
        }
        self.running: bool = True
        self.paused: bool = True
        self.clock: Any = pygame.time.Clock()

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
                    elif event.key == pygame.K_r:
                        self.animation.current_turn = 0

            keys: Any = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                self.static.vertical_scroll += 5
            if keys[pygame.K_UP]:
                self.static.vertical_scroll -= 5
            if keys[pygame.K_LEFT]:
                self.static.horizontal_scroll += 10
            if keys[pygame.K_RIGHT]:
                self.static.horizontal_scroll -= 10

            if self.static.horizontal_scroll > 0:
                self.static.horizontal_scroll = 0
            if self.static.horizontal_scroll < self.max_scroll['x']:
                self.static.horizontal_scroll = self.max_scroll['x']
            if self.static.vertical_scroll > 0:
                self.static.vertical_scroll = 0
            if self.static.vertical_scroll < self.max_scroll['y']:
                self.static.vertical_scroll = self.max_scroll['y']

            if (
                not self.paused
                and self.animation.current_turn < self.animation.max_turn
            ):
                self.animation.progress += delta_time
                if self.animation.progress > self.animation.turn_duration:
                    self.animation.progress = 0
                    self.animation.current_turn += 1

            self.static.draw_static()
            self.animation.draw_drones()
            self.display_turn_and_status()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    pygame.init()
    from parser import RawParser
    raw = RawParser('test.txt')
    # raw = RawParser('maps/challenger/01_the_impossible_dream.txt')
    print("RAW")
    from model import MapModel
    model = MapModel(raw)
    print("MODEL")
    network = Network(model)
    print("NET")
    from pathfinder import PathFinder
    pathfinder = PathFinder(network)
    print("PATH")
    simulation = Simulation(network, pathfinder)
    print("SIM")
    simulation.solver()
    print("SIM2")
    static = StaticMap(network)
    print("STATIC")
    animation = Animation(static, simulation)
    print("ANIME")
    game = GameMap(static, animation)
    print("GAME")
    game.run_game()
    print("RUN")
