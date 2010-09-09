
from pylru import *
import random


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
      

def basictest():
    a = lrucache(128)
    b = simplelrucache(128)
  
    for i in range(500):
        x = random.randint(0, 512)
        y = random.randint(0, 512)
    
        a[x] = y
        b[x] = y
        verify(a, b)
    
    for i in range(1000):
        x = random.randint(0, 512)
        if x in a:
            assert x in b
            z = a[x]
            z += b[x]
        else:
            assert x not in b
        verify(a, b)
        
    for i in range(256):
        x = random.randint(0, 512)
        if x in a:
            assert x in b
            del a[x]
            del b[x]
        else:
            assert x not in b
        verify(a, b)
        
        
        
        

def verify2(x, q, n):
    for i in range(n):
        tmp1 = None
        tmp2 = None
        try:
            tmp1 = x[i]
        except KeyError:
            tmp1 = None
           
        try:
            tmp2 = q[i]
        except KeyError:
            tmp2 = None

        assert tmp1 == tmp2

def wraptest():
    q = dict()
    x = lruwrap(q, 32)
    for i in range(256):
        a = random.randint(0, 128)
        b = random.randint(0, 256)
    
        x[a] = b
    
    verify2(x, q, 128)
        
def wraptest2():

    q = dict()
    x = lruwrap(q, 32, True)
    for i in range(256):
        a = random.randint(0, 128)
        b = random.randint(0, 256)
    
        x[a] = b
        
    x.sync()
    verify2(x, q, 128)


def wraptest3():

    q = dict()
    with lruwrap(q, 32, True) as x:
        for i in range(256):
            a = random.randint(0, 128)
            b = random.randint(0, 256)
        
            x[a] = b
        
    verify2(x, q, 128)
        
        
@lrudecorator(25)
def square(x):
    return x*x
    
def testDecorator():
    for i in range(500):
        x = random.randint(0, 100)
        assert square(x) == x*x
    
    
def verify(a, b):
    q = []
    z = a.head
    for j in range(len(a.table)):
        q.append([z.key, z.obj])
        z = z.next
  
    if q != b.cache[::-1]:
        assert False
    
    
if __name__ == '__main__':
    
    random.seed()
    
    basictest()
    wraptest()
    wraptest2()
    wraptest3()
    testDecorator()


  
