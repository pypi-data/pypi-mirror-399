// Database entry point implementation for TinyDB.
//
// This module contains the TinyDB class that serves as the main entry point
// for the database. It manages Table and Storage instances and provides
// a high-level API for database operations.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString, PyTuple};
use pyo3::PyRefMut;
use crate::table::Table;
use crate::storage::JSONStorage;

/// TinyDB is the main entry point for the database.
///
/// It manages tables and storage instances, providing a high-level API
/// for database operations. All core logic is implemented in Rust.
#[pyclass(module = "_tinydb_core")]
pub struct TinyDB {
    /// Storage instance (Python object that implements read/write methods)
    storage: Py<PyAny>,
    /// Whether the database has been opened
    _opened: bool,
    /// Cache of created Table instances
    _tables: Py<PyDict>,
    /// Default table name
    _default_table_name: String,
    /// Whether the database has been closed (for idempotent close())
    _closed: bool,
}

// Helper function to instantiate storage class
fn instantiate_storage_class(
    py: Python<'_>,
    storage_type: &Bound<'_, PyAny>,
    args: &Bound<'_, PyTuple>,
    storage_kwargs: &Bound<'_, PyDict>,
) -> PyResult<Py<PyAny>> {
    let empty_tuple = PyTuple::empty(py);
    let call_args = if args.len() > 0 { args } else { &empty_tuple };
    
    let instance = if storage_kwargs.len() > 0 {
        storage_type.call(call_args, Some(storage_kwargs))?
    } else {
        storage_type.call1(call_args)?
    };
    Ok(instance.unbind())
}

#[pymethods]
impl TinyDB {
    /// Create a new TinyDB instance.
    ///
    /// :param *args: Positional arguments (first arg is treated as path if storage is None)
    /// :param storage: Storage instance or class (default: JSONStorage)
    /// :param default_table: Name of the default table (default: "default")
    /// :param **kwargs: Additional arguments passed to storage constructor
    #[new]
    #[pyo3(signature = (*args, **kwargs))]
    fn new(
        py: Python<'_>,
        args: &Bound<'_, PyTuple>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Self> {
        // Parse kwargs to extract parameters
        let mut storage = None;
        let mut default_table = "_default".to_string();
        let storage_kwargs = PyDict::new(py);

        if let Some(kwargs_dict) = kwargs {
            // Extract 'storage' parameter
            if let Some(storage_val) = kwargs_dict.get_item("storage")? {
                storage = Some(storage_val.clone().unbind());
            }

            // Extract 'default_table' parameter
            if let Some(default_table_val) = kwargs_dict.get_item("default_table")? {
                default_table = default_table_val.extract()?;
            }

            // Collect remaining kwargs for storage constructor
            for (key, value) in kwargs_dict.iter() {
                let key_str: String = key.extract()?;
                if key_str != "storage" && key_str != "default_table" {
                    storage_kwargs.set_item(key, value)?;
                }
            }
        }

        // Determine storage instance
        let storage_instance = if let Some(storage_val) = storage {
            // Storage is provided (could be instance or class)
            let storage_bound = storage_val.bind(py);

            // Check if it's a type/class by checking if it's callable and has __mro__
            // (classes have __mro__, instances typically don't)
            let is_type = storage_bound.hasattr("__mro__")?;

            if is_type {
                // It's a class, instantiate it
                instantiate_storage_class(py, &storage_bound, args, &storage_kwargs)?
            } else if storage_bound.hasattr("__call__")? {
                // It's a callable instance (like CachingMiddleware), call it
                instantiate_storage_class(py, &storage_bound, args, &storage_kwargs)?
            } else {
                // It's already a fully initialized instance, use it directly
                storage_val
            }
        } else {
            // No storage provided, use JSONStorage as default
            let json_storage_type = py.get_type::<JSONStorage>();
            let empty_tuple = PyTuple::empty(py);
            let storage_args = if args.len() > 0 { args } else { &empty_tuple };
            instantiate_storage_class(py, &json_storage_type, storage_args, &storage_kwargs)?
        };

        // Create tables cache
        let tables_dict = PyDict::new(py);

        Ok(TinyDB {
            storage: storage_instance,
            _opened: true,
            _tables: tables_dict.unbind(),
            _default_table_name: default_table,
            _closed: false,
        })
    }

    /// Get or create a table with the given name.
    ///
    /// :param name: The table name (default: uses default_table)
    /// :param **kwargs: Additional arguments passed to Table constructor
    /// :returns: The Table instance
    #[pyo3(signature = (name = None, **kwargs))]
    fn table(
        &self,
        py: Python<'_>,
        name: Option<String>,
        kwargs: Option<&Bound<'_, PyDict>>,
    ) -> PyResult<Py<Table>> {
        // Use provided name or default table name
        let table_name = name.unwrap_or_else(|| self._default_table_name.clone());

        // Check if table already exists in cache
        let tables = self._tables.bind(py);
        let table_name_py: Py<PyAny> = PyString::new(py, &table_name).into();
        
        if let Some(cached_table) = tables.get_item(&table_name_py)? {
            // Return cached table
            let table: Py<Table> = cached_table.cast()?.clone().unbind();
            return Ok(table);
        }

        // Create new table instance
        let table_type = py.get_type::<Table>();
        
        // Prepare Table constructor arguments
        // Table.__new__(storage, name, cache_size=10, persist_empty=False)
        let cache_size = if let Some(kwargs_dict) = kwargs {
            kwargs_dict
                .get_item("cache_size")?
                .map(|v| v.extract::<usize>())
                .transpose()?
                .unwrap_or(10)
        } else {
            10
        };

        let persist_empty = if let Some(kwargs_dict) = kwargs {
            kwargs_dict
                .get_item("persist_empty")?
                .map(|v| v.extract::<bool>())
                .transpose()?
                .unwrap_or(false)
        } else {
            false
        };

        let table_instance = table_type.call1((
            self.storage.clone_ref(py),
            table_name.clone(),
            cache_size,
            persist_empty,
        ))?;
        let table: Py<Table> = table_instance.cast()?.clone().unbind();

        // Cache the table
        tables.set_item(table_name_py, &table_instance)?;

        Ok(table)
    }

    /// Get all table names from storage.
    ///
    /// :returns: A set of table names
    fn tables(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        // Read from storage to get all tables
        let storage_obj = self.storage.bind(py);
        let result = storage_obj.call_method0("read")?;

        let builtins = py.import("builtins")?;
        let set_class = builtins.getattr("set")?;

        if result.is_none() {
            return Ok(set_class.call0()?.unbind());
        }

        let db_dict = result.cast::<PyDict>()?;
        let keys = db_dict.call_method0("keys")?;
        Ok(set_class.call1((keys,))?.unbind())
    }

    /// Drop a specific table.
    ///
    /// :param name: The table name to drop
    fn drop_table(&mut self, py: Python<'_>, name: String) -> PyResult<()> {
        // Remove from cache (ignore if not exists)
        let tables = self._tables.bind(py);
        let table_name_py: Py<PyAny> = PyString::new(py, &name).into();
        let _ = tables.del_item(&table_name_py); // Ignore KeyError

        // Read current database state
        let storage_obj = self.storage.bind(py);
        let result = storage_obj.call_method0("read")?;

        if result.is_none() {
            // Database is empty, nothing to drop
            return Ok(());
        }

        let db_dict = result.cast::<PyDict>()?;
        
        // Check if table exists before trying to delete
        if db_dict.get_item(&name)?.is_some() {
            let db_dict_mut = db_dict.clone().unbind();
            db_dict_mut.bind(py).del_item(&name)?;
            // Write back to storage
            storage_obj.call_method1("write", (db_dict_mut,))?;
        }

        Ok(())
    }

    /// Drop all tables.
    fn drop_tables(&mut self, py: Python<'_>) -> PyResult<()> {
        // Clear table caches before clearing table references
        let tables = self._tables.bind(py);
        for (_, table_obj) in tables.iter() {
            if let Ok(mut table) = table_obj.extract::<pyo3::PyRefMut<'_, crate::table::Table>>() {
                table.clear_cache(py)?;
            }
        }
        
        // Clear table references
        tables.clear();

        // Write empty database to storage
        let storage_obj = self.storage.bind(py);
        let empty_dict = PyDict::new(py);
        storage_obj.call_method1("write", (empty_dict,))?;

        Ok(())
    }

    /// Close the database and storage.
    fn close(&mut self, py: Python<'_>) -> PyResult<()> {
        // Make close() idempotent - only close once
        if self._closed {
            return Ok(());
        }
        
        // Call storage.close() if it exists
        let storage_obj = self.storage.bind(py);
        if storage_obj.hasattr("close")? {
            storage_obj.call_method0("close")?;
        }
        
        self._closed = true;
        Ok(())
    }

    // Delegation methods - forward to default table

    /// Insert a document into the default table.
    ///
    /// :param document: The document to insert (dict or Document)
    /// :returns: The inserted document's ID
    fn insert(&mut self, py: Python<'_>, document: &Bound<'_, PyAny>) -> PyResult<i32> {
        // Get the table first
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        
        // Try to insert - this will handle validation and conversion
        // If document contains self-reference, it will fail during conversion
        // with appropriate error
        let result = table_bound.call_method1("insert", (document,));
        
        match result {
            Ok(r) => r.extract(),
            Err(e) => {
                // Check if it's a borrow checker error (self-reference)
                // Convert to TypeError if it's a RuntimeError about borrowing
                let err_msg = e.to_string();
                if err_msg.contains("Already mutably borrowed") || err_msg.contains("borrow") {
                    Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                        "Object is not JSON serializable"
                    ))
                } else {
                    Err(e)
                }
            }
        }
    }

    /// Insert multiple documents into the default table.
    ///
    /// :param documents: An iterable of documents to insert
    /// :returns: A list containing the inserted documents' IDs
    fn insert_multiple(
        &mut self,
        py: Python<'_>,
        documents: &Bound<'_, PyAny>,
    ) -> PyResult<Vec<i32>> {
        // First convert generator/iterable to list to avoid consumption issues
        let builtins = py.import("builtins")?;
        let list_fn = builtins.getattr("list")?;
        let documents_list = list_fn.call1((documents,))?;
        
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound
            .call_method1("insert_multiple", (documents_list,))?
            .extract()
    }

    /// Get all documents from the default table.
    ///
    /// :returns: A list of all documents
    fn all(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        Ok(table_bound.call_method0("all")?.unbind())
    }

    /// Search for documents in the default table matching the query.
    ///
    /// :param query: The query to match against
    /// :returns: A list of matching documents
    fn search(&self, py: Python<'_>, query: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        Ok(table_bound.call_method1("search", (query,))?.unbind())
    }

    /// Get a single document from the default table.
    ///
    /// :param cond: Query condition (optional)
    /// :param doc_id: Document ID (optional)
    /// :param doc_ids: List of document IDs (optional)
    /// :returns: The matching document or None
    #[pyo3(signature = (cond = None, doc_id = None, doc_ids = None))]
    fn get(
        &self,
        py: Python<'_>,
        cond: Option<&Bound<'_, PyAny>>,
        doc_id: Option<&Bound<'_, PyAny>>,
        doc_ids: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        
        let kwargs = PyDict::new(py);
        if let Some(c) = cond {
            kwargs.set_item("cond", c)?;
        }
        if let Some(d) = doc_id {
            kwargs.set_item("doc_id", d)?;
        }
        if let Some(ds) = doc_ids {
            kwargs.set_item("doc_ids", ds)?;
        }
        
        Ok(table_bound.call_method("get", (), Some(&kwargs))?.unbind())
    }

    /// Check if a document exists in the default table.
    ///
    /// :param cond: Query condition (optional)
    /// :param doc_id: Document ID (optional)
    /// :returns: True if document exists, False otherwise
    #[pyo3(signature = (cond = None, doc_id = None))]
    fn contains(
        &self,
        py: Python<'_>,
        cond: Option<&Bound<'_, PyAny>>,
        doc_id: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<bool> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        
        let kwargs = PyDict::new(py);
        if let Some(c) = cond {
            kwargs.set_item("cond", c)?;
        }
        if let Some(d) = doc_id {
            kwargs.set_item("doc_id", d)?;
        }
        
        table_bound.call_method("contains", (), Some(&kwargs))?.extract()
    }

    /// Update documents in the default table.
    ///
    /// :param fields: Fields to update (dict or callable)
    /// :param cond: Query condition (optional)
    /// :param doc_ids: List of document IDs (optional)
    /// :returns: A list of updated document IDs
    #[pyo3(signature = (fields, cond = None, doc_ids = None))]
    fn update(
        &mut self,
        py: Python<'_>,
        fields: &Bound<'_, PyAny>,
        cond: Option<&Bound<'_, PyAny>>,
        doc_ids: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Vec<i32>> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound.call_method1("update", (fields, cond, doc_ids))?.extract()
    }

    /// Update multiple documents with different values in the default table.
    ///
    /// :param updates: Sequence of (fields, condition) pairs
    /// :returns: A list of updated document IDs
    fn update_multiple(
        &mut self,
        py: Python<'_>,
        updates: &Bound<'_, PyAny>,
    ) -> PyResult<Vec<i32>> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound.call_method1("update_multiple", (updates,))?.extract()
    }

    /// Upsert a document in the default table.
    ///
    /// :param document: The document to upsert
    /// :param cond: Query condition (optional)
    /// :returns: A list of affected document IDs
    #[pyo3(signature = (document, cond = None))]
    fn upsert(
        &mut self,
        py: Python<'_>,
        document: &Bound<'_, PyAny>,
        cond: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Vec<i32>> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound.call_method1("upsert", (document, cond))?.extract()
    }

    /// Remove documents from the default table.
    ///
    /// :param cond: Query condition (optional)
    /// :param doc_ids: List of document IDs (optional)
    /// :returns: A list of removed document IDs
    #[pyo3(signature = (cond = None, doc_ids = None))]
    fn remove(
        &mut self,
        py: Python<'_>,
        cond: Option<&Bound<'_, PyAny>>,
        doc_ids: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Vec<i32>> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound.call_method1("remove", (cond, doc_ids))?.extract()
    }

    /// Truncate the default table (remove all documents).
    fn truncate(&mut self, py: Python<'_>) -> PyResult<()> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound.call_method0("truncate")?;
        Ok(())
    }

    /// Count documents in the default table.
    ///
    /// :param cond: Query condition (optional)
    /// :returns: The number of matching documents
    #[pyo3(signature = (cond = None))]
    fn count(&self, py: Python<'_>, cond: Option<&Bound<'_, PyAny>>) -> PyResult<usize> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        // Table.count accepts (query)
        // When query is provided, count matching documents; otherwise count all
        if let Some(cond_val) = cond {
            // Use search to get matching documents, then count
            let results = table_bound.call_method1("search", (cond_val,))?;
            let results_list = results.cast::<pyo3::types::PyList>()?;
            Ok(results_list.len())
        } else {
            // Return total count
            table_bound.call_method0("__len__")?.extract()
        }
    }

    /// Get the length (number of documents in the default table).
    fn __len__(&self, py: Python<'_>) -> PyResult<usize> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound.call_method0("__len__")?.extract()
    }

    /// Clear the query cache of the default table.
    fn clear_cache(&self, py: Python<'_>) -> PyResult<()> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound.call_method0("clear_cache")?;
        Ok(())
    }

    /// Get the query cache of the default table.
    #[getter]
    fn _query_cache(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        Ok(table_bound.getattr("_query_cache")?.unbind())
    }

    /// Get the internal tables cache.
    #[getter]
    fn _tables(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        Ok(self._tables.clone_ref(py).into())
    }

    /// Get the default table name.
    #[getter]
    fn default_table_name(&self) -> String {
        self._default_table_name.clone()
    }

    /// Get the storage instance.
    #[getter]
    fn storage(&self, py: Python<'_>) -> Py<PyAny> {
        self.storage.clone_ref(py)
    }

    /// Get the storage instance (alias for storage, for compatibility).
    #[getter]
    fn _storage(&self, py: Python<'_>) -> Py<PyAny> {
        self.storage.clone_ref(py)
    }

    /// Make TinyDB iterable (iterate over default table).
    fn __iter__(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let all_docs = self.all(py)?;
        let iter = all_docs.bind(py).call_method0("__iter__")?;
        Ok(iter.unbind())
    }

    /// String representation of TinyDB.
    fn __repr__(&self, py: Python<'_>) -> PyResult<String> {
        let tables_set = self.tables(py)?;
        let tables_bound = tables_set.bind(py);
        let tables_list = tables_bound.call_method0("__iter__")?;
        
        let mut table_names: Vec<String> = Vec::new();
        let iter = tables_list.try_iter()?;
        for item in iter {
            let item: Bound<'_, PyAny> = item?;
            let name: String = item.extract()?;
            table_names.push(name);
        }
        table_names.sort();
        
        // Build tables string
        let tables_str = table_names
            .iter()
            .map(|n| format!("'{}'", n))
            .collect::<Vec<_>>()
            .join(", ");
        
        // Count documents per table
        let mut doc_counts: Vec<String> = Vec::new();
        let storage_obj = self.storage.bind(py);
        let data = storage_obj.call_method0("read")?;
        
        if !data.is_none() {
            if let Ok(data_dict) = data.cast::<PyDict>() {
                for name in &table_names {
                    if let Some(table_data) = data_dict.get_item(name)? {
                        if let Ok(table_dict) = table_data.cast::<PyDict>() {
                            let count = table_dict.len();
                            doc_counts.push(format!("'{}={}'", name, count));
                        }
                    }
                }
            }
        }
        
        let doc_counts_str = doc_counts.join(", ");
        
        Ok(format!(
            "<TinyDB tables=[{}], tables_count={}, default_table_documents_count={}, all_tables_documents_count=[{}]>",
            tables_str,
            table_names.len(),
            self.__len__(py).unwrap_or(0),
            doc_counts_str
        ))
    }

    /// Get the next document ID for the default table (internal method).
    fn _get_next_id(&self, py: Python<'_>) -> PyResult<i32> {
        let table = self.table(py, None, None)?;
        let table_bound = table.bind(py);
        table_bound.call_method0("_get_next_id")?.extract()
    }

    // Context manager support

    /// Enter the context manager.
    ///
    /// :returns: self
    fn __enter__(slf: Bound<'_, Self>) -> PyResult<Py<PyAny>> {
        // Return self as Py<PyAny>
        // In Python, __enter__ should return self
        Ok(slf.unbind().into())
    }

    /// Exit the context manager.
    ///
    /// :param exc_type: Exception type (if any)
    /// :param exc_val: Exception value (if any)
    /// :param exc_tb: Exception traceback (if any)
    /// :returns: None
    #[pyo3(signature = (exc_type = None, exc_val = None, exc_tb = None))]
    fn __exit__(
        mut slf: PyRefMut<'_, Self>,
        py: Python<'_>,
        exc_type: Option<&Bound<'_, PyAny>>,
        exc_val: Option<&Bound<'_, PyAny>>,
        exc_tb: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<bool> {
        let _ = (exc_type, exc_val, exc_tb); // Not used, but kept for compatibility
        slf.close(py)?;
        Ok(false) // Don't suppress exceptions
    }
}

