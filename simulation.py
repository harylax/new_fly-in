"""Turn-based drone movement simulation for Fly-in 42.

Orchestrates the movement of all drones from the start hub to the end
hub while respecting hub and connection capacities, restricted zones
and the ranked paths produced by the pathfinder.
"""

from network import Network, Zone, Drone, Hub
from pathfinder import PathFinder


class Simulation:
    """Execute the multi-drone path-following simulation.

    The 'solver' method advances the simulation turn by turn until
    every drone has reached the end hub. A snapshot of every drone's
    position is recorded after each turn.

    Attributes:
        network: Live network graph containing hubs, connections and drones.
        pathfinder: Pre-computed ranked paths used to decide movements.
        drones_moves: History of position snapshots
            (list of lists of '(drone_id, zone_name)').
    """

    def __init__(self, network: Network, pathfinder: PathFinder):
        """Initialize the simulation and place all drones on the start hub.

        Args:
            network: Fully built network graph.
            pathfinder: PathFinder instance with ranked paths ready.
        """
        self.network: Network = network
        self.pathfinder: PathFinder = pathfinder
        self.drones_moves: list[list[tuple[int, str]]] = []
        self.init_drones_pos()

    def snapshot(self) -> list[tuple[int, str]]:
        """Capture the current position of every drone.

        Returns:
            List of '(drone_id, zone_name)' tuples ordered by drone id.
        """
        res: list[tuple[int, str]] = []
        for drone in self.network.drones:
            if drone.zone:
                res.append((drone.id, drone.zone.name))
        return res

    def init_drones_pos(self) -> None:
        """Place all drones on the start hub and take initial snapshot."""
        for drone in self.network.drones:
            drone.zone = self.network.start_hub
            self.network.start_hub.current_drones.append(drone)
            self.network.start_hub.compute_hub_capacity()
        self.drones_moves.append(self.snapshot())

    def restricted_drones(self) -> dict[str, list[Drone]]:
        """Collect drones currently travelling on restricted connections.

        Clears the connection occupancy lists after collecting the drones
        so that capacity is freed for the next turn.

        Returns:
            Mapping from destination hub name to the list of drones that
            will arrive there after the restricted transit.
        """
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
        """Release drones that finished a restricted transit onto their hub.

        Args:
            restricted: Mapping produced by the 'restricted_drones' method.
        """
        for hub in self.network.hubs:
            if hub.name in restricted:
                for drone in restricted[hub.name]:
                    hub.current_drones.append(drone)
                    drone.zone = hub
                    hub.compute_hub_capacity()
                del restricted[hub.name]

    def move_drones(self) -> None:
        """Attempt to advance as many drones as possible along ranked paths.

        Iterates over the cheapest paths first. For each edge of a path,
        moves drones from the previous hub onto the next hub (or onto the
        connecting link when the destination is restricted), respecting
        both hub and link capacities.
        """
        moved: set[int] = set()
        for path in self.pathfinder.paths[:15]:
            if len(moved) == self.network.nb_drones:
                break
            for i in range(len(path) - 1, 0, -1):
                hub: Hub = path[i]
                prev: Hub = path[i - 1]
                if not prev.current_drones:
                    continue
                if hub == self.network.start_hub:
                    break
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

    def solver(self) -> None:
        """Run the simulation until every drone reaches the end hub.

        Each iteration corresponds to one turn:
        drones currently in restricted transit are first collected,
        then free drones are moved along the ranked paths,
        and finally the collected drones are released onto their
        destination hub before the next turn.
        A snapshot is recorded after each turn.
        """
        turn: int = 0
        nb_drones: int = self.network.nb_drones
        while len(self.network.end_hub.current_drones) != nb_drones:

            restricted: dict[str, list[Drone]] = self.restricted_drones()
            self.move_drones()
            self.free_drones(restricted)

            turn += 1

            self.drones_moves.append(self.snapshot())
