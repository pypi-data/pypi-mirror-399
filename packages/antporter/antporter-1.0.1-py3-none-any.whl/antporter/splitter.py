"""
File splitting functionality.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from tqdm import tqdm

from .metadata import MetadataManager
from .utils import parse_size, format_size


class FileSplitter:
    """Split large files into smaller chunks."""
    
    def __init__(
        self,
        input_file: Path,
        chunk_size: int,
        output_dir: Optional[Path] = None,
        resume: bool = True
    ):
        """
        Initialize file splitter.
        
        Args:
            input_file: Path to file to split
            chunk_size: Size of each chunk in bytes
            output_dir: Directory for output chunks (default: same as input file)
            resume: Whether to resume from existing chunks
        """
        self.input_file = Path(input_file)
        self.chunk_size = chunk_size
        self.output_dir = Path(output_dir) if output_dir else self.input_file.parent
        self.resume = resume
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        if not self.input_file.is_file():
            raise ValueError(f"Input path is not a file: {self.input_file}")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_manager = MetadataManager()
    
    def split(self) -> Path:
        """
        Split the file into chunks.
        
        Returns:
            Path to metadata file
        """
        file_size = self.input_file.stat().st_size
        
        print(f"Splitting file: {self.input_file.name}")
        print(f"File size: {format_size(file_size)}")
        print(f"Chunk size: {format_size(self.chunk_size)}")
        
        # Calculate number of chunks
        num_chunks = (file_size + self.chunk_size - 1) // self.chunk_size
        print(f"Number of chunks: {num_chunks}")
        
        chunks_info: List[Dict[str, Any]] = []
        
        # Calculate original file MD5
        print("\nCalculating MD5 hash of original file...")
        original_md5 = MetadataManager.calculate_md5(self.input_file)
        print(f"MD5: {original_md5}")
        
        # Split file
        print("\nSplitting file into chunks...")
        with open(self.input_file, 'rb') as input_f:
            with tqdm(total=file_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                for chunk_index in range(1, num_chunks + 1):
                    chunk_filename = f"{self.input_file.name}.part{chunk_index:03d}"
                    chunk_path = self.output_dir / chunk_filename
                    
                    # Check if chunk already exists (resume functionality)
                    if self.resume and chunk_path.exists():
                        chunk_size = chunk_path.stat().st_size
                        expected_size = min(self.chunk_size, file_size - (chunk_index - 1) * self.chunk_size)
                        
                        if chunk_size == expected_size:
                            # Chunk exists and has correct size, skip it
                            chunk_md5 = MetadataManager.calculate_md5(chunk_path)
                            chunks_info.append({
                                "index": chunk_index,
                                "filename": chunk_filename,
                                "size": chunk_size,
                                "md5": chunk_md5
                            })
                            pbar.update(chunk_size)
                            input_f.seek(chunk_index * self.chunk_size)
                            continue
                    
                    # Read and write chunk
                    chunk_data = input_f.read(self.chunk_size)
                    
                    with open(chunk_path, 'wb') as chunk_f:
                        chunk_f.write(chunk_data)
                    
                    # Calculate chunk MD5
                    chunk_md5 = MetadataManager.calculate_md5(chunk_path)
                    
                    chunks_info.append({
                        "index": chunk_index,
                        "filename": chunk_filename,
                        "size": len(chunk_data),
                        "md5": chunk_md5
                    })
                    
                    pbar.update(len(chunk_data))
        
        # Create and save metadata
        print("\nCreating metadata file...")
        self.metadata_manager.create_metadata(
            original_file=self.input_file,
            original_md5=original_md5,
            chunk_size=self.chunk_size,
            chunks=chunks_info
        )
        
        metadata_path = self.output_dir / f"{self.input_file.name}.meta.json"
        self.metadata_manager.save(metadata_path)
        
        print(f"\n✓ Split complete!")
        print(f"  Chunks: {num_chunks}")
        print(f"  Output directory: {self.output_dir}")
        print(f"  Metadata file: {metadata_path.name}")
        
        return metadata_path
    
    @staticmethod
    def from_size_string(
        input_file: Path,
        chunk_size_str: str,
        output_dir: Optional[Path] = None,
        resume: bool = True
    ) -> 'FileSplitter':
        """
        Create FileSplitter from size string (e.g., "100MB", "1GB").
        
        Args:
            input_file: Path to file to split
            chunk_size_str: Chunk size as string (e.g., "100MB")
            output_dir: Directory for output chunks
            resume: Whether to resume from existing chunks
            
        Returns:
            FileSplitter instance
        """
        chunk_size = parse_size(chunk_size_str)
        return FileSplitter(input_file, chunk_size, output_dir, resume)

