import json
import os
from datetime import datetime
from typing import Dict, List, Any

class FileHandler:
    """Utility class for handling file operations"""
    
    @staticmethod
    def save_json(data: Any, filepath: str, indent: int = 2) -> bool:
        """Save data to JSON file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=indent, default=str)
            return True
        except Exception as e:
            print(f"Error saving JSON to {filepath}: {e}")
            return False
    
    @staticmethod
    def load_json(filepath: str) -> Any:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON from {filepath}: {e}")
            return None
    
    @staticmethod
    def create_timestamped_filename(base_name: str, extension: str = 'json') -> str:
        """Create filename with timestamp"""
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        return f"{base_name}_{timestamp}.{extension}"
