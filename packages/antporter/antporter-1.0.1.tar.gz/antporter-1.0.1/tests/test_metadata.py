"""
Tests for metadata management.
"""

import json
import tempfile
from pathlib import Path
import pytest

from antporter.metadata import MetadataManager


class TestMetadataManager:
    """Tests for MetadataManager class."""
    
    def test_create_metadata(self, tmp_path):
        """Test creating metadata."""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Create metadata
        manager = MetadataManager()
        chunks = [
            {"index": 1, "filename": "test.txt.part001", "size": 13, "md5": "abc123"}
        ]
        
        metadata = manager.create_metadata(
            original_file=test_file,
            original_md5="def456",
            chunk_size=1024,
            chunks=chunks
        )
        
        assert metadata["original_filename"] == "test.txt"
        assert metadata["original_size"] == 13
        assert metadata["original_md5"] == "def456"
        assert metadata["chunk_size"] == 1024
        assert metadata["chunk_count"] == 1
        assert len(metadata["chunks"]) == 1
        assert metadata["version"] == "1.0"
    
    def test_save_and_load(self, tmp_path):
        """Test saving and loading metadata."""
        # Create metadata
        manager = MetadataManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")
        
        chunks = [
            {"index": 1, "filename": "test.txt.part001", "size": 4, "md5": "abc"}
        ]
        
        manager.create_metadata(
            original_file=test_file,
            original_md5="def",
            chunk_size=1024,
            chunks=chunks
        )
        
        # Save metadata
        metadata_path = tmp_path / "test.meta.json"
        manager.save(metadata_path)
        
        assert metadata_path.exists()
        
        # Load metadata
        manager2 = MetadataManager(metadata_path)
        
        assert manager2.data["original_filename"] == "test.txt"
        assert manager2.data["chunk_count"] == 1
    
    def test_validate_valid_metadata(self, tmp_path):
        """Test validating valid metadata."""
        manager = MetadataManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")
        
        chunks = [
            {"index": 1, "filename": "test.txt.part001", "size": 4, "md5": "abc"}
        ]
        
        manager.create_metadata(
            original_file=test_file,
            original_md5="def",
            chunk_size=1024,
            chunks=chunks
        )
        
        assert manager.validate() is True
    
    def test_validate_invalid_metadata(self):
        """Test validating invalid metadata."""
        manager = MetadataManager()
        manager.data = {"invalid": "data"}
        
        assert manager.validate() is False
    
    def test_validate_mismatched_chunk_count(self, tmp_path):
        """Test validating metadata with mismatched chunk count."""
        manager = MetadataManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")
        
        chunks = [
            {"index": 1, "filename": "test.txt.part001", "size": 4, "md5": "abc"}
        ]
        
        manager.create_metadata(
            original_file=test_file,
            original_md5="def",
            chunk_size=1024,
            chunks=chunks
        )
        
        # Manually change chunk_count to mismatch
        manager.data["chunk_count"] = 2
        
        assert manager.validate() is False
    
    def test_get_chunk_info(self, tmp_path):
        """Test getting chunk information."""
        manager = MetadataManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")
        
        chunks = [
            {"index": 1, "filename": "test.txt.part001", "size": 4, "md5": "abc"},
            {"index": 2, "filename": "test.txt.part002", "size": 4, "md5": "def"}
        ]
        
        manager.create_metadata(
            original_file=test_file,
            original_md5="ghi",
            chunk_size=1024,
            chunks=chunks
        )
        
        chunk1 = manager.get_chunk_info(1)
        assert chunk1["filename"] == "test.txt.part001"
        assert chunk1["md5"] == "abc"
        
        chunk2 = manager.get_chunk_info(2)
        assert chunk2["filename"] == "test.txt.part002"
        
        chunk3 = manager.get_chunk_info(3)
        assert chunk3 is None
    
    def test_calculate_md5(self, tmp_path):
        """Test MD5 calculation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        md5 = MetadataManager.calculate_md5(test_file)
        
        # Known MD5 for "Hello, World!"
        expected_md5 = "65a8e27d8879283831b664bd8b7f0ad4"
        assert md5 == expected_md5
    
    def test_str_representation(self, tmp_path):
        """Test string representation."""
        manager = MetadataManager()
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test")
        
        chunks = [
            {"index": 1, "filename": "test.txt.part001", "size": 4, "md5": "abc"}
        ]
        
        manager.create_metadata(
            original_file=test_file,
            original_md5="def",
            chunk_size=1024,
            chunks=chunks
        )
        
        str_repr = str(manager)
        
        assert "test.txt" in str_repr
        assert "def" in str_repr
        assert "1024" in str_repr

