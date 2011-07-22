
from pylru import *
import random

# This tests PyLRU by fuzzing it with random operations, then checking the
# results against another, simpler, LRU cache implementation.

class simplelrucache:

    def __init__(self, size):

        # Initialize the cache as empty.
        self.cache = []
        self.size = size

    def __contains__(self, key):

        for x in self.cache:
            if x[0] == key:
                return True

        return False


    def __getitem__(self, key):

        for i in range(len(self.cache)):
            x = self.cache[i]
            if x[0] == key:
                del self.cache[i]
                self.cache.append(x)
                return x[1]

        raise KeyError


    def __setitem__(self, key, obj):

        for i in range(len(self.cache)):
            x = self.cache[i]
            if x[0] == key:
                x[1] = obj
                del self.cache[i]
                self.cache.append(x)
                return

        if len(self.cache) == self.size:
            self.cache = self.cache[1:]

        self.cache.append([key, obj])


    def __delitem__(self, key):

        for i in range(len(self.cache)):
            if self.cache[i][0] == key:
                del self.cache[i]
                return

        raise KeyError


def test(a, b, c, d, verify):

    for i in range(1000):
        x = random.randint(0, 512)
        y = random.randint(0, 512)

        a[x] = y
        b[x] = y
        verify(c, d)

    for i in range(1000):
        x = random.randint(0, 512)
        if x in a:
            assert x in b
            z = a[x]
            z += b[x]
        else:
            assert x not in b
        verify(c, d)

    for i in range(256):
        x = random.randint(0, 512)
        if x in a:
            assert x in b
            del a[x]
            del b[x]
        else:
            assert x not in b
        verify(c, d)


def testcache():
    def verify(a, b):
        q = []
        z = a.head
        for j in range(len(a.table)):
            q.append([z.key, z.obj])
            z = z.next

        assert q == b.cache[::-1]

        q2 = []
        for x, y in q:
            q2.append((x, y))

        assert list(a.items()) == q2
        assert zip(a.keys(), a.values()) == q2
        assert list(a.keys()) == list(a)


    a = lrucache(128)
    b = simplelrucache(128)

    test(a, b, a, b, verify)


def wraptest():

    def verify(p, x):
        assert p == x.store
        for key, value in x.cache.items():
            assert x.store[key] == value
            
        tmp = list(x.items())
        tmp.sort()
        
        tmp2 = list(p.items())
        tmp2.sort()
        
        assert tmp == tmp2

    p = dict()
    q = dict()
    x = lruwrap(q, 128)

    test(p, x, p, x, verify)



def wraptest2():

    def verify(p, x):
        for key, value in x.store.items():
            if key not in x.dirty:
                assert p[key] == value
                
        for key in x.dirty:
            assert x.cache.peek(key) == p[key]
            
        for key, value in x.cache.items():
            if key not in x.dirty:
                assert x.store[key] == p[key] == value
                
        tmp = list(x.items())
        tmp.sort()
        
        tmp2 = list(p.items())
        tmp2.sort()
        
        assert tmp == tmp2

    p = dict()
    q = dict()
    x = lruwrap(q, 128, True)

    test(p, x, p, x, verify)

    x.sync()
    assert p == q

def wraptest3():

    def verify(p, x):
        for key, value in x.store.items():
            if key not in x.dirty:
                assert p[key] == value
                
        for key in x.dirty:
            assert x.cache.peek(key) == p[key]
            
        for key, value in x.cache.items():
            if key not in x.dirty:
                assert x.store[key] == p[key] == value

    p = dict()
    q = dict()
    with lruwrap(q, 128, True) as x:
        test(p, x, p, x, verify)

    assert p == q


@lrudecorator(25)
def square(x):
    return x*x

def testDecorator():
    for i in range(1000):
        x = random.randint(0, 1493)
        assert square(x) == x*x


if __name__ == '__main__':

    random.seed()


    for i in range(20):
        testcache()
        wraptest()
        wraptest2()
        wraptest3()
        testDecorator()


