import sys
from typing import Dict, Optional

from pydantic import ValidationError

from utils.errors import ParseError
from utils.get_path import get_complete_path
from utils.models import LevelData
from utils.parser import parse_map_file


class MapManager:
    """
    Manages loading, caching, and accessing all map files within the project.
    Acts as a central registry to prevent redundant disk I/O operations.
    """

    def __init__(self) -> None:
        self._maps: Dict[str, Dict[str, LevelData]] = {
            "easy": {},
            "medium": {},
            "hard": {},
            "challenger": {},
        }
        self.load_all_maps()

    def load_all_maps(self) -> None:
        """
        Discovers, parses, and validates all .txt map files.
        """
        maps_dir = get_complete_path("maps")

        if not maps_dir.exists():
            raise FileNotFoundError(f"Maps directory not found at: {maps_dir}")

        for file_path in maps_dir.rglob("*.txt"):
            difficulty = file_path.parent.name

            if difficulty in self._maps:
                try:
                    raw_data = parse_map_file(str(file_path))
                    level_data = LevelData.model_validate(raw_data)
                    self._maps[difficulty][level_data.level_name] = level_data

                except ValidationError as e:
                    print(
                        "\033[91m[ERROR]\033[0m Failed to load the file : "
                        f"'\033[93m{file_path.name}\033[0m'\n"
                    )

                    for error in e.errors():
                        raw_msg = error.get("msg", "Unknown validation error")

                        if raw_msg.startswith("Value error, "):
                            raw_msg = raw_msg.replace("Value error, ", "", 1)

                        clean_messages = raw_msg.split("\n")

                        for i, msg in enumerate(clean_messages):
                            print(f"\033[91m[REASON {i + 1}]\033[0m {msg}")

                    print("\n\033[94m==== EXITING PROGRAM ====\033[0m")
                    sys.exit(1)

                except ParseError as e:
                    print(
                        "\033[91m[ERROR]\033[0m Failed to load the file : "
                        f"'\033[93m{file_path.name}\033[0m'\n{e}"
                    )
                    sys.exit(1)

                except Exception as e:
                    print(
                        "\033[91m[ERROR]\033[0m Unexpected error\n"
                        f"\033[91m[REASON]\033[0m {e}\n"
                    )
                    print("\n\033[94m==== EXITING PROGRAM ====\033[0m")
                    sys.exit(1)

    def get_all_maps(self) -> Dict[str, Dict[str, LevelData]]:
        """Retrieves all loaded maps."""
        return self._maps

    def get_maps_by_difficulty(self, difficulty: str) -> Dict[str, LevelData]:
        """
        Retrieves all loaded maps belonging to a specific difficulty category.
        """
        return self._maps.get(difficulty, {})

    def get_map(self, difficulty: str, level_name: str) -> Optional[LevelData]:
        """
        Retrieves a single validated LevelData object by its difficulty
        and name.
        """
        return self._maps.get(difficulty, {}).get(level_name)


maps_registry = MapManager()
