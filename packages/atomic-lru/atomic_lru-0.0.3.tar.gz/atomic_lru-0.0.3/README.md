# Atomic LRU

## What is this?

This is a **thread-safe** and **dependency-free** **in-memory** **LRU storage** Python 3.12+ library with optional Time To Live (TTL).

You can define:

- **limits** (`max-items` or `max-size-in-bytes`)
- **TTL expiration** (globally or per item)

to prevent the storage from growing too big.

You will get an automatic **LRU eviction** of the least recently used items when the limits are reached.

### High level API

The main use-case is to use it as a **cache** for your data. You store any kind of data type which will be **automatically serialized** to bytes. [^1]

```python
from atomic_lru import CACHE_MISS, Cache

# Create a Cache object instance (with a size limit of 1MB)
# (this object is thread-safe, so you can use it from multiple threads)
cache = Cache(size_limit_in_bytes=1_000_000, default_ttl=3600)

# Let's store something (a dictionnary here) in the cache with a custom TTL
cache.set("user:123", {"name": "Alice", "age": 30}, ttl=60)

# ...

# Let's retrieve it
user = cache.get("user:123")

if user is not CACHE_MISS:
    # cache hit
    print(user["name"])

```

### Low level API

But you can use it at a lower level to store any kind of data type without serialization. In that case, you will loose the `max-size-in-bytes` feature. See below for an example.

## Features

- Thread-Safe
- (optional) TTL expiration *(globally or per item)*
- (optional) Total size limit *(in bytes)* [^2]
- (optional) Max items limit
- Automatic LRU eviction *(when the limits are reached)*
- Full-typing support
- High level `Cache` API **with** automatic serialization/deserialization [^1]
- Low level `Storage` API **without** serialization/deserialization *(store only references to given objects)*

### Low level API example

```python
from atomic_lru import CACHE_MISS, Storage


class ExpensiveObject:
    """An expensive object that is not serializable."""

    pass


# Create a Storage object instance to store ExpensiveObject instances
# (this object is thread-safe, so you can use it from multiple threads)
storage = Storage[ExpensiveObject](max_items=100, default_ttl=3600)

# Create and store an ExpensiveObject instance
value = ExpensiveObject()
storage.set("key1", value, ttl=60)

# ...

# Let's retrieve it
obj = storage.get("key1")

if obj is not CACHE_MISS:
    # cache hit
    assert isinstance(obj, ExpensiveObject)
    assert id(obj) == id(value)  # this is the same object instance

```

[^1]: By default, `pickle` is used for serialization/deserialization but you can provide your own serializer/deserializer if you want to use a different format.
[^2]: This feature is only available when using the high level `Cache` API.

## DEV

This library is managed with `uv` and a `Makefile`. Execute:

- `uv sync` to create the virtual environment
- `make lint` to lint the code (style, checks, types, architecture) and fix obvious things
- `make test` to execute unit tests
- `make doc` to generate the documentation