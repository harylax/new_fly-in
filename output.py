"""Textual output formatters for the Fly-in 42 drone simulation.

Provides the Output class that turns a finished simulation history
into coloured terminal lines suitable for display.
"""

from simulation import Simulation
from network import Network
from utils import Zone, Ansi


class Output:
    """Build human-readable simulation reports from recorded moves.

    Attributes:
        _network: Runtime network used for hub/connection lookup.
        _drones_moves: Full history of position snapshots
            (list of lists of '(drone_id, zone_name)').
    """

    def __init__(self, network: Network, simulation: Simulation) -> None:
        """Store references needed to format the simulation output.

        Args:
            network: Fully built network graph.
            simulation: Simulation whose 'drones_moves' will be reported.
        """
        self._network: Network = network
        self._drones_moves: list[
            list[tuple[int, str]]
            ] = simulation.drones_moves

    def simulation_output(self) -> list[str]:
        """Format the simulation history into colored terminal lines.

        Only movements that differ from the previous turn are shown.
        Restricted-zone are colored in purple,
        their incoming connection in red and the other in yellow.

        Returns:
            List of ready-to-print strings of the simulation.
        """
        result: list[str] = []
        last_track: list[tuple[int, str]] = []
        delivered: set[int] = set()
        for i in range(1, len(self._drones_moves)):
            line = ''
            last_track.clear()
            if i > 1:
                last_track.extend(self._drones_moves[i - 1])
            for drone_id, zone_name in self._drones_moves[i]:
                if drone_id in delivered:
                    continue
                if (drone_id, zone_name) in last_track:
                    continue

                for link in self._network.connections:
                    if zone_name == link.name:
                        line += (
                            f"{Ansi.RED.value}"
                            f"D{drone_id}-{zone_name} "
                            f"{Ansi.RESET.value}"
                            )
                for hub in self._network.hubs:
                    if hub is self._network.hubs[0]:
                        continue
                    if zone_name == hub.name:
                        if hub is self._network.hubs[-1]:
                            line += (
                                f"{Ansi.GREEN.value}"
                                f"D{drone_id}-{zone_name} "
                                f"{Ansi.RESET.value}"
                            )
                            delivered.add(drone_id)
                        elif hub.zone == Zone.RESTRICTED:
                            line += (
                                f"{Ansi.PURPLE.value}"
                                f"D{drone_id}-{zone_name} "
                                f"{Ansi.RESET.value}"
                            )
                        else:
                            line += (
                                f"{Ansi.YELLOW.value}"
                                f"D{drone_id}-{zone_name} "
                                f"{Ansi.RESET.value}"
                            )
            result.append(
                f"{Ansi.BLUE.value}turn {i}: {Ansi.RESET.value}"
                f"{line}"
                )

        title: str = (
            f"{Ansi.CYAN.value}{Ansi.BOLD.value}"
            "──────────────────────────────────────────────────────\n"
            "\t\t>>>Simulation Output<<<\n"
            "──────────────────────────────────────────────────────\n"
            f"{Ansi.RESET.value}"
        )
        result.insert(0, title)
        return result
