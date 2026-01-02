from cpython.dict cimport PyDict_Keys, PyDict_Next, PyDict_Size, PyDict_New, PyDict_SetItem, PyDict_GetItem, PyDict_Items, PyDict_Values, PyDict_Check
from cpython.object cimport PyObject, PyObject_Hash
from cpython.list cimport PyList_Check
from cpython.tuple cimport PyTuple_Check
from cpython.set cimport  PySet_Contains, PySet_New, PySet_Check, PySet_Add
from frozen_cub.utils cimport BasicHashable, Hash_Object, obj_is_primitive, XOR_Hash
from frozen_cub.common cimport  FALSE, TRUE, PY_ZERO, ZERO

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .frozen cimport already_frozen, freeze_tuple_items, to_frozen_dict, to_frozen_list, to_frozen_set

cpdef bint is_primitive(object obj):
    return obj_is_primitive(obj)

cdef object c_freeze(object obj, bint return_tuples = FALSE):
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

cpdef freeze(object obj):
    """Freeze an object by making it immutable and thus hashable."""
    return c_freeze(obj)


cdef class FrozenDict(BasicHashable):
    def __cinit__(self, object data = None):
        self.data = PyDict_New()
        self.data_size = PY_ZERO
        self._keys = PySet_New(<object>NULL)
        self._list_keys = None
        self._values = None
        self._items = None

        if data is None:
            return

        if PyDict_Check(data):
           data = c_freeze(data, TRUE) # Ideally we are tuple[tuple[Any, Any], ...] by now

        for k, v in data: # type:ignore[arg-type]
            PySet_Add(self._keys, k)
            PyDict_SetItem(self.data, k, c_freeze(v))
        self.data_size = PyDict_Size(self.data)

    def __init__(self, object data = None):
        pass

    cdef object _get(self, object key, object default=None):
        if not PySet_Contains(self._keys, key):
            return default
        value = PyDict_GetItem(self.data, key)
        if value is not NULL:
            return <object>value
        return default

    cpdef object get(self, object key, object default=None):
        return self._get(key, default)

    cpdef object keys(self):
        if self._list_keys is None:
            self._list_keys = list(PyDict_Keys(self.data))
        return self._list_keys # type: ignore

    cpdef object values(self):
        if self._values is None:
            self._values = list(PyDict_Values(self.data))
        return self._values # type: ignore

    cpdef object items(self):
        if self._items is None:
            self._items = list(PyDict_Items(self.data))
        return self._items # type: ignore

    cdef long _compute_hash(self):
        cdef Py_ssize_t pos = PY_ZERO
        cdef long result = ZERO
        cdef PyObject* key_ptr
        cdef PyObject* value_ptr

        if self.data_size == PY_ZERO:
            return <long>PyObject_Hash(())

        while PyDict_Next(self.data, &pos, &key_ptr, &value_ptr):
            result = XOR_Hash(Hash_Object(key_ptr), Hash_Object(value_ptr), result)
        return result

    cdef bool _contains(self, object key):
        return bool(PySet_Contains(self._keys, key))

    cpdef long get_hash(self):
        return self._compute_hash()

    def __eq__(self, other) -> bool:
        if not isinstance(other, FrozenDict): # type: ignore | Pyright doesn't understand this in Cython
            return False
        if self.data_size != other.data_size:
            return False
        return self.data == other.data

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        if not self.hash_computed:
            self.cached_hash = self._compute_hash()
            self.hash_computed = TRUE
        return self.cached_hash

    def __contains__(self, key) -> bool:
        return self._contains(key)

    def __iter__(self):
        return iter(self.keys()) # type: ignore

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.data})"

    def __str__(self) -> str:
        return self.__repr__()

    def __getitem__(self, key):
        if not self._contains(key):
            raise KeyError(key)
        return self._get(key)

    def __len__(self) -> int:
        return <int>self.data_size

NULL_KEY = "__null__"
NULL_TUPLE = (NULL_KEY,)
NONE_TUPLE = (None,)
NONE_ITEMS_TUPLE = ((NULL_KEY, None),)

cdef class NullFrozenDict(FrozenDict):
    def __init__(self):
        self.data = PyDict_New()
        self.cacheable = FALSE
        self.data_size = PY_ZERO
        PyDict_SetItem(self.data, NULL_KEY, None)

    cpdef object keys(self):
        return NULL_TUPLE

    cpdef object values(self):
        return NONE_TUPLE

    cpdef object items(self):
        return NONE_ITEMS_TUPLE

    def __getitem__(self, key):
        return None

    def __hash__(self):
        raise NotImplementedError("NullFrozenDict does not support hashing")

    cpdef long _compute_hash(self) except *:
        raise NotImplementedError("NullFrozenDict does not support hashing")

    def __eq__(self, other) -> bool:
        return isinstance(other, NullFrozenDict)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __len__(self) -> int:
        return 0

    def __contains__(self, key) -> bool:
        return False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

NULL_FROZEN_DICT = NullFrozenDict()
