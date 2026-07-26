from game_map import GameMap, Hub, Zone
import sys
from utils import MSGError
from collections import deque


class PathError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(self, *args)


class PathFinder:
    def __init__(self, game_map: GameMap) -> None:
        self.game_map: GameMap = game_map
        self.unreachable: set[str] = set()

        try:
            self.compute_hub_cost()
        except PathError as err:
            MSGError.print_error(f"Path Error: {err}")
            sys.exit(1)

        self.paths: list[list[str]] = sorted(
            self.dfs_path(), key=self.compute_path_cost
            )

    def is_dead_end(self, hub: Hub) -> bool:
        if hub == self.game_map.end_hub:
            return False
        if hub.zone == Zone.BLOCKED:
            return True
        return hub.name in self.unreachable

    def compute_hub_cost(self) -> None:
        unvisited: set[Hub] = set(self.game_map.hubs)
        queue: deque = deque([self.game_map.end_hub])

        while queue:
            current: Hub = queue.popleft()

            if current not in unvisited:
                continue

            unvisited.remove(current)

            for previous in current.previous_hubs:
                queue.append(previous)
                if previous.zone == Zone.RESTRICTED:
                    previous.cost = current.cost + 2
                elif self.is_dead_end(previous):
                    previous.cost = current.cost + 99
                else:
                    previous.cost = current.cost + 1

        self.unreachable = {hub.name for hub in unvisited}

        if self.game_map.start_hub in unvisited:
            raise PathError("no path found")

    def dfs_path(self) -> list[list[str]]:
        res: list[list[str]] = []
        path: list[str] = []
        visited: set[str] = set()

        def dfs(hub: Hub) -> None:
            visited.add(hub.name)
            path.append(hub.name)

            if hub == self.game_map.end_hub:
                res.append(path[:])
            else:
                for next in hub.next_hubs:
                    if next.name in visited:
                        continue
                    if self.is_dead_end(next):
                        continue
                    dfs(next)

            path.pop()
            visited.remove(hub.name)

        dfs(self.game_map.start_hub)

        if not res:
            MSGError.print_error("Map Error: no path found")
            sys.exit(1)

        return res

    def compute_path_cost(self, path: list[str]) -> int:
        cost: int = 0
        for hub in self.game_map.hubs:
            if hub.name in path:
                cost += hub.cost
        return cost

    def sorted_hubs(self, hubs: list[Hub]) -> list[Hub]:
        best_path: list[str] = self.paths[0]
        return sorted(
            hubs,
            key=lambda hub: (
                hub.name in best_path,
                hub.zone == Zone.PRIORITY
            ),
            reverse=True
        )


if __name__ == "__main__":
    from parser import RawParser
    raw = RawParser('test.txt')
    from model import MapModel
    map_model = MapModel(raw)
    game_map = GameMap(map_model)
    pathfinder = PathFinder(game_map)

    for i, hubs in enumerate(pathfinder.paths, start=1):
        print(f"\nPath n{i}:")
        for hub in hubs:
            print(hub)
