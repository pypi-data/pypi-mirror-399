import json
import importlib.resources
from typing import List, Dict, Any
from pathlib import Path

def get_data_path(filename: str) -> Path:
    """
    Get the absolute path to a data file within the package.
    
    Args:
        filename: Name of the file in the 'data' subdirectory.
        
    Returns:
        Path object to the file.
    """
    # Modern importlib.resources usage for Python 3.9+
    # We assume data is a package "shobdo.data"
    try:
        ref = importlib.resources.files("shobdo.data") / filename
        with importlib.resources.as_file(ref) as path:
            return Path(path)
    except ModuleNotFoundError:
        # Fallback for development/editable installs if package structure varies
        # This assumes standard layout: src/shobdo/utils.py -> src/shobdo/data/
        current_dir = Path(__file__).parent
        data_path = current_dir / "data" / filename
        if data_path.exists():
            return data_path
        raise FileNotFoundError(f"Could not find data file: {filename}")

def load_json_data(filename: str) -> List[Dict[str, Any]]:
    """
    Load a JSON file from the package data directory.
    
    Args:
        filename: Name of the file to load.
        
    Returns:
        List of dictionary entries.
    """
    path = get_data_path(filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
