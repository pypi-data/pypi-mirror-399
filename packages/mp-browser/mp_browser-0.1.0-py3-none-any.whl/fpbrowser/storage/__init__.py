"""Storage modules."""

from .s3 import S3Storage
from .local import LocalStorage

__all__ = ["S3Storage", "LocalStorage"]
