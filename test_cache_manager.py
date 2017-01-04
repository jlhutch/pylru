import unittest

from pylru import WriteThroughCacheManager, WriteBackCacheManager
from collections import Counter, MutableMapping #Counter is a Python 2.7 feature.

class SimpleBackingStore(MutableMapping):
    def __init__(self, entries=None):
        self.calls = Counter()
        
        self.entries = {}
        if entries is not None:
            self.entries.update(entries)

    def __len__(self):
        self.calls["__len__"] += 1
        return len(self.entries)
        
    def __iter__(self):
        self.calls["__iter__"] += 1
        for key in self.entries.keys():
            yield key
        
    def __getitem__(self, key):
        self.calls["__getitem__"] += 1
        return self.entries[key]
        
    def __setitem__(self, key, value):
        self.calls["__setitem__"] += 1
        self.entries[key] = value
        
    def __delitem__(self, key):
        self.calls["__delitem__"] += 1
        del(self.entries[key])
    
    def __contains__(self, key):
        self.calls["__contains__"] += 1
        return key in self.entries
        
class SimpleBackingStoreWithMSet(SimpleBackingStore):
    def should_use_mset(self, n):
        #Returns a boolean of whether to use mset over __setitem__ for n items.
        
        #mset_cost is how many times more expensive the mset command is relative to the __setitem__ command for the backing store.
        #In the unlikely event that mset is less expensive than __setitem__, you may as well use it for everything, return 1.
        mset_cost = 10
        return n >= mset_cost
    
    def mset(self, kvps):
        self.calls["mset"] += 1
        for key, value in kvps:
            self.entries[key] = value

class TestWriteThroughCacheManager(unittest.TestCase):
    def test_insert_causes_write(self):
        cache = WriteThroughCacheManager(SimpleBackingStore(), 100)
        for i in range(10):
            cache[i] = i
            self.assertEqual(cache.store.calls["__setitem__"], i+1)
       
class TestWriteBackCacheManager(unittest.TestCase):
    def test_insert_does_not_cause_write(self):
        cache = WriteBackCacheManager(SimpleBackingStore(), 100)
        for i in range(10):
            cache[i] = i
            self.assertEqual(cache.store.calls["__setitem__"], 0)
       
    def test_sync_done_individually(self):
        cache = WriteBackCacheManager(SimpleBackingStore(), 100)
        for i in range(10):
            cache[i] = i
        cache.sync()
        self.assertEqual(cache.store.calls["__setitem__"], 10)
        self.assertEqual(len(cache.store), 10)
        
    def test_sync_done_in_bulk_if_mset_exists(self):
        cache = WriteBackCacheManager(SimpleBackingStoreWithMSet(), 100)
        for i in range(10):
            cache[i] = i
        cache.sync()
        self.assertEqual(cache.store.calls["mset"], 1)
        self.assertEqual(cache.store.calls["__setitem__"], 0)
        self.assertEqual(len(cache.store), 10)   
        
    def test_sync_on_exit(self):
        cache = WriteBackCacheManager(SimpleBackingStoreWithMSet(), 100)
        with cache:
            for i in range(10):
                cache[i] = i
        self.assertEqual(cache.store.calls["mset"], 1)
        self.assertEqual(cache.store.calls["__setitem__"], 0)
        self.assertEqual(len(cache.store), 10)
    
if __name__ == '__main__':
    unittest.main()