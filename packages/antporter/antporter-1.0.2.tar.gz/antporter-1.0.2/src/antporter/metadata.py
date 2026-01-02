"""
Metadata management for file splitting and merging operations.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class MetadataManager:
    """Manager for creating and reading metadata files."""
    
    VERSION = "1.0"
    
    def __init__(self, metadata_path: Optional[Path] = None):
        """
        Initialize metadata manager.
        
        Args:
            metadata_path: Path to metadata file (for reading existing metadata)
        """
        self.metadata_path = metadata_path
        self.data: Dict[str, Any] = {}
        
        if metadata_path and metadata_path.exists():
            self.load()
    
    def create_metadata(
        self,
        original_file: Path,
        original_md5: str,
        chunk_size: int,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create metadata dictionary for a split operation.
        
        Args:
            original_file: Path to original file
            original_md5: MD5 hash of original file
            chunk_size: Size of each chunk in bytes
            chunks: List of chunk information dictionaries
            
        Returns:
            Metadata dictionary
        """
        self.data = {
            "original_filename": original_file.name,
            "original_size": original_file.stat().st_size,
            "original_md5": original_md5,
            "chunk_size": chunk_size,
            "chunk_count": len(chunks),
            "chunks": chunks,
            "created_at": datetime.now().isoformat(),
            "version": self.VERSION
        }
        return self.data
    
    def save(self, output_path: Path) -> None:
        """
        Save metadata to JSON file.
        
        Args:
            output_path: Path where metadata file will be saved
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        self.metadata_path = output_path
    
    def load(self) -> Dict[str, Any]:
        """
        Load metadata from JSON file.
        
        Returns:
            Metadata dictionary
            
        Raises:
            FileNotFoundError: If metadata file doesn't exist
            json.JSONDecodeError: If metadata file is invalid
        """
        if not self.metadata_path:
            raise ValueError("No metadata path specified")
            
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        return self.data
    
    def validate(self) -> bool:
        """
        Validate metadata structure.
        
        Returns:
            True if metadata is valid, False otherwise
        """
        required_fields = [
            "original_filename",
            "original_size",
            "original_md5",
            "chunk_size",
            "chunk_count",
            "chunks",
            "version"
        ]
        
        for field in required_fields:
            if field not in self.data:
                return False
        
        # Validate chunks
        if not isinstance(self.data["chunks"], list):
            return False
            
        if len(self.data["chunks"]) != self.data["chunk_count"]:
            return False
        
        return True
    
    def get_chunk_info(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific chunk.
        
        Args:
            index: Chunk index (1-based)
            
        Returns:
            Chunk information dictionary or None if not found
        """
        for chunk in self.data.get("chunks", []):
            if chunk["index"] == index:
                return chunk
        return None
    
    @staticmethod
    def calculate_md5(file_path: Path, chunk_size: int = 8192) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to file
            chunk_size: Size of chunks to read for hashing
            
        Returns:
            MD5 hash as hexadecimal string
        """
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                md5_hash.update(data)
        return md5_hash.hexdigest()
    
    def __str__(self) -> str:
        """String representation of metadata."""
        if not self.data:
            return "Empty metadata"
        
        return (
            f"File: {self.data.get('original_filename', 'N/A')}\n"
            f"Size: {self.data.get('original_size', 0):,} bytes\n"
            f"MD5: {self.data.get('original_md5', 'N/A')}\n"
            f"Chunks: {self.data.get('chunk_count', 0)}\n"
            f"Chunk Size: {self.data.get('chunk_size', 0):,} bytes\n"
            f"Created: {self.data.get('created_at', 'N/A')}"
        )

