from network import Network, Zone, Drone, Hub, Connection
from collections import deque
from heapq import heappop, heappush
from itertools import count


class PathError(Exception):
    pass


class Simulation:
    def __init__(self, network: Network):
        self.network: Network = network
        self.drones_moves: list[list[tuple[int, str]]] = []
        self.init_drones_pos()
        self.unreachables: set[Hub] = self.bfs_find_unreachables()
        self.dijkstra_compute_hub_cost()

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

    def bfs_find_unreachables(self) -> set[Hub]:
        unvisited: set[Hub] = set(self.network.hubs)
        queue: deque = deque([self.network.end_hub])
        while queue:
            current: Hub = queue.popleft()
            if current.zone == Zone.BLOCKED:
                continue
            if current not in unvisited:
                continue
            unvisited.remove(current)
            for prev in current.previous_hubs:
                queue.append(prev)
        if self.network.start_hub in unvisited:
            raise PathError("no path found")
        return {hub for hub in unvisited}

    def dijkstra_compute_hub_cost(self) -> None:
        goal: Hub = self.network.end_hub
        goal.cost = 0
        counter: count = count()
        queue: list[tuple[int, int, Hub]] = ([(0, 0, goal)])
        while queue:
            current_cost, _, current = heappop(queue)
            if current_cost > current.cost:
                continue
            for prev in current.previous_hubs:
                if prev.zone == Zone.BLOCKED:
                    prev_cost: int = current.cost + 999999
                elif prev.zone == Zone.RESTRICTED:
                    prev_cost = current.cost + 2
                else:
                    prev_cost = current.cost + 1
                if prev_cost < prev.cost:
                    prev.cost = prev_cost
                    heappush(queue, (prev.cost, next(counter), prev))

    def priority_enforced_best_sorted(self, links: list[Hub]) -> list[Hub]:
        return sorted(links, key=lambda hub: (
            0 if hub.zone == Zone.PRIORITY else 1,
            hub.cost
            )
        )

    def dfs_move_drones(
            self,
            hub: Hub, queue: list[Hub] | None = None,
            visited: set[Hub] | None = None
            ) -> None:
        if queue is None:
            queue = []
        if visited is None:
            visited = set()
        if hub in visited:
            return
        if hub not in queue:
            queue.insert(0, hub)
        for next_hub in self.priority_enforced_best_sorted(hub.next_hubs):
            if next_hub in self.unreachables:
                continue
            if not next_hub.current_capacity:
                queue.append(next_hub)
                self.dfs_move_drones(next_hub, queue, visited)
                continue
            queue.append(next_hub)
            self.greedy(queue)

    def jail_restricted_drones(
            self, queue: list[Hub]
            ) -> dict[str, list[Drone]]:
        res: dict[str, list[Drone]] = {}
        for link in self.network.connections:
            if link.destination in queue and link.current_drones:
                res.setdefault(
                    link.destination.name, []
                    ).extend(link.current_drones)
                link.current_drones.clear()
                link.compute_link_capacity()
        return res

    def free_drones(
            self, jailed: dict[str, list[Drone]], queue: list[Hub]
            ) -> None:
        for hub in queue:
            if hub.name in jailed:
                for drone in jailed[hub.name]:
                    hub.current_drones.append(drone)
                    drone.zone = hub
                    hub.compute_hub_capacity()
                del jailed[hub.name]

    def greedy(self, queue: list[Hub]) -> None:
        jailed: dict[str, list[Drone]] = self.jail_restricted_drones(queue)
        for hub in reversed(queue):
            if hub.zone == Zone.RESTRICTED:
                for link in self.network.connections:
                    if (
                        link.destination == hub
                        and link.destination
                        and link.origin in hub.previous_hubs
                    ):
                        capacity: int = min(
                            link.current_capacity, hub.current_capacity,
                            len(link.origin.current_drones)
                            )
                        i: int = 0
                        while i < capacity:
                            if not link.origin.current_drones:
                                break
                            drone: Drone = link.origin.current_drones.pop(0)
                            link.current_drones.append(drone)
                            drone.zone = link
                            link.compute_link_capacity()
                            link.origin.compute_hub_capacity()
                            i += 1
            else:
                for link in self.network.connections:
                    if (
                        link.destination == hub
                        and link.origin
                        and link.origin in hub.previous_hubs
                    ):
                        capacity = min(
                            link.current_capacity, hub.current_capacity,
                            len(link.origin.current_drones)
                            )
                        i = 0
                        while i < capacity:
                            if not link.origin.current_drones:
                                break
                            drone = link.origin.current_drones.pop(0)
                            hub.current_drones.append(drone)
                            drone.zone = hub
                            hub.compute_hub_capacity()
                            link.origin.compute_hub_capacity()
                            i += 1
            self.free_drones(jailed, queue)

    def solve(self) -> None:
        turn: int = 0
        while len(
            self.network.end_hub.current_drones
                ) != self.network.nb_drones:
            self.dfs_move_drones(self.network.start_hub)
            turn += 1
            self.drones_moves.append(self.snapshot())


if __name__ == "__main__":
    default = 'maps/default/01_default_map.txt'
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
    raw = RawParser(easy1)
    from model import MapModel
    model = MapModel(raw)
    network = Network(model)
    sim = Simulation(network)
    sim.solve()

    res: list[str] = []
    for i, move in enumerate(sim.drones_moves):
        line: str = ''
        for id, name in move:
            for hub in sim.network.hubs:
                if hub.name == name:
                    zone = hub.zone.name
                    break
            line += f"D{id}-{name} [{zone}] "
        res.append(f"turn {i}: {line}")

    for line in res:
        print(line)
    print(len(sim.drones_moves))
    print(sim.network.end_hub.current_drones)   # devrait être vide []
    print(sim.network.end_hub is sim.network.start_hub)   # devrait être False
    print(sim.network.nb_drones)   # devrait être 2
