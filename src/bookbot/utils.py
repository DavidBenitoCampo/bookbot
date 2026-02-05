"""
BookBot Utilities - Helper functions and utilities.

Provides common utilities for file handling, text preprocessing,
caching, and configuration management.
"""

import hashlib
import json
import logging
import os
import pickle
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path.home() / '.cache' / 'bookbot'


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Configure logging for BookBot.
    
    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string
        log_file: Optional file to write logs to
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers
    )


def detect_encoding(file_path: Union[str, Path]) -> str:
    """
    Detect the encoding of a text file.
    
    Tries common encodings and returns the first one that works.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected encoding name
    """
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    path = Path(file_path)
    
    for encoding in encodings:
        try:
            with open(path, 'r', encoding=encoding) as f:
                f.read(1024)  # Try reading first 1KB
            return encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    # Default fallback
    return 'utf-8'


def read_file_safe(
    file_path: Union[str, Path],
    encoding: Optional[str] = None
) -> str:
    """
    Safely read a text file with automatic encoding detection.
    
    Args:
        file_path: Path to the file
        encoding: Optional encoding (auto-detected if not provided)
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if encoding is None:
        encoding = detect_encoding(path)
    
    try:
        return path.read_text(encoding=encoding)
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        raise IOError(f"Cannot read file: {path}") from e


def file_hash(file_path: Union[str, Path]) -> str:
    """
    Calculate MD5 hash of a file for caching purposes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash string
    """
    path = Path(file_path)
    
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest()


class Cache:
    """
    Simple file-based cache for analysis results.
    
    Caches analysis results to avoid re-analyzing unchanged files.
    
    Example:
        >>> cache = Cache()
        >>> cache.set("key", {"data": "value"})
        >>> cache.get("key")
        {"data": "value"}
    """
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_age_days: int = 7
    ):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory for cache files
            max_age_days: Maximum age for cache entries
        """
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age = timedelta(days=max_age_days)
    
    def _key_to_path(self, key: str) -> Path:
        """Convert a cache key to a file path."""
        # Hash the key for safe filename
        hashed = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._key_to_path(key)
        
        if not cache_path.exists():
            return None
        
        # Check age
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - mtime > self.max_age:
            cache_path.unlink()
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        cache_path = self._key_to_path(key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        count = 0
        for cache_file in self.cache_dir.glob('*.cache'):
            cache_file.unlink()
            count += 1
        
        logger.info(f"Cleared {count} cache entries")
        return count
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.
        
        Returns:
            Number of entries removed
        """
        count = 0
        now = datetime.now()
        
        for cache_file in self.cache_dir.glob('*.cache'):
            mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if now - mtime > self.max_age:
                cache_file.unlink()
                count += 1
        
        logger.info(f"Removed {count} expired cache entries")
        return count


def cached_analysis(cache: Optional[Cache] = None):
    """
    Decorator to cache analysis results.
    
    Uses file hash as cache key to invalidate when file changes.
    
    Args:
        cache: Cache instance (creates default if None)
        
    Returns:
        Decorator function
    """
    if cache is None:
        cache = Cache()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key from file path and hash
            cache_key = f"{self.file_path}:{file_hash(self.file_path)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Using cached result for: {self.file_path}")
                self._result = cached_result
                return cached_result
            
            # Run the analysis
            result = func(self, *args, **kwargs)
            
            # Cache the result
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    
    return decorator


def find_books(
    directory: Union[str, Path],
    extensions: List[str] = None,
    recursive: bool = True
) -> List[Path]:
    """
    Find book files in a directory.
    
    Args:
        directory: Directory to search
        extensions: File extensions to include
        recursive: Search subdirectories
        
    Returns:
        List of file paths
    """
    if extensions is None:
        extensions = ['.txt', '.md', '.text']
    
    path = Path(directory)
    
    if not path.is_dir():
        raise ValueError(f"Not a directory: {path}")
    
    files = []
    pattern = '**/*' if recursive else '*'
    
    for ext in extensions:
        files.extend(path.glob(f'{pattern}{ext}'))
    
    return sorted(files)


def format_duration(minutes: float) -> str:
    """
    Format a duration in minutes to a human-readable string.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Formatted string (e.g., "2h 30m" or "45m")
    """
    if minutes < 1:
        return "< 1 min"
    elif minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = int(minutes // 60)
        mins = int(minutes % 60)
        if mins == 0:
            return f"{hours}h"
        return f"{hours}h {mins}m"


def format_number(n: int) -> str:
    """
    Format a number with thousand separators.
    
    Args:
        n: Number to format
        
    Returns:
        Formatted string (e.g., "1,234,567")
    """
    return f"{n:,}"


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


class Config:
    """
    Configuration management for BookBot.
    
    Loads settings from a JSON config file.
    """
    
    DEFAULT_CONFIG = {
        'default_format': 'text',
        'use_color': True,
        'cache_enabled': True,
        'cache_max_age_days': 7,
        'output_directory': 'output',
        'verbose': False,
        'include_stop_words': False,
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to config file (optional)
        """
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        
        if config_path:
            self.load(config_path)
    
    def load(self, path: str) -> None:
        """Load configuration from a JSON file."""
        config_path = Path(path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                self.config.update(user_config)
                logger.info(f"Loaded config from: {config_path}")
            except Exception as e:
                logger.warning(f"Error loading config: {e}")
    
    def save(self, path: str) -> None:
        """Save configuration to a JSON file."""
        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        logger.info(f"Saved config to: {config_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value
