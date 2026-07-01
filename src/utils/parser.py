import re
from pathlib import Path
from typing import Any, TypedDict
from utils.errors import ParseError


class ParsedLevelData(TypedDict):
    """
    Defines the exact structure of the parsed dictionary
    to ensure full type safety with mypy.
    """
    level_name: str
    nb_drones: int
    zones: list[dict[str, Any]]
    connections: list[dict[str, Any]]


# Pre-compile regex patterns for better performance
# Matches: nb_drones: 5
PATTERN_DRONES = re.compile(r"^nb_drones:\s+(?P<count>\d+)$")

# Matches: start_hub|hub|end_hub: name x y [optional_metadata]
# Note: Zone names cannot contain spaces or dashes, hence [^\s-]+
PATTERN_ZONE = re.compile(
    r"^(?P<type>start_hub|hub|end_hub):\s+"
    r"(?P<name>[^\s-]+)\s+"
    r"(?P<x>-?\d+)\s+"
    r"(?P<y>-?\d+)"
    r"(?:\s+\[(?P<meta>.*?)\])?$"
)

# Matches: connection: name1-name2 [optional_metadata]
PATTERN_CONNECTION = re.compile(
    r"^connection:\s+"
    r"(?P<from_hub>[^\s-]+)-(?P<to_hub>[^\s-]+)"
    r"(?:\s+\[(?P<meta>.*?)\])?$"
)

# Matches key=value pairs inside the metadata brackets
PATTERN_META = re.compile(r"(?P<key>\w+)=(?P<value>[\w-]+)")


def extract_metadata(meta_string: str | None) -> dict[str, str]:
    """
    Extracts key-value pairs from a metadata string.
    """
    if not meta_string:
        return {}

    return {
        match.group("key"): match.group("value")
        for match in PATTERN_META.finditer(meta_string)
    }


def parse_map_file(filepath: str) -> ParsedLevelData:
    """
    Reads and parses a Fly-in map file.

    Args:
        filepath: The relative or absolute path to the .txt file.

    Returns:
        A dictionary containing the parsed level data, ready to be
        fed into Pydantic models.
    """
    file_path_obj = Path(filepath)

    # Extract the clean name for your Arcade GUI (e.g., "01_linear_path")
    level_name = file_path_obj.stem

    parsed_data: ParsedLevelData = {
        "level_name": level_name,
        "nb_drones": 0,
        "zones": [],
        "connections": []
    }

    try:
        with open(file_path_obj, 'r', encoding='utf-8') as file:
            for line_number, raw_line in enumerate(file, start=1):
                # Clean the line and ignore comments/empty lines
                line = raw_line.strip()
                if not line or line.startswith('#'):
                    continue

                # Check for nb_drones
                match_drones = PATTERN_DRONES.match(line)
                if match_drones:
                    parsed_data["nb_drones"] = int(match_drones.group("count"))
                    continue

                # Check for zones (start_hub, hub, end_hub)
                match_zone = PATTERN_ZONE.match(line)
                if match_zone:
                    zone_dict = match_zone.groupdict()
                    meta_dict = extract_metadata(zone_dict.pop("meta"))

                    # Merge core attributes with metadata
                    zone_data = {
                        "type": zone_dict["type"],
                        "name": zone_dict["name"],
                        "x": int(zone_dict["x"]),
                        "y": int(zone_dict["y"]),
                        "metadata": meta_dict
                    }
                    parsed_data["zones"].append(zone_data)
                    continue

                # Check for connections
                match_connection = PATTERN_CONNECTION.match(line)
                if match_connection:
                    conn_dict = match_connection.groupdict()
                    meta_dict = extract_metadata(conn_dict.pop("meta"))

                    conn_data = {
                        "from_hub": conn_dict["from_hub"],
                        "to_hub": conn_dict["to_hub"],
                        "metadata": meta_dict
                    }
                    parsed_data["connections"].append(conn_data)
                    continue

                # If we reach here, the line matched absolutely nothing
                raise ParseError(
                    "Invalid syntax or unrecognized format.", line_number
                    )

    except FileNotFoundError:
        raise Exception(f"File not found: {filepath}")

    return parsed_data
