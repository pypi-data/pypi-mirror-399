"""
TinyDB Rust implementation

TinyDB is a tiny, document oriented database optimized for your happiness :)

This is a Rust-based reimplementation of TinyDB that provides high performance
and memory safety while maintaining compatibility with the original TinyDB API.
"""

from . import utils
from ._tinydb_core import JSONStorage, MemoryStorage, TinyDB
from .queries import Query, where
from .table import Document

__all__ = [
    "utils",
    "TinyDB",
    "Query",
    "where",
    "Document",
    "JSONStorage",
    "MemoryStorage",
]

# Version compatibility
__version__ = "0.9.0"
