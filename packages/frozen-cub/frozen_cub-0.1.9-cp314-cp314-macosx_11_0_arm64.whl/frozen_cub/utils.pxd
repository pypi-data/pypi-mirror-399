from cpython.object cimport PyObject, PyObject_Hash
from cpython.ref cimport Py_INCREF
from cpython.tuple cimport PyTuple_SET_ITEM
from cpython.object cimport PyObject
from cpython.unicode cimport PyUnicode_Check
from cpython.bytes cimport PyBytes_Check
from cpython.long cimport PyLong_Check
from cpython.float cimport PyFloat_Check
from cpython.bool cimport PyBool_Check

from cpython.pythread cimport (
      PyThread_type_lock,
      PyThread_allocate_lock,
      PyThread_free_lock,
      PyThread_acquire_lock,
      PyThread_release_lock,
      PyThread_get_thread_ident,
  )
from libc.stdlib cimport malloc, free
from frozen_cub.common cimport  FALSE, TRUE, THIRTY_ONE
  
cdef inline bint c_check_conditions(tuple conditions, object arg):
    cdef object cond
    for cond in conditions:
        if not cond(arg): # type: ignore[call-arg]
            return FALSE
    return TRUE

cdef class BasicHashable:
    cdef long cached_hash
    cdef bint hash_computed
    cdef readonly Py_ssize_t data_size
    cdef readonly bint __frozen__
    cdef readonly bint cacheable
    cdef long _compute_hash(self) # type: ignore

cdef inline void Tuple_Set_INCREF(tuple obj, Py_ssize_t index, object item):
    Py_INCREF(item)
    PyTuple_SET_ITEM(obj, index, item)

cdef inline long Hash_Object(PyObject* obj):
    return PyObject_Hash(<object>obj)

cdef inline long XOR_Hash(long a, long b, long current):
    cdef long pair_hash = a ^ (b * THIRTY_ONE)
    current ^= pair_hash
    return current

cdef inline bint obj_is_primitive(object obj):
    if obj is None:
        return TRUE
    if PyBool_Check(obj):
        return TRUE
    if PyUnicode_Check(obj):
        return TRUE
    if PyBytes_Check(obj):
        return TRUE
    if PyLong_Check(obj):
        return TRUE
    if PyFloat_Check(obj):
        return TRUE
    return FALSE

cdef const long NOT_OWNED = <long>(-1) 

cdef struct RLock:
      PyThread_type_lock lock
      long owner
      int count
      bint enabled

cdef inline RLock* RLock_New(RLock* r_lock, bint enabled):
    r_lock.lock = PyThread_allocate_lock()
    r_lock.owner = NOT_OWNED
    r_lock.count = 0
    r_lock.enabled = enabled
    return r_lock

cdef inline void RLock_Free(RLock* r_lock):
    if r_lock.lock:
        PyThread_free_lock(r_lock.lock)

cdef inline void Acquire_RLock(RLock* r_lock):
    if not r_lock.enabled:
        return # type: ignore
    cdef long me = PyThread_get_thread_ident()
    if r_lock.owner == me:
        r_lock.count += 1
        return # type: ignore
    PyThread_acquire_lock(r_lock.lock, 1)
    r_lock.owner = me
    r_lock.count = 1

cdef inline void Release_RLock(RLock* r_lock):
    if not r_lock.enabled:
        return # type: ignore
    r_lock.count -= 1
    if r_lock.count == 0:
        r_lock.owner = NOT_OWNED
        PyThread_release_lock(r_lock.lock)
