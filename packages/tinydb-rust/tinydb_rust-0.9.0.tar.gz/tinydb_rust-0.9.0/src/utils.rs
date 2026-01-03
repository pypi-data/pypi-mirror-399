//! # Utility Functions and Data Structures
//!
//! This module provides utility functions and helper data structures used throughout
//! the TinyDB implementation, including LRU cache and object freezing utilities.
//!
//! ## Components
//!
//! - [`LRUCache`]: A least-recently-used cache implementation compatible with Python's TinyDB
//! - [`FrozenDict`]: An immutable, hashable dictionary for use in query caching
//! - [`freeze`]: Recursively converts mutable objects to immutable, hashable equivalents

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyFrozenSet, PyList, PySet, PyTuple};
use std::collections::HashMap;
use std::collections::VecDeque;

/// Wrapper for Python objects to use as HashMap keys
/// Uses Python's hash() function to get a hashable key
struct PyObjectKey {
    obj: Py<PyAny>,
    hash: i64,
}

impl PyObjectKey {
    fn new(py: Python<'_>, obj: Py<PyAny>) -> PyResult<Self> {
        let hash = obj.bind(py).hash()? as i64;
        Ok(PyObjectKey { obj, hash })
    }

    fn clone_ref(&self, py: Python<'_>) -> Self {
        PyObjectKey {
            obj: self.obj.clone_ref(py),
            hash: self.hash,
        }
    }
}

impl Clone for PyObjectKey {
    fn clone(&self) -> Self {
        Python::attach(|py| self.clone_ref(py))
    }
}

impl PartialEq for PyObjectKey {
    fn eq(&self, other: &Self) -> bool {
        Python::attach(|py| self.obj.bind(py).eq(other.obj.bind(py)).unwrap_or(false))
    }
}

impl Eq for PyObjectKey {}

impl std::hash::Hash for PyObjectKey {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.hash.hash(state);
    }
}

/// A least-recently-used (LRU) cache with optional capacity limit.
///
/// This cache implementation is compatible with Python's TinyDB `utils.LRUCache`.
/// It acts as a dictionary-like container with automatic eviction of the least
/// recently accessed items when the capacity is exceeded.
///
/// The cache maintains access order internally, moving items to the "most recently
/// used" position on every access. When the cache is full and a new item is added,
/// the least recently used item is automatically removed.
///
/// # Examples
///
/// ```python
/// from _tinydb_core import LRUCache
///
/// # Create a cache with capacity of 3
/// cache = LRUCache(3)
///
/// # Add items
/// cache['a'] = 1
/// cache['b'] = 2
/// cache['c'] = 3
/// assert len(cache) == 3
///
/// # Adding a 4th item evicts the least recently used ('a')
/// cache['d'] = 4
/// assert len(cache) == 3
/// assert 'a' not in cache
/// assert 'b' in cache  # 'b' is still there
///
/// # Accessing 'b' makes it most recently used
/// _ = cache['b']
/// cache['e'] = 5  # Now 'c' is evicted (least recently used)
/// assert 'c' not in cache
/// assert 'b' in cache  # 'b' was accessed, so it's kept
/// ```
///
/// # Unlimited Cache
///
/// If `capacity` is `None`, the cache has unlimited size:
///
/// ```python
/// cache = LRUCache(None)  # Unlimited capacity
/// for i in range(1000):
///     cache[i] = i
/// assert len(cache) == 1000
/// ```
#[pyclass(module = "_tinydb_core")]
pub struct LRUCache {
    cache: HashMap<PyObjectKey, Py<PyAny>>,
    order: VecDeque<PyObjectKey>,
    capacity: Option<usize>,
}

#[pymethods]
impl LRUCache {
    /// Create a new LRU cache with optional capacity.
    ///
    /// # Arguments
    ///
    /// * `capacity` - Maximum number of items the cache can hold. If `None`,
    ///   the cache has unlimited capacity.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// # Limited capacity
    /// cache = LRUCache(10)
    /// assert cache.length == 0
    ///
    /// # Unlimited capacity
    /// cache = LRUCache(None)
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    #[new]
    #[pyo3(signature = (capacity = None))]
    fn new(_py: Python<'_>, capacity: Option<usize>) -> PyResult<Self> {
        Ok(LRUCache {
            cache: HashMap::new(),
            order: VecDeque::new(),
            capacity,
        })
    }

    /// Get all keys in LRU order (least recently used first).
    ///
    /// Returns a list of keys ordered from least recently used to most recently used.
    /// This is useful for inspecting cache eviction order.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(3)
    /// cache['a'] = 1
    /// cache['b'] = 2
    /// cache['c'] = 3
    ///
    /// # Initially, order is insertion order
    /// lru_list = cache.lru
    /// assert list(lru_list) == ['a', 'b', 'c']
    ///
    /// # Accessing 'a' moves it to the end
    /// _ = cache['a']
    /// assert list(cache.lru) == ['b', 'c', 'a']
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    #[getter]
    fn lru(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let keys: Vec<Py<PyAny>> = self.order.iter().map(|k| k.obj.clone_ref(py)).collect();
        Ok(PyList::new(py, keys)?.unbind().into())
    }

    /// Get the current number of items in the cache.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(10)
    /// assert cache.length == 0
    ///
    /// cache['a'] = 1
    /// cache['b'] = 2
    /// assert cache.length == 2
    /// ```
    #[getter]
    fn length(&self) -> usize {
        self.cache.len()
    }

    /// Remove all entries from the cache.
    ///
    /// After calling this method, the cache will be empty and ready for new entries.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(10)
    /// cache['a'] = 1
    /// cache['b'] = 2
    /// assert cache.length == 2
    ///
    /// cache.clear()
    /// assert cache.length == 0
    /// assert 'a' not in cache
    /// ```
    fn clear(&mut self) {
        self.cache.clear();
        self.order.clear();
    }

    /// Get a value from the cache, returning `default` if the key is not found.
    ///
    /// Accessing a key moves it to the most recently used position, affecting
    /// the eviction order.
    ///
    /// # Arguments
    ///
    /// * `key` - The key to look up in the cache
    /// * `default` - Value to return if key is not found. If `None`, returns `None`.
    ///
    /// # Returns
    ///
    /// The value associated with `key`, or `default` if the key is not found.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(3)
    /// cache['a'] = 1
    /// cache['b'] = 2
    ///
    /// # Get existing key
    /// assert cache.get('a') == 1
    ///
    /// # Get non-existent key with default
    /// assert cache.get('c', 'default') == 'default'
    ///
    /// # Get non-existent key without default
    /// assert cache.get('c') is None
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyErr` if the key object is not hashable.
    #[pyo3(signature = (key, default = None))]
    fn get(
        &mut self,
        py: Python<'_>,
        key: Py<PyAny>,
        default: Option<Py<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let key_wrapper = PyObjectKey::new(py, key.clone_ref(py))?;

        if let Some(value) = self.cache.get(&key_wrapper) {
            // Move to end (most recently used)
            if let Some(pos) = self.order.iter().position(|k| k == &key_wrapper) {
                self.order.remove(pos);
            }
            self.order.push_back(key_wrapper.clone_ref(py));
            Ok(value.clone_ref(py))
        } else {
            Ok(default.unwrap_or_else(|| py.None()))
        }
    }

    /// Set a key-value pair in the cache.
    ///
    /// If the key already exists, its value is updated and the key is moved to
    /// the most recently used position. If the key is new and the cache is at
    /// capacity, the least recently used item is evicted.
    ///
    /// # Arguments
    ///
    /// * `key` - The key to set (must be hashable)
    /// * `value` - The value to associate with the key
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(3)
    /// cache.set('a', 1)
    /// cache.set('b', 2)
    /// cache.set('c', 3)
    ///
    /// # Update existing key
    /// cache.set('a', 10)
    /// assert cache.get('a') == 10
    ///
    /// # Adding new key when full evicts least recently used
    /// cache.set('d', 4)  # 'b' is evicted
    /// assert 'b' not in cache
    /// assert 'd' in cache
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyErr` if the key object is not hashable.
    fn set(&mut self, py: Python<'_>, key: Py<PyAny>, value: Py<PyAny>) -> PyResult<()> {
        let key_wrapper = PyObjectKey::new(py, key.clone_ref(py))?;

        if self.cache.contains_key(&key_wrapper) {
            // Update existing key and move to end
            self.cache.insert(key_wrapper.clone(), value);
            if let Some(pos) = self.order.iter().position(|k| k == &key_wrapper) {
                self.order.remove(pos);
            }
            self.order.push_back(key_wrapper);
        } else {
            // Add new key
            self.cache.insert(key_wrapper.clone(), value);
            self.order.push_back(key_wrapper);

            // Check if we need to remove old items
            if let Some(cap) = self.capacity {
                while self.cache.len() > cap {
                    if let Some(oldest_key) = self.order.pop_front() {
                        self.cache.remove(&oldest_key);
                    } else {
                        break;
                    }
                }
            }
        }
        Ok(())
    }

    /// Dictionary protocol: `cache[key]` syntax.
    ///
    /// Raises `KeyError` if the key is not found. Accessing a key moves it to
    /// the most recently used position.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(3)
    /// cache['a'] = 1
    /// assert cache['a'] == 1
    ///
    /// # Raises KeyError if key doesn't exist
    /// try:
    ///     _ = cache['nonexistent']
    /// except KeyError:
    ///     pass
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyKeyError` if the key is not found.
    /// Returns `PyErr` if the key object is not hashable.
    fn __getitem__(&mut self, py: Python<'_>, key: Py<PyAny>) -> PyResult<Py<PyAny>> {
        let result = self.get(py, key.clone_ref(py), None)?;
        if result.is_none(py) {
            Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(
                "Key not found",
            ))
        } else {
            Ok(result)
        }
    }

    /// Dictionary protocol: `cache[key] = value` syntax.
    ///
    /// Equivalent to [`set`](Self::set).
    ///
    /// # Errors
    ///
    /// Returns `PyErr` if the key object is not hashable.
    fn __setitem__(&mut self, py: Python<'_>, key: Py<PyAny>, value: Py<PyAny>) -> PyResult<()> {
        self.set(py, key, value)
    }

    /// Dictionary protocol: `del cache[key]` syntax.
    ///
    /// Removes the key-value pair from the cache. Raises `KeyError` if the key
    /// is not found.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(3)
    /// cache['a'] = 1
    /// cache['b'] = 2
    ///
    /// del cache['a']
    /// assert 'a' not in cache
    /// assert cache.length == 1
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyKeyError` if the key is not found.
    /// Returns `PyErr` if the key object is not hashable.
    fn __delitem__(&mut self, py: Python<'_>, key: Py<PyAny>) -> PyResult<()> {
        let key_wrapper = PyObjectKey::new(py, key)?;

        if self.cache.remove(&key_wrapper).is_some() {
            if let Some(pos) = self.order.iter().position(|k| k == &key_wrapper) {
                self.order.remove(pos);
            }
            Ok(())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(
                "Key not found",
            ))
        }
    }

    /// Dictionary protocol: `len(cache)` syntax.
    ///
    /// Returns the number of items in the cache. Equivalent to [`length`](Self::length).
    fn __len__(&self) -> usize {
        self.length()
    }

    /// Dictionary protocol: `key in cache` syntax.
    ///
    /// Checks if a key exists in the cache without affecting the access order.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(3)
    /// cache['a'] = 1
    ///
    /// assert 'a' in cache
    /// assert 'b' not in cache
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyErr` if the key object is not hashable.
    fn __contains__(&self, py: Python<'_>, key: Py<PyAny>) -> PyResult<bool> {
        let key_wrapper = PyObjectKey::new(py, key)?;
        Ok(self.cache.contains_key(&key_wrapper))
    }

    /// Dictionary protocol: `iter(cache)` syntax.
    ///
    /// Returns an iterator over the cache keys in LRU order (least recently used first).
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import LRUCache
    ///
    /// cache = LRUCache(3)
    /// cache['a'] = 1
    /// cache['b'] = 2
    /// cache['c'] = 3
    ///
    /// keys = list(cache)
    /// assert keys == ['a', 'b', 'c']
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    fn __iter__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let keys: Vec<Py<PyAny>> = self.order.iter().map(|k| k.obj.clone_ref(py)).collect();
        let list = PyList::new(py, keys)?;
        // Return an iterator over the list using Python's iter() function
        let iter_func = py.import("builtins")?.getattr("iter")?;
        let iterator = iter_func.call1((list,))?;
        Ok(iterator.into())
    }
}

/// An immutable, hashable dictionary for use in query caching.
///
/// Python dictionaries are not hashable because they are mutable. `FrozenDict`
/// provides an immutable wrapper around a dictionary that can be used as a
/// dictionary key or in sets. This is essential for caching queries that contain
/// dictionary values.
///
/// Once created, a `FrozenDict` cannot be modified. All mutating operations
/// (like `__setitem__`, `update`, `pop`, etc.) will raise `TypeError`.
///
/// # Hash Stability
///
/// The hash is computed from the dictionary's key-value pairs in a deterministic
/// order, ensuring that two `FrozenDict` instances with the same content will
/// have the same hash value.
///
/// # Examples
///
/// ```python
/// from _tinydb_core import FrozenDict
///
/// # Create a frozen dict
/// d = {'name': 'Alice', 'age': 30}
/// frozen = FrozenDict(d)
///
/// # Can be used as a dictionary key
/// cache = {}
/// cache[frozen] = 'value'
///
/// # Can be hashed
/// hash_value = hash(frozen)
///
/// # Immutable - cannot modify
/// try:
///     frozen['new_key'] = 'value'  # Raises TypeError
/// except TypeError:
///     pass
///
/// # Can still access values
/// assert frozen['name'] == 'Alice'
/// assert frozen.get('age') == 30
/// ```
#[pyclass(module = "_tinydb_core")]
pub struct FrozenDict {
    dict: Py<PyDict>,
    hash_value: u64,
}

#[pymethods]
impl FrozenDict {
    /// Create a new `FrozenDict` from a dictionary.
    ///
    /// The hash value is computed immediately from the dictionary contents.
    /// The original dictionary is stored internally and cannot be modified
    /// through the `FrozenDict` interface.
    ///
    /// # Arguments
    ///
    /// * `dict` - The dictionary to freeze. All keys and values must be hashable.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// d = {'a': 1, 'b': 2}
    /// frozen = FrozenDict(d)
    ///
    /// # Same content produces same hash
    /// frozen2 = FrozenDict({'a': 1, 'b': 2})
    /// assert hash(frozen) == hash(frozen2)
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyErr` if any key or value in the dictionary is not hashable.
    #[new]
    fn new(py: Python<'_>, dict: Bound<'_, PyDict>) -> PyResult<Self> {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        // Calculate hash from sorted items
        let mut hasher = DefaultHasher::new();

        // Sort items by key for stable hashing
        let mut items: Vec<(Py<PyAny>, Py<PyAny>)> =
            dict.iter().map(|(k, v)| (k.into(), v.into())).collect();

        // Sort by key hash for consistency
        items.sort_by(|a, b| {
            let hash_a = a.0.bind(py).hash().unwrap_or(0) as i64;
            let hash_b = b.0.bind(py).hash().unwrap_or(0) as i64;
            hash_a.cmp(&hash_b)
        });

        // Hash each key-value pair
        for (k, v) in items {
            let key_hash = k.bind(py).hash().unwrap_or(0) as i64;
            let val_hash = v.bind(py).hash().unwrap_or(0) as i64;
            key_hash.hash(&mut hasher);
            val_hash.hash(&mut hasher);
        }

        let hash_value = hasher.finish();

        Ok(FrozenDict {
            dict: dict.unbind(),
            hash_value,
        })
    }

    /// Return the hash value of this `FrozenDict`.
    ///
    /// The hash is computed from the dictionary's key-value pairs and is
    /// guaranteed to be stable for dictionaries with the same content.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// d1 = FrozenDict({'a': 1, 'b': 2})
    /// d2 = FrozenDict({'a': 1, 'b': 2})
    ///
    /// assert hash(d1) == hash(d2)
    /// assert hash(d1) == d1.__hash__()
    /// ```
    fn __hash__(&self) -> u64 {
        self.hash_value
    }

    /// Dictionary protocol: `frozen[key]` syntax.
    ///
    /// Returns the value associated with `key`. Raises `KeyError` if the key
    /// is not found.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// frozen = FrozenDict({'name': 'Alice', 'age': 30})
    /// assert frozen['name'] == 'Alice'
    ///
    /// # Raises KeyError if key doesn't exist
    /// try:
    ///     _ = frozen['nonexistent']
    /// except KeyError:
    ///     pass
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyKeyError` if the key is not found.
    fn __getitem__(&self, py: Python<'_>, key: Py<PyAny>) -> PyResult<Py<PyAny>> {
        self.dict.bind(py).get_item(key).and_then(|opt| {
            opt.map(|v| Ok(v.unbind())).unwrap_or_else(|| {
                Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(
                    "Key not found",
                ))
            })
        })
    }

    /// Get the value for `key`, returning `default` if the key is not found.
    ///
    /// # Arguments
    ///
    /// * `key` - The key to look up
    /// * `default` - Value to return if key is not found. If `None`, returns `None`.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// frozen = FrozenDict({'a': 1, 'b': 2})
    /// assert frozen.get('a') == 1
    /// assert frozen.get('c', 'default') == 'default'
    /// assert frozen.get('c') is None
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    fn get(
        &self,
        py: Python<'_>,
        key: Py<PyAny>,
        default: Option<Py<PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        match self.dict.bind(py).get_item(key)? {
            Some(v) => Ok(v.unbind()),
            None => Ok(default.unwrap_or_else(|| py.None())),
        }
    }

    /// Dictionary protocol: `key in frozen` syntax.
    ///
    /// Checks if a key exists in the frozen dictionary.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// frozen = FrozenDict({'a': 1, 'b': 2})
    /// assert 'a' in frozen
    /// assert 'c' not in frozen
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    fn __contains__(&self, py: Python<'_>, key: Py<PyAny>) -> PyResult<bool> {
        Ok(self.dict.bind(py).contains(key)?)
    }

    /// Dictionary protocol: `len(frozen)` syntax.
    ///
    /// Returns the number of key-value pairs in the frozen dictionary.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// frozen = FrozenDict({'a': 1, 'b': 2, 'c': 3})
    /// assert len(frozen) == 3
    /// ```
    fn __len__(&self) -> usize {
        Python::attach(|py| self.dict.bind(py).len())
    }

    /// Return a view of the dictionary keys.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// frozen = FrozenDict({'a': 1, 'b': 2})
    /// keys = list(frozen.keys())
    /// assert 'a' in keys
    /// assert 'b' in keys
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    fn keys(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self.dict.bind(py).keys().unbind().into())
    }

    /// Return a view of the dictionary values.
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// frozen = FrozenDict({'a': 1, 'b': 2})
    /// values = list(frozen.values())
    /// assert 1 in values
    /// assert 2 in values
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    fn values(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self.dict.bind(py).values().unbind().into())
    }

    /// Return a view of the dictionary items (key-value pairs).
    ///
    /// # Examples
    ///
    /// ```python
    /// from _tinydb_core import FrozenDict
    ///
    /// frozen = FrozenDict({'a': 1, 'b': 2})
    /// items = list(frozen.items())
    /// assert ('a', 1) in items
    /// assert ('b', 2) in items
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    fn items(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self.dict.bind(py).items().unbind().into())
    }

    /// Dictionary protocol: `frozen[key] = value` syntax.
    ///
    /// Always raises `TypeError` because `FrozenDict` is immutable.
    ///
    /// # Errors
    ///
    /// Always returns `PyTypeError` with message "object is immutable".
    fn __setitem__(&self, _key: Py<PyAny>, _value: Py<PyAny>) -> PyResult<()> {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "object is immutable",
        ))
    }

    /// Dictionary protocol: `del frozen[key]` syntax.
    ///
    /// Always raises `TypeError` because `FrozenDict` is immutable.
    ///
    /// # Errors
    ///
    /// Always returns `PyTypeError` with message "object is immutable".
    fn __delitem__(&self, _key: Py<PyAny>) -> PyResult<()> {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "object is immutable",
        ))
    }

    /// Remove all items from the dictionary.
    ///
    /// Always raises `TypeError` because `FrozenDict` is immutable.
    ///
    /// # Errors
    ///
    /// Always returns `PyTypeError` with message "object is immutable".
    fn clear(&self) -> PyResult<()> {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "object is immutable",
        ))
    }

    /// Set default value for a key if it doesn't exist.
    ///
    /// Always raises `TypeError` because `FrozenDict` is immutable.
    ///
    /// # Errors
    ///
    /// Always returns `PyTypeError` with message "object is immutable".
    fn setdefault(&self, _key: Py<PyAny>, _default: Option<Py<PyAny>>) -> PyResult<()> {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "object is immutable",
        ))
    }

    /// Remove and return an arbitrary (key, value) pair.
    ///
    /// Always raises `TypeError` because `FrozenDict` is immutable.
    ///
    /// # Errors
    ///
    /// Always returns `PyTypeError` with message "object is immutable".
    fn popitem(&self) -> PyResult<()> {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "object is immutable",
        ))
    }

    /// Update the dictionary with key-value pairs from another dictionary.
    ///
    /// Always raises `TypeError` because `FrozenDict` is immutable.
    ///
    /// # Errors
    ///
    /// Always returns `PyTypeError` with message "object is immutable".
    fn update(&self, _e: Option<Py<PyAny>>, _f: Option<&Bound<'_, PyDict>>) -> PyResult<()> {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "object is immutable",
        ))
    }

    /// Remove and return the value for a key.
    ///
    /// Always raises `TypeError` because `FrozenDict` is immutable.
    ///
    /// # Errors
    ///
    /// Always returns `PyTypeError` with message "object is immutable".
    fn pop(&self, _k: Py<PyAny>, _d: Option<Py<PyAny>>) -> PyResult<()> {
        Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "object is immutable",
        ))
    }
}

/// Recursively convert mutable objects to immutable, hashable equivalents.
///
/// This function is used to prepare objects for use as dictionary keys or in sets
/// by making them immutable. It recursively processes nested structures:
///
/// - `dict` → [`FrozenDict`]
/// - `list` → `tuple`
/// - `set` → `frozenset`
/// - Other objects remain unchanged
///
/// This is essential for caching queries that contain nested dictionaries or lists,
/// as these structures need to be hashable to be used as cache keys.
///
/// # Arguments
///
/// * `obj` - The object to freeze. Can be any Python object, including nested structures.
///
/// # Returns
///
/// A new immutable object with the same structure as `obj`. The original object
/// is not modified.
///
/// # Examples
///
/// ```python
/// from _tinydb_core import freeze
///
/// # Freeze a dictionary
/// d = {'name': 'Alice', 'scores': [85, 90, 88]}
/// frozen = freeze(d)
/// assert isinstance(frozen, FrozenDict)
///
/// # Freeze a list (becomes tuple)
/// lst = [1, 2, 3]
/// frozen_lst = freeze(lst)
/// assert isinstance(frozen_lst, tuple)
///
/// # Freeze nested structures
/// nested = {
///     'users': [
///         {'name': 'Alice', 'age': 30},
///         {'name': 'Bob', 'age': 25}
///     ]
/// }
/// frozen_nested = freeze(nested)
/// # All dicts become FrozenDict, all lists become tuples
/// ```
///
/// # Errors
///
/// Returns `PyErr` if any object in the structure is not hashable (after freezing).
/// This typically occurs if the structure contains unhashable types that cannot
/// be converted (e.g., custom objects without `__hash__` methods).
#[pyfunction]
pub fn freeze(py: Python<'_>, obj: Py<PyAny>) -> PyResult<Py<PyAny>> {
    if let Ok(dict) = obj.bind(py).cast::<PyDict>() {
        // Transform dict into FrozenDict
        // First, recursively freeze all values
        let frozen_dict = PyDict::new(py);
        for (key, value) in dict.iter() {
            let frozen_value = freeze(py, value.into())?;
            frozen_dict.set_item(key, frozen_value)?;
        }
        // Create FrozenDict from the frozen dict
        let frozen = Py::new(py, FrozenDict::new(py, frozen_dict)?)?;
        Ok(frozen.into())
    } else if let Ok(list) = obj.bind(py).cast::<PyList>() {
        // Transform list into tuple
        let mut items = Vec::new();
        for item in list.iter() {
            items.push(freeze(py, item.into())?);
        }
        Ok(PyTuple::new(py, items)?.unbind().into())
    } else if let Ok(set) = obj.bind(py).cast::<PySet>() {
        // Transform set into frozenset
        let mut items = Vec::new();
        for item in set.iter() {
            items.push(freeze(py, item.into())?);
        }
        Ok(PyFrozenSet::new(py, items)?.unbind().into())
    } else {
        // Don't handle other objects
        Ok(obj)
    }
}
