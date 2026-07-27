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
        "Usage:\npython3 -m venv venv"
        "\nsource venv/bin/activate"
        "\npython3 -m pip install pydantic"
    )
    sys.exit(1)


class Zone(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class HubData(BaseModel):
    name: str = Field(...)
    x: int = Field(...)
    y: int = Field(...)
    zone: Zone = Field(default=Zone.NORMAL)
    color: Color = Field(default=Color.NONE)
    max_drones: int = Field(default=1, ge=1)


class ConnectionData(BaseModel):
    name: str = Field(...)
    origin: str = Field(...)
    destination: str = Field(...)
    max_link_capacity: int = Field(default=1, ge=1)


class MapModel:
    def __init__(self, raw: RawParser) -> None:
        try:
            if raw.nb_drones:
                self.nb_drones = int(raw.nb_drones)
        except ValueError as err:
            MSGError.print_error(f"ValueError: {err}")
            sys.exit(1)
        if self.nb_drones < 0:
            MSGError.print_error(
                "ValueError: invalid negative value for 'nb_drones'"
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


if __name__ == "__main__":
    raw = RawParser('test.txt')
    model = MapModel(raw)
    print(f"nb_drones: {model.nb_drones}\n")
    print(f"start_hub: {model.start_hub}")
    print(f"end_hub: {model.end_hub}")
    for i, hub in enumerate(model.hubs, start=1):
        print(f"hub {i}: {hub}")
    for i, link in enumerate(model.connections, start=1):
        print(f"connection {i}: {link}")
