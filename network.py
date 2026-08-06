"""Runtime network graph for the Fly-in 42 drone simulation.

Builds a live graph of hubs and connections from a validated 'MapModel' class.
Tracks current drone occupancy, capacities and neighbour relationships
used by the pathfinder and simulation.
"""

from __future__ import annotations
from model import HubData, ConnectionData, MapModel
from utils import Color, MSGError, Zone


class Drone:
    """Represent a single drone participating in the simulation.

    Attributes:
        id: Unique integer identifier of the drone.
        zone: Current location of the drone (Hub or Connection).
    """

    def __init__(self, id: int) -> None:
        """Create a drone with the given identifier.

        Args:
            id: Unique drone identifier.
        """
        self.id: int = id
        self.zone: Hub | Connection | None = None


class Hub:
    """Runtime representation of a hub in the network graph.

    Attributes:
        name: Unique hub name.
        x: Horizontal coordinate for visualisation.
        y: Vertical coordinate for visualisation.
        zone: Traffic zone type.
        color: Display color.
        max_drones: Maximum simultaneous drones allowed on the hub.
        current_drones: List of drones currently occupying the hub.
        previous_hubs: Incoming neighbouring hubs.
        next_hubs: Outgoing neighbouring hubs.
        previous_connections: Incoming connections that lead to this hub.
        cost: Path-finding cost associated with the zone type.
        current_capacity: Remaining free slots on the hub.
    """

    def __init__(self, hub: HubData) -> None:
        """Build a runtime hub from validated hub data.

        Args:
            hub: Validated 'HubData' instance.
        """
        self.name: str = hub.name
        self.x: int = hub.x
        self.y: int = hub.y
        self.zone: Zone = hub.zone
        self.color: Color = hub.color
        self.max_drones: int = hub.max_drones
        self.current_drones: list[Drone] = []
        self.previous_hubs: list[Hub] = []
        self.next_hubs: list[Hub] = []
        self.previous_connections: list[Connection] = []
        self.cost: float = (
            float('inf') if hub.zone == Zone.BLOCKED
            else 2.0 if hub.zone == Zone.RESTRICTED
            else 0.5 if hub.zone == Zone.PRIORITY
            else 1.0
        )
        self.current_capacity: int = 0
        self.compute_hub_capacity()

    def compute_hub_capacity(self) -> None:
        """Recalculate the remaining free capacity of the hub.

        For restricted zones, drones currently in transit on incoming
        connections are also counted against the capacity.
        """
        in_transit: int = 0
        if self.zone == Zone.RESTRICTED:
            in_transit = sum(
                len(link.current_drones) for link in self.previous_connections
            )
        self.current_capacity = (
            self.max_drones - len(self.current_drones) - in_transit
            )


class Connection:
    """Runtime representation of a directed link between two hubs.

    Attributes:
        name: Full connection name ('origin-destination').
        max_link_capacity: Maximum simultaneous drones on the link.
        origin: Source 'Hub' (set after graph construction).
        destination: Target 'Hub' (set after graph construction).
        current_drones: Drones currently travelling on the link.
        current_capacity: Remaining free slots on the link.
        used_this_turn: Usage of the link during a turn.
    """

    def __init__(self, connection: ConnectionData) -> None:
        """Build a runtime connection from validated connection data.

        Args:
            connection: Validated 'ConnectionData' instance.
        """
        self.name: str = connection.name
        self.max_link_capacity: int = connection.max_link_capacity
        self.origin: Hub | None = None
        self.destination: Hub | None = None
        self.current_drones: list[Drone] = []
        self.current_capacity: int = 0
        self.used_this_turn: int = 0
        self.compute_link_capacity()

    def compute_link_capacity(self) -> None:
        """Recalculate the remaining free capacity of the connection."""
        self.current_capacity = (
            self.max_link_capacity
            - len(self.current_drones)
            - self.used_this_turn
            )


class Network:
    """Complete runtime graph of hubs, connections and drones.

    Instantiated from a 'MapModel' class.
    Builds neighbour relationships, places drones on the start hub
    and guarantees that the end hub has enough capacity for all drones.

    Attributes:
        nb_drones: Total number of drones.
        hubs: Ordered list of hubs (start, intermediates, end).
        connections: List of all connections.
        drones: List of 'Drone' instances.
        start_hub: Reference to the first hub.
        end_hub: Reference to the last hub.
    """

    def __init__(self, map_model: MapModel) -> None:
        """Construct the live network from a validated map model.

        Args:
            map_model: Fully validated 'MapModel' instance.
        """
        self.nb_drones: int = map_model.nb_drones

        self.hubs: list[Hub] = [Hub(hub_data) for hub_data in map_model.hubs]
        self.hubs.insert(0, Hub(map_model.start_hub))
        self.hubs.append(Hub(map_model.end_hub))
        self.connections: list[Connection] = [
            Connection(connection_data)
            for connection_data in map_model.connections
        ]
        self.drones: list[Drone] = [
            Drone(i) for i in range(1, self.nb_drones + 1)
        ]

        self._get_connections_hubs()
        self._get_hub_neighbors()

        self.start_hub: Hub = self.hubs[0]
        self.end_hub: Hub = self.hubs[-1]

        if self.end_hub.max_drones < self.nb_drones:
            MSGError.print_error(
                "Map Error: nb_drones is more than end hub capacity, "
                f"set it to {self.nb_drones}"
                )
            self.end_hub.max_drones = self.nb_drones

    def _get_hub_neighbors(self) -> None:
        """Populate 'next_hubs' and 'previous_hubs' for every hub."""
        for hub in self.hubs:
            for link in self.connections:
                if link.origin == hub:
                    if link.destination:
                        hub.next_hubs.append(link.destination)
                if link.destination == hub:
                    if link.origin:
                        hub.previous_hubs.append(link.origin)

    def _get_connections_hubs(self) -> None:
        """Resolve origin/destination hub references on every connection.

        Also registers each connection on the destination hub's
        'previous_connections' list.
        """
        for link in self.connections:
            origin_name, _, destination_name = link.name.partition('-')
            for hub in self.hubs:
                if hub.name == origin_name:
                    link.origin = hub
                if hub.name == destination_name:
                    link.destination = hub
                    hub.previous_connections.append(link)

    def __str__(self) -> str:
        """Return a human-readable summary of the whole network."""
        hubs_str: str = ''
        for hub in self.hubs:
            hubs_str += (
                f"  {hub.name} ({hub.x},{hub.y}) "
                f"zone={hub.zone.value} color={hub.color.value} "
                f"max_drones={hub.max_drones}\n"
            )

        connections_str: str = ''
        for link in self.connections:
            connections_str += (
                f"  {link.name} "
                f"(origin={link.origin.name if link.origin else 'None'}, "
                "destination="
                f"{link.destination.name if link.destination else 'None'}) "
                f"max_link_capacity={link.max_link_capacity}\n"
            )
        drones_str: str = ', '.join(f"D{drone.id}" for drone in self.drones)

        return (
            f"nb_drones: {self.nb_drones}\n\n"
            f"hubs:\n{hubs_str}\n"
            f"connections:\n{connections_str}\n"
            f"drones: {drones_str}"
        )
