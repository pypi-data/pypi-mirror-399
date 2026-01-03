"""
Operations for TinyDB document updates.

These functions provide transformations for use with the `update` method.
"""

__all__ = ['delete', 'add', 'subtract', 'set', 'increment', 'decrement']


def delete(field: str):
    """
    Delete a given field from the document.
    
    :param field: the field to delete
    """
    def transform(doc):
        del doc[field]
    return transform


def add(field: str, n):
    """
    Add n to a given field in the document.
    
    :param field: the field to add to
    :param n: the value to add (number or string for concatenation)
    """
    def transform(doc):
        doc[field] += n
    return transform


def subtract(field: str, n):
    """
    Subtract n from a given field in the document.
    
    :param field: the field to subtract from
    :param n: the value to subtract
    """
    def transform(doc):
        doc[field] -= n
    return transform


def set(field: str, val):
    """
    Set a given field to a given value in the document.
    
    :param field: the field to set
    :param val: the value to set it to
    """
    def transform(doc):
        doc[field] = val
    return transform


def increment(field: str):
    """
    Increment a given field in the document by 1.
    
    :param field: the field to increment
    """
    def transform(doc):
        doc[field] += 1
    return transform


def decrement(field: str):
    """
    Decrement a given field in the document by 1.
    
    :param field: the field to decrement
    """
    def transform(doc):
        doc[field] -= 1
    return transform

