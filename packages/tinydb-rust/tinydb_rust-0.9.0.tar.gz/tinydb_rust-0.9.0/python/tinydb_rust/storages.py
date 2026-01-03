"""
Storage backends for TinyDB.

This module provides storage classes and utilities that wrap the Rust implementation
for API compatibility with the original TinyDB.
"""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ._tinydb_core import JSONStorage, MemoryStorage

__all__ = ['Storage', 'JSONStorage', 'MemoryStorage', 'touch']


class Storage(ABC):
    """
    The abstract base class for all Storages.

    A Storage (de-)serializes the current state of the database and stores it in
    some place (memory, file on disk, ...).

    This is an abstract class that defines the interface for storage backends.
    The actual implementations (JSONStorage, MemoryStorage) are in Rust.
    """

    @abstractmethod
    def read(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Read the current state.

        Any kind of deserialization should go here.

        :return: the saved data (if any), None otherwise
        """
        raise NotImplementedError('To be overridden!')

    @abstractmethod
    def write(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Write the current state of the database to the storage.

        Any kind of serialization should go here.

        :param data: the current state of the database
        """
        raise NotImplementedError('To be overridden!')

    def close(self) -> None:
        """
        Optional: close open file handles.

        This is called when the database is closed.
        """
        pass


def touch(path: str, create_dirs: bool) -> None:
    """
    Create a file if it doesn't exist yet.

    :param path: the file path
    :param create_dirs: whether to create all missing parent directories
    """
    if create_dirs:
        base_dir = os.path.dirname(path)
        if base_dir:
            os.makedirs(base_dir, exist_ok=True)

    # Create the file by opening it in 'a' mode
    with open(path, 'a'):
        pass

