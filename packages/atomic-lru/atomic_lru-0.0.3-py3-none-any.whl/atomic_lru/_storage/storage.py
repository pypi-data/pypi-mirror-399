import sys
import threading
from collections import OrderedDict
from dataclasses import dataclass, field
from itertools import islice

from atomic_lru._storage.thread import ExpirationThread
from atomic_lru._storage.types import (
    CACHE_MISS,
    DEFAULT_TTL,
    CacheMissSentinel,
    DefaultTTLSentinel,
)
from atomic_lru._storage.value import Value

# Approximate size (in bytes) of an item in the OrderedDict
PER_ITEM_APPROXIMATE_SIZE = 32


@dataclass
class Storage[T]:
    """Thread-safe in-memory storage with LRU eviction and optional TTL expiration.

    This class provides a thread-safe storage mechanism that automatically evicts
    the least recently used (LRU) items when size or item count limits are reached.
    It supports optional time-to-live (TTL) expiration for stored values, with a
    background thread that periodically cleans expired entries.

    The storage uses an OrderedDict internally to maintain insertion order and
    efficiently move items to the end when accessed (LRU behavior). All operations
    are protected by a lock to ensure thread safety.

    Args:
        size_limit_in_bytes: Optional maximum size limit in bytes. When set, items
            are evicted (LRU) to stay under this limit. Must be >= 4096 if specified.
            Only works correctly when storing `bytes` values. If None, no size limit
            is enforced.
        max_items: Optional maximum number of items to store. When exceeded, the
            least recently used items are evicted. If None, no item count limit is
            enforced.
        default_ttl: Optional default time-to-live in seconds for stored values.
            Can be overridden per item when calling `set()`. If None, values don't
            expire by default. Use `DEFAULT_TTL` sentinel to use this default when
            calling `set()`.
        expiration_thread_delay: Delay in seconds between expiration check iterations
            in the background thread. Defaults to 10.0 seconds.
        expiration_thread_max_checks_per_iteration: Maximum number of items to check
            for expiration in each iteration. This limits the work done per iteration
            to avoid blocking. Defaults to 10,000.
        expiration_thread_log: Whether to enable debug logging for expiration
            operations. Defaults to False.
        expiration_disabled: If True, disables TTL expiration entirely. No background
            thread is created, and all TTL values are ignored. Defaults to False.

    Example:
        >>> from atomic_lru import Storage
        >>> # Create storage with size limit
        >>> storage = Storage[bytes](size_limit_in_bytes=1024 * 1024)  # 1MB
        >>> storage.set("key1", b"value1")
        >>> value = storage.get("key1")
        >>> if value is not CACHE_MISS:
        ...     print(value)  # b'value1'
        >>> storage.close()

    Note:
        When using `size_limit_in_bytes`, values must be of type `bytes`. The size
        calculation is approximate and includes overhead for the storage structure.
        Items larger than half the size limit are rejected to prevent storage
        from being dominated by a single item.
    """

    size_limit_in_bytes: int | None = None
    max_items: int | None = None
    default_ttl: float | None = None
    expiration_thread_delay: float = 10.0
    expiration_thread_max_checks_per_iteration: int = 10_000
    expiration_thread_log: bool = False
    expiration_disabled: bool = False

    # Internal tracking of approximate size in bytes
    _size_in_bytes: int = 0

    # Internal OrderedDict storing key-value pairs
    _data: OrderedDict[str, Value[T]] = field(default_factory=OrderedDict)

    # Internal threading lock for thread safety
    __lock: threading.Lock = field(default_factory=threading.Lock)

    # Internal background thread for cleaning expired entries
    __expiration_thread: ExpirationThread | None = None

    # Internal flag indicating whether the storage has been closed
    __closed: bool = False

    def __post_init__(self) -> None:
        """Initialize the storage instance.

        Sets up the initial size tracking, starts the expiration thread if enabled,
        and validates configuration parameters.

        Raises:
            ValueError: If `size_limit_in_bytes` is set to a value less than 4096.
        """
        self._size_in_bytes = sys.getsizeof(self._data)
        if not self.expiration_disabled:
            self.__expiration_thread = ExpirationThread(
                clean_callback=self.clean_expired,
                delay=self.expiration_thread_delay,
                max_checks_per_iteration=self.expiration_thread_max_checks_per_iteration,
                log=self.expiration_thread_log,
            )
            self.__expiration_thread.start()
        if self.size_limit_in_bytes is not None and self.size_limit_in_bytes < 4096:
            raise ValueError("size_limit_in_bytes must be greater than 4096")

    def close(self, wait: bool = False) -> None:
        """Close the storage and stop the expiration thread.

        Marks the storage as closed and stops the background expiration thread
        if it was started. After closing, all operations except `size_in_bytes`
        and `number_of_items` will raise a `RuntimeError`.

        Args:
            wait: If True, blocks until the expiration thread has fully stopped.
                If False, returns immediately after signaling the thread to stop.
                Defaults to False.

        Note:
            This method is idempotent - calling it multiple times has no effect.
            It's recommended to call this method when you're done with the storage
            to ensure proper cleanup of background threads.
        """
        if self.__closed:
            return
        self.__closed = True
        if not self.expiration_disabled:
            assert self.__expiration_thread is not None
            self.__expiration_thread.stop(wait=wait)

    def _assert_not_closed(self) -> None:
        if self.__closed:
            raise RuntimeError("Storage is closed")

    @property
    def size_in_bytes(self) -> int:
        """Get the approximate current size of the storage in bytes.

        Returns:
            The approximate size in bytes. This includes the size of stored values
            and overhead for the storage structure. The calculation is approximate
            and only accurate when storing `bytes` values.

        Note:
            This property can be accessed even after the storage is closed.
        """
        with self.__lock:
            return self._size_in_bytes

    @property
    def number_of_items(self) -> int:
        """Get the current number of items stored.

        Returns:
            The number of key-value pairs currently stored in the cache.

        Note:
            This property can be accessed even after the storage is closed.
        """
        with self.__lock:
            return len(self._data)

    def __delete(self, key: str) -> None:
        value_obj = self._data[key]
        self._size_in_bytes -= value_obj.size_in_bytes + PER_ITEM_APPROXIMATE_SIZE
        del self._data[key]

    def __delete_least_recently_used_item(self) -> None:
        try:
            _, value_obj = self._data.popitem(last=False)
        except KeyError:
            return
        # popitem already removed the item, so we only need to update size tracking
        self._size_in_bytes -= value_obj.size_in_bytes + PER_ITEM_APPROXIMATE_SIZE

    def __delete_least_recently_used_items(
        self,
        until_size_in_bytes: int | None = None,
        until_number_of_items: int | None = None,
    ) -> None:
        if until_size_in_bytes is not None:
            while self._size_in_bytes > until_size_in_bytes:
                self.__delete_least_recently_used_item()
        if until_number_of_items is not None:
            while len(self._data) > until_number_of_items:
                self.__delete_least_recently_used_item()

    def _calculate_size_needed_for_eviction(
        self, new_value_obj: Value[T], old_value_obj: Value[T] | None
    ) -> int | None:
        """Calculate the target size for eviction before adding a new value.

        Args:
            new_value_obj: The new value object to be stored.
            old_value_obj: The existing value object if overwriting, None if new key.

        Returns:
            The target size in bytes to evict down to, or None if no size limit.
        """
        if self.size_limit_in_bytes is None:
            return None

        if old_value_obj is not None:
            # When overwriting, PER_ITEM_APPROXIMATE_SIZE stays the same,
            # so we only need to account for the difference in value sizes
            net_size_change = new_value_obj.size_in_bytes - old_value_obj.size_in_bytes
            return self.size_limit_in_bytes - net_size_change
        else:
            # When adding a new item, need space for value + PER_ITEM overhead
            return (
                self.size_limit_in_bytes
                - new_value_obj.size_in_bytes
                - PER_ITEM_APPROXIMATE_SIZE
            )

    def set(
        self, key: str, value: T, ttl: float | DefaultTTLSentinel | None = DEFAULT_TTL
    ) -> None:
        """Store a value in the cache.

        Stores a key-value pair in the cache. If size or item limits are set and
        exceeded, the least recently used items are automatically evicted to make
        room. The item is moved to the end of the LRU order (most recently used).

        Args:
            key: The key to store the value under. Must be a string.
            value: The value to store. If `size_limit_in_bytes` is set, must be
                of type `bytes`.
            ttl: Time-to-live in seconds. Use `DEFAULT_TTL` to use the instance's
                `default_ttl` value, `None` to disable expiration for this item,
                or a float to set a specific TTL. If `expiration_disabled` is True,
                this parameter is ignored.

        Raises:
            RuntimeError: If the storage has been closed.
            ValueError: If `size_limit_in_bytes` is set and `value` is not `bytes`,
                or if the value is larger than half the size limit.

        Note:
            Items larger than half the `size_limit_in_bytes` are rejected to prevent
            a single large item from dominating the cache. If the value is rejected
            due to size, this method returns silently without storing the value.
        """
        # Validate value type and size before acquiring lock
        if self.size_limit_in_bytes is not None:
            if not isinstance(value, bytes):
                raise ValueError("Value must be bytes if size_limit_in_bytes is set")
            if len(value) > self.size_limit_in_bytes / 2:
                return

        # Resolve TTL before acquiring lock
        if self.expiration_disabled:
            ttl = None
        resolved_ttl: float | None = (
            self.default_ttl if isinstance(ttl, DefaultTTLSentinel) else ttl
        )

        value_obj = Value[T](value=value, ttl=resolved_ttl)

        with self.__lock:
            self._assert_not_closed()

            # Check if we're overwriting an existing key
            old_value_obj: Value[T] | None = self._data.get(key)
            is_overwriting = old_value_obj is not None

            # Compute target sizes
            until_size_in_bytes = self._calculate_size_needed_for_eviction(
                value_obj, old_value_obj
            )
            until_number_of_items: int | None = None
            if self.max_items is not None and not is_overwriting:
                until_number_of_items = self.max_items - 1

            # Evict items if needed to make room
            self.__delete_least_recently_used_items(
                until_size_in_bytes=until_size_in_bytes,
                until_number_of_items=until_number_of_items,
            )

            # Update size tracking: calculate net change instead of subtract then add
            if is_overwriting:
                # Net change: new size - old size (PER_ITEM_APPROXIMATE_SIZE cancels out)
                assert old_value_obj is not None  # Type narrowing for type checker
                size_delta = value_obj.size_in_bytes - old_value_obj.size_in_bytes
                self._size_in_bytes += size_delta
            else:
                # New item: add value size + overhead
                self._size_in_bytes += (
                    value_obj.size_in_bytes + PER_ITEM_APPROXIMATE_SIZE
                )

            # Store the value (moves to end of OrderedDict for LRU)
            self._data[key] = value_obj

    def get(self, key: str) -> T | CacheMissSentinel:
        """Retrieve a value from the cache.

        Retrieves the value associated with the given key. If the key exists and
        the value hasn't expired, it is moved to the end of the LRU order (most
        recently used) and returned. If the key doesn't exist or the value has
        expired, `CACHE_MISS` is returned.

        Args:
            key: The key to look up.

        Returns:
            The stored value if found and not expired, or `CACHE_MISS` if the key
            doesn't exist or the value has expired.

        Note:
            Expired items are automatically deleted when accessed. This method does
            not raise exceptions for missing keys - use `CACHE_MISS` to check for
            cache misses.
        """
        with self.__lock:
            value_obj = self._data.get(key)
            if value_obj is None:
                return CACHE_MISS
            if value_obj.is_expired:
                self.__delete(key)
                return CACHE_MISS
            self._data.move_to_end(key)
            return value_obj.value

    def delete(self, key: str) -> bool:
        """Delete a key-value pair from the cache.

        Removes the specified key and its associated value from the cache if it
        exists. The size tracking is updated accordingly.

        Args:
            key: The key to delete.

        Returns:
            True if the key existed and was deleted, False if the key didn't exist.

        Raises:
            RuntimeError: If the storage has been closed.
        """
        with self.__lock:
            self._assert_not_closed()
            if key not in self._data:
                return False
            self.__delete(key)
            return True

    def clean_expired(
        self, start: int | None = None, stop: int | None = None
    ) -> tuple[int, int]:
        """Clean expired items from the cache.

        Checks items in the specified range for expiration and removes those that
        have expired. This method is typically called by the background expiration
        thread, but can also be called manually.

        Args:
            start: Optional start index (inclusive) for the range of items to check.
                If None, checks from the beginning.
            stop: Optional stop index (exclusive) for the range of items to check.
                If None, checks until the end.

        Returns:
            A tuple of (tested_count, deleted_count) where:
            - tested_count: Number of items checked for expiration
            - deleted_count: Number of expired items that were deleted

        Raises:
            RuntimeError: If the storage has been closed.

        Note:
            If `expiration_disabled` is True, this method returns (0, 0) without
            performing any checks. The items are checked in insertion order (LRU order).
        """
        if self.expiration_disabled:
            return 0, 0
        tested: int = 0
        deleted: int = 0
        with self.__lock:
            self._assert_not_closed()
            expired_keys: list[str] = []
            for key, value_obj in islice(self._data.items(), start, stop):
                tested += 1
                if value_obj.is_expired:
                    expired_keys.append(key)
            for key in expired_keys:
                deleted += 1
                self.__delete(key)
        return tested, deleted
