"""Validated data models for the Fly-in 42 drone simulation.

Transforms the raw tuples produced by the parser module into
strongly-typed Pydantic models. Zone types, colors and capacity
constraints are validated at construction time.
"""

import sys
from utils import Color, MSGError
from enum import Enum
from parser import RawParser
try:
    from pydantic import BaseModel, Field, ValidationError  # type: ignore
except ImportError as err:
    MSGError.print_error(
        f"Import Error: {err}\n"
        "Please, install pydantic before any run.\n"
        "Usage:\npython3 -m venv .venv"
        "\nsource venv/bin/activate"
        "\npython3 -m pip install pydantic"
    )
    sys.exit(1)


class Zone(Enum):
    """Enumeration of possible hub zone types.

    Attributes:
        NORMAL: Standard zone (cost 1.0, 1 turn).
        BLOCKED: Completely inaccessible zone.
        RESTRICTED: Slow zone (cost 2.0, 2 turns via connection).
        PRIORITY: Preferred zone (cost 0.5).
    """

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class HubData(BaseModel):
    """Validated representation of a single hub.

    Attributes:
        name: Unique hub identifier.
        x: Horizontal coordinate used for visualisation.
        y: Vertical coordinate used for visualisation.
        zone: Traffic zone type (default 'NORMAL').
        color: Display color (default 'NONE').
        max_drones: Maximum number of drones that may occupy the hub
            simultaneously (default 1, minimum 1).
    """

    name: str = Field(...)
    x: int = Field(...)
    y: int = Field(...)
    zone: Zone = Field(default=Zone.NORMAL)
    color: Color = Field(default=Color.NONE)
    max_drones: int = Field(default=1, ge=1)


class ConnectionData(BaseModel):
    """Validated representation of a directed connection between two hubs.

    Attributes:
        name: Full connection name of the form 'origin-destination'.
        origin: Name of the source hub.
        destination: Name of the target hub.
        max_link_capacity: Maximum number of drones that may travel the
            link at the same time (default 1, minimum 1).
    """

    name: str = Field(...)
    origin: str = Field(...)
    destination: str = Field(...)
    max_link_capacity: int = Field(default=1, ge=1)


class MapModel:
    """High-level validated map model built from the RawParser class.

    Converts every raw hub and connection into the corresponding
    Pydantic model, ensuring type safety and constraint validation.

    Attributes:
        nb_drones: Number of drones that will participate in the simulation.
        hubs: List of intermediate 'HubData' instances.
        start_hub: Starting hub of the network.
        end_hub: Goal hub of the network.
        connections: List of 'ConnectionData' instances.
    """

    def __init__(self, raw: RawParser) -> None:
        """Build the model from a fully parsed 'RawParser'.

        Args:
            raw: Parser instance that already holds the raw map data.
        """
        try:
            if raw.nb_drones:
                self.nb_drones = int(raw.nb_drones)
        except ValueError as err:
            MSGError.print_error(f"ValueError: {err}")
            sys.exit(1)
        if self.nb_drones <= 0:
            MSGError.print_error(
                "ValueError: 'nb_drones' must be defined "
                "as a positive integer."
                )
            sys.exit(1)

        try:
            self.hubs: list[HubData] = [
                HubData(
                    name=hub[0],
                    x=hub[1],
                    y=hub[2],
                    zone=hub[3].get('zone', Zone.NORMAL),
                    color=hub[3].get('color', Color.NONE),
                    max_drones=hub[3].get('max_drones', 1)
                ) for hub in raw.hubs
            ]
        except ValidationError as err:
            for error in err.errors():
                MSGError.print_error(
                    f"Pydantic ValidationError: {error['msg']}"
                    )
                sys.exit(1)

        try:
            if raw.start_hub:
                self.start_hub: HubData = HubData(
                        name=raw.start_hub[0],
                        x=raw.start_hub[1],
                        y=raw.start_hub[2],
                        zone=raw.start_hub[3].get('zone', Zone.NORMAL),
                        color=raw.start_hub[3].get('color', Color.NONE),
                        max_drones=raw.start_hub[3].get('max_drones', 1)
                    )
        except ValidationError as err:
            for error in err.errors():
                MSGError.print_error(
                    f"Pydantic ValidationError: {error['msg']}"
                    )
                sys.exit(1)
        try:
            if raw.end_hub:
                self.end_hub: HubData = HubData(
                        name=raw.end_hub[0],
                        x=raw.end_hub[1],
                        y=raw.end_hub[2],
                        zone=raw.end_hub[3].get('zone', Zone.NORMAL),
                        color=raw.end_hub[3].get('color', Color.NONE),
                        max_drones=raw.end_hub[3].get('max_drones', 1)
                    )
        except ValidationError as err:
            for error in err.errors():
                MSGError.print_error(
                    f"Pydantic ValidationError: {error['msg']}"
                    )
                sys.exit(1)

        try:
            self.connections: list[ConnectionData] = [
                ConnectionData(
                    name=link[0],
                    origin=link[1],
                    destination=link[2],
                    max_link_capacity=link[3].get('max_link_capacity', 1)
                ) for link in raw.connections
            ]
        except ValidationError as err:
            for error in err.errors():
                MSGError.print_error(
                    f"Pydantic ValidationError: {error['msg']}"
                    )
                sys.exit(1)
