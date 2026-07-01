# from pathlib import Path
from typing import Dict, Optional
from utils.models import LevelData
from utils.parser import parse_map_file
from utils.get_path import get_complete_path


class MapManager:
    """
    Manages loading, caching, and accessing all map files within the project.
    Acts as a central registry to prevent redundant disk I/O operations.
    """
    def __init__(self) -> None:
        # Maps categorized by difficulty: {difficulty: {level_name: LevelData}}
        self._maps: Dict[str, Dict[str, LevelData]] = {
            "easy": {},
            "medium": {},
            "hard": {},
            "challenger": {}
        }
        self.load_all_maps()

    def load_all_maps(self) -> None:
        """
        Discovers, parses, and validates all .txt map files under the maps directory.
        Categories are automatically determined based on subfolder names.
        """
        maps_dir = get_complete_path("maps")

        if not maps_dir.exists():
            raise FileNotFoundError(f"Maps directory not found at: {maps_dir}")

        # rglob searches recursively for all matching files
        for file_path in maps_dir.rglob("*.txt"):
            difficulty = file_path.parent.name

            # Ensure the folder name corresponds to a valid difficulty level
            if difficulty in self._maps:
                try:
                    # 1. Parse into a raw dictionary using regex
                    raw_data = parse_map_file(str(file_path))

                    # 2. Validate and convert to Pydantic object
                    level_data = LevelData(**raw_data)

                    # 3. Cache the object using its clean level name as the key
                    self._maps[difficulty][level_data.level_name] = level_data

                except Exception as e:
                    print("[ERROR] Failed to load map file "
                          f"'{file_path.name}': {e}")

    def get_all_maps(self) -> Dict[str, LevelData]:
        """Retrieves all loaded maps."""
        return self._maps

    def get_maps_by_difficulty(self, difficulty: str) -> Dict[str, LevelData]:
        """
        Retrieves all loaded maps belonging to a specific difficulty category.
        """
        return self._maps.get(difficulty, {})

    def get_map(self, difficulty: str, level_name: str) -> Optional[LevelData]:
        """
        Retrieves a single validated LevelData object by its difficulty and name.
        """
        return self._maps.get(difficulty, {}).get(level_name)


maps_registry = MapManager()
