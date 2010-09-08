
PyLRU
=====

A least recently used (LRU) cache for Python.

Pylru implements a true LRU cache along with several support classes. The cache is efficient and written in pure Python. Basic operations (lookup, insert, delete) all run in a constant amount of time, regardless of the cache size.

This documentation is a work in progress. Check back soon, I'm working on it regularly. Until then see the source.


Usage
=====

You can install pylru, or you can just copy the source file pylru.py and use it in your own project.

An LRU cache object has a dictionary like interface and can be used in the same way::

    import pylru
    
    size = 32
    cache = pylru.lrucache(size)

    cache[key] = value  # Add a key/value pair
    key in cache        # Test for membership
    value = cache[key]  # Lookup a value given its key
    del cache[key]      # Remove a value given its key

    cache.size()        # Returns the size of the cache
    cache.size(x)       # Changes the size of the cache. x MUST be greater than
                        # zero. Decreasing the size of the cache will cause
                        # elements to be ejected from the cache if the new size
                        # is smaller than len(cache).
                        
    x = len(cache)      # Returns the number of elements stored in the cache.
                        # x will be less than or equal to cache.size()                        
                        
    cache.clear()       # Remove all elements from the cache.
    
    
