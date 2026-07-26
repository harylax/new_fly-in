from game_map import GameMap, Zone, Drone
from pathfinder import PathFinder


class Simulation:
    def __init__(self, game_map: GameMap, pathfinder: PathFinder):
        self.game_map: GameMap = game_map
        self.pathfinder: PathFinder = pathfinder
        self.drones_moves: list[list[tuple[int, str]]] = []
        self.init_drones_pos()

    def snapshot(self) -> list[tuple[int, str]]:
        res: list[tuple[int, str]] = []
        for drone in self.game_map.drones:
            if drone.zone:
                res.append((drone.id, drone.zone.name))
        return res

    def init_drones_pos(self) -> None:
        for drone in self.game_map.drones:
            drone.zone = self.game_map.start_hub
            self.game_map.start_hub.current_drones.append(drone)
            self.game_map.start_hub.compute_hub_capacity()
        self.drones_moves.append(self.snapshot())

    def restricted_drones(self) -> dict[str, list[Drone]]:
        res: dict[str, list[Drone]] = {}
        for link in self.game_map.connections:
            if link.current_drones and link.destination:
                res.setdefault(
                    link.destination.name, []
                    ).extend(link.current_drones)
                link.current_drones.clear()
                link.compute_link_capacity()
        return res

    def free_drones(self, restricted: dict[str, list[Drone]]) -> None:
        for hub in self.game_map.hubs:
            if hub.name in restricted:
                for drone in restricted[hub.name]:
                    hub.current_drones.append(drone)
                    drone.zone = hub
                    hub.compute_hub_capacity()
                del restricted[hub.name]

    def solver(self) -> None:
        turn: int = 0
        nb_drones: int = self.game_map.nb_drones
        while len(self.game_map.end_hub.current_drones) != nb_drones:

            restricted: dict[str, list[Drone]] = self.restricted_drones()

            for hub in reversed(self.game_map.hubs):
                if self.pathfinder.is_dead_end(hub):
                    continue
                for prev in self.pathfinder.sorted_hubs(hub.previous_hubs):
                    if self.pathfinder.is_dead_end(prev):
                        continue
                    if not prev.current_drones:
                        continue
                    if hub.zone == Zone.RESTRICTED:
                        for link in self.game_map.connections:
                            if link.destination == hub and link.origin == prev:
                                capacity: int = min(
                                    link.current_capacity, hub.current_capacity
                                    )
                                i: int = 0
                                while i < capacity:
                                    if not prev.current_drones:
                                        break
                                    drone: Drone = prev.current_drones.pop(0)
                                    link.current_drones.append(drone)
                                    drone.zone = link
                                    link.compute_link_capacity()
                                    prev.compute_hub_capacity()
                                    i += 1
                    else:
                        for link in self.game_map.connections:
                            if link.destination == hub and link.origin == prev:
                                capacity = min(
                                    link.current_capacity, hub.current_capacity
                                )
                                i = 0
                                while i < capacity:
                                    if not prev.current_drones:
                                        break
                                    drone = prev.current_drones.pop(0)
                                    hub.current_drones.append(drone)
                                    drone.zone = hub
                                    hub.compute_hub_capacity()
                                    prev.compute_hub_capacity()
                                    i += 1

            self.free_drones(restricted)

            turn += 1

            self.drones_moves.append(self.snapshot())


if __name__ == "__main__":
    easy1 = 'maps/easy/01_linear_path.txt'
    easy2 = 'maps/easy/02_simple_fork.txt'
    easy3 = 'maps/easy/03_basic_capacity.txt'
    med1 = 'maps/medium/01_dead_end_trap.txt'
    med2 = 'maps/medium/02_circular_loop.txt'
    med3 = 'maps/medium/03_priority_puzzle.txt'
    hard1 = 'maps/hard/01_maze_nightmare.txt'
    hard2 = 'maps/hard/02_capacity_hell.txt'
    hard3 = 'maps/hard/03_ultimate_challenge.txt'
    hard4 = 'maps/challenger/01_the_impossible_dream.txt'

    from parser import RawParser
    raw = RawParser(hard4)
    from model import MapModel
    model = MapModel(raw)
    game_map = GameMap(model)
    pathfinder = PathFinder(game_map)
    sim = Simulation(game_map, pathfinder)
    sim.solver()

    result: list[str] = []
    for i, moves in enumerate(sim.drones_moves):
        line = ''
        for drone_id, hub_name in moves:
            line += f"D{drone_id}-{hub_name} "
        result.append(f"turn {i}: {line}")

    for res in result:
        print(res)
