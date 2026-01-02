class DefaultTTLSentinel:
    """Sentinel value indicating that the default TTL should be used.

    This class is used as a sentinel value to indicate that when setting a cache
    value, the instance's `default_ttl` should be used instead of explicitly
    providing a TTL value or disabling expiration.

    Example:
        >>> from atomic_lru import Cache, DEFAULT_TTL
        >>> cache = Cache(default_ttl=3600)  # 1 hour default
        >>> # Use default TTL
        >>> cache.set("key1", "value1", ttl=DEFAULT_TTL)
        >>> # Override with specific TTL
        >>> cache.set("key2", "value2", ttl=1800)  # 30 minutes
        >>> # Disable expiration for this item
        >>> cache.set("key3", "value3", ttl=None)
    """

    def __repr__(self) -> str:
        return "<DefaultTTL>"


DEFAULT_TTL = DefaultTTLSentinel()
"""Sentinel instance indicating use of the default TTL.

Use this constant when calling `set()` to indicate that the instance's
`default_ttl` should be used for the item being stored.
"""


class CacheMissSentinel:
    """Sentinel value returned when a cache lookup fails.

    This class is used as a sentinel value to indicate that a requested key
    was not found in the cache or the value has expired. It's returned by
    `get()` methods instead of raising an exception or returning None.

    Example:
        >>> from atomic_lru import Cache, CACHE_MISS
        >>> cache = Cache()
        >>> result = cache.get("nonexistent_key")
        >>> if result is CACHE_MISS:
        ...     print("Key not found")
        ... else:
        ...     print(f"Found: {result}")
    """

    def __repr__(self) -> str:
        return "<CacheMiss>"


CACHE_MISS = CacheMissSentinel()
"""Sentinel instance returned when a cache lookup fails.

This constant is returned by `get()` methods when the requested key doesn't
exist in the cache or the value has expired. Use `is` or `is not` to check
for cache misses:

    >>> if cache.get("key") is CACHE_MISS:
    ...     # Handle cache miss
"""
