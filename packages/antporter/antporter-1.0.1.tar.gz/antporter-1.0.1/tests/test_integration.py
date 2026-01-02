"""
Integration tests for AntPorter.
"""

import os
from pathlib import Path
import pytest

from antporter import FileSplitter, FileMerger, MetadataManager


class TestIntegration:
    """Integration tests for split and merge operations."""
    
    def test_split_and_merge_small_file(self, tmp_path):
        """Test splitting and merging a small file."""
        # Create test file
        test_file = tmp_path / "test.bin"
        test_data = b"Hello, World!" * 1000  # ~13KB
        test_file.write_bytes(test_data)
        
        # Split file
        chunks_dir = tmp_path / "chunks"
        chunks_dir.mkdir()
        
        splitter = FileSplitter(
            input_file=test_file,
            chunk_size=5000,  # 5KB chunks
            output_dir=chunks_dir
        )
        
        metadata_path = splitter.split()
        
        # Verify chunks were created
        assert metadata_path.exists()
        assert (chunks_dir / "test.bin.part001").exists()
        assert (chunks_dir / "test.bin.part002").exists()
        assert (chunks_dir / "test.bin.part003").exists()
        
        # Merge file
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        merger = FileMerger(
            metadata_file=metadata_path,
            output_dir=output_dir,
            verify=True
        )
        
        merged_file = merger.merge()
        
        # Verify merged file
        assert merged_file.exists()
        assert merged_file.read_bytes() == test_data
    
    def test_split_with_resume(self, tmp_path):
        """Test split with resume functionality."""
        # Create test file
        test_file = tmp_path / "test.bin"
        test_data = os.urandom(10000)  # 10KB
        test_file.write_bytes(test_data)
        
        chunks_dir = tmp_path / "chunks"
        chunks_dir.mkdir()
        
        # First split
        splitter1 = FileSplitter(
            input_file=test_file,
            chunk_size=3000,  # 3KB chunks
            output_dir=chunks_dir,
            resume=True
        )
        
        metadata_path1 = splitter1.split()
        
        # Get modification time of first chunk
        chunk1_path = chunks_dir / "test.bin.part001"
        mtime1 = chunk1_path.stat().st_mtime
        
        # Second split (should resume)
        splitter2 = FileSplitter(
            input_file=test_file,
            chunk_size=3000,
            output_dir=chunks_dir,
            resume=True
        )
        
        metadata_path2 = splitter2.split()
        
        # Verify first chunk was not recreated
        mtime2 = chunk1_path.stat().st_mtime
        assert mtime1 == mtime2  # File not modified
    
    def test_merge_with_cleanup(self, tmp_path):
        """Test merge with cleanup functionality."""
        # Create and split test file
        test_file = tmp_path / "test.bin"
        test_data = b"Test data" * 1000
        test_file.write_bytes(test_data)
        
        chunks_dir = tmp_path / "chunks"
        chunks_dir.mkdir()
        
        splitter = FileSplitter(
            input_file=test_file,
            chunk_size=5000,
            output_dir=chunks_dir
        )
        
        metadata_path = splitter.split()
        
        # Verify chunks exist
        chunk_files = list(chunks_dir.glob("*.part*"))
        assert len(chunk_files) > 0
        
        # Merge with cleanup
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        merger = FileMerger(
            metadata_file=metadata_path,
            output_dir=output_dir,
            verify=True,
            cleanup=True
        )
        
        merged_file = merger.merge()
        
        # Verify chunks were deleted
        chunk_files_after = list(chunks_dir.glob("*.part*"))
        assert len(chunk_files_after) == 0
        
        # Verify metadata was deleted
        assert not metadata_path.exists()
        
        # Verify merged file is correct
        assert merged_file.read_bytes() == test_data
    
    def test_large_file_split_merge(self, tmp_path):
        """Test splitting and merging a larger file."""
        # Create larger test file (1MB)
        test_file = tmp_path / "large.bin"
        test_data = os.urandom(1024 * 1024)  # 1MB
        test_file.write_bytes(test_data)
        
        # Split into 100KB chunks
        chunks_dir = tmp_path / "chunks"
        chunks_dir.mkdir()
        
        splitter = FileSplitter.from_size_string(
            input_file=test_file,
            chunk_size_str="100KB",
            output_dir=chunks_dir
        )
        
        metadata_path = splitter.split()
        
        # Verify number of chunks
        manager = MetadataManager(metadata_path)
        assert manager.data["chunk_count"] == 11  # 1MB / 100KB = 10.24 -> 11 chunks
        
        # Merge
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        merger = FileMerger(
            metadata_file=metadata_path,
            output_dir=output_dir,
            verify=True
        )
        
        merged_file = merger.merge()
        
        # Verify
        assert merged_file.read_bytes() == test_data
        
        # Verify MD5
        original_md5 = MetadataManager.calculate_md5(test_file)
        merged_md5 = MetadataManager.calculate_md5(merged_file)
        assert original_md5 == merged_md5

