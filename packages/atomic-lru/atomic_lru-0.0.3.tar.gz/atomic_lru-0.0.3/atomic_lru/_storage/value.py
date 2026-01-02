# Approximate size (in bytes) of a Value object in memory
# (if T is bytes)
import time
from dataclasses import dataclass

OBJECT_SIZE_APPROXIMATE_SIZE = 129


@dataclass(frozen=True, kw_only=True, slots=True)
class Value[T]:
    """A wrapper class for cache values with optional time-to-live (TTL) support.

    This class stores a value along with optional expiration metadata. When a TTL
    is provided, the value can be checked for expiration using the `is_expired`
    property. The class is immutable (frozen) and uses slots for memory efficiency.

    Args:
        value: The actual value to store in the cache.
        ttl: Optional time-to-live in seconds. If provided, the value will expire
            after this duration. Must be non-negative if specified. If None, the
            value never expires.

    Attributes:
        value: The stored value.
        ttl: The time-to-live in seconds, or None if the value never expires.

    Raises:
        ValueError: If `ttl` is negative.

    Example:
        >>> from atomic_lru._storage import _Value
        >>> # Value without expiration
        >>> val1 = _Value(value="hello", ttl=None)
        >>> val1.is_expired
        False
        >>> # Value with 60 second TTL
        >>> val2 = _Value(value="world", ttl=60.0)
        >>> val2.is_expired  # False immediately after creation
        False
    """

    value: T
    ttl: float | None = None

    # Internal timestamp when the value expires. None if the value never expires.
    _expire_at: float | None = None

    def __post_init__(self) -> None:
        """Initialize expiration timestamp based on TTL.

        If TTL is provided, calculates the expiration timestamp using
        `time.perf_counter()`. If TTL is None, sets expiration to None.
        """
        if self.ttl is None:
            object.__setattr__(self, "_expire_at", None)
        else:
            if self.ttl < 0:
                raise ValueError("TTL cannot be negative")
            object.__setattr__(self, "_expire_at", time.perf_counter() + self.ttl)

    @property
    def is_expired(self) -> bool:
        """Check if the value has expired.

        Returns:
            True if the value has a TTL and the current time exceeds the
            expiration timestamp, False otherwise. Values without a TTL
            (ttl=None) never expire.

        Note:
            Uses `time.perf_counter()` for high-resolution timing.
        """
        return self._expire_at is not None and self._expire_at < time.perf_counter()

    @property
    def size_in_bytes(self) -> int:
        """Calculate the approximate memory size of this instance in bytes.

        Returns:
            The approximate size in bytes if the value is of type `bytes`,
            including the object overhead. Returns 0 if the value is not bytes.

        Note:
            The size calculation includes an approximation of the object overhead
            (`_OBJECT_SIZE_APPROXIMATE_SIZE`) plus the length of the bytes value.
            For non-bytes values, this method returns 0 as accurate size
            calculation would require introspection of the value type.
        """
        if not isinstance(self.value, bytes):
            return 0
        return OBJECT_SIZE_APPROXIMATE_SIZE + len(self.value)
