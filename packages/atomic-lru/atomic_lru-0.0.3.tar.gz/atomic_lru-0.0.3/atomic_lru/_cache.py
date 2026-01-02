import pickle
from dataclasses import dataclass, field
from typing import Any, Protocol

from atomic_lru._storage import (
    CACHE_MISS,
    DEFAULT_TTL,
    CacheMissSentinel,
    DefaultTTLSentinel,
    Storage,
)


class Serializer(Protocol):
    """Protocol for serializing values to bytes.

    A serializer is a callable that takes any value and converts it to bytes
    for storage in the cache. The default implementation uses pickle.

    Example:
        >>> def my_serializer(value: Any) -> bytes:
        ...     return json.dumps(value).encode('utf-8')
    """

    def __call__(self, value: Any) -> bytes: ...


class Deserializer(Protocol):
    """Protocol for deserializing values from bytes.

    A deserializer is a callable that takes bytes and converts them back to
    the original value. It should be the inverse of the serializer.

    Example:
        >>> def my_deserializer(value: bytes) -> Any:
        ...     return json.loads(value.decode('utf-8'))
    """

    def __call__(self, value: bytes) -> Any: ...


def _default_serializer(value: Any) -> bytes:
    """Default serializer using pickle.

    Serializes any picklable Python object to bytes using pickle.dumps().

    Args:
        value: Any picklable Python object.

    Returns:
        The serialized bytes representation of the value.

    Raises:
        pickle.PickleError: If the value cannot be pickled.
    """
    return pickle.dumps(value)


def _default_deserializer(value: bytes) -> Any:
    """Default deserializer using pickle.

    Deserializes bytes back to a Python object using pickle.loads().

    Args:
        value: Bytes to deserialize.

    Returns:
        The deserialized Python object.

    Raises:
        pickle.PickleError: If the bytes cannot be unpickled.

    Warning:
        Unpickling data from untrusted sources can be a security risk.
        Only deserialize data from trusted sources.
    """
    return pickle.loads(value)  # noqa: S301


@dataclass
class Cache(Storage[bytes]):
    """High-level cache with automatic serialization and deserialization.

    This class extends `Storage[bytes]` to provide a convenient API for caching
    arbitrary Python objects. Values are automatically serialized to bytes when
    stored and deserialized when retrieved. By default, pickle is used for
    serialization, but custom serializers can be provided.

    The cache inherits all features from `Storage`, including:
    - Thread-safe operations
    - LRU eviction when limits are reached
    - Optional TTL expiration
    - Size and item count limits

    Args:
        serializer: Callable that serializes values to bytes. Defaults to
            pickle-based serialization.
        deserializer: Callable that deserializes bytes back to values. Defaults
            to pickle-based deserialization. Must be the inverse of the serializer.
        size_limit_in_bytes: Optional maximum size limit in bytes. When set, items
            are evicted (LRU) to stay under this limit. Must be >= 4096 if specified.
        max_items: Optional maximum number of items to store. When exceeded, the
            least recently used items are evicted.
        default_ttl: Optional default time-to-live in seconds for stored values.
        expiration_thread_delay: Delay in seconds between expiration check iterations.
            Defaults to 10.0 seconds.
        expiration_thread_max_checks_per_iteration: Maximum number of items to check
            for expiration in each iteration. Defaults to 10,000.
        expiration_thread_log: Whether to enable debug logging for expiration
            operations. Defaults to False.
        expiration_disabled: If True, disables TTL expiration entirely. Defaults to False.

    Example:
        >>> from atomic_lru import Cache
        >>> cache = Cache(max_items=100, default_ttl=3600)  # 1 hour TTL
        >>> # Store any Python object
        >>> cache.set("user:123", {"name": "Alice", "age": 30})
        >>> # Retrieve it
        >>> user = cache.get("user:123")
        >>> if user is not CACHE_MISS:
        ...     print(user["name"])  # "Alice"
        >>> cache.close()

    Note:
        The cache stores serialized bytes internally, so `size_limit_in_bytes` works
        correctly with this class. Custom serializers should ensure they produce
        bytes that can be accurately measured for size calculations.
    """

    serializer: Serializer = field(default_factory=lambda: _default_serializer)
    deserializer: Deserializer = field(default_factory=lambda: _default_deserializer)

    def _serialize(self, value: Any) -> bytes:
        """Serialize a value to bytes using the configured serializer.

        Args:
            value: The value to serialize.

        Returns:
            The serialized bytes representation.

        Raises:
            ValueError: If serialization fails.
        """
        try:
            return self.serializer(value)
        except Exception as e:
            raise ValueError(
                f"Failed to serialize value of type: {type(value).__name__}"
            ) from e

    def _deserialize(self, value: bytes) -> Any:
        """Deserialize bytes to a value using the configured deserializer.

        Args:
            value: The bytes to deserialize.

        Returns:
            The deserialized value.

        Raises:
            ValueError: If deserialization fails.
        """
        try:
            return self.deserializer(value)
        except Exception as e:
            raise ValueError("Failed to deserialize value") from e

    def set(
        self, key: str, value: Any, ttl: float | DefaultTTLSentinel | None = DEFAULT_TTL
    ) -> None:
        """Store a value in the cache with automatic serialization.

        Serializes the value to bytes and stores it in the underlying storage.
        The value can be any Python object that can be serialized by the configured
        serializer.

        Args:
            key: The key to store the value under. Must be a string.
            value: The value to store. Can be any Python object serializable by
                the configured serializer.
            ttl: Time-to-live in seconds. Use `DEFAULT_TTL` to use the instance's
                `default_ttl` value, `None` to disable expiration for this item,
                or a float to set a specific TTL.

        Raises:
            RuntimeError: If the cache has been closed.
            ValueError: If serialization fails, or if size limits are set and
                the serialized value is too large.

        Note:
            The value is serialized before size checks are performed, so the
            serialized size is what counts toward size limits.
        """
        serialized_value = self._serialize(value)
        super().set(key=key, value=serialized_value, ttl=ttl)

    def get(self, key: str) -> Any | CacheMissSentinel:
        """Retrieve a value from the cache with automatic deserialization.

        Retrieves the value associated with the given key, deserializing it from
        bytes back to the original Python object. If the key doesn't exist or the
        value has expired, `CACHE_MISS` is returned.

        Args:
            key: The key to look up.

        Returns:
            The deserialized value if found and not expired, or `CACHE_MISS` if
            the key doesn't exist or the value has expired.

        Raises:
            ValueError: If deserialization fails (e.g., corrupted data).

        Note:
            Expired items are automatically deleted when accessed. This method
            does not raise exceptions for missing keys - use `CACHE_MISS` to
            check for cache misses.
        """
        serialized_value = super().get(key=key)
        if serialized_value is CACHE_MISS:
            return CACHE_MISS
        assert not isinstance(serialized_value, CacheMissSentinel)
        return self._deserialize(serialized_value)
