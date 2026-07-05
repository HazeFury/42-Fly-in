from pathlib import Path

import pytest
from pydantic import ValidationError

from utils.errors import ParseError
from utils.models import LevelData
from utils.parser import parse_map_file


def test_parse_valid_minimal_file(tmp_path: Path) -> None:
    """
    Test parsing a perfectly valid, minimal map file without metadata.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "end_hub: goal 10 10\n"
        "connection: start-goal\n"
    )
    test_file = tmp_path / "valid_map.txt"
    test_file.write_text(map_content)

    raw_data = parse_map_file(str(test_file))

    assert raw_data["nb_drones"] == 2
    assert len(raw_data["zones"]) == 2
    assert len(raw_data["connections"]) == 1

    # Check if Pydantic accepts the raw data
    level = LevelData.model_validate(raw_data)
    assert level.level_name == "valid_map"


def test_ignore_comments_and_empty_lines(tmp_path: Path) -> None:
    """
    Test that the parser correctly skips comments and empty lines.
    """
    map_content = (
        "# This is a comment\n"
        "\n"
        "nb_drones: 5\n"
        "start_hub: start 0 0\n"
        "   \n"
        "# Another comment\n"
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "comments_map.txt"
    test_file.write_text(map_content)

    raw_data = parse_map_file(str(test_file))
    assert raw_data["nb_drones"] == 5
    assert len(raw_data["zones"]) == 2


def test_missing_file() -> None:
    """
    Test that the parser raises an Exception when the file does not exist.
    """
    with pytest.raises(Exception, match="File not found"):
        parse_map_file("non_existent_path.txt")


def test_invalid_syntax_raises_parse_error(tmp_path: Path) -> None:
    """
    Test that completely invalid lines raise a ParseError with the
    exact line number.
    """
    map_content = (
        "nb_drones: 3\n"
        "start_hub: start 0 0\n"
        "this is garbage data\n"  # Line 3
    )
    test_file = tmp_path / "garbage_map.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError) as exc_info:
        parse_map_file(str(test_file))

    # Assert that the error correctly identified line 3
    assert exc_info.value.line_number == 3


def test_dash_in_zone_name_raises_error(tmp_path: Path) -> None:
    """
    Test that using a dash in a zone name triggers a ParseError,
    as dashes are reserved for connection splitting.
    """
    map_content = (
        "nb_drones: 1\n"
        "start_hub: invalid-name 0 0\n"  # Line 2
    )
    test_file = tmp_path / "dash_map.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError) as exc_info:
        parse_map_file(str(test_file))

    assert exc_info.value.line_number == 2


def test_pydantic_validation_missing_start_hub(tmp_path: Path) -> None:
    """
    Test that Pydantic rejects a map missing a start_hub.
    """
    map_content = "nb_drones: 2\nhub: missing_start 0 0\nend_hub: goal 10 10\n"
    test_file = tmp_path / "missing_start.txt"
    test_file.write_text(map_content)

    raw_data = parse_map_file(str(test_file))

    with pytest.raises(ValidationError) as exc_info:
        LevelData.model_validate(raw_data)

    assert "Map must have exactly one start_hub" in str(exc_info.value)


def test_pydantic_validation_negative_capacity(tmp_path: Path) -> None:
    """
    Test that Pydantic enforces positive integers for max_drones metadata.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "hub: mid 1 1 [max_drones=-5]\n"
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "negative_cap.txt"
    test_file.write_text(map_content)

    raw_data = parse_map_file(str(test_file))

    with pytest.raises(ValidationError) as exc_info:
        LevelData.model_validate(raw_data)

    assert "Input should be greater than 0" in str(exc_info.value)


def test_pydantic_invalid_zone_type(tmp_path: Path) -> None:
    """
    Test that Pydantic rejects unknown zone types.
    Allowed types are: normal, blocked, restricted, priority.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "hub: mid 1 1 [zone=magical]\n"
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "invalid_zone.txt"
    test_file.write_text(map_content)

    raw_data = parse_map_file(str(test_file))

    with pytest.raises(ValidationError) as exc_info:
        LevelData.model_validate(raw_data)

    assert "Input should be 'normal', 'blocked',"
    "'restricted' or 'priority'" in str(exc_info.value)


def test_invalid_element_order_raises_error(tmp_path: Path) -> None:
    """
    Test that the parser enforces the order: nb_drones, hubs, connections.
    """
    map_content = (
        "start_hub: start 0 0\n"
        "nb_drones: 2\n"  # Should be at the very top
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "order_map.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError) as exc_info:
        parse_map_file(str(test_file))
    assert "order" in str(exc_info.value).lower()


def test_negative_nb_drones_raises_error(tmp_path: Path) -> None:
    """
    Test that a negative number of drones is rejected.
    """
    map_content = "nb_drones: -5\nstart_hub: start 0 0\nend_hub: goal 10 10\n"
    test_file = tmp_path / "negative_drones.txt"
    test_file.write_text(map_content)

    # Could be ParseError or ValidationError depending on implementation
    with pytest.raises((ParseError, ValidationError)):
        raw_data = parse_map_file(str(test_file))
        LevelData.model_validate(raw_data)


def test_duplicate_hub_names_raises_error(tmp_path: Path) -> None:
    """
    Test that declaring two hubs with the exact same name is forbidden.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: my_hub 0 0\n"
        "hub: my_hub 1 1\n"  # Duplicate name
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "dup_hub_name.txt"
    test_file.write_text(map_content)

    with pytest.raises(ValidationError) as exc_info:
        raw_data = parse_map_file(str(test_file))
        LevelData.model_validate(raw_data)
    assert "duplicate" in str(exc_info.value).lower()


def test_duplicate_hub_coordinates_raises_error(tmp_path: Path) -> None:
    """
    Test that two hubs cannot share the exact same X and Y coordinates.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "hub: mid_zone 0 0\n"  # Duplicate coordinates
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "dup_hub_coords.txt"
    test_file.write_text(map_content)

    with pytest.raises(ValidationError):
        raw_data = parse_map_file(str(test_file))
        LevelData.model_validate(raw_data)


def test_connection_with_unknown_hub_raises_error(tmp_path: Path) -> None:
    """
    Test that creating a connection with a hub that doesn't exist
    raises an error.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "end_hub: goal 10 10\n"
        "connection: start-ghost_hub\n"  # ghost_hub is never defined
    )
    test_file = tmp_path / "unknown_hub_conn.txt"
    test_file.write_text(map_content)

    with pytest.raises(ValidationError):
        raw_data = parse_map_file(str(test_file))
        LevelData.model_validate(raw_data)


def test_duplicate_bidirectional_connections_raises_error(
    tmp_path: Path,
) -> None:
    """
    Test that identical connections (a-b and b-a) are flagged as duplicates.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "end_hub: goal 10 10\n"
        "connection: start-goal\n"
        "connection: goal-start\n"  # Duplicate in reverse
    )
    test_file = tmp_path / "dup_connections.txt"
    test_file.write_text(map_content)

    with pytest.raises(ValidationError):
        raw_data = parse_map_file(str(test_file))
        LevelData.model_validate(raw_data)


def test_metadata_unknown_key_raises_error(tmp_path: Path) -> None:
    """
    Test that unsupported metadata keys are rejected.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0 [magic=true]\n"  # 'magic' is not a valid key
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "unknown_meta.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError):
        parse_map_file(str(test_file))


def test_metadata_duplicate_key_raises_error(tmp_path: Path) -> None:
    """
    Test that the same metadata key cannot be defined twice in the same block.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0 [color=red color=blue]\n"
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "dup_meta_key.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError):
        parse_map_file(str(test_file))


def test_multiple_metadata_brackets_raises_error(tmp_path: Path) -> None:
    """
    Test that having more than one set of brackets on a single line is invalid.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0 [color=red] [zone=normal]\n"
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "multiple_brackets.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError):
        parse_map_file(str(test_file))


def test_strict_invalid_zone_type_raises_error(tmp_path: Path) -> None:
    """
    Test that an invalid zone type raises a parsing error as required.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0\n"
        "hub: mid 1 1 [zone=swamp]\n"  # 'swamp' is not allowed
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "invalid_zone_type.txt"
    test_file.write_text(map_content)

    with pytest.raises((ParseError, ValidationError)):
        raw_data = parse_map_file(str(test_file))
        LevelData.model_validate(raw_data)


def test_metadata_unique_word_raises_error(tmp_path: Path) -> None:
    """
    Test that a unique word in metadata is rejected.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0 [toto]\n"  # 'toto' is not valid
        "end_hub: goal 10 10\n"
    )
    test_file = tmp_path / "unknown_meta.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError):
        parse_map_file(str(test_file))


def test_hub_metadata_in_connection_raises_error(tmp_path: Path) -> None:
    """
    Test that a unique word in metadata is rejected.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0 [color=green]\n"
        "hub: waypoint1 1 0 [color=blue]\n"
        "hub: waypoint2 2 0 [color=blue]\n"
        "end_hub: goal 3 0 [color=red]\n"
        "connection: start-waypoint1 [max_drones=5]\n"
        "connection: waypoint1-waypoint2\n"
        "connection: waypoint2-goal\n"
    )
    test_file = tmp_path / "swap_meta.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError):
        parse_map_file(str(test_file))


def test_connection_metadata_in_hub_raises_error(tmp_path: Path) -> None:
    """
    Test that a unique word in metadata is rejected.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0 [color=green max_link_capacity=4]\n"
        "hub: waypoint1 1 0 [color=blue]\n"
        "hub: waypoint2 2 0 [color=blue]\n"
        "end_hub: goal 3 0 [color=red]\n"
        "connection: start-waypoint1\n"
        "connection: waypoint1-waypoint2\n"
        "connection: waypoint2-goal\n"
    )
    test_file = tmp_path / "swap_meta.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError):
        parse_map_file(str(test_file))


def test_case_sensivity_hub_name_raises_error(tmp_path: Path) -> None:
    """
    Test that a unique word in metadata is rejected.
    """
    map_content = (
        "nb_drones: 2\n"
        "start_hub: start 0 0 [color=green max_link_capacity=4]\n"
        "hub: waypoint1 1 0 [color=blue]\n"
        "hub: waypoint2 2 0 [color=blue]\n"
        "hub: Waypoint2 4 0 [color=blue]\n"
        "end_hub: goal 3 0 [color=red]\n"
        "connection: start-waypoint1\n"
        "connection: waypoint1-waypoint2\n"
        "connection: waypoint2-goal\n"
    )
    test_file = tmp_path / "swap_meta.txt"
    test_file.write_text(map_content)

    with pytest.raises(ParseError):
        parse_map_file(str(test_file))
