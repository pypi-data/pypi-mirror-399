from cpython.dict cimport PyDict_Next, PyDict_Size, PyDict_Check
from cpython.object cimport PyObject, PyObject_IsInstance
from cpython.list cimport PyList_Size, PyList_GET_ITEM, PyList_Check
from cpython.tuple cimport PyTuple_New, PyTuple_Size, PyTuple_GET_ITEM, PyTuple_Check
from cpython.set cimport  PySet_Size, PyFrozenSet_New, PySet_Check
from frozen_cub.common cimport  FALSE, TRUE, PY_ZERO, PY_ONE, PY_TWO
from frozen_cub.utils cimport BasicHashable, Tuple_Set_INCREF, obj_is_primitive

cdef inline bint already_frozen(object obj):
    return PyObject_IsInstance(obj, BasicHashable)

cdef inline object to_frozen_dict(dict obj, bint return_tuples = FALSE):
    cdef Py_ssize_t pos = PY_ZERO, index = PY_ZERO, size = PyDict_Size(obj)
    cdef PyObject* key_ptr
    cdef PyObject* value_ptr
    cdef tuple items = PyTuple_New(size), item

    while PyDict_Next(obj, &pos, &key_ptr, &value_ptr):
        item = PyTuple_New(PY_TWO)
        Tuple_Set_INCREF(item, PY_ZERO, <object>key_ptr)
        Tuple_Set_INCREF(item, PY_ONE, c_freeze(<object>value_ptr))
        Tuple_Set_INCREF(items, index, item)
        index += 1
    if return_tuples:
        return items
    return FrozenDict(items) # type: ignore

cdef inline tuple to_frozen_list(list obj):
    cdef Py_ssize_t size = PyList_Size(obj), index = PY_ZERO
    cdef tuple items = PyTuple_New(size)
    
    while index < size:
        Tuple_Set_INCREF(items, index, c_freeze(<object>PyList_GET_ITEM(obj, index)))
        index += 1
    return items

cdef inline object to_frozen_set(set obj):
    cdef tuple frozen_items = PyTuple_New(PySet_Size(obj))
    cdef Py_ssize_t index = PY_ZERO
    for item in obj:
        Tuple_Set_INCREF(frozen_items, index, c_freeze(item))
        index += 1
    return PyFrozenSet_New(frozen_items)

cdef inline tuple freeze_tuple_items(tuple obj):
    cdef Py_ssize_t size = PyTuple_Size(obj), index = PY_ZERO
    cdef tuple frozen_items = PyTuple_New(size)
    while index < size:
        Tuple_Set_INCREF(frozen_items, index, c_freeze(<object>PyTuple_GET_ITEM(obj, index)))
        index += 1
    return frozen_items

cdef inline object inline_freeze(object obj, return_tuples = *):
    if obj_is_primitive(obj):
        return obj
    if already_frozen(obj):
        return obj
    if PyTuple_Check(obj):
        return freeze_tuple_items(obj) # type: ignore Pyright isn't recognizing PyTuple_Check
    if PyDict_Check(obj):
        return to_frozen_dict(obj, return_tuples) # type: ignore Pyright isn't recognizing PyDict_Check
    if PyList_Check(obj):
        return to_frozen_list(obj) # type: ignore Pyright isn't recognizing PyList_Check
    if PySet_Check(obj):
        return to_frozen_set(obj) # type: ignore Pyright isn't recognizing PySet_Check
    return obj

cpdef bint is_primitive(object obj)
cdef object c_freeze(object obj, bint return_tuples = *)
cpdef freeze(object obj)

cdef class FrozenDict(BasicHashable):
    cdef readonly dict data
    cdef readonly object _list_keys
    cdef readonly set _keys
    cdef readonly object _values
    cdef readonly object _items

    cdef object _get(self, object key, object default=*) # type: ignore
    cpdef object get(self, object key, object default=*) # type: ignore
    cpdef object keys(self) # type: ignore
    cpdef object values(self) # type: ignore
    cpdef object items(self) # type: ignore
    cdef long _compute_hash(self) # type: ignore
    cdef bool _contains(self, object key) # type: ignore
    cpdef long get_hash(self) # type: ignore
