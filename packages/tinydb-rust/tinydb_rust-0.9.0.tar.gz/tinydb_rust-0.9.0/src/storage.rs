//! # Storage Implementations
//!
//! This module provides storage backends for TinyDB that handle reading and writing
//! database state. All storage implementations use Rust's standard library for I/O
//! operations, providing better performance and memory safety compared to Python's
//! file operations.
//!
//! ## Available Storage Backends
//!
//! - [`JSONStorage`]: Persistent storage using JSON files on disk
//! - [`MemoryStorage`]: In-memory storage for testing or temporary databases

use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyFloat, PyInt, PyList, PyString, PyTuple};
use serde_json::Value;
use std::fs::{File, OpenOptions};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::PathBuf;

/// Persistent storage backend that stores database state in a JSON file on disk.
///
/// This is the default storage backend for TinyDB. All file I/O operations are
/// performed using Rust's standard library for optimal performance and reliability.
///
/// The storage supports various file access modes and can handle custom JSON
/// serialization options (indentation, key sorting, etc.) through Python's `json` module.
///
/// # File Access Modes
///
/// - `'r'` or `'rb'`: Read-only mode (file must exist)
/// - `'r+'` or `'rb+'`: Read-write mode (file is created if it doesn't exist)
///
/// **Warning**: Using other access modes (like `'w'` or `'a'`) may cause data loss
/// or corruption and will trigger a warning.
///
/// # Examples
///
/// ```python
/// from tinydb_rust.storages import JSONStorage
///
/// # Create storage with default settings
/// storage = JSONStorage('db.json')
///
/// # Create storage with custom options
/// storage = JSONStorage(
///     'db.json',
///     create_dirs=True,  # Create parent directories if needed
///     indent=2,  # Pretty-print JSON with 2-space indentation
///     sort_keys=True  # Sort dictionary keys
/// )
///
/// # Read database state
/// data = storage.read()  # Returns dict or None if file is empty
///
/// # Write database state
/// storage.write({'table1': {'1': {'name': 'Alice'}}})
///
/// # Close the storage
/// storage.close()
/// ```
#[pyclass(module = "tinydb_rust.storages")]
pub struct JSONStorage {
    /// Path to the JSON file
    #[allow(dead_code)]
    path: PathBuf,
    /// File handle for reading/writing
    handle: Option<File>,
    /// Access mode (r, r+, etc.)
    access_mode: String,
    /// Whether to create parent directories
    #[allow(dead_code)]
    create_dirs: bool,
    /// Encoding for file I/O
    encoding: Option<String>,
    /// JSON serialization options (sort_keys, indent, separators, etc.)
    json_kwargs: Py<PyDict>,
}

#[pymethods]
impl JSONStorage {
    /// Create a new `JSONStorage` instance.
    ///
    /// # Arguments
    ///
    /// * `path` - Path to the JSON file. Can be a string, bytes, or any `PathLike` object.
    /// * `create_dirs` - If `True`, create parent directories if they don't exist.
    /// * `encoding` - File encoding (kept for compatibility, but UTF-8 is always used internally).
    /// * `access_mode` - File access mode. Valid values: `'r'`, `'rb'`, `'r+'`, `'rb+'`.
    ///   Default is `'r+'` (read-write, create if missing).
    /// * `**kwargs` - Additional JSON serialization options passed to `json.dumps`:
    ///   - `indent`: Number of spaces for indentation (for pretty-printing)
    ///   - `sort_keys`: If `True`, sort dictionary keys in output
    ///   - `separators`: Tuple of (item_separator, key_separator)
    ///   - `ensure_ascii`: If `True`, escape non-ASCII characters
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import JSONStorage
    ///
    /// # Basic usage
    /// storage = JSONStorage('data.json')
    ///
    /// # With pretty-printing
    /// storage = JSONStorage('data.json', indent=2, sort_keys=True)
    ///
    /// # Create parent directories
    /// storage = JSONStorage('/path/to/db.json', create_dirs=True)
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyIOError` if:
    /// - The file cannot be opened (e.g., permission denied)
    /// - Parent directories cannot be created (when `create_dirs=True`)
    ///
    /// Returns `PyFileNotFoundError` if:
    /// - The file doesn't exist and `access_mode` is read-only (`'r'` or `'rb'`)
    ///
    /// # Panics
    ///
    /// This function does not panic.
    #[new]
    #[pyo3(signature = (path, *, create_dirs=false, encoding=None, access_mode="r+", **kwargs))]
    fn new(
        py: Python<'_>,
        path: &Bound<'_, PyAny>,
        create_dirs: bool,
        encoding: Option<String>,
        access_mode: &str,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Self> {
        // Convert path to string - supports str, bytes, and PathLike objects
        let path: String = if let Ok(s) = path.extract::<String>() {
            s
        } else {
            // Try to use os.fspath() to convert PathLike objects
            let os = py.import("os")?;
            let fspath = os.getattr("fspath")?;
            fspath.call1((path,))?.extract()?
        };
        let encoding_clone = encoding.clone(); // Store encoding for later use
        let path_buf = PathBuf::from(&path);

        // Validate access mode
        let valid_modes = ["r", "rb", "r+", "rb+"];
        if !valid_modes.contains(&access_mode) {
            Python::attach(|py| {
                let warnings = py.import("warnings")?;
                warnings.call_method1(
                    "warn",
                    ("Using an `access_mode` other than 'r', 'rb', 'r+' or 'rb+' can cause data loss or corruption",),
                )?;
                Ok::<(), PyErr>(())
            })
            .ok(); // Ignore warning errors
        }

        // Parse kwargs for JSON serialization options
        // Store JSON serialization options (sort_keys, indent, separators, etc.)
        let json_kwargs = if let Some(kwargs_dict) = kwargs {
            // Filter out non-JSON options
            let json_opts = PyDict::new(py);
            let json_option_keys = ["sort_keys", "indent", "separators", "ensure_ascii"];
            for key in json_option_keys {
                if let Some(value) = kwargs_dict.get_item(key)? {
                    json_opts.set_item(key, value)?;
                }
            }
            json_opts.unbind()
        } else {
            PyDict::new(py).unbind()
        };

        // Create parent directories if needed
        if create_dirs {
            if let Some(parent) = path_buf.parent() {
                std::fs::create_dir_all(parent).map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                        "Failed to create directories: {}",
                        e
                    ))
                })?;
            }
        }

        // Open the file
        let handle = if access_mode.contains('+') || access_mode.contains('w') || access_mode.contains('a') {
            // Writing mode: create file if it doesn't exist
            OpenOptions::new()
                .read(true)
                .write(true)
                .create(true)
                .open(&path_buf)
                .map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                        "Failed to open file '{}': {}",
                        path, e
                    ))
                })?
        } else {
            // Read-only mode - don't create file if it doesn't exist
            OpenOptions::new()
                .read(true)
                .open(&path_buf)
                .map_err(|e| {
                    // Check if it's a "file not found" error
                    if e.kind() == std::io::ErrorKind::NotFound {
                        // Convert to Python's FileNotFoundError
                        Python::attach(|py| -> PyResult<PyErr> {
                            let file_not_found_error = py.get_type::<pyo3::exceptions::PyFileNotFoundError>();
                            Err(PyErr::from_value(file_not_found_error.call1((
                                format!("Failed to open file '{}': {}", path, e),
                            ))?))
                        })
                        .unwrap_or_else(|_| {
                            PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(format!(
                                "Failed to open file '{}': {}",
                                path, e
                            ))
                        })
                    } else {
                        PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                            "Failed to open file '{}': {}",
                            path, e
                        ))
                    }
                })?
        };

        Ok(JSONStorage {
            path: path_buf,
            handle: Some(handle),
            access_mode: access_mode.to_string(),
            create_dirs,
            encoding: encoding_clone,
            json_kwargs,
        })
    }

    /// Read the current database state from the JSON file.
    ///
    /// If the file is empty or doesn't exist, returns `None`. Otherwise, parses
    /// the JSON content and returns it as a Python dictionary.
    ///
    /// # Returns
    ///
    /// - `None` if the file is empty or doesn't exist
    /// - A Python dictionary containing the database state otherwise
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import JSONStorage
    ///
    /// storage = JSONStorage('db.json')
    ///
    /// # Read database state
    /// data = storage.read()
    /// if data is None:
    ///     print("Database is empty")
    /// else:
    ///     print(f"Database has {len(data)} tables")
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyRuntimeError` if the file handle is closed.
    ///
    /// Returns `PyIOError` if:
    /// - The file cannot be read
    /// - The file cannot be seeked
    ///
    /// Returns `PyValueError` or `JSONDecodeError` if:
    /// - The file contains invalid JSON
    /// - The JSON root is not an object (must be a dictionary)
    ///
    /// # Panics
    ///
    /// This function does not panic.
    fn read(&mut self) -> PyResult<Option<Py<PyAny>>> {
        let handle = self.handle.as_mut().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("File handle is closed")
        })?;

        // Get file size
        let size = handle.seek(SeekFrom::End(0)).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to seek file: {}", e))
        })?;

        if size == 0 {
            // File is empty, return None
            return Ok(None);
        }

        // Return to beginning of file
        handle.seek(SeekFrom::Start(0)).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to seek file: {}", e))
        })?;

        // Read file contents
        // If encoding is specified and not UTF-8, we need to use Python's encoding conversion
        let contents = match &self.encoding {
            Some(enc) if enc.to_lowercase() != "utf-8" && enc.to_lowercase() != "utf8" => {
                // Use Python's codecs to read with specified encoding
                Python::attach(|py| -> PyResult<String> {
                    let codecs = py.import("codecs")?;
                    let open_fn = codecs.getattr("open")?;
                    let file_obj = open_fn.call1((&self.path.to_string_lossy(), "r", enc))?;
                    let read_method = file_obj.getattr("read")?;
                    let content = read_method.call0()?;
                    let close_method = file_obj.getattr("close")?;
                    close_method.call0()?;
                    content.extract()
                })?
            }
            _ => {
                // UTF-8 encoding, use standard Rust read
                let mut contents = String::new();
                handle.read_to_string(&mut contents).map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to read file: {}", e))
                })?;
                contents
            }
        };

        // Parse JSON
        // If parsing fails and encoding was specified, it might be an encoding mismatch
        let json_value: Value = serde_json::from_str(&contents).map_err(|e| {
            // Try to raise JSONDecodeError if available, otherwise ValueError
            Python::attach(|py| -> PyResult<PyErr> {
                let json_module = py.import("json")?;
                // Try to get JSONDecodeError from json.decoder
                let json_decoder = py.import("json.decoder")?;
                if let Ok(json_decode_error) = json_decoder.getattr("JSONDecodeError") {
                    // Raise JSONDecodeError with proper signature: (msg, doc, pos)
                    // Extract error message from serde_json error
                    let msg = format!("{}", e);
                    Ok(PyErr::from_value(json_decode_error.call1((
                        msg,
                        contents.clone(),
                        0,
                    ))?))
                } else if let Ok(json_decode_error) = json_module.getattr("JSONDecodeError") {
                    // Fallback to json.JSONDecodeError
                    Ok(PyErr::from_value(json_decode_error.call1((
                        format!("Failed to parse JSON: {}", e),
                        py.None(),
                        0,
                    ))?))
                } else {
                    // Fallback to ValueError
                    Ok(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to parse JSON: {}", e)))
                }
            })
            .unwrap_or_else(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to parse JSON: {}", e)))
        })?;

        // Convert to Python dict
        Python::attach(|py| {
            let dict = PyDict::new(py);
            convert_json_to_pydict(py, &json_value, &dict)?;
            Ok(Some(dict.into()))
        })
    }

    /// Write the database state to the JSON file.
    ///
    /// Serializes the database state to JSON and writes it to the file. The file
    /// is truncated to the new content size, ensuring no old data remains.
    ///
    /// # Arguments
    ///
    /// * `data` - The database state as a Python dictionary. The dictionary structure
    ///   should match TinyDB's internal format: `{table_name: {doc_id: document, ...}, ...}`
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import JSONStorage
    ///
    /// storage = JSONStorage('db.json')
    ///
    /// # Write database state
    /// data = {
    ///     'users': {
    ///         '1': {'name': 'Alice', 'age': 30},
    ///         '2': {'name': 'Bob', 'age': 25}
    ///     }
    /// }
    /// storage.write(data)
    /// ```
    ///
    /// # Errors
    ///
    /// Returns `PyRuntimeError` if the file handle is closed.
    ///
    /// Returns `PyIOError` if:
    /// - The file is opened in read-only mode (`'r'` or `'rb'`)
    /// - The file cannot be written to
    /// - The file cannot be flushed or synced to disk
    ///
    /// # Panics
    ///
    /// This function does not panic.
    fn write(&mut self, data: &Bound<'_, PyDict>) -> PyResult<()> {
        let handle = self.handle.as_mut().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("File handle is closed")
        })?;

        // Check if file is writable
        if !self.access_mode.contains('+') && !self.access_mode.contains('w') && !self.access_mode.contains('a') {
            return Err(PyErr::new::<pyo3::exceptions::PyIOError, _>(format!(
                "Cannot write to the database. Access mode is \"{}\"",
                self.access_mode
            )));
        }

        // Serialize to JSON string using Python's json module to support custom options
        let serialized = Python::attach(|py| -> PyResult<String> {
            let json_module = py.import("json")?;
            let dumps_fn = json_module.getattr("dumps")?;
            
            // Call json.dumps with data and kwargs
            let json_kwargs_bound = self.json_kwargs.bind(py);
            let result = if json_kwargs_bound.len() > 0 {
                dumps_fn.call((data,), Some(&json_kwargs_bound))?
            } else {
                dumps_fn.call1((data,))?
            };
            result.extract()
        })?;

        // Seek to beginning
        handle.seek(SeekFrom::Start(0)).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to seek file: {}", e))
        })?;

        // Write data with encoding if specified
        let bytes_to_write = match &self.encoding {
            Some(enc) if enc.to_lowercase() != "utf-8" && enc.to_lowercase() != "utf8" => {
                // Use Python's codecs to encode with specified encoding
                Python::attach(|py| -> PyResult<Vec<u8>> {
                    let codecs = py.import("codecs")?;
                    let encode_fn = codecs.getattr("encode")?;
                    let result = encode_fn.call1((serialized, enc))?;
                    // codecs.encode returns (bytes, int) tuple
                    if let Ok(tuple) = result.cast::<pyo3::types::PyTuple>() {
                        // It's a tuple, get the first element (bytes)
                        tuple.get_item(0)?.extract::<Vec<u8>>()
                    } else {
                        // It's directly bytes
                        result.extract::<Vec<u8>>()
                    }
                })?
            }
            _ => {
                // UTF-8 encoding, use standard Rust bytes
                serialized.into_bytes()
            }
        };

        // Write data
        handle.write_all(&bytes_to_write).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to write file: {}", e))
        })?;

        // Flush to ensure data is written
        handle.flush().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to flush file: {}", e))
        })?;

        // Sync to disk
        handle.sync_all().map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to sync file: {}", e))
        })?;

        // Truncate file to remove any data beyond current position
        let pos = handle.seek(SeekFrom::Current(0)).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to seek file: {}", e))
        })?;
        handle.set_len(pos).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyIOError, _>(format!("Failed to truncate file: {}", e))
        })?;

        Ok(())
    }

    /// Close the file handle and release resources.
    ///
    /// After calling this method, the storage cannot be used for reading or writing.
    /// This method is idempotent - calling it multiple times is safe.
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import JSONStorage
    ///
    /// storage = JSONStorage('db.json')
    /// # ... use storage ...
    /// storage.close()  # Release file handle
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    ///
    /// # Panics
    ///
    /// This function does not panic.
    fn close(&mut self) -> PyResult<()> {
        if let Some(handle) = self.handle.take() {
            drop(handle);
        }
        Ok(())
    }

    /// Get the file handle status (for testing and compatibility).
    ///
    /// Returns a mock object with a `closed` attribute indicating whether the
    /// file handle is closed. This is primarily used for testing compatibility
    /// with the original TinyDB implementation.
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import JSONStorage
    ///
    /// storage = JSONStorage('db.json')
    /// handle = storage._handle
    /// assert not handle.closed
    ///
    /// storage.close()
    /// assert storage._handle.closed
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    #[getter]
    fn _handle(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        // Return a mock object that has a 'closed' attribute
        // Create a simple object with closed attribute
        let types_module = py.import("types")?;
        let simple_namespace = types_module.getattr("SimpleNamespace")?;
        let closed = self.handle.is_none();
        // SimpleNamespace(**kwargs) - need to pass as keyword arguments
        let kwargs = PyDict::new(py);
        kwargs.set_item("closed", closed)?;
        let empty_tuple = PyTuple::empty(py);
        let handle_instance = simple_namespace.call(&empty_tuple, Some(&kwargs))?;
        Ok(handle_instance.unbind())
    }
}

/// In-memory storage backend that stores database state in RAM.
///
/// This storage backend is useful for testing, temporary databases, or when
/// persistence is not required. Data is lost when the `MemoryStorage` instance
/// is destroyed or the process exits.
///
/// Unlike [`JSONStorage`], `MemoryStorage` does not perform any file I/O operations,
/// making it faster for temporary use cases.
///
/// # Examples
///
/// ```python
/// from tinydb_rust.storages import MemoryStorage
/// from tinydb_rust import TinyDB
///
/// # Create a database with in-memory storage
/// storage = MemoryStorage()
/// db = TinyDB(storage=storage)
///
/// # Use the database normally
/// db.insert({'name': 'Alice'})
/// results = db.search(Query().name == 'Alice')
///
/// # Data is lost when storage is destroyed
/// ```
#[pyclass(module = "tinydb_rust.storages")]
pub struct MemoryStorage {
    /// In-memory storage as JSON value
    memory: Option<Value>,
}

#[pymethods]
impl MemoryStorage {
    /// Create a new `MemoryStorage` instance.
    ///
    /// The storage starts empty. Use [`read`](Self::read) and [`write`](Self::write)
    /// to interact with the stored data.
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import MemoryStorage
    ///
    /// storage = MemoryStorage()
    /// assert storage.read() is None  # Initially empty
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    ///
    /// # Panics
    ///
    /// This function does not panic.
    #[new]
    fn new() -> Self {
        MemoryStorage { memory: None }
    }

    /// Read the current database state from memory.
    ///
    /// Returns `None` if no data has been written yet, otherwise returns the
    /// stored data as a Python dictionary.
    ///
    /// # Returns
    ///
    /// - `None` if no data has been written
    /// - A Python dictionary containing the database state otherwise
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import MemoryStorage
    ///
    /// storage = MemoryStorage()
    /// assert storage.read() is None  # Empty initially
    ///
    /// storage.write({'table1': {'1': {'name': 'Alice'}}})
    /// data = storage.read()
    /// assert data is not None
    /// assert 'table1' in data
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    ///
    /// # Panics
    ///
    /// This function does not panic.
    fn read(&self) -> PyResult<Option<Py<PyAny>>> {
        match &self.memory {
            None => Ok(None),
            Some(json_value) => {
                Python::attach(|py| {
                    let dict = PyDict::new(py);
                    convert_json_to_pydict(py, json_value, &dict)?;
                    Ok(Some(dict.into()))
                })
            }
        }
    }

    /// Write the database state to memory.
    ///
    /// Stores the database state in memory. Any previously stored data is replaced.
    ///
    /// # Arguments
    ///
    /// * `data` - The database state as a Python dictionary. The dictionary structure
    ///   should match TinyDB's internal format: `{table_name: {doc_id: document, ...}, ...}`
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import MemoryStorage
    ///
    /// storage = MemoryStorage()
    ///
    /// data = {
    ///     'users': {
    ///         '1': {'name': 'Alice', 'age': 30}
    ///     }
    /// }
    /// storage.write(data)
    ///
    /// # Read it back
    /// retrieved = storage.read()
    /// assert retrieved == data
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    ///
    /// # Panics
    ///
    /// This function does not panic.
    fn write(&mut self, data: &Bound<'_, PyDict>) -> PyResult<()> {
        // Convert Python dict to JSON Value
        let json_value = convert_pydict_to_json(data)?;
        self.memory = Some(json_value);
        Ok(())
    }

    /// Close the storage (no-op for memory storage).
    ///
    /// This method exists for API compatibility with other storage backends.
    /// For `MemoryStorage`, it does nothing since no resources need to be released.
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import MemoryStorage
    ///
    /// storage = MemoryStorage()
    /// storage.close()  # Safe to call, does nothing
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    ///
    /// # Panics
    ///
    /// This function does not panic.
    fn close(&self) -> PyResult<()> {
        // Memory storage doesn't need cleanup
        Ok(())
    }

    /// Get the stored data as a Python dictionary (for compatibility with tests).
    ///
    /// Returns the same data as [`read`](Self::read), but as a property for
    /// compatibility with the original TinyDB implementation's test suite.
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust.storages import MemoryStorage
    ///
    /// storage = MemoryStorage()
    /// storage.write({'table1': {'1': {'name': 'Alice'}}})
    ///
    /// # Access stored data
    /// data = storage.memory
    /// assert 'table1' in data
    /// ```
    ///
    /// # Errors
    ///
    /// This function does not return errors.
    ///
    /// # Panics
    ///
    /// This function does not panic.
    #[getter]
    fn memory(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        match &self.memory {
            None => Ok(py.None()),
            Some(json_value) => {
                let dict = PyDict::new(py);
                convert_json_to_pydict(py, json_value, &dict)?;
                Ok(dict.into())
            }
        }
    }
}

/// Convert a Python dict to serde_json::Value recursively.
///
/// This helper function recursively converts Python objects to JSON values,
/// handling dictionaries, lists, and primitive types.
fn convert_pydict_to_json(dict: &Bound<'_, PyDict>) -> PyResult<Value> {
    let mut map = serde_json::Map::new();
    
    for (key, value) in dict.iter() {
        let key_str = key.extract::<String>()?;
        let json_value = convert_pyobject_to_json(&value)?;
        map.insert(key_str, json_value);
    }
    
    Ok(Value::Object(map))
}

/// Convert a Python object to serde_json::Value.
///
/// Recursively converts Python objects to their JSON equivalents.
fn convert_pyobject_to_json(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    // Try to extract as different types
    if obj.is_none() {
        return Ok(Value::Null);
    }
    
    // Try bool
    if let Ok(b) = obj.extract::<bool>() {
        return Ok(Value::Bool(b));
    }
    
    // Try integer
    if let Ok(i) = obj.extract::<i64>() {
        return Ok(Value::Number(i.into()));
    }
    
    // Try float
    if let Ok(f) = obj.extract::<f64>() {
        return Ok(Value::Number(
            serde_json::Number::from_f64(f)
                .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid number"))?,
        ));
    }
    
    // Try string
    if let Ok(s) = obj.extract::<String>() {
        return Ok(Value::String(s));
    }
    
    // Try dict
    if let Ok(dict) = obj.cast::<PyDict>() {
        let mut map = serde_json::Map::new();
        for (key, value) in dict.iter() {
            let key_str: String = key.extract()?;
            let json_value = convert_pyobject_to_json(&value)?;
            map.insert(key_str, json_value);
        }
        return Ok(Value::Object(map));
    }
    
    // Try list
    if let Ok(list) = obj.cast::<PyList>() {
        let mut arr = Vec::new();
        for item in list.iter() {
            let json_value = convert_pyobject_to_json(&item)?;
            arr.push(json_value);
        }
        return Ok(Value::Array(arr));
    }
    
    // Fallback: try to convert to string representation
    let repr = obj.repr()?.to_string();
    Ok(Value::String(repr))
}

/// Convert a serde_json::Value to a Python dict recursively.
///
/// This helper function recursively converts JSON values to Python objects,
/// handling dictionaries, lists, and primitive types.
fn convert_json_to_pydict(
    py: Python<'_>,
    value: &Value,
    dict: &Bound<'_, PyDict>,
) -> PyResult<()> {
    match value {
        Value::Object(map) => {
            for (key, val) in map {
                let py_key: Py<PyAny> = PyString::new(py, key).into();
                let py_val = convert_json_value_to_pyobject(py, val)?;
                dict.set_item(py_key, py_val)?;
            }
        }
        _ => {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Expected JSON object at root level",
            ));
        }
    }
    Ok(())
}

/// Convert a serde_json::Value to a Python object.
///
/// Recursively converts JSON values to their Python equivalents.
fn convert_json_value_to_pyobject(py: Python<'_>, value: &Value) -> PyResult<Py<PyAny>> {
    match value {
        Value::Null => Ok(py.None().into()),
        Value::Bool(b) => {
            let py_bool = Py::from(PyBool::new(py, *b));
            Ok(<Py<PyBool> as Into<Py<PyAny>>>::into(py_bool))
        }
        Value::Number(n) => {
            if n.is_i64() {
                let py_int = Py::from(PyInt::new(py, n.as_i64().unwrap()));
                Ok(<Py<PyInt> as Into<Py<PyAny>>>::into(py_int))
            } else if n.is_u64() {
                let u = n.as_u64().unwrap();
                // u64 might be too large for i64, try to convert
                if u <= i64::MAX as u64 {
                    let py_int = Py::from(PyInt::new(py, u as i64));
                    Ok(<Py<PyInt> as Into<Py<PyAny>>>::into(py_int))
                } else {
                    // For very large u64, use string representation
                    let py_str = Py::from(PyString::new(py, &u.to_string()));
                    Ok(<Py<PyString> as Into<Py<PyAny>>>::into(py_str))
                }
            } else if n.is_f64() {
                let py_float = Py::from(PyFloat::new(py, n.as_f64().unwrap()));
                Ok(<Py<PyFloat> as Into<Py<PyAny>>>::into(py_float))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Invalid number",
                ))
            }
        }
        Value::String(s) => {
            let py_str = Py::from(PyString::new(py, s));
            Ok(<Py<PyString> as Into<Py<PyAny>>>::into(py_str))
        }
        Value::Array(arr) => {
            let list = PyList::empty(py);
            for item in arr {
                let py_item = convert_json_value_to_pyobject(py, item)?;
                list.append(py_item)?;
            }
            Ok(list.into())
        }
        Value::Object(map) => {
            let dict = PyDict::new(py);
            for (key, val) in map {
                let py_key: Py<PyAny> = PyString::new(py, key).into();
                let py_val = convert_json_value_to_pyobject(py, val)?;
                dict.set_item(py_key, py_val)?;
            }
            Ok(dict.into())
        }
    }
}

