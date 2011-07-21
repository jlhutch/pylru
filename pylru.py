

# Cache implementaion with a Least Recently Used (LRU) replacement policy and a
# basic dictionary interface.

# Copyright (C) 2006, 2009, 2010, 2011  Jay Hutchinson

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


        # Initalize the list with one empty node. Create a node and
        # assign it to the 'head' variable, which represents the head node in
        # the list.
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
        for node in self.dli():
            node.key = None
            node.obj = None

        self.table.clear()


    def __contains__(self, key):
        # XXX Should this move the object to front of list? XXX
        return key in self.table

    # Looks up a value in the cache without affecting cache order.
    def peek(self, key):
        # Look up the node
        node = self.table[key]
        return node.obj


    def __getitem__(self, key):
        # Look up the node
        node = self.table[key]

        # Update the list ordering. Move this node so that is directly proceeds
        # the head node. Then set the 'head' variable to it. This makes it the
        # new head of the list.
        self.mtf(node)
        self.head = node

        # Return the object
        return node.obj


    def __setitem__(self, key, obj):
        # First, see if any object is stored under 'key' in the cache already.
        # If so we are going to replace that object with the new one.
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
            if self.callback is not None:
                self.callback(node.key, node.obj)
            del self.table[node.key]

        # Place the new key and object in the node
        node.key = key
        node.obj = obj

        # Add the node to the dictionary under the new key.
        self.table[key] = node

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

    def __iter__(self):

        # Return an iterator that returns the keys in the cache in order from
        # the most recently to least recently used. Does not modify the cache
        # order.
        for node in self.dli():
            yield node.key

    def items(self):

        # Return an iterator that returns the (key, value) pairs in the cache
        # in order from the most recently to least recently used. Does not
        # modify the cache order.
        for node in self.dli():
            yield (node.key, node.obj)

    def keys(self):

        # Return an iterator that returns the keys in the cache in order from
        # the most recently to least recently used. Does not modify the cache
        # order.
        for node in self.dli():
            yield node.key

    def values(self):

        # Return an iterator that returns the values in the cache in order from
        # the most recently to least recently used. Does not modify the cache
        # order.
        for node in self.dli():
            yield node.obj

    def size(self, size=None):

        if size is not None:
            assert size > 0
            if size > self.listSize:
                self.addTailNode(size - self.listSize)
            elif size < self.listSize:
                self.removeTailNode(self.listSize - size)

        return self.listSize

    # Increases the size of the cache by inserting n empty nodes at the tail of
    # the list.
    def addTailNode(self, n):
        for i in range(n):
            node = _dlnode()
            node.next = self.head
            node.prev = self.head.prev

            self.head.prev.next = node
            self.head.prev = node

        self.listSize += n

    # Decreases the size of the list by removing n nodes from the tail of the
    # list.
    def removeTailNode(self, n):
        assert self.listSize > 1   # Invarient. XXX REMOVE this line XXX
        for i in range(n):
            node = self.head.prev
            if node.key is not None:
                if self.callback is not None:
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


    # This method adjusts the ordering of the doubly linked list so that 'node'
    # directly precedes the 'head' node. Because of the order of operations, if
    # 'node' already directly precedes the 'head' node or if 'node' is the
    # 'head' node the order of the list will be unchanged.
    def mtf(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

        node.prev = self.head.prev
        node.next = self.head.prev.next

        node.next.prev = node
        node.prev.next = node

    # This method returns an iterator that iterates over the non-empty nodes in
    # the doubly linked list in order from the most recently to the least
    # recently used.
    def dli(self):
        node = self.head
        for i in range(len(self.table)):
            yield node
            node = node.next


# The lruwrap class

class lruwrap(object):
    def __init__(self, store, size, writeback=False):
        self.store = store
        self.writeback = writeback

        if not self.writeback:
            # Create a cache object. This cache will be used to (hopefully)
            # speed up access to self.store.
            self.cache = lrucache(size)
        else:
            # Create a set to hold the dirty keys. Initially empty to match the
            # empty cache we are going to create.
            self.dirty = set()

            # Define a callback function to be called by the cache when a
            # key/value pair is about to be ejected. This callback will check to
            # see if the key is in the dirty set. If so, then it will update
            # the store object and remove the key from the dirty set.
            def callback(key, value):
                if key in self.dirty:
                    self.store[key] = value
                    self.dirty.remove(key)
                    
            # Create the cache object. This cache will be used to (hopefully)
            # speed up access to self.store. Set the callback function.
            self.cache = lrucache(size, callback)

    def __len__(self):
        # XXX Need a way to efficiently return len() when writeback is turned
        # on. If you really need the length you can call sync() then call
        # len(self.store), but syncing all of the time kind of defeats the
        # purpose of a writeback cache.
        assert self.writeback == False
        return len(self.store)

    # Returns/sets the size of the managed cache.
    def size(self, size=None):
        return self.cache.size(size)

    def clear(self):
        self.cache.clear()
        self.store.clear()
        if self.writeback:
            self.dirty.clear()

    def __contains__(self, key):
        # XXX Should this bring the key/value into the cache?
        # Check the cache first, since if it is there we can return quickly.
        if key in self.cache:
            return True

        # Not in the cache. Might be in the underlying store.
        if key in self.store:
            return True

        return False

    def __getitem__(self, key):
        # First we try the cache. If successful we just return the value. If not
        # we catch KeyError and ignore it since that just means the key was not
        # in the cache.
        try:
            return self.cache[key]
        except KeyError:
            pass

        # It wasn't in the cache. Look it up in the store, add the entry to the
        # cache, and return the value.
        value = self.store[key]
        self.cache[key] = value
        return value

    def __setitem__(self, key, value):
        # Add the key/value pair to the cache.
        self.cache[key] = value

        # If writeback is turned on then we just mark the key as dirty. That way
        # when the key/value pair is ejected from the cache it will be written
        # back to the store by the callback.
        #
        # If writeback is off (i.e. write-through is on) we go ahead and update
        # the store as well.
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

        else:
            # Write-through behavior cache and store should be consistent.
            # Delete it from the store.
            del self.store[key]
            try:
                # Ok, delete from the store was successful. It might also be in
                # the cache, try and delete it. If not we catch the KeyError and
                # ignore it.
                del self.cache[key]
            except KeyError:
                pass

    def __iter__(self):
        return self.keys()

    def keys(self):
        if self.writeback:
            for key in self.store.keys():
                if key not in self.dirty:
                    yield key
                
            for key in self.dirty:
                yield key
        else:
            for key in self.store.keys():
                yield key

    def values(self):
        if self.writeback:
            for key, value in self.items():
                yield value
        else:
            for value in self.store.values():
                yield value

    def items(self):
        if self.writeback:
            for key, value in self.store.items():
                if key not in self.dirty:
                    yield (key, value)
                
            for key in self.dirty:
                value = self.cache.peek(key)
                yield (key, value)
        else:
            for item in self.store.items():
                yield item


    def sync(self):
        # A cache with write-through behavior is always in sync with the
        # underlying store so we only need to work if write-back is on.
        if self.writeback:
            # For each dirty key, peek at its value in the cache and update the
            # store. Doesn't change the cache's order.
            for key in self.dirty:
                self.store[key] = self.cache.peek(key)
            # There are no dirty keys now.
            self.dirty.clear()

    def flush(self):
        self.sync()
        self.cache.clear()

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
