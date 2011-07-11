
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


    a = lrucache(128)
    b = simplelrucache(128)

    test(a, b, a, b, verify)


def wraptest():

    def verify(p, q):
        assert p == q

    p = dict()
    q = dict()
    x = lruwrap(q, 128)

    test(p, x, p, q, verify)



def wraptest2():

    def verify(x, y):
        pass

    p = dict()
    q = dict()
    x = lruwrap(q, 128, True)

    test(p, x, None, None, verify)

    x.sync()
    assert p == q

def wraptest3():

    def verify(x, y):
        pass

    p = dict()
    q = dict()
    with lruwrap(q, 128, True) as x:
        test(p, x, None, None, verify)

    assert p == q


@lrudecorator(25)
def square(x):
    return x*x

def testDecorator():
    for i in range(1000):
        x = random.randint(0, 1493)
        assert square(x) == x*x


def testItems():
    a = lrucache(128)
    b = simplelrucache(128)

    for i in range(1000):
        x = random.randint(0, 512)
        y = random.randint(0, 512)
        a[x] = y
        b[x] = y

    for k, v in a.items():
        assert k in a
        assert a[k] == v
        assert b[k] == v

    # ensure the order returned in items() is correct.
    items = a.items()
    for k, v in reversed(items):
        a[k] = v

    # test the order is returned correctly.
    assert items == a.items()


if __name__ == '__main__':

    random.seed()


    for i in range(20):
        testcache()
        wraptest()
        wraptest2()
        wraptest3()
        testDecorator()
        testItems()


