"""Path-finding algorithms for the Fly-in 42 drone simulation.

Computes all feasible paths from the start hub to the end hub,
filters out dead-ends and blocked zones,
and ranks the remaining paths by cost.
"""

from network import Network, Hub
import sys
from utils import MSGError, Zone
from collections import deque


class PathError(Exception):
    """Raised when no valid path exists between start and end hubs."""

    pass


class PathFinder:
    """Discover and rank all viable paths in the network graph.

    Uses a reverse BFS from the end hub to identify unreachable nodes,
    then a DFS from the start hub to enumerate complete paths.
    Paths are sorted by total cost (priority < normal < restricted).

    Attributes:
        network: The runtime 'Network' class to analyse.
        unreachable: Set of hub names that cannot reach the end hub.
        paths: List of paths sorted by ascending cost.
    """

    def __init__(self, network: Network) -> None:
        """Compute unreachable hubs and all ranked paths.

        Args:
            network: Fully built network graph.
        """
        self.network: Network = network
        self._unreachable: set[str] = set()

        if self.network.start_hub.zone == Zone.BLOCKED:
            MSGError.print_error("Path Error: 'start_hub' is blocked")
            sys.exit(1)
        if self.network.end_hub.zone == Zone.BLOCKED:
            MSGError.print_error("Path Error: 'end_hub' is blocked")
            sys.exit(1)

        try:
            self._bfs_find_unreachable()
        except PathError as err:
            MSGError.print_error(f"Path Error: {err}")
            sys.exit(1)

        self.paths: list[list[Hub]] = sorted(
            self._dfs_path(), key=self._compute_path_cost
        )

    def _is_dead_end(self, hub: Hub) -> bool:
        """Check whether the given hub is a dead-end or blocked.

        Args:
            hub: Hub to test.

        Returns:
            'True' if the hub is blocked or cannot reach the end hub.
        """
        if hub == self.network.end_hub:
            return False
        if hub.zone == Zone.BLOCKED:
            return True
        return hub.name in self.unreachable

    def _bfs_find_unreachable(self) -> None:
        """Mark every hub that cannot reach the end hub.

        Performs a reverse BFS starting from the end hub, following
        'previous_hubs' links. Any hub left unvisited is considered
        unreachable.

        Raises:
            PathError: If the start hub itself is unreachable.
        """
        unvisited: set[Hub] = set(self.network.hubs)
        queue: deque[Hub] = deque([self.network.end_hub])

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

    def _dfs_path(self) -> list[list[Hub]]:
        """Enumerate all simple paths from start to end via depth-first search.

        Dead-ends and already-visited hubs are pruned. The resulting
        paths are returned as lists of 'Hub' objects.

        Returns:
            List of complete paths (each a list of hubs).
        """
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
                    if self._is_dead_end(nxt):
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

    def _compute_path_cost(self, path: list[Hub]) -> float:
        """Compute the total cost of a path (sum of individual hub costs).

        Args:
            path: Sequence of hubs forming a complete path.

        Returns:
            floating cost value of the path.
        """
        return sum(hub.cost for hub in path)
