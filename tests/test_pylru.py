from __future__ import annotations

import random
from typing import Any, Callable

from pylru import (
    WriteBackCacheManager,
    WriteThroughCacheManager,
    lrucache,
    lrudecorator,
    lruwrap,
)


class SimpleLRUCache:
    """A naive LRU cache used as a reference implementation for fuzz testing."""

    def __init__(self, size: int) -> None:
        self.cache: list[list[int]] = []
        self.size = size

    def __contains__(self, key: object) -> bool:
        for x in self.cache:
            if x[0] == key:
                return True
        return False

    def __getitem__(self, key: int) -> int:
        for i in range(len(self.cache)):
            x = self.cache[i]
            if x[0] == key:
                del self.cache[i]
                self.cache.append(x)
                return x[1]
        raise KeyError

    def __setitem__(self, key: int, value: int) -> None:
        for i in range(len(self.cache)):
            x = self.cache[i]
            if x[0] == key:
                x[1] = value
                del self.cache[i]
                self.cache.append(x)
                return

        if len(self.cache) == self.size:
            self.cache = self.cache[1:]

        self.cache.append([key, value])

    def __delitem__(self, key: int) -> None:
        for i in range(len(self.cache)):
            if self.cache[i][0] == key:
                del self.cache[i]
                return
        raise KeyError

    def resize(self, x: int) -> None:
        assert x > 0
        self.size = x
        if x < len(self.cache):
            del self.cache[: len(self.cache) - x]


def _fuzz(
    a: Any,
    b: Any,
    c: Any,
    d: Any,
    verify: Callable[[Any, Any], None],
) -> None:
    """Run random insert/lookup/delete operations and verify consistency."""
    # when / then — random insertions
    for _ in range(1000):
        x = random.randint(0, 512)
        y = random.randint(0, 512)
        a[x] = y
        b[x] = y
        verify(c, d)

    # when / then — random lookups
    for _ in range(1000):
        x = random.randint(0, 512)
        if x in a:
            assert x in b
            _ = a[x]
            _ = b[x]
        else:
            assert x not in b
        verify(c, d)

    # when / then — random deletions
    for _ in range(256):
        x = random.randint(0, 512)
        if x in a:
            assert x in b
            del a[x]
            del b[x]
        else:
            assert x not in b
        verify(c, d)


def _verify_cache(a: lrucache, b: SimpleLRUCache) -> None:
    """Verify that the lrucache and SimpleLRUCache are consistent."""
    q: list[list[Any]] = []
    z = a.head
    for _ in range(len(a.table)):
        q.append([z.key, z.value])
        z = z.next

    assert q == b.cache[::-1]

    q2 = [(x, y) for x, y in q]
    assert list(a.items()) == q2
    assert list(zip(a.keys(), a.values())) == q2
    assert list(a.keys()) == list(a)


def test_lrucache_basic() -> None:
    """Fuzz test the basic lrucache with random operations and resizes."""
    # given
    a = lrucache(128)
    b = SimpleLRUCache(128)

    # when / then
    _verify_cache(a, b)
    _fuzz(a, b, a, b, _verify_cache)

    # when — resize smaller
    a.size(71)
    b.resize(71)

    # then
    _verify_cache(a, b)
    _fuzz(a, b, a, b, _verify_cache)

    # when — resize larger
    a.size(341)
    b.resize(341)

    # then
    _verify_cache(a, b)
    _fuzz(a, b, a, b, _verify_cache)

    # when — resize smaller again
    a.size(127)
    b.resize(127)

    # then
    _verify_cache(a, b)
    _fuzz(a, b, a, b, _verify_cache)


def test_write_through_cache_manager() -> None:
    """Fuzz test WriteThroughCacheManager against a plain dict."""

    def verify(p: dict[int, int], x: WriteThroughCacheManager) -> None:
        assert p == x.store
        for key, value in x.cache.items():
            assert x.store[key] == value

        tmp = sorted(x.items())
        tmp2 = sorted(p.items())
        assert tmp == tmp2

    # given
    p: dict[int, int] = {}
    q: dict[int, int] = {}
    x = lruwrap(q, 128)
    assert isinstance(x, WriteThroughCacheManager)

    # when / then
    _fuzz(p, x, p, x, verify)


def test_write_back_cache_manager() -> None:
    """Fuzz test WriteBackCacheManager against a plain dict."""

    def verify(p: dict[int, int], x: WriteBackCacheManager) -> None:
        for key, value in x.store.items():
            if key not in x.dirty:
                assert p[key] == value

        for key in x.dirty:
            assert x.cache.peek(key) == p[key]

        for key, value in x.cache.items():
            if key not in x.dirty:
                assert x.store[key] == p[key] == value

        tmp = sorted(x.items())
        tmp2 = sorted(p.items())
        assert tmp == tmp2

    # given
    p: dict[int, int] = {}
    q: dict[int, int] = {}
    x = lruwrap(q, 128, True)
    assert isinstance(x, WriteBackCacheManager)

    # when / then
    _fuzz(p, x, p, x, verify)

    x.sync()
    assert p == q


def test_write_back_context_manager() -> None:
    """Fuzz test WriteBackCacheManager used as a context manager."""

    def verify(p: dict[int, int], x: WriteBackCacheManager) -> None:
        for key, value in x.store.items():
            if key not in x.dirty:
                assert p[key] == value

        for key in x.dirty:
            assert x.cache.peek(key) == p[key]

        for key, value in x.cache.items():
            if key not in x.dirty:
                assert x.store[key] == p[key] == value

    # given
    p: dict[int, int] = {}
    q: dict[int, int] = {}

    # when
    with WriteBackCacheManager(q, 128) as x:
        _fuzz(p, x, p, x, verify)

    # then
    assert p == q


def test_decorator() -> None:
    """Test that the lrudecorator correctly caches function results."""

    @lrudecorator(100)
    def square(x: int) -> int:
        return x * x

    # when / then
    for _ in range(1000):
        x = random.randint(0, 200)
        assert square(x) == x * x
