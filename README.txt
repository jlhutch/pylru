
PyLRU
=====

A least recently used (LRU) cache for Python.

Pylru implements a true LRU cache along with several support classes. The cache is efficient and written in pure Python. It works with Python 2.6+ including the new 3.x series. Basic operations (lookup, insert, delete) all run in a constant amount of time.


Usage
=====

You can install pylru, or you can just copy the source file pylru.py and use it in your own project.

An LRU cache object has a dictionary like interface and can be used in the same way::

    import pylru

    size = 100
    cache = pylru.lrucache(size)

    cache[key] = value  # Add a key/value pair
    key in cache        # Test for membership
    value = cache[key]  # Lookup a value given its key
    del cache[key]      # Remove a value given its key

    cache.keys()        # Returns the keys in the cache *
    cache.values()      # Returns the values in the cache *
    cache.items()       # Returns the key, value pairs in the cache *

    cache.size()        # Returns the size of the cache
    cache.size(x)       # Changes the size of the cache. x MUST be greater than
                        # zero.

    x = len(cache)      # Returns the number of elements stored in the cache.
                        # x will be less than or equal to cache.size()

    cache.clear()       # Remove all elements from the cache.

* These calls have no effect on the cache order.

The lrucache takes an optional callback function as a second argument. Since the cache has a fixed size some operations, such as an insertion, may cause a key/value pair to be ejected. If the optional callback function is given it will be called when this occurs. For example::

    import pylru

    def callback(key, value):
        print (key, value)    # A dumb callback that just prints the key/value

    size = 100
    cache = pylru.lrucache(size, callback)

    # Use the cache... When it gets full some pairs may be ejected due to
    # the fixed cache size. But, not before the callback is called to let you
    # know.

Often a cache is used to speed up access to some other low latency object. If that object has a dictionary interface a convenience wrapper class provided by PyLRU can be used. This class takes as an argument the object you want to wrap and the cache size. It then creates an LRU cache for the object and automatically manages it. For example, imagine you have an object with a dictionary interface that reads/writes its values to and from a remote server. Let us call this object slowDict::

    import pylru

    size = 100
    cacheDict = pylru.lruwrap(slowDict, size)

    # Now cacheDict can be used just like slowDict, except all of the lookups
    # are automatically cached for you using an LRU cache.

By default lruwrap uses write-through semantics. For instance, in the above example insertions are updated in the cache and written through to slowDict immediatly. The cache and the underlying object are not allowed to get out of sync. So only lookup performace can be improved by the cache. lruwrap takes an optional third argument. If set to True write-back semantics will be used. Insertions will be updated to the cache. The underlying slowDict will automatically be updated only when a "dirty" key/value pair is ejected from the cache.

The programmer is responsible for one thing though. They MUST call sync() when they are finished. This ensures that the last of the "dirty" entries in the cache are written back::


    import pylru

    size = 100
    cacheDict = pylru.lruwrap(slowDict, size, True)

    # Now cacheDict can be used just like slowDict, except all of the lookups
    # are automatically cached for you using an LRU cache with Write-Back
    # semantics.

    # DON'T forget to call sync() when finished
    cacheDict.sync()

To help the programmer with this the lruwrap can be used in a with statement::

    with pylru.lruwrap(slowDict, size, True) as cacheDict

        # Use cacheDict, sync() is called automatically for you when leaving the
        # with statment block.


PyLRU also provides a function decorator::

    from pylru import lrudecorator

    @lrudecorator(100)
    def square(x):
        return x*x

    # Now results of the square function are cached for future lookup.

To iterate over the cache elements, use .items()::

    import pylru

    cache = pylru.lrucache(size, callback)

    # items() returns a list of key, value pairs without modifying order.
    for key, val in cache.items():
      print key, val

    # WARNING: while keys() does not modify order, the cache[key] call does!
    for key in cache.keys():
      print key, cache[key]
