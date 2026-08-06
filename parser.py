"""Map file parser for the Fly-in 42 drone simulation.

Reads map definition files (plain text or embedded in maps.tar.gz)
and extracts raw hub, connection and metadata information.
Ckeck basic syntax before handing data to the model module.
"""

from utils import MSGError
import sys
from typing import IO, Any
import tarfile


class ParsingError(Exception):
    """Raised when a map file contains invalid syntax."""

    pass


class RawParser:
    """Parse a map definition file into structured raw data.

    The parser accepts either a path relative to the embedded
    'maps.tar.gz' archive or a regular filesystem path.
    It extracts the number of drones, start/end hubs, intermediate
    hubs and connections, then validates their consistency.

    Attributes:
        path: Path of the map file to parse.
        nb_drones: Raw string value of the number of drones.
        hubs: List of intermediate hub tuples
            '(name, x, y, metadata_dict)'.
        start_hub: Start hub tuple or 'None'.
        end_hub: End hub tuple or 'None'.
        connections: List of connection tuples
            '(name, origin, destination, metadata_dict)'.
    """

    def __init__(self, path: str) -> None:
        """Initialize the parser and immediately parse the given map.

        Args:
            path: Path to the map definition file.
        """
        self._path: str = path
        self.nb_drones: str | None = None
        self.hubs: list[tuple[str, str, str, dict[str, str]]] = []
        self.start_hub: tuple[str, str, str, dict[str, str]] | None = None
        self.end_hub: tuple[str, str, str, dict[str, str]] | None = None
        self.connections: list[tuple[str, str, str, dict[str, str]]] = []
        self._fill_attributes()
        try:
            self._check_matching_names()
            self._check_duplicates_connections()
            self._check_overlapping_hub()
            self._check_invalid_metadata()
        except ParsingError as err:
            MSGError.print_error(f"Parsing Error: {err}")
            sys.exit(1)

    def _parse_to_raw_list(self) -> list[str]:
        """Read the map file content as a list of lines.

        First attempts to extract the file from 'maps.tar.gz'.
        If that fails, falls back to opening the path on the filesystem.

        Returns:
            List of non-empty lines from the map file.
        """
        content: list[str] = []
        try:
            with tarfile.open('maps.tar.gz') as tar:
                f: IO[bytes] | None = tar.extractfile(self._path)
                if f:
                    content.extend(f.read().decode().split('\n'))
        except (OSError, KeyError, AttributeError, TypeError):
            pass

        if content:
            return content

        try:
            with open(self._path) as fl:
                return fl.read().split('\n')
        except OSError as err:
            MSGError.print_error(
                f"{err.__class__.__name__} for {self._path}: {err}"
                )
            sys.exit(1)

    def _parse_to_raw_dict(self) -> dict[str, Any]:
        """Convert the raw lines into a dictionary of map components.

        Parses key-value pairs ('key: value'), collecting hubs and
        connections into dedicated lists. Comments (starts with '#')
        and empty lines are ignored.

        Returns:
            Dictionary containing at least 'nb_drones', 'start_hub',
            'end_hub', 'hubs' and 'connections'.

        Raises:
            ParsingError: If a required key is missing or a line is malformed.
        """
        res: dict[str, Any] = {}
        hubs: list[str] = []
        connections: list[str] = []
        raw_list: list[str] = self._parse_to_raw_list()

        j: int = 0
        try:
            while not raw_list[j] or raw_list[j].startswith('#'):
                j += 1
        except IndexError:
            raise ParsingError("empty map definition file.")

        if not raw_list[j].strip().startswith('nb_drones'):
            raise ParsingError(
                "The first line must define the number of drones "
                "('nb_drones')"
                )

        seen: set[str] = set()
        for line_num, line in enumerate(
            raw_list,
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
                    if key in seen:
                        raise ParsingError(f"got a duplicate '{key}'")
                    res[key] = value
                    seen.add(key)
                except KeyError as err:
                    MSGError.print_error(
                        f"Parsing Error: line n{line_num}, {err}"
                        )
                    sys.exit(1)

        res['hubs'] = hubs
        res['connections'] = connections

        if (
            'nb_drones' not in res
            or 'start_hub' not in res
            or 'end_hub' not in res
            or not res['hubs']
            or not res['connections']
        ):
            raise ParsingError(
                "missing key in map from "
                "'nb_drones', 'start_hub', 'hub', 'end_hub', 'connection'"
                )

        return res

    def _parse_metadata(self, s: str) -> dict[str, str]:
        """Parse optional metadata enclosed in square brackets.

        Expected format: '[key1=value1 key2=value2 ...]'.

        Args:
            s: Raw metadata string, possibly empty.

        Returns:
            Dictionary of key-value pairs extracted from the metadata.

        Raises:
            ParsingError: If the syntax is invalid.
        """
        s = s.strip()
        if not s:
            return {}
        if not s.startswith('[') or not s.endswith(']'):
            raise ParsingError(
                "metadata syntax should be in the format [key=value], "
                f"got: {s}"
                )
        s = s.strip('[]')
        raw: list[str] = s.split()

        res: dict[str, str] = {}

        seen: set[str] = set()
        for element in raw:
            key, _, value = element.partition('=')
            key = key.strip()
            value = value.strip()
            if not key or not value:
                raise ParsingError(
                    "metadata syntax should be in the format [key=value], "
                    f"got: {s}, error '{key}={value}'"
                    )
            if key not in ['zone', 'color', 'max_drones', 'max_link_capacity']:
                raise ParsingError(
                    f"got invalid metadata: {key}"
                )
            if key in seen:
                raise ParsingError(
                    f"got multiple {key}={value}"
                )
            res[key] = value
            seen.add(key)

        return res

    def _is_valid_name(self, s: str) -> bool:
        """Check whether a hub/zone name is syntactically valid.

        A valid name must not contain dashes and must not be pure whitespace.

        Args:
            s: Candidate name string.

        Returns:
            'True' if the name is valid, 'False' otherwise.
        """
        return '-' not in s and not all(c.isspace() for c in s)

    def _parse_hub_data(self, s: str) -> tuple[str, str, str, dict[str, str]]:
        """Parse a single hub definition line.

        Expected format: 'name x y [metadata]'.

        Args:
            s: Raw hub definition string.

        Returns:
            Tuple '(name, x, y, metadata_dict)'.

        Raises:
            ParsingError: If name, coordinates or metadata are invalid.
        """
        def is_valid_int(s: str) -> bool:
            """Check whether the parameter can be a valid integer.

            Args:
                s: String to be tested.

            Returns:
                'True' if the argument is convertible to int, otherwise 'False'
            """
            try:
                int(s)
                return True
            except ValueError:
                return False

        raw: list[str] = s.split(' ', 3)
        if (
            not self._is_valid_name(raw[0])
            or not is_valid_int(raw[1])
            or not is_valid_int(raw[2])
        ):
            raise ParsingError(
                f"missing/error in hub data <name={raw[0]}> "
                f"<x={raw[1]}> <y={raw[2]}>"
                )
        metadata: str = ''
        try:
            metadata += raw[3]
        except IndexError:
            pass
        return (
            raw[0].strip(),
            raw[1].strip(),
            raw[2].strip(),
            self._parse_metadata(metadata)
            )

    def _parse_connection_data(self, s: str) -> tuple[
        str, str, str, dict[str, str]
    ]:
        """Parse a single connection definition line.

        Expected format: 'origin-destination [metadata]'.

        Args:
            s: Raw connection definition string.

        Returns:
            Tuple '(full_name, origin, destination, metadata_dict)'.

        Raises:
            ParsingError: If the connection syntax is invalid.
        """
        raw: list[str] = s.split(' ', 1)
        if raw[0].count('-') > 1:
            raise ParsingError(
                "the connection syntax forbids dashes in zone names"
                )
        hub: list[str] = raw[0].split('-', 1)
        if (
            not raw[0] or not raw[0].count('-')
            or not self._is_valid_name(hub[0])
            or not self._is_valid_name(hub[1])
        ):
            raise ParsingError(
                "missing/error in connection data <name1>-<name2>, "
                f"got '{raw[0]}'"
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
            self._parse_metadata(metadata)
            )

    def _check_matching_names(self) -> None:
        """Verify that every connection references existing hub names.

        Also detects duplicate hub names.

        Raises:
            ParsingError: If a connection points to an unknown hub or if
                duplicate hub names are found.
        """
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

    def _fill_attributes(self) -> None:
        """Populate instance attributes from the parsed raw dictionary.

        Converts the dictionary returned by with 'parse_to_raw_dict'
        method into the typed attributes of the parser.
        """
        try:
            raw: dict[str, Any] = self._parse_to_raw_dict()
        except ParsingError as err:
            MSGError.print_error(f"Parsing Error: {err}")
            sys.exit(1)

        self.nb_drones = raw['nb_drones']
        if not self.nb_drones:
            MSGError.print_error("Parsing Error: missing nb_drones value")
            sys.exit(1)
        try:
            self.start_hub = self._parse_hub_data(raw['start_hub'])
            self.end_hub = self._parse_hub_data(raw['end_hub'])
        except ParsingError as err:
            MSGError.print_error(f"Parsing Error: {err}")
            sys.exit(1)
        for hub in raw['hubs']:
            try:
                self.hubs.append(self._parse_hub_data(hub))
            except ParsingError as err:
                MSGError.print_error(f"Parsing Error: {err}")
                sys.exit(1)
        for connection in raw['connections']:
            try:
                self.connections.append(
                    self._parse_connection_data(connection)
                    )
            except ParsingError as err:
                MSGError.print_error(f"Parsing Error: {err}")
                sys.exit(1)

    def _check_duplicates_connections(self) -> None:
        """Detect duplicate or reverse-duplicate connections.

        A connection 'a-b' is considered a duplicate of 'b-a'.

        Raises:
            ParsingError: If any duplicated connections detected.
        """
        for i in range(len(self.connections)):
            _, origin1, dest1, _ = self.connections[i]
            for j in range(i + 1, len(self.connections)):
                _, origin2, dest2, _ = self.connections[j]
                if (
                    (origin1, dest1) == (origin2, dest2)
                    or (origin1, dest1) == (dest2, origin2)
                ):
                    raise ParsingError(
                        "duplicates connections detected: "
                        f"{origin1}-{dest1} and {origin2}-{dest2}"
                        )

    def _check_overlapping_hub(self) -> None:
        """Detect overlapping hubs.

        A hub is overlapping another if they share the same positions (x, y).

        Raises:
            ParsingError: If any duplicated hub position detected.
        """
        hubs: list[tuple[str, str, str]] = [
            (hub[0], hub[1], hub[2]) for hub in self.hubs
        ]
        if self.start_hub and self.end_hub:
            hubs.insert(0, (
                self.start_hub[0],
                self.start_hub[1],
                self.start_hub[2]
                ))
            hubs.append((
                self.end_hub[0],
                self.end_hub[1],
                self.end_hub[2]
                ))
        for i in range(len(hubs)):
            name1, x1, y1 = hubs[i]
            for j in range(i + 1, len(hubs)):
                name2, x2, y2 = hubs[j]
                if (x1, y1) == (x2, y2):
                    raise ParsingError(
                        "overlapping hubs detected: "
                        f"{name1}={(x1, y1)} and {name2}={(x2, y2)}"
                    )

    def _check_invalid_metadata(self) -> None:
        """Detect metadata used at wrong place.

        Ensures that hubs do not define the 'max_link_capacity metadata,
        and connections do not define the 'zone', 'color', or
        'max_drones' metadata.

        Raises:
            ParsingError: If an invalid metadata field is fond
                on a hub or a connection.
        """
        hubs_meta: list[tuple[str, dict[str, str]]] = [
            (hub[0], hub[3]) for hub in self.hubs
        ]
        if self.start_hub and self.end_hub:
            hubs_meta.insert(0, (self.start_hub[0], self.start_hub[3]))
            hubs_meta.append((self.end_hub[0], self.end_hub[3]))
        for hub_meta in hubs_meta:
            if 'max_link_capacity' in hub_meta[1]:
                raise ParsingError(
                    f"invalid 'max_link_capacity' metadata for {hub_meta[0]}"
                    )
        for connection in self.connections:
            for key in ['zone', 'color', 'max_drones']:
                if key in connection[3]:
                    raise ParsingError(
                        f"invalid '{key}' metadata for {connection[0]}"
                        )
