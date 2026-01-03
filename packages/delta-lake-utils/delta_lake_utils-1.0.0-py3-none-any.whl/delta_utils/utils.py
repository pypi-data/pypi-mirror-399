import math
from typing import Dict, Any


def format_bytes(bytes_val: float, precision: int = 2) -> str:
    """Format bytes into human-readable string"""
    if bytes_val == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = int(math.floor(math.log(bytes_val, 1024)))
    unit_index = min(unit_index, len(units) - 1)
    
    value = bytes_val / math.pow(1024, unit_index)
    return f"{value:.{precision}f} {units[unit_index]}"


def validate_table_path(table_path: str) -> bool:
    """Validate Delta table path format"""
    if not table_path:
        raise ValueError("Table path cannot be empty")
    return True
