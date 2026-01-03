//! # TinyDB Rust Implementation
//!
//! A high-performance, memory-safe Rust reimplementation of [TinyDB](https://tinydb.readthedocs.io/),
//! a lightweight document-oriented database optimized for developer happiness.
//!
//! ## Overview
//!
//! This crate provides a complete Rust implementation of TinyDB's core functionality,
//! exposed to Python through PyO3 bindings. All database operations, query evaluation,
//! and storage I/O are implemented in Rust for maximum performance and type safety.
//!
//! ## Key Features
//!
//! - **100% API Compatible**: Drop-in replacement for the original TinyDB Python library
//! - **High Performance**: Core logic implemented in Rust for optimal speed
//! - **Memory Safe**: Leverages Rust's ownership system to prevent common bugs
//! - **Type Safe**: Strong typing throughout the Rust implementation
//! - **Thread Safe**: Safe concurrent access using Rust's concurrency primitives
//!
//! ## Architecture
//!
//! The library is organized into several core modules:
//!
//! - [`database`](database::TinyDB): Main database entry point, manages tables and storage
//! - [`table`](table::Table): Table operations (CRUD, queries, caching)
//! - [`query`](query::Query): Query engine for filtering and matching documents
//! - [`storage`](storage): Storage backends (JSON file, in-memory)
//! - [`utils`](utils): Utility functions (LRU cache, object freezing)
//!
//! ## Python Integration
//!
//! This module is exposed to Python as `_tinydb_core` and provides all core classes
//! and functions. The Python package `tinydb_rust` wraps these with additional
//! syntax sugar and compatibility layers.
//!
//! ## Example Usage (Python)
//!
//! ```python
//! from tinydb_rust import TinyDB, Query
//!
//! # Create a database
//! db = TinyDB('db.json')
//!
//! # Insert documents
//! db.insert({'name': 'Alice', 'age': 30})
//! db.insert({'name': 'Bob', 'age': 25})
//!
//! # Query documents
//! results = db.search(Query().age > 25)
//! print(results)  # [{'name': 'Alice', 'age': 30, 'doc_id': 1}]
//! ```

use pyo3::prelude::*;

mod utils;
mod storage;
mod table;
mod query;
mod database;

use utils::{freeze, FrozenDict, LRUCache};
use storage::{JSONStorage, MemoryStorage};
use table::Table;
use query::{Query, where_func};
use database::TinyDB;

/// PyO3 module entry point for TinyDB Rust implementation.
///
/// This function registers all public classes and functions with Python,
/// making them available to Python code through the `_tinydb_core` module.
///
/// # Registered Components
///
/// - **Classes**: [`LRUCache`](utils::LRUCache), [`FrozenDict`](utils::FrozenDict),
///   [`JSONStorage`](storage::JSONStorage), [`MemoryStorage`](storage::MemoryStorage),
///   [`Table`](table::Table), [`Query`](query::Query), [`TinyDB`](database::TinyDB)
/// - **Functions**: [`freeze`](utils::freeze), [`where_func`](query::where_func)
///
/// # Errors
///
/// Returns `PyErr` if any class or function registration fails.
///
/// # Examples
///
/// This function is automatically called by PyO3 when the module is imported:
///
/// ```python
/// import _tinydb_core
/// # All classes and functions are now available
/// ```
#[pymodule]
fn _tinydb_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<LRUCache>()?;
    m.add_class::<FrozenDict>()?;
    m.add_function(wrap_pyfunction!(freeze, m)?)?;
    m.add_class::<JSONStorage>()?;
    m.add_class::<MemoryStorage>()?;
    m.add_class::<Table>()?;
    m.add_class::<Query>()?;
    m.add_function(wrap_pyfunction!(where_func, m)?)?;
    m.add_class::<TinyDB>()?;
    Ok(())
}
