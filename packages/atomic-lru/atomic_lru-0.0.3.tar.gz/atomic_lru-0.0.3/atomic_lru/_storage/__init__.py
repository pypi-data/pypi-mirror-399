"""Storage module for thread-safe in-memory LRU cache.

This module provides the low-level `Storage` class for storing values in a
thread-safe in-memory cache with LRU eviction and optional TTL expiration.
The storage operates on raw values (typically bytes) without serialization.

The module also exports sentinel values for cache operations:
- `CACHE_MISS`: Returned when a key is not found or has expired
- `DEFAULT_TTL`: Used to indicate that the default TTL should be used
"""

from atomic_lru._storage.storage import Storage
from atomic_lru._storage.types import (
    CACHE_MISS,
    DEFAULT_TTL,
    CacheMissSentinel,
    DefaultTTLSentinel,
)

__all__ = [
    "CACHE_MISS",
    "DEFAULT_TTL",
    "CacheMissSentinel",
    "DefaultTTLSentinel",
    "Storage",
]
