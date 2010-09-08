

# Cache implementaion with a Least Recently Used (LRU) replacement policy and a
# basic dictionary interface.

# Copyright (C) 2006, 2009, 2010  Jay Hutchinson

# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



# The cache is implemented using a combination of a hash table (python
# dictionary) and a circular doubly linked list. Objects in the cache are
# stored in nodes. These nodes make up the linked list. The list is used to
# efficiently maintain the order that the objects have been used in. The front
# or "head" of the list contains the most recently used object, the "tail" of
# the list contains the least recently used object. When an object is "used" it
# can easily (in a constant amount of time) be moved to the front of the list,
# thus updating its position in the ordering. These nodes are also placed in
# the hash table under their associated key. The hash table allows efficient
# lookup of objects by key.

# The doubly linked list is composed of nodes. Each
# node has a 'prev' and 'next' variable to hold the node that comes before
# it and after it respectivly. Initially the two variables each point to
# the node itself, creating a circular doubly linked list of size one. Each
# node has a 'obj' and 'key' variable, holding the object and the key it is
# stored under respectivly.
class _dlnode(object):
    def __init__(self):
	    self.key = None


class lrucache(object):
  
    def __init__(self, size, callback=None):
      
        self.callback = callback
        # Initialize the hash table as empty.
        self.table = {}

    
        # Initalize the list with 'size' empty nodes. Create the first node and
        # assign it to the 'head' variable, which represents the head node in the
        # list. Then each iteration of the loop creates a subsequent node and
        # inserts it directly after the head node.
        self.head = _dlnode()
        self.head.next = self.head
        self.head.prev = self.head
	
        self.listSize = 1
        
        # Adjust the size
        self.size(size)


    def __len__(self):
        return len(self.table)
    
    # Does not call callback to write any changes!
    def clear(self):
        self.table.clear()
	
        node = self.head
        for i in range(self.listSize):
            node.key = None
            node.obj = None
            node = node.next
            
    
    def __contains__(self, key):
        return key in self.table
        # XXX Should this move the object to front of list? XXX
    
    def peek(self, key):
        # Look up the node
        node = self.table[key]
        return node.obj
    
    def __getitem__(self, key):
    
        # Look up the node
        node = self.table[key]
    
        # Update the list ordering. Move this node so that is directly proceeds the
        # head node. Then set the 'head' variable to it. This makes it the new head
        # of the list.
        self.mtf(node)
        self.head = node
    
        # Return the object
        return node.obj
  
  
    def __setitem__(self, key, obj):
    
        # First, see if any object is stored under 'key' in the cache already. If
        # so we are going to replace that object with the new one.
        if key in self.table:
      
            # Lookup the node
            node = self.table[key]
      
            # Replace the object
            node.obj = obj
      
            # Update the list ordering.
            self.mtf(node)
            self.head = node
      
            return
      
        # Ok, no object is currently stored under 'key' in the cache. We need to
        # choose a node to place the object 'obj' in. There are two cases. If the
        # cache is full some object will have to be pushed out of the cache. We
        # want to choose the node with the least recently used object. This is the
        # node at the tail of the list. If the cache is not full we want to choose
        # a node that is empty. Because of the way the list is managed, the empty
        # nodes are always together at the tail end of the list. Thus, in either
        # case, by chooseing the node at the tail of the list our conditions are
        # satisfied.
    
        # Since the list is circular, the tail node directly preceeds the 'head'
        # node.
        node = self.head.prev
    
        # If the node already contains something we need to remove the old key from
        # the dictionary.
        if node.key is not None:
            if self.callback:
                self.callback(node.key, node.obj)
            del self.table[node.key]
    
        # Place the new key and object in the node
        node.key = key
        node.obj = obj
    
        # Add the node to the dictionary under the new key.
        self.table[node.key] = node 
    
        # We need to move the node to the head of the list. The node is the tail
        # node, so it directly preceeds the head node due to the list being
        # circular. Therefore, the ordering is already correct, we just need to
        # adjust the 'head' variable.
        self.head = node
  
  
    def __delitem__(self, key):
    
        # Lookup the node, then remove it from the hash table.
        node = self.table[key]
        del self.table[key]
    
        # Set the 'key' to None to indicate that the node is empty. We also set the
        # 'obj' to None to release the reference to the object, though it is not
        # strictly necessary.
        node.key = None
        node.obj = None
    
        # Because this node is now empty we want to reuse it before any non-empty
        # node. To do that we want to move it to the tail of the list. We move it
        # so that it directly preceeds the 'head' node. This makes it the tail
        # node. The 'head' is then adjusted. This adjustment ensures correctness
        # even for the case where the 'node' is the 'head' node.
        self.mtf(node)
        self.head = node.next

      
    
    def size(self, size=None):
      
        if size is not None:
            assert size > 0
            if size > self.listSize:
                self.addTailNode(size - self.listSize)
            elif size < self.listSize:
                self.removeTailNode(self.listSize - size)
                
        return self.listSize
            
	
    def addTailNode(self, n):
        for i in range(n):
            node = _dlnode()
            node.next = self.head
            node.prev = self.head.prev
      
            self.head.prev.next = node
            self.head.prev = node
        
        self.listSize += n


    def removeTailNode(self, n):
        assert self.listSize > 1   # Invarient. XXX REMOVE this line XXX
        for i in range(n):
            node = self.head.prev
            if node.key is not None:
                if self.callback:
                    self.callback(node.key, node.obj)
                del self.table[node.key]
            
            # Splice the tail node out of the list
            self.head.prev = node.prev
            node.prev.next = self.head
            
            # The next four lines are not strictly necessary.
            node.prev = None
            node.next = None
            
            node.key = None
            node.obj = None
            
        self.listSize -= n
  
    def __del__(self):
        # When we are finished with the cache, special care is taken to break the
        # doubly linked list, so that there are no cycles. First all of the 'prev'
        # links are broken. Then the 'next' link between the 'tail' node and the
        # 'head' node is broken.
    
        tail = self.head.prev
    
        node = self.head
        while node.prev is not None:
            node = node.prev
            node.next.prev = None
      
        tail.next = None
  
  
    # This method adjusts the doubly linked list so that 'node' directly preeceds
    # the 'head' node. Note that it works even if 'node' already directly
    # preceeds the 'head' node or if 'node' is the 'head' node, in either case
    # the order of the list is unchanged.
    def mtf(self, node):
    
        node.prev.next = node.next
        node.next.prev = node.prev

        node.prev = self.head.prev
        node.next = self.head.prev.next
    
        node.next.prev = node
        node.prev.next = node



class lruwrap(object):
    def __init__(self, store, size, writeback=False):
        self.store = store
        self.writeback = writeback

        if not self.writeback:
            self.cache = lrucache(size)
        else:
            self.dirty = set()
            def callback(key, value):
                if key in self.dirty:
                    self.store[key] = value
                    self.dirty.remove(key)
            self.cache = lrucache(size, callback)
        
    def __len__(self):
        return len(self.store)
        
    def size(self, size=None):
        self.cache.size(size)
        
    def clear(self):
        self.cache.clear()
        self.store.clear()
        if self.writeback:
            self.dirty.clear()
        
    def __contains__(self, key):
        # XXX Should this bring the key/value into the cache?
        if key in self.cache:
            return True
        if key in self.store:
            return True
            
        return False
    
    def __getitem__(self, key):
        try:
            return self.cache[key]
        except KeyError:
            pass
        
        return self.store[key] # XXX Re-raise exception?
        
    def __setitem__(self, key, value):
        self.cache[key] = value
        
        if self.writeback:
            self.dirty.add(key)
        else:
            self.store[key] = value
            
    def __delitem__(self, key):
        if self.writeback:
            found = False
            try:
                del self.cache[key]
                found = True
                self.dirty.remove(key)
            except KeyError:
                pass
            
            try:
                del self.store[key]
                found = True
            except KeyError:
                pass
            
            if not found:  # If not found in cache or store, raise error.
                raise KeyError

        else:  # Write-through behavior, cache and store should be consistent
            del self.store[key]
            try:
                del self.cache[key]
            except KeyError:
                pass
        
        
    def sync(self):
        if self.writeback:
            for key in self.dirty:
                value = self.cache.peek(key)  # Doesn't change the cache's order
                self.store[key] = value
            self.dirty.clear()
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sync()
        return False


class lrudecorator(object):
    def __init__(self, size):
        self.cache = lrucache(size)
        
    def __call__(self, func):
        def wrapped(*args):  # XXX What about kwargs
            try:
                return self.cache[args]
            except KeyError:
                pass
            
            value = func(*args)
            self.cache[args] = value
            return value
        return wrapped
