"""
AntPorter - A simple tool for splitting and merging files.

This package provides utilities to split large files into smaller chunks
and merge them back, useful for bypassing file size limits in HPC clusters.
"""

__version__ = "1.0.2"
__author__ = "AntPorter Team"

from .splitter import FileSplitter
from .merger import FileMerger
from .metadata import MetadataManager

__all__ = ["FileSplitter", "FileMerger", "MetadataManager"]

