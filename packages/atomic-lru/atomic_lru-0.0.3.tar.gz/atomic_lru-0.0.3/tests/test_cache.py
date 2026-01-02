import time

import pytest

from atomic_lru import CACHE_MISS, DEFAULT_TTL, Cache, DefaultTTLSentinel


def test_cache_basic():
    cache = Cache(size_limit_in_bytes=4096, max_items=100, default_ttl=None)
    assert cache.number_of_items == 0

    # Test storing and retrieving various types
    cache.set("str_key", "hello")
    assert cache.get("str_key") == "hello"

    cache.set("int_key", 42)
    assert cache.get("int_key") == 42

    cache.set("float_key", 3.14)
    assert cache.get("float_key") == 3.14

    cache.set("list_key", [1, 2, 3])
    assert cache.get("list_key") == [1, 2, 3]

    cache.set("dict_key", {"a": 1, "b": 2})
    assert cache.get("dict_key") == {"a": 1, "b": 2}

    cache.set("tuple_key", (1, 2, 3))
    assert cache.get("tuple_key") == (1, 2, 3)

    cache.set("bool_key", True)
    assert cache.get("bool_key") is True

    cache.set("none_key", None)
    assert cache.get("none_key") is None

    assert cache.number_of_items == 8


def test_cache_miss():
    cache = Cache()
    assert cache.get("nonexistent") is CACHE_MISS

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    assert cache.get("key2") is CACHE_MISS


def test_cache_overwrite():
    cache = Cache()
    cache.set("key", "value1")
    assert cache.get("key") == "value1"

    cache.set("key", "value2")
    assert cache.get("key") == "value2"
    assert cache.number_of_items == 1


def test_cache_ttl():
    cache = Cache(default_ttl=0.1, expiration_thread_max_checks_per_iteration=0)

    # Test with default TTL
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    time.sleep(0.2)
    assert cache.get("key1") is CACHE_MISS

    # Test with explicit TTL
    cache.set("key2", "value2", ttl=0.1)
    assert cache.get("key2") == "value2"

    time.sleep(0.2)
    assert cache.get("key2") is CACHE_MISS

    # Test with no TTL
    cache.set("key3", "value3", ttl=None)
    assert cache.get("key3") == "value3"

    time.sleep(0.2)
    assert cache.get("key3") == "value3"  # Should still be there

    # Test with DEFAULT_TTL sentinel
    cache.set("key4", "value4", ttl=DEFAULT_TTL)
    assert cache.get("key4") == "value4"

    time.sleep(0.2)
    assert cache.get("key4") is CACHE_MISS


def test_cache_ttl_thread():
    cache = Cache(
        default_ttl=0.1,
        expiration_thread_delay=0.01,
        expiration_thread_max_checks_per_iteration=10,
    )

    cache.set("key1", "value1", ttl=0.1)
    cache.set("key2", "value2", ttl=60.0)  # Should not expire

    assert cache.number_of_items == 2

    time.sleep(0.5)

    assert cache.get("key1") is CACHE_MISS
    assert cache.get("key2") == "value2"
    assert cache.number_of_items == 1

    cache.close()


def test_cache_custom_serializer():
    def custom_serializer(value):
        if isinstance(value, str):
            return value.encode("utf-8")
        raise ValueError("Can only serialize strings")

    def custom_deserializer(value):
        return value.decode("utf-8")

    cache = Cache(serializer=custom_serializer, deserializer=custom_deserializer)

    cache.set("key", "hello")
    assert cache.get("key") == "hello"

    # Should raise ValueError for non-string values
    with pytest.raises(ValueError, match="Failed to serialize"):
        cache.set("key2", 42)


def test_cache_serialization_error():
    def failing_serializer(value):
        raise RuntimeError("Serialization failed")

    cache = Cache(serializer=failing_serializer)

    with pytest.raises(ValueError, match="Failed to serialize value of type"):
        cache.set("key", "value")


def test_cache_deserialization_error():
    def failing_deserializer(value):
        raise RuntimeError("Deserialization failed")

    cache = Cache(deserializer=failing_deserializer)

    # Use default serializer to store, but failing deserializer to retrieve
    cache.set("key", "value")

    with pytest.raises(ValueError, match="Failed to deserialize value"):
        cache.get("key")


def test_cache_complex_objects():
    cache = Cache()

    # Test nested structures
    nested_dict = {"a": {"b": {"c": [1, 2, 3]}}}
    cache.set("nested", nested_dict)
    assert cache.get("nested") == nested_dict

    # Test objects with various types
    complex_obj = {
        "str": "text",
        "int": 42,
        "float": 3.14,
        "list": [1, "two", 3.0],
        "dict": {"nested": "value"},
        "tuple": (1, 2, 3),
        "bool": True,
        "none": None,
    }
    cache.set("complex", complex_obj)
    assert cache.get("complex") == complex_obj


def test_cache_lru_behavior():
    cache = Cache(max_items=3, size_limit_in_bytes=None, default_ttl=None)

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    assert cache.number_of_items == 3

    # Access key1 to make it recently used
    assert cache.get("key1") == "value1"

    # Add key4, should evict key2 (least recently used)
    cache.set("key4", "value4")

    assert cache.number_of_items == 3
    assert cache.get("key1") == "value1"  # Should still be there
    assert cache.get("key2") is CACHE_MISS  # Should be evicted
    assert cache.get("key3") == "value3"  # Should still be there
    assert cache.get("key4") == "value4"  # Should be there


def test_cache_size_limit():
    cache = Cache(size_limit_in_bytes=8192, max_items=100, default_ttl=None)

    # Store some small values
    for i in range(10):
        cache.set(f"key{i}", f"value{i}")

    assert cache.number_of_items > 0
    assert cache.size_in_bytes < 8192

    # Try to store a very large value
    large_value = "x" * 10000
    cache.set("large", large_value)

    # Large value should be rejected (exceeds size_limit_in_bytes / 2)
    assert cache.get("large") is CACHE_MISS


def test_cache_delete():
    cache = Cache()

    cache.set("key1", "value1")
    cache.set("key2", "value2")

    assert cache.number_of_items == 2
    assert cache.get("key1") == "value1"

    cache.delete("key1")

    assert cache.number_of_items == 1
    assert cache.get("key1") is CACHE_MISS
    assert cache.get("key2") == "value2"

    # Delete non-existent key should do nothing
    cache.delete("nonexistent")
    assert cache.number_of_items == 1


def test_cache_clean_expired():
    cache = Cache(
        default_ttl=0.1,
        expiration_thread_max_checks_per_iteration=0,
    )

    cache.set("key1", "value1", ttl=0.1)
    cache.set("key2", "value2", ttl=None)  # No expiration

    assert cache.number_of_items == 2

    time.sleep(0.2)

    checked, deleted = cache.clean_expired()
    assert checked == 2
    assert deleted == 1
    assert cache.number_of_items == 1
    assert cache.get("key1") is CACHE_MISS
    assert cache.get("key2") == "value2"


def test_cache_close():
    cache = Cache(default_ttl=None)

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    cache.close(wait=True)

    # Should still be able to get values after close
    assert cache.get("key1") == "value1"

    # Should not be able to set new values after close
    with pytest.raises(RuntimeError):
        cache.set("key2", "value2")

    # Should be able to close multiple times
    cache.close(wait=True)


def test_cache_default_serializer_pickle():
    cache = Cache()

    # Test that default serializer can handle complex nested structures
    # This implicitly tests that pickle is working
    complex_nested = {
        "level1": {
            "level2": {
                "level3": {
                    "list": [1, 2, 3, {"nested": "dict"}],
                    "set": {1, 2, 3},  # Sets are pickled
                }
            }
        }
    }
    cache.set("complex", complex_nested)

    retrieved = cache.get("complex")
    assert retrieved == complex_nested
    assert retrieved is not CACHE_MISS
    assert isinstance(retrieved, dict)
    assert retrieved["level1"]["level2"]["level3"]["list"][3]["nested"] == "dict"


def test_cache_multiple_operations():
    cache = Cache(max_items=100, default_ttl=None)

    # Perform many operations
    for i in range(50):
        cache.set(f"key{i}", f"value{i}")

    assert cache.number_of_items == 50

    # Update some values
    for i in range(25):
        cache.set(f"key{i}", f"updated_value{i}")

    assert cache.number_of_items == 50

    # Verify updates
    for i in range(25):
        assert cache.get(f"key{i}") == f"updated_value{i}"

    # Verify unchanged values
    for i in range(25, 50):
        assert cache.get(f"key{i}") == f"value{i}"


def test_cache_empty_values():
    cache = Cache()

    cache.set("empty_str", "")
    assert cache.get("empty_str") == ""

    cache.set("empty_list", [])
    assert cache.get("empty_list") == []

    cache.set("empty_dict", {})
    assert cache.get("empty_dict") == {}

    cache.set("zero", 0)
    assert cache.get("zero") == 0

    cache.set("false", False)
    assert cache.get("false") is False


def test_cache_default_ttl_sentinel():
    cache = Cache(default_ttl=0.1, expiration_thread_max_checks_per_iteration=0)

    # Using DefaultTTLSentinel should use the default TTL
    cache.set("key1", "value1", ttl=DefaultTTLSentinel())
    assert cache.get("key1") == "value1"

    time.sleep(0.2)
    assert cache.get("key1") is CACHE_MISS

    # Setting ttl=None should override default
    cache.set("key2", "value2", ttl=None)
    assert cache.get("key2") == "value2"

    time.sleep(0.2)
    assert cache.get("key2") == "value2"  # Should still be there
