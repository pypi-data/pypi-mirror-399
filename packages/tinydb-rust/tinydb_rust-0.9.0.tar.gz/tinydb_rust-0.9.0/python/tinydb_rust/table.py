"""
Table and Document classes for TinyDB.

This module provides the Document class that wraps dictionary data with a doc_id.
The actual Table implementation is in Rust.
"""

from typing import Mapping

__all__ = ['Document']


class Document(dict):
    """
    A document stored in the database.

    This class provides a way to access both a document's content and
    its ID using ``doc.doc_id``.
    
    Documents are essentially dictionaries with an additional ``doc_id`` attribute
    that uniquely identifies them within a table.
    """

    def __init__(self, value: Mapping, doc_id: int):
        """
        Create a new Document.

        :param value: The document data (a mapping/dict)
        :param doc_id: The document's unique identifier
        """
        super().__init__(value)
        self.doc_id = doc_id

    def __repr__(self) -> str:
        return f'Document({dict(self)}, doc_id={self.doc_id})'

