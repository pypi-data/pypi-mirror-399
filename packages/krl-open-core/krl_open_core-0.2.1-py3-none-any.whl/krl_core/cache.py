# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# SPDX-License-Identifier: MIT
# ----------------------------------------------------------------------

"""
KRL Core - Cache Module
=======================

Provides caching utilities for the KRL platform.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional
import json
import hashlib
import time

# Try to import pandas for DataFrame support
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class DataFrameEncoder(json.JSONEncoder):
    """JSON encoder that handles pandas DataFrames."""
    
    def default(self, obj):
        if HAS_PANDAS and isinstance(obj, pd.DataFrame):
            return {
                "__type__": "DataFrame",
                "data": obj.to_dict(orient="split"),
            }
        return super().default(obj)


def decode_dataframe(obj):
    """Decode DataFrames from JSON-serialized format."""
    if isinstance(obj, dict) and obj.get("__type__") == "DataFrame":
        if HAS_PANDAS:
            return pd.DataFrame(**obj["data"])
    return obj


class Cache(ABC):
    """Abstract base class for cache implementations."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in the cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all values from the cache."""
        pass


class FileCache(Cache):
    """File-based cache implementation with TTL support."""

    def __init__(
        self,
        cache_dir: str = ".cache",
        default_ttl: int = 3600,
        namespace: Optional[str] = None,
    ):
        """
        Initialize file cache.

        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (default: 1 hour)
            namespace: Optional namespace to isolate cache entries
        """
        cache_dir = Path(cache_dir).expanduser()
        if namespace:
            cache_dir = cache_dir / namespace
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.namespace = namespace or ""
        # Statistics tracking
        self._hits = 0
        self._misses = 0

    def _get_cache_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Retrieve a value from the cache."""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            self._misses += 1
            return default

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)

            # Check TTL
            if data.get("expires_at") and time.time() > data["expires_at"]:
                cache_path.unlink()
                self._misses += 1
                return default

            # Decode any DataFrames in the cached value
            value = data.get("value")
            self._hits += 1
            return decode_dataframe(value) if isinstance(value, dict) else value
        except (json.JSONDecodeError, IOError):
            self._misses += 1
            return default

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in the cache."""
        cache_path = self._get_cache_path(key)
        ttl = ttl or self.default_ttl

        data = {
            "key": key,
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl if ttl else None,
        }

        with open(cache_path, "w") as f:
            json.dump(data, f, cls=DataFrameEncoder)

    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False

    def clear(self) -> None:
        """Clear all values from the cache."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        self._hits = 0
        self._misses = 0

    def has(self, key: str) -> bool:
        """Check if a key exists in the cache and is not expired."""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return False

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)

            # Check TTL
            if data.get("expires_at") and time.time() > data["expires_at"]:
                cache_path.unlink()
                return False

            return True
        except (json.JSONDecodeError, IOError):
            return False

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        cache_size = len(list(self.cache_dir.glob("*.json")))

        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "cache_size": cache_size,
        }

    def cleanup_expired(self) -> int:
        """Remove expired cache entries and return the count of removed entries."""
        removed = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)

                if data.get("expires_at") and time.time() > data["expires_at"]:
                    cache_file.unlink()
                    removed += 1
            except (json.JSONDecodeError, IOError):
                # Remove corrupted files
                cache_file.unlink()
                removed += 1

        return removed

    def __repr__(self) -> str:
        """Return string representation of the cache."""
        size = len(list(self.cache_dir.glob("*.json")))
        return f"FileCache(cache_dir='{self.cache_dir}', size={size})"


class RedisCache(Cache):
    """Redis-based cache implementation (placeholder)."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, **kwargs):
        """
        Initialize Redis cache.

        Note: This is a placeholder implementation. For production use,
        install redis-py and implement actual Redis connectivity.
        """
        self.host = host
        self.port = port
        self.db = db
        self._cache: dict = {}  # In-memory fallback

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in the cache."""
        self._cache[key] = value

    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all values from the cache."""
        self._cache.clear()
