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


# Pre-compile regex patterns
# Matches: nb_drones: x
PATTERN_DRONES = re.compile(r"^nb_drones:\s+(?P<count>-?\d+)$")

# Matches: start_hub|hub|end_hub: name x y [optional_metadata]
PATTERN_ZONE = re.compile(
    r"^(?P<type>start_hub|hub|end_hub):\s+"
    r"(?P<name>[^\s-]+)\s+"
    r"(?P<x>-?\d+)\s+"
    r"(?P<y>-?\d+)"
    r"(?:\s+\[(?P<meta>[^\[\]]+)\])?$"
)

# Matches: connection: name1-name2 [optional_metadata]
PATTERN_CONNECTION = re.compile(
    r"^connection:\s+"
    r"(?P<from_hub>[^\s-]+)-(?P<to_hub>[^\s-]+)"
    r"(?:\s+\[(?P<meta>[^\[\]]+)\])?$"
)

# Matches key=value pairs inside the metadata brackets
PATTERN_META = re.compile(r"^(?P<key>\w+)=(?P<value>[\w-]+)$")

# Strict list of allowed metadata keys according to the subject specifications
HUB_META_KEYS = {"zone", "color", "max_drones"}
CONN_META_KEYS = {"max_link_capacity"}


def extract_metadata(
    meta_string: str | None,
    line_number: int,
    allowed_keys: set[str],
) -> dict[str, str]:
    """
    Extracts key-value pairs from a metadata string.
    Raises a ParseError if the format is invalid, or if unknown/duplicate
    keys are found.
    """
    if not meta_string:
        return {}

    meta_dict: dict[str, str] = {}

    tokens = meta_string.split()

    for token in tokens:
        match = PATTERN_META.match(token)

        if not match:
            raise ParseError(
                "Invalid metadata format: "
                f"'\033[93m{token}\033[0m'. Expected "
                "'\033[92mkey=value\033[0m'.",
                line_number,
            )

        key = match.group("key")
        value = match.group("value")

        if key not in allowed_keys:
            raise ParseError(
                f"Unknown metadata key: '\033[93m{key}\033[0m'", line_number
            )

        if key in meta_dict:
            raise ParseError(
                f"Duplicate metadata key: '\033[93m{key}\033[0m'", line_number
            )

        meta_dict[key] = value

    return meta_dict


def parse_map_file(filepath: str) -> ParsedLevelData:
    """
    Reads and parses a Fly-in map file, ensuring strict syntax and order.

    Args:
        filepath: The relative or absolute path to the .txt file.

    Returns:
        A dictionary containing the parsed level data.
    """
    file_path_obj = Path(filepath)
    level_name = file_path_obj.stem

    parsed_data: ParsedLevelData = {
        "level_name": level_name,
        "nb_drones": 0,
        "zones": [],
        "connections": [],
    }

    # State machine to enforce block order:
    # 0 = Expecting nb_drones
    # 1 = Parsing zones
    # 2 = Parsing connections
    state = 0

    try:
        with open(file_path_obj, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.split("#")[0].strip()

                if not line:
                    continue

                if line.count("[") > 1 or line.count("]") > 1:
                    raise ParseError(
                        "Multiple metadata brackets are not allowed.",
                        line_number,
                    )

                # --- 1. nb_drones validation ---
                match_drones = PATTERN_DRONES.match(line)
                if match_drones:
                    if state > 0:
                        raise ParseError(
                            "Invalid order: nb_drones must be"
                            " defined at the very top of the "
                            "file.",
                            line_number,
                        )

                    count = int(match_drones.group("count"))
                    if count <= 0:
                        raise ParseError(
                            "nb_drones must be a strictly positive integer.",
                            line_number,
                        )

                    parsed_data["nb_drones"] = count
                    state = 1
                    continue

                # --- 2. Zones validation ---
                match_zone = PATTERN_ZONE.match(line)
                if match_zone:
                    if state == 0:
                        raise ParseError(
                            "Invalid order: Hubs must be defined "
                            "after nb_drones.",
                            line_number,
                        )
                    if state == 2:
                        raise ParseError(
                            "Invalid order: Hubs cannot be "
                            "defined after "
                            "connections.",
                            line_number,
                        )

                    zone_dict = match_zone.groupdict()
                    meta_dict = extract_metadata(
                        zone_dict.pop("meta"), line_number, HUB_META_KEYS
                    )

                    zone_data = {
                        "type": zone_dict["type"],
                        "name": zone_dict["name"],
                        "x": int(zone_dict["x"]),
                        "y": int(zone_dict["y"]),
                        "metadata": meta_dict,
                    }
                    parsed_data["zones"].append(zone_data)
                    continue

                # --- 3. Connections validation ---
                match_connection = PATTERN_CONNECTION.match(line)
                if match_connection:
                    if state == 0:
                        raise ParseError(
                            "Invalid order: Connections must be "
                            "defined after nb_drones and "
                            "hubs.",
                            line_number,
                        )

                    # Lock the state so no more hubs can be defined
                    state = 2

                    conn_dict = match_connection.groupdict()
                    meta_dict = extract_metadata(
                        conn_dict.pop("meta"), line_number, CONN_META_KEYS
                    )

                    conn_data = {
                        "from_hub": conn_dict["from_hub"],
                        "to_hub": conn_dict["to_hub"],
                        "metadata": meta_dict,
                    }
                    parsed_data["connections"].append(conn_data)
                    continue

                # If the line matched none of the strict regexes above
                raise ParseError(
                    "Invalid syntax or unrecognized format.", line_number
                )

    except FileNotFoundError:
        raise Exception(f"File not found: {filepath}")

    return parsed_data
