from utils import MSGError
import sys
from typing import Any


class ParsingError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class RawParser:
    def __init__(self, path: str) -> None:
        self.path: str = path
        self.nb_drones: str | None = None
        self.hubs: list[tuple[str, str, str, dict[str, str]]] = []
        self.start_hub: tuple[str, str, str, dict[str, str]] | None = None
        self.end_hub: tuple[str, str, str, dict[str, str]] | None = None
        self.connections: list[tuple[str, str, str, dict[str, str]]] = []
        self.fill_attributes()
        try:
            self.check_matching_names()
        except ParsingError as err:
            MSGError.print_error(f"Parsing Error: {err}")
            sys.exit(1)

    def parse_to_raw_list(self) -> list[str]:
        try:
            with open(self.path) as f:
                return f.read().split('\n')
        except OSError as err:
            MSGError.print_error(f"{err.__class__.__name__}: {err}")
            sys.exit(1)

    def parse_to_raw_dict(self) -> dict[str, Any]:

        res: dict[str, Any] = {}
        hubs: list[str] = []
        connections: list[str] = []

        for line_num, line in enumerate(
            self.parse_to_raw_list(),
            start=1
        ):
            if not line:
                continue
            if line.startswith('#'):
                continue
            if ':' not in line:
                raise ParsingError(f"line n{line_num}, missing ':'")

            key, _,  value = line.partition(':')
            key = key.strip()
            value = value.strip()

            if key == 'hub':
                if not value:
                    raise ParsingError(
                        f"line n{line_num}, missing hub data"
                        )
                hubs.append(value)

            elif key == 'connection':
                if not value:
                    raise ParsingError(
                        f"line n{line_num}, missing connection data"
                        )
                connections.append(value)

            else:
                try:
                    res[key] = value
                except KeyError as err:
                    MSGError.print_error(
                        f"Parsing Error: line n{line_num}, {err}"
                        )
                    sys.exit(1)

        res['hubs'] = hubs
        res['connections'] = connections

        return res

    def parse_metadata(self, s: str) -> dict[str, str]:
        s = s.strip()
        s = s.strip('[]')
        raw: list[str] = s.split()

        res: dict[str, str] = {}

        for element in raw:
            key, _, value = element.partition('=')
            key = key.strip()
            value = value.strip()
            if not key or not value:
                raise ParsingError(
                    "metadata syntax should be in the format [key=value]"
                    )
            res[key] = value

        return res

    def is_valid_name(self, s: str) -> bool:
        return '-' not in s and not all(c.isspace() for c in s)

    def parse_hub_data(self, s: str) -> tuple[str, str, str, dict[str, str]]:
        def is_valid_int(s: str) -> bool:
            try:
                int(s)
                return True
            except ValueError:
                return False

        raw: list[str] = s.split(' ', 3)
        if (
            not self.is_valid_name(raw[0])
            or not is_valid_int(raw[1])
            or not is_valid_int(raw[2])
        ):
            raise ParsingError("missing/error in hub data <name> <x> <y>")
        metadata: str = ''
        try:
            metadata += raw[3]
        except IndexError:
            pass
        return (
            raw[0].strip(),
            raw[1].strip(),
            raw[2].strip(),
            self.parse_metadata(metadata)
            )

    def parse_connection_data(self, s: str) -> tuple[
        str, str, str, dict[str, str]
    ]:
        raw: list[str] = s.split(' ', 1)
        if raw[0].count('-') > 1:
            raise ParsingError(
                "the connection syntax forbids dashes in zone names"
                )
        hub: list[str] = raw[0].split('-', 1)
        if (
            not raw[0] or not raw[0].count('-')
            or not self.is_valid_name(hub[0])
            or not self.is_valid_name(hub[1])
        ):
            raise ParsingError(
                "missing/error in connection data <name1>-<name2>"
                )
        metadata: str = ''
        try:
            metadata += raw[1]
        except IndexError:
            pass
        return (
            raw[0].strip(),
            hub[0].strip(),
            hub[1].strip(),
            self.parse_metadata(metadata)
            )

    def check_matching_names(self) -> None:
        hub_names: list[str] = [hub[0] for hub in self.hubs]

        if self.start_hub:
            hub_names.insert(0, self.start_hub[0])
        if self.end_hub:
            hub_names.append(self.end_hub[0])

        for name in hub_names:
            if hub_names.count(name) > 1:
                raise ParsingError(f"duplicated hub name: {name}")

        for link in self.connections:
            if link[1] not in hub_names:
                raise ParsingError(f"No matching hub name for {link[1]}")
            if link[2] not in hub_names:
                raise ParsingError(f"No matching hub name for {link[2]}")

    def fill_attributes(self) -> None:
        try:
            raw: dict[str, Any] = self.parse_to_raw_dict()
        except ParsingError as err:
            MSGError.print_error(f"Parsing Error: {err}")
            sys.exit(1)

        self.nb_drones = raw['nb_drones']
        if not self.nb_drones:
            MSGError.print_error("Parsing Error: missing nb_drones value")
            sys.exit(1)
        try:
            self.start_hub = self.parse_hub_data(raw['start_hub'])
            self.end_hub = self.parse_hub_data(raw['end_hub'])
        except ParsingError as err:
            MSGError.print_error(f"Parsing Error: {err}")
            sys.exit(1)
        for hub in raw['hubs']:
            try:
                self.hubs.append(self.parse_hub_data(hub))
            except ParsingError as err:
                MSGError.print_error(f"Parsing Error: {err}")
                sys.exit(1)
        for connection in raw['connections']:
            try:
                self.connections.append(self.parse_connection_data(connection))
            except ParsingError as err:
                MSGError.print_error(f"Parsing Error: {err}")
                sys.exit(1)


if __name__ == "__main__":
    path = "test.txt"
    raw = RawParser(path)
    print(f"nb_drones: {raw.nb_drones}\n")
    print(f"start_hub: {raw.start_hub}")
    print(f"end_hub: {raw.end_hub}")
    for i, hub in enumerate(raw.hubs, start=1):
        print(f"hub {i}: {hub}")
    for i, hub in enumerate(raw.connections, start=1):
        print(f"connection {i}: {hub}")
