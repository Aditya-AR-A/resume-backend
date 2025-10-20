import json
from pathlib import Path
from typing import Dict, Any, Optional

from app.config.settings import app_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_json_data(filename: str) -> Dict[str, Any]:
    """
    Load JSON data from the data directory

    Args:
        filename: Name of the JSON file (without .json extension)

    Returns:
        Dictionary containing the JSON data

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the JSON is invalid
    """
    file_path = app_settings.data_dir / f"{filename}.json"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded data from {filename}.json")
        return data
    except FileNotFoundError:
        logger.error(f"Data file not found: {filename}.json")
        raise FileNotFoundError(f"Data file not found: {filename}.json")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filename}.json: {e}")
        raise json.JSONDecodeError(f"Invalid JSON in {filename}.json: {e}")


def get_data_file_path(filename: str) -> Path:
    """
    Get the full path to a data file

    Args:
        filename: Name of the file

    Returns:
        Path object to the file
    """
    return app_settings.data_dir / filename


def validate_data_directory() -> bool:
    """
    Validate that the data directory exists and contains required files

    Returns:
        True if valid, False otherwise
    """
    if not app_settings.data_dir.exists():
        logger.error(f"Data directory does not exist: {app_settings.data_dir}")
        return False

    required_files = ['intro.json', 'jobs.json', 'projects.json']
    missing_files = []

    for file in required_files:
        if not (app_settings.data_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        logger.warning(f"Missing data files: {missing_files}")
        return False

    return True
