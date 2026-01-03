//! # Query Engine Implementation
//!
//! This module provides the query engine for TinyDB, allowing users to build and
//! evaluate queries using a fluent API. All query evaluation logic is implemented
//! in Rust for high performance.
//!
//! ## Query Building
//!
//! Queries are built using a fluent API similar to the original TinyDB:
//!
//! ```python
//! from tinydb_rust import Query
//!
//! # Simple field access
//! Query().name == "Alice"
//!
//! # Nested field access
//! Query().user.name == "Bob"
//!
//! # Complex queries with logical operators
//! (Query().age > 25) & (Query().city == "NYC")
//! ```
//!
//! ## Query Evaluation
//!
//! Queries are evaluated against documents using the [`evaluate_condition`] function,
//! which recursively traverses the condition tree and matches documents.

use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde_json::Value;
use regex::Regex;
use std::hash::Hash;

/// Query condition tree representing all possible query operations.
///
/// This enum forms the intermediate representation (IR) for queries. It represents
/// a tree structure that can be recursively evaluated against documents. Each variant
/// corresponds to a different query operation (equality, comparison, logical operations, etc.).
///
/// The condition tree is built by the [`Query`] class and evaluated by [`evaluate_condition`].
///
/// # Examples
///
/// Conditions are typically created through the [`Query`] API:
///
/// ```python
/// from tinydb_rust import Query
///
/// # Creates Condition::Eq
/// query = Query().name == "Alice"
///
/// # Creates Condition::And with two Condition::Eq children
/// query = (Query().age > 25) & (Query().city == "NYC")
/// ```
#[derive(Debug)]
pub enum Condition {
    /// Equality: path == value
    Eq {
        path: Vec<String>,
        value: Value,
    },
    /// Not equal: path != value
    Ne {
        path: Vec<String>,
        value: Value,
    },
    /// Less than: path < value
    Lt {
        path: Vec<String>,
        value: Value,
    },
    /// Less than or equal: path <= value
    Le {
        path: Vec<String>,
        value: Value,
    },
    /// Greater than: path > value
    Gt {
        path: Vec<String>,
        value: Value,
    },
    /// Greater than or equal: path >= value
    Ge {
        path: Vec<String>,
        value: Value,
    },
    /// Logical AND: left && right
    And {
        left: Box<Condition>,
        right: Box<Condition>,
    },
    /// Logical OR: left || right
    Or {
        left: Box<Condition>,
        right: Box<Condition>,
    },
    /// Logical NOT: !condition
    Not {
        condition: Box<Condition>,
    },
    /// Field exists: path exists in document
    Exists {
        path: Vec<String>,
    },
    /// Regex match: path matches regex pattern
    Matches {
        path: Vec<String>,
        pattern: String,
    },
    /// Regex search: path contains regex pattern
    Search {
        path: Vec<String>,
        pattern: String,
    },
    /// Test with Python function: test_func(document) -> bool
    /// This is stored as a Py<PyAny> and will be called during evaluation
    Test {
        path: Vec<String>,
        func: Py<PyAny>, // Python callable
    },
}

impl Clone for Condition {
    fn clone(&self) -> Self {
        match self {
            Condition::Eq { path, value } => Condition::Eq {
                path: path.clone(),
                value: value.clone(),
            },
            Condition::Ne { path, value } => Condition::Ne {
                path: path.clone(),
                value: value.clone(),
            },
            Condition::Lt { path, value } => Condition::Lt {
                path: path.clone(),
                value: value.clone(),
            },
            Condition::Le { path, value } => Condition::Le {
                path: path.clone(),
                value: value.clone(),
            },
            Condition::Gt { path, value } => Condition::Gt {
                path: path.clone(),
                value: value.clone(),
            },
            Condition::Ge { path, value } => Condition::Ge {
                path: path.clone(),
                value: value.clone(),
            },
            Condition::And { left, right } => Condition::And {
                left: left.clone(),
                right: right.clone(),
            },
            Condition::Or { left, right } => Condition::Or {
                left: left.clone(),
                right: right.clone(),
            },
            Condition::Not { condition } => Condition::Not {
                condition: condition.clone(),
            },
            Condition::Exists { path } => Condition::Exists {
                path: path.clone(),
            },
            Condition::Matches { path, pattern } => Condition::Matches {
                path: path.clone(),
                pattern: pattern.clone(),
            },
            Condition::Search { path, pattern } => Condition::Search {
                path: path.clone(),
                pattern: pattern.clone(),
            },
            Condition::Test { path, func } => Condition::Test {
                path: path.clone(),
                func: Python::attach(|py| func.clone_ref(py)),
            },
        }
    }
}

/// Query builder for constructing and evaluating database queries.
///
/// This class provides a fluent API for building queries that matches the original
/// TinyDB syntax. Queries are built by chaining field access and comparison operations,
/// then combined with logical operators (`&`, `|`, `~`).
///
/// # Query Building
///
/// Queries are built using attribute access and comparison operators:
///
/// ```python
/// from tinydb_rust import Query
///
/// # Simple equality
/// Query().name == "Alice"
///
/// # Nested field access
/// Query().user.profile.name == "Bob"
///
/// # Dictionary-style access
/// Query()['field'] == "value"
///
/// # Comparison operators
/// Query().age > 25
/// Query().score <= 100
/// Query().price < 50.0
/// ```
///
/// # Logical Operators
///
/// Queries can be combined using logical operators:
///
/// ```python
/// # AND: both conditions must be true
/// (Query().age > 25) & (Query().city == "NYC")
///
/// # OR: either condition can be true
/// (Query().status == "active") | (Query().status == "pending")
///
/// # NOT: negate a condition
/// ~(Query().deleted == True)
/// ```
///
/// # Special Query Operations
///
/// ```python
/// # Check if field exists
/// Query().email.exists()
///
/// # Regex match (full match)
/// Query().name.matches(r'^A.*')
///
/// # Regex search (partial match)
/// Query().description.search(r'python')
///
/// # Custom test function
/// Query().age.test(lambda x: x > 18 and x < 65)
/// ```
///
/// # Examples
///
/// ```python
/// from tinydb_rust import TinyDB, Query
///
/// db = TinyDB('db.json')
///
/// # Insert some documents
/// db.insert({'name': 'Alice', 'age': 30, 'city': 'NYC'})
/// db.insert({'name': 'Bob', 'age': 25, 'city': 'LA'})
///
/// # Search with query
/// results = db.search(Query().age > 25)
/// assert len(results) == 1
/// assert results[0]['name'] == 'Alice'
///
/// # Complex query
/// results = db.search((Query().age > 20) & (Query().city == 'NYC'))
/// assert len(results) == 1
/// ```
#[pyclass(module = "_tinydb_core")]
pub struct Query {
    /// Current field path being built
    path: Vec<String>,
    /// Condition tree (None while building path, Some when condition is complete)
    pub(crate) condition: Option<Condition>,  // pub(crate) to allow direct access from table.rs via PyRef
}

#[pymethods]
impl Query {
    /// Create a new `Query` instance.
    ///
    /// The query starts with an empty path. Use attribute access or dictionary-style
    /// access to build the field path, then use comparison operators to create conditions.
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust import Query
    ///
    /// # Create empty query
    /// q = Query()
    ///
    /// # Build a query
    /// q = Query().name == "Alice"
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
        Query {
            path: Vec::new(),
            condition: None,
        }
    }

    /// Attribute access for building field paths: `Query().field`.
    ///
    /// This method enables the fluent API for accessing nested fields. Each call
    /// appends a field name to the current path.
    ///
    /// # Arguments
    ///
    /// * `name` - The field name to access
    ///
    /// # Returns
    ///
    /// A new `Query` instance with the field name appended to the path.
    ///
    /// # Examples
    ///
    /// ```python
    /// from tinydb_rust import Query
    ///
    /// # Access top-level field
    /// q = Query().name
    ///
    /// # Access nested field
    /// q = Query().user.profile.name
    /// ```
    ///
    /// # Panics
    ///
    /// This function does not panic.
    fn __getattr__(&self, name: &str) -> Self {
        let mut new_path = self.path.clone();
        new_path.push(name.to_string());
        Query {
            path: new_path,
            condition: None,
        }
    }

    /// Get item (dictionary-style access)
    ///
    /// This allows Query()['field'] syntax, which builds the path.
    fn __getitem__(&self, key: &Bound<'_, PyAny>) -> PyResult<Self> {
        let key_str: String = key.extract()?;
        let mut new_path = self.path.clone();
        new_path.push(key_str);
        Ok(Query {
            path: new_path,
            condition: None,
        })
    }

    /// Equality operator: ==
    fn __eq__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let value = convert_pyobject_to_json(other)?;
        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Eq {
                path: self.path.clone(),
                value,
            }),
        })
    }

    /// Not equal operator: !=
    fn __ne__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let value = convert_pyobject_to_json(other)?;
        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Ne {
                path: self.path.clone(),
                value,
            }),
        })
    }

    /// Less than operator: <
    fn __lt__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let value = convert_pyobject_to_json(other)?;
        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Lt {
                path: self.path.clone(),
                value,
            }),
        })
    }

    /// Less than or equal operator: <=
    fn __le__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let value = convert_pyobject_to_json(other)?;
        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Le {
                path: self.path.clone(),
                value,
            }),
        })
    }

    /// Greater than operator: >
    fn __gt__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let value = convert_pyobject_to_json(other)?;
        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Gt {
                path: self.path.clone(),
                value,
            }),
        })
    }

    /// Greater than or equal operator: >=
    fn __ge__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let value = convert_pyobject_to_json(other)?;
        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Ge {
                path: self.path.clone(),
                value,
            }),
        })
    }

    /// Logical AND operator: &
    fn __and__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let self_condition = self.condition.as_ref().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Left operand must be a complete query condition",
            )
        })?;

        // Try to extract condition from other Query object
        let other_query = other.extract::<PyRef<Query>>()
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Right operand must be a Query instance",
            ))?;
        
        let other_condition = other_query.condition.as_ref().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Right operand must be a complete query condition",
            )
        })?.clone();

        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::And {
                left: Box::new(self_condition.clone()),
                right: Box::new(other_condition),
            }),
        })
    }

    /// Logical OR operator: |
    fn __or__(&self, other: &Bound<'_, PyAny>) -> PyResult<Self> {
        let self_condition = self.condition.as_ref().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Left operand must be a complete query condition",
            )
        })?;

        // Try to extract condition from other Query object
        let other_query = other.extract::<PyRef<Query>>()
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Right operand must be a Query instance",
            ))?;
        
        let other_condition = other_query.condition.as_ref().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Right operand must be a complete query condition",
            )
        })?.clone();

        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Or {
                left: Box::new(self_condition.clone()),
                right: Box::new(other_condition),
            }),
        })
    }

    /// Logical NOT operator: ~
    fn __invert__(&self) -> PyResult<Self> {
        let condition = self.condition.as_ref().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Query must be a complete condition to invert",
            )
        })?;

        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Not {
                condition: Box::new(condition.clone()),
            }),
        })
    }

    /// Call operator: query(document) -> bool
    ///
    /// This allows the query to be used as a callable, evaluating
    /// the condition against a document.
    fn __call__(&self, py: Python<'_>, document: &Bound<'_, PyDict>) -> PyResult<bool> {
        let condition = self.condition.as_ref().ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Query must be a complete condition to evaluate",
            )
        })?;

        // Convert document to JSON value
        let doc_value = convert_pydict_to_json(document)?;

        // Evaluate condition
        evaluate_condition(py, condition, &doc_value)
    }

    /// Check if field exists
    fn exists(&self) -> Self {
        Query {
            path: Vec::new(),
            condition: Some(Condition::Exists {
                path: self.path.clone(),
            }),
        }
    }

    /// Match field against regex pattern
    fn matches(&self, pattern: &str) -> Self {
        Query {
            path: Vec::new(),
            condition: Some(Condition::Matches {
                path: self.path.clone(),
                pattern: pattern.to_string(),
            }),
        }
    }

    /// Search field for regex pattern
    fn search(&self, pattern: &str) -> Self {
        Query {
            path: Vec::new(),
            condition: Some(Condition::Search {
                path: self.path.clone(),
                pattern: pattern.to_string(),
            }),
        }
    }

    /// Test field with a Python function
    fn test(&self, _py: Python<'_>, func: &Bound<'_, PyAny>) -> PyResult<Self> {
        // Verify that func is callable
        if !func.is_callable() {
            return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "test() requires a callable function",
            ));
        }

        Ok(Query {
            path: Vec::new(),
            condition: Some(Condition::Test {
                path: self.path.clone(),
                func: func.clone().unbind(),
            }),
        })
    }

    /// String representation for debugging
    fn __repr__(&self) -> String {
        if let Some(ref condition) = self.condition {
            format!("Query({:?})", condition)
        } else if !self.path.is_empty() {
            format!("Query(path: {:?})", self.path)
        } else {
            "Query()".to_string()
        }
    }

    /// Hash implementation for use as cache key
    fn __hash__(&self, py: Python<'_>) -> PyResult<u64> {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        if let Some(ref condition) = self.condition {
            hash_condition(&mut hasher, py, condition)?;
        } else {
            // Hash the path
            self.path.hash(&mut hasher);
        }
        Ok(hasher.finish())
    }
}

// Note: condition field is now pub(crate) to allow direct access from table.rs via PyRef
// No need for get_condition() method anymore

/// Evaluate a query condition against a document.
///
/// This is the core query evaluation function that recursively traverses the
/// condition tree and determines whether a document matches the query.
///
/// # Arguments
///
/// * `py` - Python interpreter instance (required for calling Python test functions)
/// * `condition` - The condition tree to evaluate
/// * `doc` - The document to evaluate against (as a `serde_json::Value`)
///
/// # Returns
///
/// `true` if the document matches the condition, `false` otherwise.
///
/// # Examples
///
/// This function is typically called internally by [`Table::search`](crate::table::Table::search),
/// but can be used directly for custom query evaluation:
///
/// ```python
/// from tinydb_rust import Query
/// import json
///
/// # Create a query
/// query = Query().age > 25
///
/// # Evaluate against a document
/// doc = {'name': 'Alice', 'age': 30}
/// # (evaluation happens internally in Table.search)
/// ```
///
/// # Errors
///
/// Returns `PyErr` if:
/// - A field path cannot be resolved (field doesn't exist in document)
/// - A Python test function raises an exception
/// - A regex pattern is invalid (for `matches` or `search` operations)
///
/// # Panics
///
/// This function does not panic.
pub fn evaluate_condition(
    py: Python<'_>,
    condition: &Condition,
    doc: &Value,
) -> PyResult<bool> {
    match condition {
        Condition::Eq { path, value } => {
            // Optimize: for single-field paths, directly access the field without path resolution
            if path.len() == 1 {
                if let Value::Object(map) = doc {
                    Ok(map.get(&path[0]).map_or(false, |doc_value| doc_value == value))
                } else {
                    Ok(false)
                }
            } else {
                // Multi-field path: use path resolution
                Ok(resolve_path_optional_ref(doc, path).map_or(false, |doc_value| doc_value == value))
            }
        }
        Condition::Ne { path, value } => {
            if path.len() == 1 {
                if let Value::Object(map) = doc {
                    Ok(map.get(&path[0]).map_or(false, |doc_value| doc_value != value))
                } else {
                    Ok(false)
                }
            } else {
                Ok(resolve_path_optional_ref(doc, path).map_or(false, |doc_value| doc_value != value))
            }
        }
        Condition::Lt { path, value } => {
            let doc_value = if path.len() == 1 {
                if let Value::Object(map) = doc {
                    map.get(&path[0])
                } else {
                    None
                }
            } else {
                resolve_path_optional_ref(doc, path)
            };
            Ok(doc_value.map_or(false, |dv| compare_json_values(dv, value) == Some(std::cmp::Ordering::Less)))
        }
        Condition::Le { path, value } => {
            let doc_value = if path.len() == 1 {
                if let Value::Object(map) = doc {
                    map.get(&path[0])
                } else {
                    None
                }
            } else {
                resolve_path_optional_ref(doc, path)
            };
            Ok(doc_value.map_or(false, |dv| {
                matches!(compare_json_values(dv, value), Some(std::cmp::Ordering::Less | std::cmp::Ordering::Equal))
            }))
        }
        Condition::Gt { path, value } => {
            let doc_value = if path.len() == 1 {
                if let Value::Object(map) = doc {
                    map.get(&path[0])
                } else {
                    None
                }
            } else {
                resolve_path_optional_ref(doc, path)
            };
            Ok(doc_value.map_or(false, |dv| compare_json_values(dv, value) == Some(std::cmp::Ordering::Greater)))
        }
        Condition::Ge { path, value } => {
            let doc_value = if path.len() == 1 {
                if let Value::Object(map) = doc {
                    map.get(&path[0])
                } else {
                    None
                }
            } else {
                resolve_path_optional_ref(doc, path)
            };
            Ok(doc_value.map_or(false, |dv| {
                matches!(compare_json_values(dv, value), Some(std::cmp::Ordering::Greater | std::cmp::Ordering::Equal))
            }))
        }
        Condition::And { left, right } => {
            let left_result = evaluate_condition(py, left, doc)?;
            if !left_result {
                return Ok(false);
            }
            evaluate_condition(py, right, doc)
        }
        Condition::Or { left, right } => {
            let left_result = evaluate_condition(py, left, doc)?;
            if left_result {
                return Ok(true);
            }
            evaluate_condition(py, right, doc)
        }
        Condition::Not { condition } => {
            let result = evaluate_condition(py, condition, doc)?;
            Ok(!result)
        }
        Condition::Exists { path } => {
            Ok(resolve_path_optional_ref(doc, path).is_some())
        }
        Condition::Matches { path, pattern } => {
            let doc_value = match resolve_path_optional_ref(doc, path) {
                Some(Value::String(s)) => s,
                Some(_) => return Ok(false),
                None => return Ok(false),
            };
                let re = Regex::new(pattern).map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Invalid regex pattern: {}",
                        e
                    ))
                })?;
                Ok(re.is_match(doc_value))
        }
        Condition::Search { path, pattern } => {
            let doc_value = match resolve_path_optional_ref(doc, path) {
                Some(Value::String(s)) => s,
                Some(_) => return Ok(false),
                None => return Ok(false),
            };
                let re = Regex::new(pattern).map_err(|e| {
                    PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                        "Invalid regex pattern: {}",
                        e
                    ))
                })?;
                Ok(re.find(doc_value).is_some())
        }
        Condition::Test { path, func } => {
            let doc_value = resolve_path_optional_ref(doc, path).cloned();
            let func_bound = func.bind(py);

            // Call Python function with the field value
            let py_value = match doc_value {
                Some(value) => convert_json_value_to_pyobject(py, &value)?,
                None => py.None().into(),
            };
            let result = func_bound.call1((py_value,))?;
            result.extract::<bool>()
        }
    }
}

/// Resolve a path in a JSON value
///
/// Returns the value at the given path, or an error if the path doesn't exist.
#[allow(dead_code)]
fn resolve_path(doc: &Value, path: &[String]) -> PyResult<Value> {
    let mut current = doc;

    for segment in path {
        match current {
            Value::Object(map) => {
                current = map.get(segment).ok_or_else(|| {
                    PyErr::new::<pyo3::exceptions::PyKeyError, _>(format!(
                        "Field '{}' not found",
                        segment
                    ))
                })?;
            }
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "Cannot access '{}' on non-object value",
                    segment
                )));
            }
        }
    }

    Ok(current.clone())
}

/// Resolve a path in a JSON value (optional)
///
/// Returns Some(value) if the path exists, None otherwise.
fn resolve_path_optional(doc: &Value, path: &[String]) -> Option<Value> {
    let mut current = doc;

    for segment in path {
        match current {
            Value::Object(map) => {
                current = map.get(segment)?;
            }
            _ => return None,
        }
    }

    Some(current.clone())
}

/// Resolve a path in a JSON value (optional, returns reference)
///
/// Returns Some(reference) if the path exists, None otherwise.
/// This avoids cloning for simple comparisons.
fn resolve_path_optional_ref<'a>(doc: &'a Value, path: &[String]) -> Option<&'a Value> {
    let mut current = doc;

    for segment in path {
        match current {
            Value::Object(map) => {
                current = map.get(segment)?;
            }
            _ => return None,
        }
    }

    Some(current)
}

/// Compare two JSON values
fn compare_json_values(a: &Value, b: &Value) -> Option<std::cmp::Ordering> {
    // Handle numeric comparisons
    if let (Some(a_num), Some(b_num)) = (a.as_f64(), b.as_f64()) {
        return a_num.partial_cmp(&b_num);
    }
    if let (Some(a_num), Some(b_num)) = (a.as_i64(), b.as_i64()) {
        return Some(a_num.cmp(&b_num));
    }
    if let (Some(a_num), Some(b_num)) = (a.as_u64(), b.as_u64()) {
        return Some(a_num.cmp(&b_num));
    }
    
    // Try to compare as strings
    if let (Some(a_str), Some(b_str)) = (a.as_str(), b.as_str()) {
        return Some(a_str.cmp(b_str));
    }
    
    // Try to compare as booleans
    if let (Some(a_bool), Some(b_bool)) = (a.as_bool(), b.as_bool()) {
        return Some(a_bool.cmp(&b_bool));
    }
    
    // Types don't match or can't be compared
    None
}

/// Compare two JSON values using a comparison function
fn compare_values<F>(a: &Value, b: &Value, cmp: F) -> PyResult<bool>
where
    F: FnOnce(&Value, &Value) -> bool,
{
    Ok(cmp(a, b))
}

/// Convert a Python object to serde_json::Value
fn convert_pyobject_to_json(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    use pyo3::types::PyList;

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

    // Fallback: convert to string representation
    let repr = obj.repr()?.to_string();
    Ok(Value::String(repr))
}

/// Convert a Python dict to serde_json::Value
fn convert_pydict_to_json(dict: &Bound<'_, PyDict>) -> PyResult<Value> {
    let mut map = serde_json::Map::new();

    for (key, value) in dict.iter() {
        let key_str: String = key.extract()?;
        let json_value = convert_pyobject_to_json(&value)?;
        map.insert(key_str, json_value);
    }

    Ok(Value::Object(map))
}

/// Syntax sugar function for creating queries: `where('field') == value`.
///
/// This function provides a convenient alternative to `Query()[key]` for building
/// queries. It's equivalent to the original TinyDB's `where()` function.
///
/// # Arguments
///
/// * `key` - The field name to query
///
/// # Returns
///
/// A new `Query` instance with the field path set to `[key]`.
///
/// # Examples
///
/// ```python
/// from tinydb_rust import where, TinyDB
///
/// db = TinyDB('db.json')
///
/// # Use where() function
/// results = db.search(where('name') == 'Alice')
/// results = db.search(where('age') > 25)
///
/// # Equivalent to Query()['name'] == 'Alice'
/// from tinydb_rust import Query
/// results = db.search(Query()['name'] == 'Alice')
/// ```
///
/// # Errors
///
/// This function does not return errors.
///
/// # Panics
///
/// This function does not panic.
#[pyfunction]
pub fn where_func(key: &str) -> Query {
    Query {
        path: vec![key.to_string()],
        condition: None,
    }
}

/// Recursively hash a condition tree
fn hash_condition<H: std::hash::Hasher>(
    hasher: &mut H,
    py: Python<'_>,
    condition: &Condition,
) -> PyResult<()> {
    match condition {
        Condition::Eq { path, value } => {
            "Eq".hash(hasher);
            path.hash(hasher);
            hash_json_value(hasher, value)?;
        }
        Condition::Ne { path, value } => {
            "Ne".hash(hasher);
            path.hash(hasher);
            hash_json_value(hasher, value)?;
        }
        Condition::Lt { path, value } => {
            "Lt".hash(hasher);
            path.hash(hasher);
            hash_json_value(hasher, value)?;
        }
        Condition::Le { path, value } => {
            "Le".hash(hasher);
            path.hash(hasher);
            hash_json_value(hasher, value)?;
        }
        Condition::Gt { path, value } => {
            "Gt".hash(hasher);
            path.hash(hasher);
            hash_json_value(hasher, value)?;
        }
        Condition::Ge { path, value } => {
            "Ge".hash(hasher);
            path.hash(hasher);
            hash_json_value(hasher, value)?;
        }
        Condition::And { left, right } => {
            "And".hash(hasher);
            hash_condition(hasher, py, left)?;
            hash_condition(hasher, py, right)?;
        }
        Condition::Or { left, right } => {
            "Or".hash(hasher);
            hash_condition(hasher, py, left)?;
            hash_condition(hasher, py, right)?;
        }
        Condition::Not { condition: cond } => {
            "Not".hash(hasher);
            hash_condition(hasher, py, cond)?;
        }
        Condition::Exists { path } => {
            "Exists".hash(hasher);
            path.hash(hasher);
        }
        Condition::Matches { path, pattern } => {
            "Matches".hash(hasher);
            path.hash(hasher);
            pattern.hash(hasher);
        }
        Condition::Search { path, pattern } => {
            "Search".hash(hasher);
            path.hash(hasher);
            pattern.hash(hasher);
        }
        Condition::Test { path, func } => {
            "Test".hash(hasher);
            path.hash(hasher);
            let func_hash = func.bind(py).hash()? as u64;
            func_hash.hash(hasher);
        }
    }
    Ok(())
}

/// Hash a JSON value for use in query hashing
fn hash_json_value<H: std::hash::Hasher>(hasher: &mut H, value: &Value) -> PyResult<()> {
    match value {
        Value::Null => "null".hash(hasher),
        Value::Bool(b) => b.hash(hasher),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                i.hash(hasher);
            } else if let Some(f) = n.as_f64() {
                // Hash float by converting to string (not perfect but works)
                f.to_string().hash(hasher);
            } else {
                n.to_string().hash(hasher);
            }
        }
        Value::String(s) => s.hash(hasher),
        Value::Array(arr) => {
            for item in arr {
                hash_json_value(hasher, item)?;
            }
        }
        Value::Object(map) => {
            // Sort keys for stable hashing
            let mut keys: Vec<&String> = map.keys().collect();
            keys.sort();
            for key in keys {
                key.hash(hasher);
                hash_json_value(hasher, &map[key])?;
            }
        }
    }
    Ok(())
}

/// Convert a serde_json::Value to a Python object
fn convert_json_value_to_pyobject(py: Python<'_>, value: &Value) -> PyResult<Py<PyAny>> {
    use pyo3::types::{PyBool, PyFloat, PyInt, PyString};

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
                if u <= i64::MAX as u64 {
                    let py_int = Py::from(PyInt::new(py, u as i64));
                    Ok(<Py<PyInt> as Into<Py<PyAny>>>::into(py_int))
                } else {
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
            let list = pyo3::types::PyList::empty(py);
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

