from __future__ import annotations
from model import HubData, ConnectionData, MapModel, Zone
from utils import Color, MSGError


class Drone:
    def __init__(self, id: int = 0) -> None:
        self.id: int = id
        self.zone: Hub | Connection | None = None


class Hub:
    def __init__(self, hub: HubData) -> None:
        self.name: str = hub.name
        self.x: int = hub.x
        self.y: int = hub.y
        self.zone: Zone = hub.zone
        self.color: Color = hub.color
        self.max_drones: int = hub.max_drones
        self.current_drones: list[Drone] = []
        self.previous_hubs: list[Hub] = []
        self.next_hubs: list[Hub] = []
        self.cost: int = 0
        self.current_capacity: int = 0
        self.compute_hub_capacity()

    def compute_hub_capacity(self) -> None:
        self.current_capacity = self.max_drones - len(self.current_drones)


class Connection:
    def __init__(self, connection: ConnectionData) -> None:
        self.name: str = connection.name
        self.max_link_capacity: int = connection.max_link_capacity
        self.origin: Hub | None = None
        self.destination: Hub | None = None
        self.current_drones: list[Drone] = []
        self.current_capacity: int = 0
        self.compute_link_capacity()

    def compute_link_capacity(self) -> None:
        self.current_capacity = self.max_link_capacity - len(
            self.current_drones
            )


class GameMap:
    def __init__(self, map_model: MapModel) -> None:
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

        self.get_connections_hubs()
        self.get_hub_neighbors()

        self.start_hub: Hub = self.hubs[0]
        self.end_hub: Hub = self.hubs[-1]

        if self.end_hub.max_drones < self.nb_drones:
            MSGError.print_error(
                "Map Error: nb_drones is more than end hub capacity, "
                f"set it to {self.nb_drones}"
                )
            self.end_hub.max_drones = self.nb_drones

    def get_hub_neighbors(self) -> None:
        for hub in self.hubs:
            for link in self.connections:
                if link.origin == hub:
                    if link.destination:
                        hub.next_hubs.append(link.destination)
                if link.destination == hub:
                    if link.origin:
                        hub.previous_hubs.append(link.origin)

    def get_connections_hubs(self) -> None:
        for link in self.connections:
            origin_name, _, destination_name = link.name.partition('-')
            for hub in self.hubs:
                if hub.name == origin_name:
                    link.origin = hub
                if hub.name == destination_name:
                    link.destination = hub

    def __str__(self) -> str:
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


if __name__ == "__main__":
    from parser import RawParser
    raw = RawParser('test.txt')
    map_model = MapModel(raw)
    game_map = GameMap(map_model)
    print(game_map)
