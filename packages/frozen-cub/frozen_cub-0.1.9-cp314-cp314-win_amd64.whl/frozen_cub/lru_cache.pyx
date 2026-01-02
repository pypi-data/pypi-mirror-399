# type: ignore : Type Checker doesn't know about Header Files
from cython cimport final
from cpython.object cimport PyObject_Hash, PyObject
from cpython.ref cimport Py_INCREF
from frozen_cub.common cimport FALSE, FUNC_SUCCESS
from frozen_cub.utils cimport RLock, Acquire_RLock, Release_RLock, RLock_New, RLock_Free

EMPTY_KEY = <long>(-1)
NOT_FOUND = <size_t>(-1)
MIN_BUCKETS = <size_t>16
ZERO = <size_t>0
LOAD_FACTOR_NUM = <size_t>7    # Rehash when occupied > 7/10 of buckets
LOAD_FACTOR_DEN = <size_t>10
MIN_CAPACITY = <size_t>1
DEFAULT_CAPACITY = <size_t>512
MAX_CAPACITY = <size_t>1000000 # 1 million max capacity
MISSING = object()

@final
cdef class LRUCache:
    def __cinit__(self):
        self._cache = NULL
    
    def __dealloc__(self):
        if self._cache:
            cache_destroy(self._cache)
        RLock_Free(&self._mutex)
    
    def __init__(self, size_t capacity, bint thread_safe=FALSE):
        RLock_New(&self._mutex, thread_safe)
        self._cache = cache_create(capacity)
        if not self._cache:
            raise MemoryError("Failed to allocate LRU cache")
    
    cpdef void clear(self):
        Acquire_RLock(&self._mutex)
        cache_clear(self._cache)
        Release_RLock(&self._mutex)

    cpdef size_t length(self):
        return self._cache.length

    # ========================================================================
    # Internal API (cdef) - hash + original key
    # ========================================================================
    cdef bint _has(self, long hash_key, object orig_key):
        cdef bint result
        Acquire_RLock(&self._mutex)
        result = cache_has(self._cache, hash_key, orig_key)
        Release_RLock(&self._mutex)
        return result

    cdef object _get(self, long hash_key, object orig_key, object default = MISSING):
        cdef bint found
        cdef object result
        Acquire_RLock(&self._mutex)
        result = cache_get(self._cache, hash_key, orig_key, default, &found)
        Release_RLock(&self._mutex)
        return result

    cdef void _set(self, long hash_key, object orig_key, object value):
        Acquire_RLock(&self._mutex)
        if cache_set(self._cache, hash_key, orig_key, value) != FUNC_SUCCESS:
            Release_RLock(&self._mutex)
            raise MemoryError("Failed to insert into LRU cache")
        Release_RLock(&self._mutex)
    
    cdef void _delete(self, long hash_key, object orig_key):
        Acquire_RLock(&self._mutex)
        cache_delete(self._cache, hash_key, orig_key)
        Release_RLock(&self._mutex)

    cdef object _pop(self, long hash_key, object orig_key, object default = MISSING):
        cdef LRUNode* node
        cdef object value
        Acquire_RLock(&self._mutex)
        node = hash_get(self._cache, hash_key, orig_key)
        if node:
            value = value_get(node)
            Py_INCREF(value)  # Keep alive before node_release decrefs it
            list_unlink(node, self._cache)
            hash_delete(self._cache, hash_key, orig_key)
            node_release(self._cache, node)
            self._cache.length -= 1
            Release_RLock(&self._mutex)
            return value  # Cython will decref on return, balancing our incref
        Release_RLock(&self._mutex)
        return default

    # ========================================================================
    # Public API - accepts any hashable, uses PyObject_Hash internally
    # ========================================================================
    cpdef bint has(self, object key):
        return self._has(PyObject_Hash(key), key)

    cpdef object get(self, object key, object default=None):
        cdef long temp_hash = PyObject_Hash(key)
        cdef object result = self._get(temp_hash, key, default)
        if result is MISSING:
            return default
        return result

    cpdef void set(self, object key, object value):
        self._set(PyObject_Hash(key), key, value)

    cpdef void delete(self, object key):
        self._delete(PyObject_Hash(key), key)

    cpdef object pop(self, object key, object default=None):
        return self._pop(PyObject_Hash(key), key, default)

    cdef list _collect_keys(self):
        cdef LRUNode* current = self._cache.head
        cdef list keys = []

        while current:
            keys.append(key_get(current))
            current = current.next
        return keys

    def keys(self):
        """Return keys in LRU order."""
        Acquire_RLock(&self._mutex)
        cdef list result = self._collect_keys()
        Release_RLock(&self._mutex)
        return result

    cdef list _collect_values(self):
        cdef LRUNode* current = self._cache.head
        cdef list vals = []

        while current:
            vals.append(value_get(current))
            current = current.next
        return vals

    cdef list _collect_items(self):
        cdef LRUNode* current = self._cache.head
        cdef list result = []

        while current:
            result.append((key_get(current), value_get(current)))
            current = current.next
        return result

    cpdef void _lock_it(self):
        Acquire_RLock(&self._mutex)

    cpdef void _unlock_it(self):
        Release_RLock(&self._mutex)

    def values(self):
        """Return values in LRU order."""
        self._lock_it()
        cdef list result = self._collect_values()
        self._unlock_it()
        return result

    def items(self):
        """Return (key, value) pairs in LRU order."""
        self._lock_it()
        cdef list result = self._collect_items()
        self._unlock_it()
        return result

    @property
    def capacity(self):
        return self._cache.capacity

    @property
    def head(self):
        """Least recently used key, or None if empty."""
        if not self._cache.head:
            return None
        return key_get(self._cache.head)

    @property
    def tail(self):
        """Most recently used key, or None if empty."""
        if not self._cache.tail:
            return None
        return key_get(self._cache.tail)

    def __reduce__(self):
        raise TypeError("LRUCache cannot be pickled")

    def __contains__(self, object key):
        return self.has(key)
    
    def __len__(self):
        return self._cache.length

    def __getitem__(self, object key):
        cdef object result = self.get(key, MISSING)
        if result is MISSING:
            raise KeyError(key)
        return result

    def __setitem__(self, object key, object value):
        self.set(key, value)

    def __delitem__(self, object key):
        if self.pop(key, MISSING) is MISSING:
            raise KeyError(key)
    
    def __iter__(self):
        """Iterate keys in LRU order (least recent first)."""
        self._lock_it()
        cdef list keys = self._collect_keys()
        self._unlock_it()
        return iter(keys)
