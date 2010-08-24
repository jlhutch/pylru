

from lru import lrucache

def _selftest():
    
    class simplelrucache:

        def __init__(self, size):
            self.size = size
            self.length = 0
            self.items = []

        def __contains__(self, key):
            for x in self.items:
                if x[0] == key:
                    return True
    
            return False

	
	
	
	
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
      
        assert False
  
  
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
    
        return
  
    def __delitem__(self, key):
    
        for i in range(len(self.cache)):
            if self.cache[i][0] == key:
                del self.cache[i]
                return
    
        return
      
  
    
    
    
def testa():
  
    a = lrucache(16)
  
    for i in range(len(vect)):
        a[vect[i]] = 0
    
def testb():
  
    a = simplelrucache(16)
  
    for i in range(len(vect)):
        a[vect[i]] = 0
    
    
if __name__ == '__main__':
  
    import random
  
    a = lrucache(20)
    b = simplelrucache(20)
  
    for i in range(256):
        x = random.randint(0, 256)
        y = random.randint(0, 256)
    
        a[x] = y
        b[x] = y
    
        q = []
        z = a.head
        for j in range(len(a.table)):
            q.append([z.key, z.obj])
            z = z.next
      
        if q != b.cache[::-1]:
            print i
            print b.cache[::-1]
            print q
            print a.table.keys()
            assert False
  
  

    from timeit import Timer
    import random
  
    global vect
  
    vect = []
    for i in range(1000000):
        vect.append(random.randint(0, 1000))
  
    t = Timer("testa()", "from __main__ import testa")
    print t.timeit(1)

    t = Timer("testb()", "from __main__ import testb")
    print t.timeit(1)
  
