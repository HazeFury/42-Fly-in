import pytest
from pathlib import Path
from pydantic import ValidationError
from src.utils.errors import ParseError
from src.utils.parser import parse_map_file
from src.utils.models import LevelData


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
    map_content = (
        "nb_drones: 2\n"
        "hub: missing_start 0 0\n"
        "end_hub: goal 10 10\n"
    )
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
