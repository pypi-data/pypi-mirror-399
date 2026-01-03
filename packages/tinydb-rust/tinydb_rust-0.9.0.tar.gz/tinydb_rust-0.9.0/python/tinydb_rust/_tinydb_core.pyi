"""TinyDB Rust implementation

TinyDB is a tiny, document oriented database optimized for your happiness :)

This is a Rust-based reimplementation of TinyDB that provides high performance
and memory safety while maintaining compatibility with the original TinyDB API.
"""

from typing import Any, Callable, Iterator, Mapping, MutableMapping, Optional, Protocol, Union

# Document type: dict with doc_id attribute (defined in table.py)
Document = dict[str, Any]


class LRUCache(MutableMapping[Any, Any]):
    """LRU Cache implementation compatible with Python's TinyDB utils.LRUCache

    A least-recently used (LRU) cache with a fixed cache size.
    This class acts as a dictionary but has a limited size. If the number of
    entries in the cache exceeds the cache size, the least-recently accessed
    entry will be discarded.
    """

    @property
    def lru(self) -> list[Any]:
        """Get the list of keys in LRU order (least recently used first)."""
        ...

    @property
    def length(self) -> int:
        """Get the current length of the cache."""
        ...

    def __init__(self, capacity: Optional[int] = None) -> None:
        """Create a new LRUCache with optional capacity.

        If capacity is None, the cache has unlimited size.
        """
        ...

    def clear(self) -> None:
        """Clear all entries from the cache."""
        ...

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        """Get a value from the cache, returning default if key is not found.

        Accessing a key moves it to the most recently used position.
        """
        ...

    def set(self, key: Any, value: Any) -> None:
        """Set a key-value pair in the cache.

        If the cache is full, the least recently used item will be removed.
        """
        ...

    def __getitem__(self, key: Any) -> Any:
        ...

    def __setitem__(self, key: Any, value: Any) -> None:
        ...

    def __delitem__(self, key: Any) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __contains__(self, key: Any) -> bool:
        ...

    def __iter__(self) -> Iterator[Any]:
        ...


class FrozenDict(Mapping[Any, Any]):
    """FrozenDict - An immutable dictionary that can be hashed

    This is used to generate stable hashes for queries that contain dicts.
    Usually, Python dicts are not hashable because they are mutable. This
    class removes the mutability and implements the __hash__ method.
    """

    def __init__(self, dict: dict[Any, Any]) -> None:
        """Create a new FrozenDict from a dictionary."""
        ...

    def __hash__(self) -> int:
        ...

    def __getitem__(self, key: Any) -> Any:
        ...

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        """Get item with default value."""
        ...

    def __contains__(self, key: Any) -> bool:
        ...

    def __len__(self) -> int:
        ...

    def keys(self) -> Iterator[Any]:
        ...

    def values(self) -> Iterator[Any]:
        ...

    def items(self) -> Iterator[tuple[Any, Any]]:
        ...


def freeze(obj: Any) -> Any:
    """Freeze an object by making it immutable and thus hashable.

    This function recursively processes objects:
    - dict -> FrozenDict
    - list -> tuple
    - set -> frozenset
    - Other objects remain unchanged
    """
    ...


class JSONStorage:
    """Persistent storage backend that stores database state in a JSON file on disk.

    This is the default storage backend for TinyDB. All file I/O operations are
    performed using Rust's standard library for optimal performance and reliability.
    """

    def __init__(
        self,
        path: Union[str, bytes, Any],
        *,
        create_dirs: bool = False,
        encoding: Optional[str] = None,
        access_mode: str = "r+",
        **kwargs: Any
    ) -> None:
        """Create a new JSONStorage instance.

        :param path: Path to the JSON file
        :param create_dirs: If True, create parent directories if they don't exist
        :param encoding: File encoding (kept for compatibility)
        :param access_mode: File access mode ('r', 'r+', 'rb', 'rb+')
        :param **kwargs: Additional JSON serialization options (indent, sort_keys, etc.)
        """
        ...

    def read(self) -> Optional[dict[str, dict[str, Any]]]:
        """Read the current database state from the JSON file.

        :returns: The database state as a dict, or None if file is empty
        """
        ...

    def write(self, data: dict[str, dict[str, Any]]) -> None:
        """Write the database state to the JSON file.

        :param data: The database state as a dict
        """
        ...

    def close(self) -> None:
        """Close the storage and release file handle."""
        ...


class MemoryStorage:
    """In-memory storage backend that stores database state in RAM.

    This storage backend is useful for testing, temporary databases, or when
    persistence is not required. Data is lost when the MemoryStorage instance
    is destroyed or the process exits.
    """

    def __init__(self) -> None:
        """Create a new MemoryStorage instance."""
        ...

    def read(self) -> Optional[dict[str, dict[str, Any]]]:
        """Read the current database state from memory.

        :returns: The database state as a dict, or None if no data has been written
        """
        ...

    def write(self, data: dict[str, dict[str, Any]]) -> None:
        """Write the database state to memory.

        :param data: The database state as a dict
        """
        ...

    def close(self) -> None:
        """Close the storage (no-op for memory storage)."""
        ...


class QueryLike(Protocol):
    """Protocol for query-like objects that can be called to test documents."""

    def __call__(self, value: Mapping[str, Any]) -> bool:
        """Evaluate the query against a document."""
        ...

    def __hash__(self) -> int:
        """Hash implementation for use as cache key."""
        ...


class Query:
    """Query builder for constructing and evaluating database queries.

    This class provides a fluent API for building queries that matches the original
    TinyDB syntax. Queries are built by chaining field access and comparison operations,
    then combined with logical operators (&, |, ~).
    """

    def __init__(self) -> None:
        """Create a new Query instance."""
        ...

    def __getattr__(self, name: str) -> "Query":
        """Attribute access for building field paths: Query().field"""
        ...

    def __getitem__(self, key: str) -> "Query":
        """Dictionary-style access for building field paths: Query()['field']"""
        ...

    def __eq__(self, other: Any) -> QueryLike:
        """Equality operator: Query().field == value"""
        ...

    def __ne__(self, other: Any) -> QueryLike:
        """Inequality operator: Query().field != value"""
        ...

    def __lt__(self, other: Any) -> QueryLike:
        """Less than operator: Query().field < value"""
        ...

    def __le__(self, other: Any) -> QueryLike:
        """Less than or equal operator: Query().field <= value"""
        ...

    def __gt__(self, other: Any) -> QueryLike:
        """Greater than operator: Query().field > value"""
        ...

    def __ge__(self, other: Any) -> QueryLike:
        """Greater than or equal operator: Query().field >= value"""
        ...

    def __and__(self, other: QueryLike) -> QueryLike:
        """AND operator: (Query().field1 == value1) & (Query().field2 == value2)"""
        ...

    def __or__(self, other: QueryLike) -> QueryLike:
        """OR operator: (Query().field1 == value1) | (Query().field2 == value2)"""
        ...

    def __invert__(self) -> QueryLike:
        """NOT operator: ~(Query().field == value)"""
        ...

    def exists(self) -> QueryLike:
        """Check if field exists: Query().field.exists()"""
        ...

    def matches(self, pattern: str) -> QueryLike:
        """Regex match (full match): Query().field.matches(pattern)"""
        ...

    def search(self, pattern: str) -> QueryLike:
        """Regex search (partial match): Query().field.search(pattern)"""
        ...

    def test(self, func: Callable[[Any], bool]) -> QueryLike:
        """Custom test function: Query().field.test(lambda x: x > 10)"""
        ...

    def __call__(self, doc: Mapping[str, Any]) -> bool:
        """Evaluate the query against a document."""
        ...

    def __repr__(self) -> str:
        ...

    def __hash__(self) -> int:
        ...


def where(key: str) -> Query:
    """Convenience function for building queries: where('field') == value

    This function provides a convenient alternative to Query()[key] for building
    queries. It's equivalent to the original TinyDB's where() function.

    :param key: The field name to query
    :returns: A new Query instance with the field path set to [key]
    """
    ...


class Table:
    """Table represents a single TinyDB table.

    It provides methods for accessing and manipulating documents.
    All core logic is implemented in Rust for performance and type safety.
    """

    def __init__(
        self,
        storage: Any,
        name: str,
        *,
        cache_size: int = 10,
        persist_empty: bool = False
    ) -> None:
        """Create a new Table instance.

        :param storage: The storage instance to use for this table
        :param name: The table name
        :param cache_size: Maximum capacity of query cache (default: 10)
        :param persist_empty: Store new table even with no operations on it
        """
        ...

    @property
    def name(self) -> str:
        """Get the table name."""
        ...

    def insert(self, document: Union[dict[str, Any], Document]) -> int:
        """Insert a new document into the table.

        :param document: The document to insert (dict or Document with doc_id)
        :returns: The inserted document's ID
        """
        ...

    def insert_multiple(
        self, documents: Union[list[dict[str, Any]], Iterator[dict[str, Any]]]
    ) -> list[int]:
        """Insert multiple documents into the table.

        :param documents: An iterable of documents to insert
        :returns: A list containing the inserted documents' IDs
        """
        ...

    def all(self) -> list[Document]:
        """Get all documents stored in the table.

        :returns: A list with all documents as Document objects
        """
        ...

    def search(self, query: QueryLike) -> list[Document]:
        """Search for documents matching a query.

        :param query: The query condition
        :returns: A list of matching documents as Document objects
        """
        ...

    def get(
        self,
        cond: Optional[QueryLike] = None,
        doc_id: Optional[int] = None,
        *,
        cache: Optional[Any] = None
    ) -> Optional[Document]:
        """Get a single document matching a query or document ID.

        :param cond: Query condition
        :param doc_id: Document ID
        :param cache: Query cache (internal use)
        :returns: The matching document as a Document object, or None
        """
        ...

    def contains(self, cond: Optional[QueryLike] = None, doc_id: Optional[int] = None) -> bool:
        """Check if the table contains a document matching a query or document ID.

        :param cond: Query condition
        :param doc_id: Document ID
        :returns: True if a matching document exists, False otherwise
        """
        ...

    def count(self, query: QueryLike) -> int:
        """Count the number of documents matching a query.

        :param query: The query condition
        :returns: The number of matching documents
        """
        ...

    def update(
        self,
        fields: Union[dict[str, Any], Callable[[dict[str, Any]], None]],
        cond: Optional[QueryLike] = None,
        doc_ids: Optional[list[int]] = None
    ) -> list[int]:
        """Update all matching documents to have a given set of fields.

        :param fields: The fields that the matching documents will have (dict or callable)
        :param cond: Query condition
        :param doc_ids: A list of document IDs
        :returns: A list containing the updated documents' IDs
        """
        ...

    def update_multiple(
        self, updates: list[tuple[dict[str, Any], QueryLike]]
    ) -> list[int]:
        """Update multiple documents with different values.

        :param updates: A sequence of (fields, condition) pairs
        :returns: A list containing the updated documents' IDs
        """
        ...

    def upsert(
        self, document: dict[str, Any], cond: Optional[QueryLike] = None
    ) -> list[int]:
        """Update documents matching a query or insert a document.

        :param document: The document to insert or update with
        :param cond: Query condition
        :returns: A list containing the updated/inserted document IDs
        """
        ...

    def remove(
        self, cond: Optional[QueryLike] = None, doc_ids: Optional[list[int]] = None
    ) -> list[int]:
        """Remove all matching documents from the table.

        :param cond: Query condition
        :param doc_ids: A list of document IDs
        :returns: A list containing the removed documents' IDs
        """
        ...

    def truncate(self) -> None:
        """Remove all documents from the table."""
        ...

    def clear_cache(self) -> None:
        """Clear the query cache and table cache."""
        ...

    def __len__(self) -> int:
        """Get the total number of documents in this table."""
        ...

    def __iter__(self) -> Iterator[Document]:
        """Make the table iterable."""
        ...

    def __repr__(self) -> str:
        ...


class TinyDB:
    """TinyDB is the main entry point for the database.

    It manages tables and storage instances, providing a high-level API
    for database operations. All core logic is implemented in Rust.
    """

    def __init__(
        self,
        *args: Any,
        storage: Optional[Union[JSONStorage, MemoryStorage, Any]] = None,
        default_table: str = "_default",
        **kwargs: Any
    ) -> None:
        """Create a new TinyDB instance.

        :param *args: Positional arguments (first arg is treated as path if storage is None)
        :param storage: Storage instance or class (default: JSONStorage)
        :param default_table: Name of the default table (default: "_default")
        :param **kwargs: Additional arguments passed to storage constructor
        """
        ...

    def table(self, name: Optional[str] = None, **kwargs: Any) -> Table:
        """Get or create a table with the given name.

        :param name: The table name (default: uses default_table)
        :param **kwargs: Additional arguments passed to Table constructor
        :returns: The Table instance
        """
        ...

    def tables(self) -> set[str]:
        """Get a set of all table names in the database.

        :returns: A set of table names
        """
        ...

    def drop_table(self, name: str) -> None:
        """Drop a table from the database.

        :param name: The name of the table to drop
        """
        ...

    def drop_tables(self) -> None:
        """Drop all tables from the database."""
        ...

    def insert(self, document: dict[str, Any]) -> int:
        """Insert a new document into the default table.

        :param document: The document to insert
        :returns: The inserted document's ID
        """
        ...

    def insert_multiple(
        self, documents: Union[list[dict[str, Any]], Iterator[dict[str, Any]]]
    ) -> list[int]:
        """Insert multiple documents into the default table.

        :param documents: An iterable of documents to insert
        :returns: A list containing the inserted documents' IDs
        """
        ...

    def all(self) -> list[Document]:
        """Get all documents from the default table.

        :returns: A list of all documents
        """
        ...

    def search(self, query: QueryLike) -> list[Document]:
        """Search for documents in the default table matching a query.

        :param query: The query condition
        :returns: A list of matching documents
        """
        ...

    def get(
        self,
        cond: Optional[QueryLike] = None,
        doc_id: Optional[int] = None,
        *,
        cache: Optional[Any] = None
    ) -> Optional[Document]:
        """Get a single document from the default table.

        :param cond: Query condition
        :param doc_id: Document ID
        :param cache: Query cache (internal use)
        :returns: The matching document, or None
        """
        ...

    def contains(self, cond: Optional[QueryLike] = None, doc_id: Optional[int] = None) -> bool:
        """Check if the default table contains a document.

        :param cond: Query condition
        :param doc_id: Document ID
        :returns: True if a matching document exists, False otherwise
        """
        ...

    def count(self, query: QueryLike) -> int:
        """Count the number of documents in the default table matching a query.

        :param query: The query condition
        :returns: The number of matching documents
        """
        ...

    def update(
        self,
        fields: Union[dict[str, Any], Callable[[dict[str, Any]], None]],
        cond: Optional[QueryLike] = None,
        doc_ids: Optional[list[int]] = None
    ) -> list[int]:
        """Update documents in the default table.

        :param fields: The fields that the matching documents will have (dict or callable)
        :param cond: Query condition
        :param doc_ids: A list of document IDs
        :returns: A list containing the updated documents' IDs
        """
        ...

    def update_multiple(
        self, updates: list[tuple[dict[str, Any], QueryLike]]
    ) -> list[int]:
        """Update multiple documents in the default table.

        :param updates: A sequence of (fields, condition) pairs
        :returns: A list containing the updated documents' IDs
        """
        ...

    def upsert(self, document: dict[str, Any], cond: Optional[QueryLike] = None) -> list[int]:
        """Update documents in the default table or insert a document.

        :param document: The document to insert or update with
        :param cond: Query condition
        :returns: A list containing the updated/inserted document IDs
        """
        ...

    def remove(
        self, cond: Optional[QueryLike] = None, doc_ids: Optional[list[int]] = None
    ) -> list[int]:
        """Remove documents from the default table.

        :param cond: Query condition
        :param doc_ids: A list of document IDs
        :returns: A list containing the removed documents' IDs
        """
        ...

    def truncate(self) -> None:
        """Remove all documents from the default table."""
        ...

    def close(self) -> None:
        """Close the database and release resources."""
        ...

    @property
    def default_table_name(self) -> str:
        """Get the default table name."""
        ...

    @property
    def storage(self) -> Union[JSONStorage, MemoryStorage, Any]:
        """Get the storage instance."""
        ...

    def __len__(self) -> int:
        """Get the total number of documents in the default table."""
        ...

    def __iter__(self) -> Iterator[Document]:
        """Make TinyDB iterable (iterate over default table)."""
        ...

    def __repr__(self) -> str:
        ...

    def __enter__(self) -> "TinyDB":
        """Enter the context manager."""
        ...

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any]
    ) -> bool:
        """Exit the context manager.

        :returns: False to not suppress exceptions
        """
        ...
