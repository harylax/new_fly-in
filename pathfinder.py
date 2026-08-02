from network import Network, Hub, Zone
import sys
from utils import MSGError
from collections import deque


class PathError(Exception):
    pass


class PathFinder:
    def __init__(self, network: Network) -> None:
        self.network: Network = network
        self.unreachable: set[str] = set()

        if self.network.start_hub.zone == Zone.BLOCKED:
            MSGError.print_error("Path Error: 'start_hub' is blocked")
            sys.exit(1)
        if self.network.end_hub.zone == Zone.BLOCKED:
            MSGError.print_error("Path Error: 'end_hub' is blocked")
            sys.exit(1)

        try:
            self.bfs_find_unreachable()
        except PathError as err:
            MSGError.print_error(f"Path Error: {err}")
            sys.exit(1)

        self.paths: list[list[Hub]] = sorted(
            self.dfs_path(), key=self.compute_path_cost
        )

    def is_dead_end(self, hub: Hub) -> bool:
        if hub == self.network.end_hub:
            return False
        if hub.zone == Zone.BLOCKED:
            return True
        return hub.name in self.unreachable

    def bfs_find_unreachable(self) -> None:
        unvisited: set[Hub] = set(self.network.hubs)
        queue: deque = deque([self.network.end_hub])

        while queue:
            current: Hub = queue.popleft()
            if current not in unvisited:
                continue
            unvisited.remove(current)
            if current.zone == Zone.BLOCKED:
                continue
            for previous in current.previous_hubs:
                queue.append(previous)
        self.unreachable = {hub.name for hub in unvisited}
        if self.network.start_hub in unvisited:
            raise PathError("no path found")

    def dfs_path(self) -> list[list[Hub]]:
        res: list[list[str]] = []
        path: list[str] = []
        visited: set[str] = set()

        def dfs(hub: Hub) -> None:
            visited.add(hub.name)
            path.append(hub.name)

            if hub == self.network.end_hub:
                res.append(path[:])
            else:
                for nxt in hub.next_hubs:
                    if nxt.name in visited:
                        continue
                    if self.is_dead_end(nxt):
                        continue
                    dfs(nxt)

            path.pop()
            visited.remove(hub.name)

        dfs(self.network.start_hub)

        if not res:
            MSGError.print_error("Map Error: no path found")
            sys.exit(1)

        final: list[list[Hub]] = []
        for line in res:
            path_hub: list[Hub] = []
            for name in line:
                for hub in self.network.hubs:
                    if name == hub.name:
                        path_hub.append(hub)
            final.append(path_hub)
        return final

    def compute_path_cost(self, path: list[Hub]) -> float:
        return sum(hub.cost for hub in path)


if __name__ == "__main__":
    from parser import RawParser
    raw = RawParser('maps/default/01_default_map.txt')
    # raw = RawParser('maps/medium/02_circular_loop.txt')
    # raw = RawParser('maps/challenger/01_the_impossible_dream.txt')
    from model import MapModel
    map_model = MapModel(raw)
    network = Network(map_model)
    pathfinder = PathFinder(network)

    for i, path in enumerate(pathfinder.paths):
        print(f"path {i}:")
        print(' - '.join(hub.name for hub in path))
