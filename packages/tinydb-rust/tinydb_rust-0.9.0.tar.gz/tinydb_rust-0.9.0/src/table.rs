// Table implementation for TinyDB.
//
// This module contains the Table class that handles all CRUD operations
// for documents in a TinyDB table. All core logic is implemented in Rust.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString, PyTuple};
use serde_json::Value;
use std::collections::HashMap;
use crate::utils::LRUCache;
use crate::query::{Query, evaluate_condition};

/// Table represents a single TinyDB table.
///
/// It provides methods for accessing and manipulating documents.
/// All core logic is implemented in Rust for performance and type safety.
#[pyclass(module = "_tinydb_core")]
pub struct Table {
    /// Table name
    name: String,
    /// Storage instance (Python object that implements read/write methods)
    storage: Py<PyAny>,
    /// Query cache for optimizing repeated queries
    query_cache: Py<LRUCache>,
    /// Next document ID to use (cached for performance)
    next_id: Option<i32>,
    /// Custom _read_table function (for testing, can be patched)
    custom_read_table: Option<Py<PyAny>>,
    /// Cached Document class to avoid repeated imports
    document_class: Option<Py<PyAny>>,
    /// Cached table data to avoid repeated Python-Rust conversions
    table_cache: Option<HashMap<String, Value>>,
}

#[pymethods]
impl Table {
    /// Create a new Table instance.
    ///
    /// :param storage: The storage instance to use for this table
    /// :param name: The table name
    /// :param cache_size: Maximum capacity of query cache (default: 10)
    /// :param persist_empty: Store new table even with no operations on it (not yet implemented)
    #[new]
    #[pyo3(signature = (storage, name, cache_size = 10, persist_empty = false))]
    fn new(
        py: Python<'_>,
        storage: Py<PyAny>,
        name: String,
        cache_size: usize,
        persist_empty: bool,
    ) -> PyResult<Self> {
        // Create LRU cache for query results
        // We need to call the Python constructor
        let cache_type = py.get_type::<LRUCache>();
        let cache_instance = cache_type.call1((Some(cache_size),))?;
        let query_cache = cache_instance.cast::<LRUCache>()?.clone().unbind();

        let table = Table {
            name: name.clone(),
            storage: storage.clone_ref(py),
            query_cache,
            next_id: None,
            custom_read_table: None,
            document_class: None,
            table_cache: None,
        };

        // If persist_empty is True, write empty table to storage immediately
        if persist_empty {
            // Read current database state
            let storage_obj = storage.bind(py);
            let db_result = storage_obj.call_method0("read")?;

            let db_dict = if db_result.is_none() {
                PyDict::new(py).unbind()
            } else {
                db_result.cast::<PyDict>()?.clone().unbind()
            };

            // Create empty table dict
            let table_dict = PyDict::new(py);
            
            // Update the database dict with the empty table
            let table_name: Py<PyAny> = PyString::new(py, &name).into();
            db_dict.bind(py).set_item(table_name, table_dict)?;

            // Write back to storage
            storage_obj.call_method1("write", (db_dict,))?;
        }

        Ok(table)
    }

    /// Get the table name.
    #[getter]
    fn name(&self) -> String {
        self.name.clone()
    }

    /// Insert a new document into the table.
    ///
    /// :param document: the document to insert (dict or Document with doc_id)
    /// :returns: the inserted document's ID
    fn insert(&mut self, py: Python<'_>, document: &Bound<'_, PyAny>) -> PyResult<i32> {
        // Check if document has a doc_id attribute (it's a Document object)
        let custom_doc_id: Option<i32> = if document.hasattr("doc_id")? {
            document.getattr("doc_id")?.extract().ok()
        } else {
            None
        };

        // Convert to dict and then to JSON value
        let doc_value = if document.is_instance_of::<PyDict>() {
            let dict = document.cast::<PyDict>()?;
            convert_pydict_to_json(&dict)?
        } else {
            // Verify it's a Mapping type before converting
            let mapping_type = py.import("collections.abc")?.getattr("Mapping")?;
            if !document.is_instance(&mapping_type)? {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Document is not a Mapping",
                ));
            }
            // Convert Mapping to dict
            let builtins = py.import("builtins")?;
            let dict_fn = builtins.getattr("dict")?;
            let dict_obj = dict_fn.call1((document,))?;
            let dict = dict_obj.cast::<PyDict>()?;
            convert_pydict_to_json(&dict)?
        };

        // Read table once for both getting next ID and updating
        let mut table = self._read_table_internal(py)?;
        
        // Get the document ID
        let doc_id = if let Some(id) = custom_doc_id {
            id
        } else {
            // Get next ID from the table we just read
            self._get_next_id_internal(&table)?
        };

        // Check if document ID already exists
        let doc_id_str = doc_id.to_string();
        if table.contains_key(&doc_id_str) {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Document with ID {} already exists", doc_id),
            ));
        }

        // Insert the document into the table
        table.insert(doc_id_str, doc_value);

        // Write the updated table back (take ownership to avoid clone)
        self._write_table_owned(py, table)?;

        // Update next_id if we used a custom ID that's higher
        if let Some(id) = custom_doc_id {
            let current_next = self.next_id.unwrap_or(1);
            if id >= current_next {
                self.next_id = Some(id + 1);
            }
        }

        Ok(doc_id)
    }

    /// Insert multiple documents into the table.
    ///
    /// :param documents: an iterable of documents to insert
    /// :returns: a list containing the inserted documents' IDs
    fn insert_multiple(
        &mut self,
        py: Python<'_>,
        documents: &Bound<'_, PyAny>,
    ) -> PyResult<Vec<i32>> {
        let mut doc_ids = Vec::new();

        // Convert all documents to JSON values and collect IDs + custom doc_ids
        let mut doc_entries: Vec<(Option<i32>, serde_json::Value)> = Vec::new();
        
        // Convert to list first if it's a generator (generators can only be consumed once)
        let builtins = py.import("builtins")?;
        let list_fn = builtins.getattr("list")?;
        let documents_list = list_fn.call1((documents,))?;
        let documents_list = documents_list.cast::<PyList>()?;

        let dict_fn = builtins.getattr("dict")?;
        
        for item in documents_list.iter() {
            // Check for custom doc_id
            let custom_doc_id: Option<i32> = if item.hasattr("doc_id")? {
                item.getattr("doc_id")?.extract().ok()
            } else {
                None
            };

            // Convert to dict and then to JSON value
            let doc_value = if item.is_instance_of::<PyDict>() {
                let dict = item.cast::<PyDict>()?;
                convert_pydict_to_json(&dict)?
            } else {
                let dict_obj = dict_fn.call1((&item,))?;
                let dict = dict_obj.cast::<PyDict>()?;
                convert_pydict_to_json(&dict)?
            };
            doc_entries.push((custom_doc_id, doc_value));
        }

        // Read current table directly and update in-place
        let mut table = self._read_table_internal(py)?;
        let mut next_id = self.next_id.unwrap_or_else(|| {
            if table.is_empty() {
                1
            } else {
                table.keys()
                    .filter_map(|k| k.parse::<i32>().ok())
                    .max()
                    .unwrap_or(0) + 1
            }
        });

        // Insert all documents directly
        for (custom_id, doc_value) in doc_entries {
            let doc_id = custom_id.unwrap_or_else(|| {
                let id = next_id;
                next_id += 1;
                id
            });
            let doc_id_str = doc_id.to_string();

            // Check if document ID already exists
            if table.contains_key(&doc_id_str) {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Document with ID {} already exists", doc_id),
                ));
            }

            // Update next_id if custom_id is higher
            if custom_id.is_some() && doc_id >= next_id {
                next_id = doc_id + 1;
            }

            // Insert the document
            table.insert(doc_id_str, doc_value);
            doc_ids.push(doc_id);
        }

        // Write table once at the end (take ownership to avoid clone)
        self._write_table_owned(py, table)?;

        // Update cached next_id
        self.next_id = Some(next_id);

        Ok(doc_ids)
    }

    /// Get all documents stored in the table.
    ///
    /// :returns: a list with all documents as Document objects
    fn all(&mut self, py: Python<'_>) -> PyResult<Py<PyList>> {
        let table = self._read_table_internal(py)?;
        let list = PyList::empty(py);

        // Import Document class
        let table_module = py.import("tinydb_rust.table")?;
        let document_class = table_module.getattr("Document")?;

        // Sort by doc_id for consistent ordering
        let mut entries: Vec<_> = table.iter().collect();
        entries.sort_by_key(|(k, _)| k.parse::<i32>().unwrap_or(0));

        for (doc_id_str, doc_value) in entries {
            // Parse document ID
            let doc_id: i32 = doc_id_str.parse().unwrap_or(0);

            // Convert JSON value to Python dict
            let doc_dict = convert_json_to_pydict(py, doc_value)?;

            // Create Document object
            let doc = document_class.call1((doc_dict, doc_id))?;
            list.append(doc)?;
        }

        Ok(list.into())
    }

    /// Search for all documents matching a query condition.
    ///
    /// Supports both Rust Query objects (fast path) and Python callables (slow path).
    ///
    /// :param query: the query condition (Query object or Python callable)
    /// :returns: list of matching documents as Document objects
    fn search(&mut self, py: Python<'_>, query: &Bound<'_, PyAny>) -> PyResult<Py<PyAny>> {
        let document_class_unbound = self.get_document_class(py)?;

        // Check if query is cacheable
        let is_cacheable = query.getattr("is_cacheable")
            .and_then(|method| {
                if method.is_callable() {
                    method.call0()?.extract::<bool>()
                } else {
                    Ok(true)
                }
            })
            .unwrap_or(true);

        // Check cache first (only for cacheable queries)
        if is_cacheable {
            let cache_key = query.clone().unbind();
            let cache_bound = self.query_cache.bind(py);
            
            if let Ok(cached_list) = cache_bound.call_method1("get", (cache_key.clone_ref(py), py.None())) {
                if !cached_list.is_none() {
                    // Return a copy of cached results
                    let builtins = py.import("builtins")?;
                    let list_fn = builtins.getattr("list")?;
                    let copied_list = list_fn.call1((cached_list,))?;
                    return Ok(copied_list.unbind());
                }
            }
        }

        // Read all documents from table
        let table = self._read_table_internal(py)?;
        let list = PyList::empty(py);

        // Optimize: if query has a _rust_query attribute, use it directly to avoid cloning condition
        // Extract PyRef<Query> once and reuse it in the loop to avoid cloning the condition tree
        let rust_query_opt = query.getattr("_rust_query")
            .ok()
            .and_then(|rust_query_attr| {
                if rust_query_attr.is_none() {
                    return None;
                }
                rust_query_attr.extract::<pyo3::PyRef<'_, Query>>().ok()
            });
        
        if let Some(rust_query_ref) = rust_query_opt {
            // Fast path: evaluate directly in Rust without Python-Rust FFI per document
            // Use reference to condition to avoid cloning
            if let Some(ref condition) = rust_query_ref.condition {
                // Bind document_class once outside the loop
                let document_class = document_class_unbound.bind(py);
                for (doc_id_str, doc_value) in table.iter() {
                    // Evaluate condition directly in Rust using reference (avoid parsing doc_id if not needed)
                    let matches = evaluate_condition(py, condition, doc_value)?;
                    
                    if matches {
                        // Parse doc_id only when document matches
                        let doc_id: i32 = doc_id_str.parse().unwrap_or(0);
                        // Only convert to Python dict when we need to create Document object
                        let doc_dict = convert_json_to_pydict(py, doc_value)?;
                        let doc = document_class.call1((doc_dict, doc_id))?;
                        list.append(doc)?;
                    }
                }
            }
        } else {
            // Standard path: use Python callable for query evaluation
            if !query.is_callable() {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "Query must be a Query object or a callable function",
                ));
            }
            
            for (doc_id_str, doc_value) in table.iter() {
                // Convert document to Python dict for query
                let doc_dict = convert_json_to_pydict(py, doc_value)?;
                let doc_id: i32 = doc_id_str.parse().unwrap_or(0);

                // Call Python function with document (without doc_id for query)
                let result = query.call1((doc_dict.clone(),))?;
                let matches: bool = result.extract()?;

                if matches {
                    // Create Document object for result
                    let document_class = document_class_unbound.bind(py);
                    let doc = document_class.call1((doc_dict, doc_id))?;
                    list.append(doc)?;
                }
            }
        }

        // Cache the results (only for cacheable queries)
        if is_cacheable {
            let cache_key = query.clone().unbind();
            let cache_bound = self.query_cache.bind(py);
            // Store a copy of the results
            let builtins = py.import("builtins")?;
            let list_fn = builtins.getattr("list")?;
            let cached_copy = list_fn.call1((list.clone(),))?;
            cache_bound.call_method1("__setitem__", (cache_key, cached_copy))?;
        }

        Ok(list.into())
    }

    /// Update all matching documents to have a given set of fields.
    ///
    /// :param fields: the fields that the matching documents will have (dict or callable)
    /// :param query: which documents to update (optional)
    /// :param doc_ids: a list of document IDs (optional)
    /// :returns: a list containing the updated documents' IDs
    #[pyo3(signature = (fields, query = None, doc_ids = None))]
    fn update(
        &mut self,
        py: Python<'_>,
        fields: &Bound<'_, PyAny>,
        query: Option<&Bound<'_, PyAny>>,
        doc_ids: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Vec<i32>> {
        let is_callable = fields.is_callable();
        let fields_value = if !is_callable {
            // Convert dict or Mapping to JSON value
            if fields.is_instance_of::<PyDict>() {
                let dict = fields.cast::<PyDict>()?;
                Some(convert_pydict_to_json(&dict)?)
            } else {
                let builtins = py.import("builtins")?;
                let dict_fn = builtins.getattr("dict")?;
                let dict_obj = dict_fn.call1((fields,))?;
                let dict = dict_obj.cast::<PyDict>()?;
                Some(convert_pydict_to_json(&dict)?)
            }
        } else {
            None
        };

        let mut updated_ids = Vec::new();
        let mut table = self._read_table_internal(py)?;

        // Inline helper: apply fields update to a document
        let apply_update = |py: Python<'_>, doc: &mut Value, fields: &Bound<'_, PyAny>, 
                            fields_value: &Option<Value>, is_callable: bool| -> PyResult<()> {
            if is_callable {
                let doc_dict = convert_json_to_pydict(py, doc)?;
                fields.call1((doc_dict.clone(),))?;
                *doc = convert_pydict_to_json(&doc_dict)?;
            } else if let Some(ref fv) = fields_value {
                merge_json_values(doc, fv)?;
            }
            Ok(())
        };

        // Update documents by IDs
        if let Some(doc_ids_val) = doc_ids {
            if !doc_ids_val.is_none() {
                let doc_ids_list = doc_ids_val.cast::<PyList>()?;
                let ids: Vec<i32> = doc_ids_list.extract()?;
                updated_ids = ids.clone();

                for doc_id in &ids {
                    let doc_id_str = doc_id.to_string();
                    if let Some(doc) = table.get_mut(&doc_id_str) {
                        apply_update(py, doc, fields, &fields_value, is_callable)?;
                    }
                }

                self._write_table_owned(py, table)?;
                updated_ids.sort();
                return Ok(updated_ids);
            }
        }

        // Query-based update: try Rust fast path first
        if let Some(query_obj) = query {
            if !query_obj.is_none() {
                // Try to get Rust query condition
                let rust_query_condition: Option<pyo3::PyRef<'_, crate::query::Query>> = 
                    if query_obj.hasattr("_rust_query")? {
                        query_obj.getattr("_rust_query")?.extract().ok()
                    } else {
                        None
                    };

                if let Some(ref rust_query_ref) = rust_query_condition {
                    if let Some(ref condition) = rust_query_ref.condition {
                        // Fast path: evaluate in Rust
                        for (doc_id_str, doc) in table.iter_mut() {
                            if crate::query::evaluate_condition(py, condition, doc)? {
                                updated_ids.push(doc_id_str.parse().unwrap_or(0));
                                apply_update(py, doc, fields, &fields_value, is_callable)?;
                            }
                        }
                        self._write_table_owned(py, table)?;
                        updated_ids.sort();
                        return Ok(updated_ids);
                    }
                }

                // Slow path: Python callback
                for (doc_id_str, doc) in table.iter_mut() {
                    let doc_dict = convert_json_to_pydict(py, doc)?;
                    if query_obj.call1((doc_dict.clone(),))?.extract::<bool>()? {
                        updated_ids.push(doc_id_str.parse().unwrap_or(0));
                        if is_callable {
                            fields.call1((doc_dict,))?;
                            *doc = convert_pydict_to_json(&convert_json_to_pydict(py, doc)?)?;
                        } else if let Some(ref fv) = fields_value {
                            merge_json_values(doc, fv)?;
                        }
                    }
                }

                self._write_table_owned(py, table)?;
                updated_ids.sort();
                return Ok(updated_ids);
            }
        }
        
        // If no query or doc_ids specified, update all documents
        for (doc_id_str, doc) in table.iter_mut() {
            updated_ids.push(doc_id_str.parse().unwrap_or(0));
            apply_update(py, doc, fields, &fields_value, is_callable)?;
        }

        self._write_table_owned(py, table)?;
        updated_ids.sort();
        Ok(updated_ids)
    }

    /// Update multiple documents with different values.
    ///
    /// :param updates: a sequence of (fields, condition) pairs
    /// :returns: a list containing the updated documents' IDs
    fn update_multiple(
        &mut self,
        py: Python<'_>,
        updates: &Bound<'_, PyAny>,
    ) -> PyResult<Vec<i32>> {
        let mut all_updated_ids = Vec::new();
        
        // Iterate over updates (sequence of (fields, condition) tuples)
        let iter = updates.try_iter()?;
        for item in iter {
            let item: Bound<'_, PyAny> = item?;
            let tuple = item.cast::<PyTuple>()?;
            
            if tuple.len() != 2 {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "Each update must be a (fields, condition) tuple",
                ));
            }
            
            let fields = tuple.get_item(0)?;
            let condition = tuple.get_item(1)?;
            
            // Call update with these parameters
            let updated_ids = self.update(py, &fields, Some(&condition), None)?;
            all_updated_ids.extend(updated_ids);
        }
        
        Ok(all_updated_ids)
    }

    /// Insert or update a document.
    ///
    /// :param document: the document to insert or update
    /// :param cond: the condition to check against (optional)
    /// :returns: a list containing the affected document IDs
    #[pyo3(signature = (document, cond = None))]
    fn upsert(
        &mut self,
        py: Python<'_>,
        document: &Bound<'_, PyAny>,
        cond: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Vec<i32>> {
        // If condition is provided, try to update first
        if let Some(query_obj) = cond {
            if !query_obj.is_none() {
                // Check if any documents match
                let table_data = self._read_table_internal(py)?;
                
                for (_, doc_value) in table_data.iter() {
                    let doc_dict = convert_json_to_pydict(py, doc_value)?;
                    let matches = query_obj.call1((doc_dict,))?.extract::<bool>()?;
                    if matches {
                        // Update matching documents
                        return self.update(py, document, Some(query_obj), None);
                    }
                }
                
                // No match found, insert new document
                let doc_id = self.insert(py, document)?;
                return Ok(vec![doc_id]);
            }
        }
        
        // Check if document has a doc_id attribute (it's a Document object)
        if document.hasattr("doc_id")? {
            if let Ok(doc_id) = document.getattr("doc_id")?.extract::<i32>() {
                let table_data = self._read_table_internal(py)?;
                let doc_id_str = doc_id.to_string();
                
                if table_data.contains_key(&doc_id_str) {
                    // Update existing document
                    let doc_dict = document.cast::<PyDict>()?;
                    let doc_value = convert_pydict_to_json(&doc_dict)?;
                    
                    self._update_table(py, |table| {
                        if let Some(doc) = table.get_mut(&doc_id_str) {
                            *doc = doc_value;
                        }
                        Ok(())
                    })?;
                    
                    return Ok(vec![doc_id]);
                }
                
                // Insert with this doc_id
                let doc_id = self.insert(py, document)?;
                return Ok(vec![doc_id]);
            }
        }
        
        // No condition and no doc_id - raise error
        Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "If you don't specify a query, you must provide a doc_id in the document",
        ))
    }

    /// Get exactly one document specified by a query or a document ID.
    ///
    /// :param cond: the condition to check against (optional)
    /// :param doc_id: the document's ID (optional)
    /// :param doc_ids: the document's IDs for multiple (optional)
    /// :returns: the document or None
    #[pyo3(signature = (cond = None, doc_id = None, doc_ids = None))]
    fn get(
        &mut self,
        py: Python<'_>,
        cond: Option<&Bound<'_, PyAny>>,
        doc_id: Option<&Bound<'_, PyAny>>,
        doc_ids: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Py<PyAny>> {
        let table = self._read_table_internal(py)?;

        // Case 1: Get by single doc_id
        if let Some(doc_id_val) = doc_id {
            if !doc_id_val.is_none() {
                // Check for NaN
                if let Ok(f) = doc_id_val.extract::<f64>() {
                    if f.is_nan() {
                        return Ok(py.None());
                    }
                }
                
                let doc_id_int: i32 = doc_id_val.extract()?;
                let doc_id_str = doc_id_int.to_string();

                if let Some(doc_value) = table.get(&doc_id_str) {
                    let table_module = py.import("tinydb_rust.table")?;
                    let document_class = table_module.getattr("Document")?;
                    
                    let doc_dict = convert_json_to_pydict(py, doc_value)?;
                    let doc = document_class.call1((doc_dict, doc_id_int))?;
                    return Ok(doc.unbind());
                }
                return Ok(py.None());
            }
        }

        // Case 2: Get by multiple doc_ids
        if let Some(doc_ids_val) = doc_ids {
            if !doc_ids_val.is_none() {
                let doc_ids_list = doc_ids_val.cast::<PyList>()?;
                let result_list = PyList::empty(py);
                
                let table_module = py.import("tinydb_rust.table")?;
                let document_class = table_module.getattr("Document")?;
                
                for item in doc_ids_list.iter() {
                    let doc_id_int: i32 = item.extract()?;
                    let doc_id_str = doc_id_int.to_string();
                    
                    if let Some(doc_value) = table.get(&doc_id_str) {
                        let doc_dict = convert_json_to_pydict(py, doc_value)?;
                        let doc = document_class.call1((doc_dict, doc_id_int))?;
                        result_list.append(doc)?;
                    }
                }
                return Ok(result_list.into());
            }
        }

        // Case 3: Get by condition
        if let Some(cond_val) = cond {
            if !cond_val.is_none() {
                let table_module = py.import("tinydb_rust.table")?;
                let document_class = table_module.getattr("Document")?;

                // Sort by doc_id for consistent ordering (return first match)
                let mut entries: Vec<_> = table.iter().collect();
                entries.sort_by_key(|(k, _)| k.parse::<i32>().unwrap_or(0));

                for (doc_id_str, doc_value) in entries {
                    let doc_dict = convert_json_to_pydict(py, doc_value)?;
                    let doc_id: i32 = doc_id_str.parse().unwrap_or(0);

                    let matches = cond_val.call1((doc_dict.clone(),))?.extract::<bool>()?;
                    if matches {
                        let doc = document_class.call1((doc_dict, doc_id))?;
                        return Ok(doc.unbind());
                    }
                }
                return Ok(py.None());
            }
        }

        // No valid arguments provided
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "You have to pass either cond or doc_id or doc_ids",
        ))
    }

    /// Remove all matching documents.
    ///
    /// :param cond: the condition to check against (optional)
    /// :param doc_ids: a list of document IDs (optional)
    /// :returns: a list containing the removed documents' IDs
    #[pyo3(signature = (cond = None, doc_ids = None))]
    fn remove(
        &mut self,
        py: Python<'_>,
        cond: Option<&Bound<'_, PyAny>>,
        doc_ids: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<Vec<i32>> {
        // Handle doc_ids
        if let Some(doc_ids_val) = doc_ids {
            if !doc_ids_val.is_none() {
                let doc_ids_list = doc_ids_val.cast::<PyList>()?;
                let ids: Vec<i32> = doc_ids_list.extract()?;
                let removed_ids = ids.clone();

                self._update_table(py, |table| {
                    for doc_id in &ids {
                        let doc_id_str = doc_id.to_string();
                        table.remove(&doc_id_str);
                    }
                    Ok(())
                })?;

                return Ok(removed_ids);
            }
        }
        
        // Handle query condition
        if let Some(query_obj) = cond {
            if !query_obj.is_none() {
                if !query_obj.is_callable() {
                    return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                        "Query must be a Query object or a callable function",
                    ));
                }
                
                // Use Python callable
                let table_data = self._read_table_internal(py)?;
                let mut ids_to_remove = Vec::new();

                // First pass: find matching documents
                for (doc_id_str, doc_value) in table_data.iter() {
                    let doc_dict = convert_json_to_pydict(py, doc_value)?;
                    let result = query_obj.call1((doc_dict,))?;
                    let matches: bool = result.extract()?;

                    if matches {
                        ids_to_remove.push(doc_id_str.clone());
                    }
                }

                // Second pass: remove matching documents
                let mut removed_ids: Vec<i32> = ids_to_remove
                    .iter()
                    .filter_map(|s| s.parse::<i32>().ok())
                    .collect();

                if !ids_to_remove.is_empty() {
                    self._update_table(py, |table| {
                        for doc_id_str in &ids_to_remove {
                            table.remove(doc_id_str);
                        }
                        Ok(())
                    })?;
                } else {
                    // Even if no documents were removed, clear cache
                    // because remove operation may have invalidated cached queries
                    self.query_cache.bind(py).call_method0("clear")?;
                }

                removed_ids.sort();
                return Ok(removed_ids);
            }
        }
        
        // Neither cond nor doc_ids provided
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "Use truncate() to remove all documents",
        ))
    }

    /// Truncate the table by removing all documents.
    fn truncate(&mut self, py: Python<'_>) -> PyResult<()> {
        self._update_table(py, |table| {
            table.clear();
            Ok(())
        })?;

        // Reset document ID counter
        self.next_id = None;

        Ok(())
    }

    /// Count the documents matching a query.
    ///
    /// :param query: the condition to use
    /// :returns: the number of matching documents
    fn count(&mut self, py: Python<'_>, query: &Bound<'_, PyAny>) -> PyResult<usize> {
        // Use search to get matching documents, then count
        let results = self.search(py, query)?;
        let results_list = results.bind(py);
        results_list.len()
    }

    /// Check whether the table contains a document matching a query or an ID.
    ///
    /// :param cond: the condition to use (optional)
    /// :param doc_id: the document ID to look for (optional)
    /// :returns: True if a matching document exists, False otherwise
    #[pyo3(signature = (cond = None, doc_id = None))]
    fn contains(
        &mut self,
        py: Python<'_>,
        cond: Option<&Bound<'_, PyAny>>,
        doc_id: Option<&Bound<'_, PyAny>>,
    ) -> PyResult<bool> {
        // Handle doc_id
        if let Some(doc_id_val) = doc_id {
            if !doc_id_val.is_none() {
                let result = self.get(py, None, Some(doc_id_val), None)?;
                return Ok(!result.bind(py).is_none());
            }
        }

        // Handle condition
        if let Some(cond_val) = cond {
            if !cond_val.is_none() {
                let result = self.get(py, Some(cond_val), None, None)?;
                return Ok(!result.bind(py).is_none());
            }
        }

        // Neither cond nor doc_id provided
        Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
            "You have to pass either cond or doc_id",
        ))
    }

    /// Clear the query cache and table cache.
    pub fn clear_cache(&mut self, py: Python<'_>) -> PyResult<()> {
        self.query_cache.bind(py).call_method0("clear")?;
        self._invalidate_cache();
        Ok(())
    }

    /// Get the total number of documents in this table.
    fn __len__(&mut self, py: Python<'_>) -> PyResult<usize> {
        let table = self._read_table_internal(py)?;
        Ok(table.len())
    }

    /// Make the table iterable.
    fn __iter__(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        let all_docs = self.all(py)?;
        let iter = all_docs.bind(py).call_method0("__iter__")?;
        Ok(iter.unbind())
    }

    /// String representation of the table.
    fn __repr__(&mut self, py: Python<'_>) -> PyResult<String> {
        let table = self._read_table_internal(py)?;
        let storage_repr = self.storage.bind(py).repr()?.to_string();
        // Replace tinydb_rust.storages with tinydb.storages for compatibility
        let storage_repr = storage_repr.replace("tinydb_rust.storages", "tinydb.storages");
        Ok(format!(
            "<Table name='{}', total={}, storage={}>",
            self.name,
            table.len(),
            storage_repr
        ))
    }

    /// Get the query cache.
    #[getter]
    fn _query_cache(&self, py: Python<'_>) -> Py<LRUCache> {
        self.query_cache.clone_ref(py)
    }

    /// Get the storage.
    #[getter]
    fn storage(&self, py: Python<'_>) -> Py<PyAny> {
        self.storage.clone_ref(py)
    }

    /// Public method to get the next document ID.
    fn _get_next_id(&mut self, py: Python<'_>) -> PyResult<i32> {
        let table = self._read_table_internal(py)?;
        self._get_next_id_internal(&table)
    }

    /// Read the table data (internal method exposed for testing).
    fn _read_table_py(&mut self, py: Python<'_>) -> PyResult<Py<PyDict>> {
        let table = self._read_table_internal(py)?;
        let dict = PyDict::new(py);
        for (key, value) in table.iter() {
            let py_key = PyString::new(py, key);
            let py_value = convert_json_value_to_pyobject(py, value)?;
            dict.set_item(py_key, py_value)?;
        }
        Ok(dict.unbind())
    }

    /// Get the _read_table function (for testing, can be patched).
    /// This is exposed as a property in Python, allowing tests to patch it.
    #[getter]
    fn _read_table(&self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        if let Some(ref custom_fn) = self.custom_read_table {
            Ok(custom_fn.clone_ref(py))
        } else {
            // Return a callable that wraps _read_table_py
            // We'll use Python's types.MethodType to create a bound method
            // First, get the _read_table_py method as an unbound method
            let table_type = py.get_type::<Table>();
            let unbound_method = table_type.getattr("_read_table_py")?;
            
            // Create a bound method using types.MethodType
            let types_module = py.import("types")?;
            let _method_type = types_module.getattr("MethodType")?;
            
            // Get self as a PyObject - we need to use Py::from
            // Actually, we can't easily get self as PyObject here
            // Let's use a simpler approach: return a lambda that will be bound later
            // Or, we can use __get__ descriptor behavior
            // For now, let's just return the unbound method and let Python handle binding
            Ok(unbound_method.unbind())
        }
    }

    /// Set the _read_table function (for testing, allows patching).
    #[setter(_read_table)]
    #[allow(non_snake_case)]
    fn set__read_table(&mut self, _py: Python<'_>, value: Py<PyAny>) -> PyResult<()> {
        self.custom_read_table = Some(value);
        Ok(())
    }
}

// Private helper methods
impl Table {
    /// Get or initialize the Document class (cached for performance).
    fn get_document_class(&mut self, py: Python<'_>) -> PyResult<Py<PyAny>> {
        if let Some(ref doc_class) = self.document_class {
            Ok(doc_class.clone_ref(py))
        } else {
            let table_module = py.import("tinydb_rust.table")?;
            let document_class = table_module.getattr("Document")?;
            let document_class_unbound = document_class.clone().unbind();
            self.document_class = Some(document_class_unbound.clone_ref(py));
            Ok(document_class_unbound)
        }
    }

    /// Internal method to get next ID from a table.
    fn _get_next_id_internal(&mut self, table: &HashMap<String, Value>) -> PyResult<i32> {
        // If we already know the next ID, use it
        if let Some(next_id) = self.next_id {
            self.next_id = Some(next_id + 1);
            return Ok(next_id);
        }

        // Determine the next document ID by finding the max ID
        if table.is_empty() {
            let next_id = 1;
            self.next_id = Some(2);
            return Ok(next_id);
        }

        // Find the maximum ID
        let max_id = table
            .keys()
            .filter_map(|k| k.parse::<i32>().ok())
            .max()
            .unwrap_or(0);

        let next_id = max_id + 1;
        self.next_id = Some(next_id + 1);

        Ok(next_id)
    }

    /// Read the table data from the underlying storage.
    ///
    /// Returns a HashMap mapping document IDs (as strings) to document values.
    /// Uses cache when available to avoid repeated Python-Rust conversions.
    fn _read_table_internal(&mut self, py: Python<'_>) -> PyResult<HashMap<String, Value>> {
        // Return cached data if available
        if let Some(ref cached) = self.table_cache {
            return Ok(cached.clone());
        }

        // If custom_read_table is set, use it
        if let Some(ref custom_fn) = self.custom_read_table {
            let result = custom_fn.bind(py).call0()?;
            if result.is_none() {
                return Ok(HashMap::new());
            }
            let table_dict = result.cast::<PyDict>()?;
            let mut hashmap = HashMap::new();
            for (key, value) in table_dict.iter() {
                let key_str = key.extract::<String>()?;
                let json_value = convert_pyobject_to_json(&value)?;
                hashmap.insert(key_str, json_value);
            }
            return Ok(hashmap);
        }

        // Call storage.read() method
        let storage_obj = self.storage.bind(py);
        let result = storage_obj.call_method0("read")?;

        // Handle None case (empty database)
        if result.is_none() {
            self.table_cache = Some(HashMap::new());
            return Ok(HashMap::new());
        }

        // Extract the database dict
        let db_dict = result.cast::<PyDict>()?;

        // Get the table data
        let table_name = PyString::new(py, &self.name);
        let table_data = db_dict.get_item(table_name)?;

        if let Some(table_dict) = table_data {
            // Convert Python dict to HashMap<String, Value>
            let table_dict = table_dict.cast::<PyDict>()?;
            let mut table_result = HashMap::new();

            for (key, value) in table_dict.iter() {
                let key_str = key.extract::<String>()?;
                let json_value = convert_pyobject_to_json(&value)?;
                table_result.insert(key_str, json_value);
            }

            // Cache the result
            self.table_cache = Some(table_result.clone());
            Ok(table_result)
        } else {
            // Table doesn't exist yet
            self.table_cache = Some(HashMap::new());
            Ok(HashMap::new())
        }
    }

    /// Invalidate the table cache (called after write operations).
    fn _invalidate_cache(&mut self) {
        self.table_cache = None;
    }

    /// Update the table data and write it back to storage.
    ///
    /// This method reads the current table data, applies the updater function,
    /// and writes the updated data back to storage. It also clears the query cache.
    fn _update_table<F>(&mut self, py: Python<'_>, updater: F) -> PyResult<()>
    where
        F: FnOnce(&mut HashMap<String, Value>) -> PyResult<()>,
    {
        // Read current table data
        let mut table = self._read_table_internal(py)?;

        // Apply the updater function
        updater(&mut table)?;

        // Write the table back (take ownership to avoid clone)
        self._write_table_owned(py, table)?;

        Ok(())
    }

    /// Write table data directly and take ownership of the table.
    fn _write_table_owned(&mut self, py: Python<'_>, table: HashMap<String, Value>) -> PyResult<()> {
        let storage_obj = self.storage.bind(py);
        
        // Convert table HashMap to Python dict
        let table_dict = PyDict::new(py);
        for (key, value) in table.iter() {
            table_dict.set_item(key, convert_json_value_to_pyobject(py, value)?)?;
        }

        // Read current database state
        let db_result = storage_obj.call_method0("read")?;
        
        // Get or create the database dict, update with table data, and write
        if db_result.is_none() {
            let db_dict = PyDict::new(py);
            db_dict.set_item(&self.name, table_dict)?;
            storage_obj.call_method1("write", (db_dict,))?;
        } else {
            let db_dict = db_result.downcast::<PyDict>()?;
            db_dict.set_item(&self.name, table_dict)?;
            storage_obj.call_method1("write", (db_dict,))?;
        };

        // Update table cache with new data (move instead of clone)
        self.table_cache = Some(table);
        
        // Clear query cache (table contents have changed)
        self.query_cache.bind(py).call_method0("clear")?;

        Ok(())
    }
}

// Helper functions for converting between Python and JSON

/// Convert a Python dict to serde_json::Value.
fn convert_pydict_to_json(dict: &Bound<'_, PyDict>) -> PyResult<Value> {
    let mut map = serde_json::Map::new();

    for (key, value) in dict.iter() {
        let key_str: String = key.extract()?;
        let json_value = convert_pyobject_to_json(&value)?;
        map.insert(key_str, json_value);
    }

    Ok(Value::Object(map))
}

/// Convert a Python object to serde_json::Value.
fn convert_pyobject_to_json(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    use pyo3::types::{PyBool, PyFloat, PyInt, PyString};

    if obj.is_none() {
        return Ok(Value::Null);
    }

    // Check bool first (bool is subclass of int in Python)
    if obj.is_instance_of::<PyBool>() {
        return Ok(Value::Bool(obj.extract::<bool>()?));
    }

    // Check int
    if obj.is_instance_of::<PyInt>() {
        return Ok(Value::Number(obj.extract::<i64>()?.into()));
    }

    // Check float
    if obj.is_instance_of::<PyFloat>() {
        let f = obj.extract::<f64>()?;
        return Ok(Value::Number(
            serde_json::Number::from_f64(f)
                .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid number"))?,
        ));
    }

    // Check string
    if obj.is_instance_of::<PyString>() {
        return Ok(Value::String(obj.extract::<String>()?));
    }

    // Check dict
    if let Ok(dict) = obj.downcast::<PyDict>() {
        let mut map = serde_json::Map::new();
        for (key, value) in dict.iter() {
            let key_str: String = key.extract()?;
            map.insert(key_str, convert_pyobject_to_json(&value)?);
        }
        return Ok(Value::Object(map));
    }

    // Check list
    if let Ok(list) = obj.downcast::<PyList>() {
        let mut arr = Vec::with_capacity(list.len());
        for item in list.iter() {
            arr.push(convert_pyobject_to_json(&item)?);
        }
        return Ok(Value::Array(arr));
    }

    // Unsupported type
    Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
        format!("Object is not JSON serializable")
    ))
}

/// Convert a serde_json::Value to a Python dict.
fn convert_json_to_pydict<'py>(py: Python<'py>, value: &Value) -> PyResult<Bound<'py, PyDict>> {
    match value {
        Value::Object(map) => {
            let dict = PyDict::new(py);
            for (key, val) in map {
                let py_key = PyString::new(py, key);
                let py_val = convert_json_value_to_pyobject(py, val)?;
                dict.set_item(py_key, py_val)?;
            }
            Ok(dict)
        }
        _ => Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
            "Expected JSON object",
        )),
    }
}

/// Convert a serde_json::Value to a Python object.
fn convert_json_value_to_pyobject(py: Python<'_>, value: &Value) -> PyResult<Py<PyAny>> {
    use pyo3::types::{PyBool, PyFloat, PyInt, PyString};

    match value {
        Value::Null => Ok(py.None().into()),
        Value::Bool(b) => Ok(PyBool::new(py, *b).to_owned().into_any().unbind()),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                Ok(PyInt::new(py, i).into_any().unbind())
            } else if let Some(u) = n.as_u64() {
                if u <= i64::MAX as u64 {
                    Ok(PyInt::new(py, u as i64).into_any().unbind())
                } else {
                    Ok(PyString::new(py, &u.to_string()).into_any().unbind())
                }
            } else if let Some(f) = n.as_f64() {
                Ok(PyFloat::new(py, f).into_any().unbind())
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>("Invalid number"))
            }
        }
        Value::String(s) => Ok(PyString::new(py, s).into_any().unbind()),
        Value::Array(arr) => {
            // Pre-allocate list with known size
            let mut items: Vec<Py<PyAny>> = Vec::with_capacity(arr.len());
            for item in arr {
                items.push(convert_json_value_to_pyobject(py, item)?);
            }
            Ok(PyList::new(py, items)?.unbind().into_any())
        }
        Value::Object(map) => {
            let dict = PyDict::new(py);
            for (key, val) in map {
                dict.set_item(key, convert_json_value_to_pyobject(py, val)?)?;
            }
            Ok(dict.unbind().into_any())
        }
    }
}

/// Merge fields from source into target JSON value.
///
/// This function recursively merges two JSON objects, updating target
/// with values from source.
fn merge_json_values(target: &mut Value, source: &Value) -> PyResult<()> {
    match target {
        Value::Object(ref mut target_map) => {
            if let Value::Object(source_map) = source {
                for (key, source_val) in source_map {
                    if let Some(target_val) = target_map.get_mut(key) {
                        // Recursively merge if both are objects
                        if target_val.is_object() && source_val.is_object() {
                            merge_json_values(target_val, source_val)?;
                        } else {
                            // Otherwise, replace
                            *target_val = source_val.clone();
                        }
                    } else {
                        // New key, insert it
                        target_map.insert(key.clone(), source_val.clone());
                    }
                }
            } else {
                // Source is not an object, replace target entirely
                *target = source.clone();
            }
        }
        _ => {
            // If target is not an object, replace it entirely
            *target = source.clone();
        }
    }
    Ok(())
}


