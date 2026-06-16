from pathlib import Path


def get_complete_path(ressource: str) -> Path:
    """
    Determine the root directory of the application.
    If the script is bundled by PyInstaller, it returns the directory
    containing the executable, allowing users to modify the external JSON.
    """
    # Running in a standard development environment
    # Moves up from 'src/utils/config_loader.py' to the project root
    project_root = Path(__file__).resolve().parent.parent.parent
    return project_root / ressource
