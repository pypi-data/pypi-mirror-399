"""
Utility functions for Django Context Memory
"""

import logging
from pathlib import Path
from typing import Optional


def setup_logging(verbose: bool = False, log_file: Optional[str] = None):
    """
    Configure logging for the library

    Args:
        verbose: If True, set DEBUG level; otherwise INFO
        log_file: Optional file path to log to
    """
    level = logging.DEBUG if verbose else logging.INFO

    # Configure root logger
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Configure logging
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True  # Override any existing configuration
    )


def validate_django_project(path: Path) -> bool:
    """
    Check if path is a Django project root

    Args:
        path: Path to check

    Returns:
        True if it appears to be a Django project
    """
    path = Path(path)

    if not path.is_dir():
        return False

    # Check for Django project indicators
    indicators = [
        'manage.py',
        'settings.py',
        'wsgi.py',
        'asgi.py',
    ]

    # Check for any indicator in the root
    if any((path / indicator).exists() for indicator in indicators):
        return True

    # Check for settings.py in subdirectories (common Django structure)
    for subdir in path.iterdir():
        if subdir.is_dir():
            if (subdir / 'settings.py').exists():
                return True

    return False


def safe_read_file(path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read file with encoding fallback

    Args:
        path: Path to the file
        encoding: Initial encoding to try (default: utf-8)

    Returns:
        File contents as string, or None if read fails
    """
    path = Path(path)

    if not path.exists() or not path.is_file():
        return None

    # Try primary encoding
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        pass

    # Fallback encodings
    fallback_encodings = ['latin-1', 'cp1252', 'iso-8859-1']

    for fallback_encoding in fallback_encodings:
        try:
            return path.read_text(encoding=fallback_encoding)
        except (UnicodeDecodeError, LookupError):
            continue

    # Last resort: read as binary and decode with errors='replace'
    try:
        return path.read_bytes().decode('utf-8', errors='replace')
    except Exception:
        return None


def format_size(bytes_size: int) -> str:
    """
    Format bytes as human-readable size

    Args:
        bytes_size: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if bytes_size < 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(bytes_size)

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    if unit_index == 0:  # Bytes
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def format_duration(seconds: float) -> str:
    """
    Format duration as human-readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "2m 30s")
    """
    if seconds < 0:
        return "0s"

    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60

    if minutes < 60:
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds:.0f}s"
        return f"{minutes}m"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if remaining_minutes > 0:
        return f"{hours}h {remaining_minutes}m"
    return f"{hours}h"


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, creating it if necessary

    Args:
        path: Directory path

    Returns:
        The path (for chaining)

    Raises:
        OSError: If directory cannot be created
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_relative_path(path: Path, base: Path) -> str:
    """
    Get relative path from base, with error handling

    Args:
        path: Path to convert
        base: Base path

    Returns:
        Relative path as string
    """
    try:
        return str(path.relative_to(base))
    except ValueError:
        # path is not relative to base
        return str(path)


def count_lines(file_path: Path) -> int:
    """
    Count lines in a file

    Args:
        file_path: Path to the file

    Returns:
        Number of lines, or 0 if file cannot be read
    """
    try:
        content = safe_read_file(file_path)
        if content is None:
            return 0
        return len(content.splitlines())
    except Exception:
        return 0


def is_binary_file(file_path: Path, sample_size: int = 512) -> bool:
    """
    Check if file is binary by sampling first bytes

    Args:
        file_path: Path to the file
        sample_size: Number of bytes to sample

    Returns:
        True if file appears to be binary
    """
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)

        # Check for null bytes (common in binary files)
        if b'\x00' in sample:
            return True

        # Check if most bytes are non-printable
        non_printable = sum(1 for byte in sample if byte < 32 and byte not in (9, 10, 13))
        ratio = non_printable / len(sample) if sample else 0

        return ratio > 0.3  # If more than 30% non-printable, likely binary

    except Exception:
        return False
