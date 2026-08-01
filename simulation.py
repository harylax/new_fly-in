from network import Network, Zone, Drone, Hub
from pathfinder import PathFinder


class Simulation:
    def __init__(self, network: Network, pathfinder: PathFinder):
        self.network: Network = network
        self.pathfinder: PathFinder = pathfinder
        self.drones_moves: list[list[tuple[int, str]]] = []
        self.init_drones_pos()

    def snapshot(self) -> list[tuple[int, str]]:
        res: list[tuple[int, str]] = []
        for drone in self.network.drones:
            if drone.zone:
                res.append((drone.id, drone.zone.name))
        return res

    def init_drones_pos(self) -> None:
        for drone in self.network.drones:
            drone.zone = self.network.start_hub
            self.network.start_hub.current_drones.append(drone)
            self.network.start_hub.compute_hub_capacity()
        self.drones_moves.append(self.snapshot())

    def restricted_drones(self) -> dict[str, list[Drone]]:
        res: dict[str, list[Drone]] = {}
        for link in self.network.connections:
            if link.current_drones and link.destination:
                res.setdefault(
                    link.destination.name, []
                    ).extend(link.current_drones)
                link.current_drones.clear()
                link.compute_link_capacity()
        return res

    def free_drones(self, restricted: dict[str, list[Drone]]) -> None:
        for hub in self.network.hubs:
            if hub.name in restricted:
                for drone in restricted[hub.name]:
                    hub.current_drones.append(drone)
                    drone.zone = hub
                    hub.compute_hub_capacity()
                del restricted[hub.name]

    def move_drones(self, unmoved: set[int]) -> None:
        moved: set[int] = set()
        for path in self.pathfinder.paths:
            if len(moved) == self.network.nb_drones:
                break
            for i in range(len(path) - 1, 0, -1):
                hub: Hub = path[i]
                prev: Hub = path[i - 1]
                if not prev.current_drones:
                    continue
                if hub == self.network.start_hub:
                    break
                # if hub.zone is Zone.RESTRICTED and all(nxt.zone is Zone.RESTRICTED for nxt in hub.next_hubs):
                #     for link in self.network.connections:
                #         if link.destination is not hub and link.origin == prev:
                #             if not link.destination or self.pathfinder.is_dead_end(link.destination):
                #                 continue
                #             while True:
                #                 candidates = [
                #                     dr for dr in prev.current_drones
                #                     if dr.id not in moved
                #                 ]
                #                 capacity = min(
                #                     link.current_capacity,
                #                     link.destination.current_capacity,
                #                     len(candidates)
                #                     )
                #                 if capacity <= 0 or not candidates:
                #                     break
                #                 drone = candidates[0]
                #                 prev.current_drones.remove(drone)
                #                 link.destination.current_drones.append(drone)
                #                 drone.zone = hub
                #                 link.compute_link_capacity()
                #                 prev.compute_hub_capacity()
                #                 link.destination.compute_hub_capacity()
                #                 moved.add(drone.id)
                #                 unmoved.remove(drone.id)
                if hub.zone is Zone.RESTRICTED:
                    for link in self.network.connections:
                        if link.destination == hub and link.origin == prev:
                            while True:
                                candidates = [
                                    dr for dr in prev.current_drones
                                    if dr.id not in moved
                                ]
                                capacity = min(
                                    link.current_capacity,
                                    hub.current_capacity,
                                    len(candidates)
                                    )
                                if capacity <= 0 or not candidates:
                                    break
                                drone = candidates[0]
                                prev.current_drones.remove(drone)
                                link.current_drones.append(drone)
                                drone.zone = link
                                link.compute_link_capacity()
                                prev.compute_hub_capacity()
                                hub.compute_hub_capacity()
                                moved.add(drone.id)
                                unmoved.remove(drone.id)
                else:
                    for link in self.network.connections:
                        if link.destination == hub and link.origin == prev:
                            while True:
                                candidates = [
                                    dr for dr in prev.current_drones
                                    if dr.id not in moved
                                ]
                                capacity = min(
                                    link.current_capacity,
                                    hub.current_capacity,
                                    len(candidates)
                                    )
                                if capacity <= 0 or not candidates:
                                    break
                                drone = candidates[0]
                                prev.current_drones.remove(drone)
                                hub.current_drones.append(drone)
                                drone.zone = hub
                                link.compute_link_capacity()
                                prev.compute_hub_capacity()
                                hub.compute_hub_capacity()
                                moved.add(drone.id)
                                unmoved.remove(drone.id)

    def traffic_jam(self, unmoved: set[int]) -> None:
        for hub in reversed(self.network.hubs):
            if self.pathfinder.is_dead_end(hub):
                continue
            for prev in hub.previous_hubs:
                if self.pathfinder.is_dead_end(prev):
                    continue
                if not prev.current_drones:
                    continue
                if hub.zone is Zone.RESTRICTED:
                    for link in self.network.connections:
                        if link.destination == hub and link.origin == prev:
                            while True:
                                candidates: list[Drone] = [
                                    dr for dr in prev.current_drones
                                    if dr.id in unmoved
                                ]
                                capacity: int = min(
                                    link.current_capacity,
                                    hub.current_capacity,
                                    len(candidates)
                                    )
                                if capacity <= 0 or not candidates:
                                    break
                                drone: Drone = candidates[0]
                                prev.current_drones.remove(drone)
                                link.current_drones.append(drone)
                                drone.zone = link
                                link.compute_link_capacity()
                                prev.compute_hub_capacity()
                                hub.compute_hub_capacity()
                                unmoved.remove(drone.id)
                else:
                    for link in self.network.connections:
                        if link.destination == hub and link.origin == prev:
                            while True:
                                candidates = [
                                    dr for dr in prev.current_drones
                                    if dr.id in unmoved
                                ]
                                capacity = min(
                                    link.current_capacity,
                                    hub.current_capacity,
                                    len(candidates)
                                    )
                                if capacity <= 0 or not candidates:
                                    break
                                drone = candidates[0]
                                prev.current_drones.remove(drone)
                                hub.current_drones.append(drone)
                                drone.zone = hub
                                link.compute_link_capacity()
                                prev.compute_hub_capacity()
                                hub.compute_hub_capacity()
                                unmoved.remove(drone.id)

    def solver(self) -> None:
        turn: int = 0
        nb_drones: int = self.network.nb_drones
        while len(self.network.end_hub.current_drones) != nb_drones:

            restricted: dict[str, list[Drone]] = self.restricted_drones()
            unmoved: set[int] = {dr.id for dr in self.network.drones}
            self.move_drones(unmoved)
            if unmoved:
                self.traffic_jam(unmoved)
            unmoved.clear()
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
    network = Network(model)
    pathfinder = PathFinder(network)
    sim = Simulation(network, pathfinder)
    sim.solver()

    result: list[str] = []
    for i, moves in enumerate(sim.drones_moves, start=1):
        line = ''
        for drone_id, hub_name in moves:
            line += f"D{drone_id}-{hub_name} "
        result.append(f"turn {i}: {line}")

    for res in result:
        print(res)
