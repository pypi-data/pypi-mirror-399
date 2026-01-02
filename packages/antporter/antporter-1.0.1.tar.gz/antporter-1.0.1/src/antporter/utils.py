"""
Utility functions for AntPorter.
"""

import re
from typing import Union


def parse_size(size_str: str) -> int:
    """
    Parse size string to bytes.
    
    Supports formats like:
    - "100" or "100B" -> 100 bytes
    - "10KB" or "10K" -> 10 * 1024 bytes
    - "5MB" or "5M" -> 5 * 1024^2 bytes
    - "2GB" or "2G" -> 2 * 1024^3 bytes
    - "1TB" or "1T" -> 1 * 1024^4 bytes
    
    Args:
        size_str: Size string to parse
        
    Returns:
        Size in bytes
        
    Raises:
        ValueError: If size string format is invalid
    """
    size_str = size_str.strip().upper()
    
    # Match number and optional unit
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$', size_str)
    
    if not match:
        raise ValueError(
            f"Invalid size format: {size_str}\n"
            f"Expected format: <number>[unit], e.g., '100MB', '1.5GB'"
        )
    
    number_str, unit = match.groups()
    number = float(number_str)
    
    # Define multipliers
    multipliers = {
        '': 1,
        'B': 1,
        'K': 1024,
        'KB': 1024,
        'M': 1024 ** 2,
        'MB': 1024 ** 2,
        'G': 1024 ** 3,
        'GB': 1024 ** 3,
        'T': 1024 ** 4,
        'TB': 1024 ** 4,
    }
    
    multiplier = multipliers.get(unit, 1)
    return int(number * multiplier)


def format_size(size_bytes: Union[int, float]) -> str:
    """
    Format bytes to human-readable size string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "10.5 MB")
    """
    size_bytes = float(size_bytes)
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            if unit == 'B':
                return f"{int(size_bytes)} {unit}"
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.2f} PB"


def validate_chunk_size(chunk_size: int, file_size: int) -> None:
    """
    Validate chunk size against file size.
    
    Args:
        chunk_size: Chunk size in bytes
        file_size: File size in bytes
        
    Raises:
        ValueError: If chunk size is invalid
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    
    if chunk_size > file_size:
        raise ValueError(
            f"Chunk size ({format_size(chunk_size)}) is larger than "
            f"file size ({format_size(file_size)})"
        )
    
    # Warn if chunk size is too small (would create too many chunks)
    max_chunks = 10000
    num_chunks = (file_size + chunk_size - 1) // chunk_size
    
    if num_chunks > max_chunks:
        raise ValueError(
            f"Chunk size too small: would create {num_chunks} chunks "
            f"(maximum recommended: {max_chunks})\n"
            f"Please use a larger chunk size."
        )

