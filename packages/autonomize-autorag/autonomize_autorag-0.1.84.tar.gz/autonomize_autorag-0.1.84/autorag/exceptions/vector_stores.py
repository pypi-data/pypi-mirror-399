"""Exceptions for vector stores."""


class VectorStoreException(Exception):
    """Base exception for vector store errors."""


class VectorStoreClientCreationException(VectorStoreException):
    """Exception raised when Vector Store Client cannot be created"""


class VectorStoreCollectionNotFoundException(VectorStoreException):
    """Exception raised when the collection name is not found in the vector store."""


class VectorStoreCollectionAlreadyExistsException(VectorStoreException):
    """Exception raised when the collection name already exists in the vector store."""


class VectorStoreDataMismatchException(VectorStoreException):
    """Exception raised when the data in the vector store does not match the expected data."""

class VectorStoreTransientException(Exception):
    def __init__(
        self,
        status_code: int,
        exception: str,
    ):
        self.status_code = status_code
        self.exception = exception

class VectorStoreNonTransientException(Exception):
    def __init__(
        self,
        status_code: int,
        exception: str,
    ):
        self.status_code = status_code
        self.exception = exception
