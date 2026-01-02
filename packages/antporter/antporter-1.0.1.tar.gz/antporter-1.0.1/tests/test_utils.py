"""
Tests for utility functions.
"""

import pytest
from antporter.utils import parse_size, format_size, validate_chunk_size


class TestParseSize:
    """Tests for parse_size function."""
    
    def test_bytes(self):
        """Test parsing bytes."""
        assert parse_size("100") == 100
        assert parse_size("100B") == 100
        assert parse_size("100 B") == 100
    
    def test_kilobytes(self):
        """Test parsing kilobytes."""
        assert parse_size("1KB") == 1024
        assert parse_size("1K") == 1024
        assert parse_size("10KB") == 10 * 1024
        assert parse_size("1.5KB") == int(1.5 * 1024)
    
    def test_megabytes(self):
        """Test parsing megabytes."""
        assert parse_size("1MB") == 1024 ** 2
        assert parse_size("1M") == 1024 ** 2
        assert parse_size("100MB") == 100 * 1024 ** 2
        assert parse_size("2.5MB") == int(2.5 * 1024 ** 2)
    
    def test_gigabytes(self):
        """Test parsing gigabytes."""
        assert parse_size("1GB") == 1024 ** 3
        assert parse_size("1G") == 1024 ** 3
        assert parse_size("5GB") == 5 * 1024 ** 3
    
    def test_terabytes(self):
        """Test parsing terabytes."""
        assert parse_size("1TB") == 1024 ** 4
        assert parse_size("1T") == 1024 ** 4
        assert parse_size("2TB") == 2 * 1024 ** 4
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        assert parse_size("100mb") == 100 * 1024 ** 2
        assert parse_size("100MB") == 100 * 1024 ** 2
        assert parse_size("100Mb") == 100 * 1024 ** 2
    
    def test_invalid_format(self):
        """Test invalid format raises error."""
        with pytest.raises(ValueError):
            parse_size("invalid")
        
        with pytest.raises(ValueError):
            parse_size("100XB")
        
        with pytest.raises(ValueError):
            parse_size("MB100")


class TestFormatSize:
    """Tests for format_size function."""
    
    def test_bytes(self):
        """Test formatting bytes."""
        assert format_size(100) == "100 B"
        assert format_size(1023) == "1023 B"
    
    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_size(1024) == "1.00 KB"
        assert format_size(10 * 1024) == "10.00 KB"
        assert format_size(1536) == "1.50 KB"
    
    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_size(1024 ** 2) == "1.00 MB"
        assert format_size(100 * 1024 ** 2) == "100.00 MB"
    
    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_size(1024 ** 3) == "1.00 GB"
        assert format_size(5 * 1024 ** 3) == "5.00 GB"
    
    def test_terabytes(self):
        """Test formatting terabytes."""
        assert format_size(1024 ** 4) == "1.00 TB"
        assert format_size(2 * 1024 ** 4) == "2.00 TB"


class TestValidateChunkSize:
    """Tests for validate_chunk_size function."""
    
    def test_valid_chunk_size(self):
        """Test valid chunk size."""
        # Should not raise
        validate_chunk_size(1024, 10240)
        validate_chunk_size(1024 ** 2, 1024 ** 3)
    
    def test_zero_chunk_size(self):
        """Test zero chunk size raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            validate_chunk_size(0, 1024)
    
    def test_negative_chunk_size(self):
        """Test negative chunk size raises error."""
        with pytest.raises(ValueError, match="must be positive"):
            validate_chunk_size(-1024, 10240)
    
    def test_chunk_larger_than_file(self):
        """Test chunk size larger than file raises error."""
        with pytest.raises(ValueError, match="larger than file size"):
            validate_chunk_size(10240, 1024)
    
    def test_too_many_chunks(self):
        """Test chunk size that creates too many chunks."""
        # 1GB file with 100B chunks = 10,485,760 chunks (> 10,000 limit)
        with pytest.raises(ValueError, match="too small"):
            validate_chunk_size(100, 1024 ** 3)

