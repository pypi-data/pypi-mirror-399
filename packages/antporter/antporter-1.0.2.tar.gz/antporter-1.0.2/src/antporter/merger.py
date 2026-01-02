"""
File merging functionality.
"""

import os
from pathlib import Path
from typing import Optional
from tqdm import tqdm

from .metadata import MetadataManager
from .utils import format_size


class FileMerger:
    """Merge file chunks back into original file."""
    
    def __init__(
        self,
        metadata_file: Path,
        output_dir: Optional[Path] = None,
        verify: bool = True,
        cleanup: bool = False
    ):
        """
        Initialize file merger.
        
        Args:
            metadata_file: Path to metadata JSON file
            output_dir: Directory for output file (default: same as metadata file)
            verify: Whether to verify MD5 hash after merging
            cleanup: Whether to delete chunk files after successful merge
        """
        self.metadata_file = Path(metadata_file)
        self.output_dir = Path(output_dir) if output_dir else self.metadata_file.parent
        self.verify = verify
        self.cleanup = cleanup
        
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {self.metadata_file}")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load metadata
        self.metadata_manager = MetadataManager(self.metadata_file)
        
        if not self.metadata_manager.validate():
            raise ValueError("Invalid metadata file")
    
    def merge(self) -> Path:
        """
        Merge chunks back into original file.
        
        Returns:
            Path to merged file
            
        Raises:
            FileNotFoundError: If any chunk file is missing
            ValueError: If MD5 verification fails
        """
        metadata = self.metadata_manager.data
        original_filename = metadata["original_filename"]
        original_size = metadata["original_size"]
        original_md5 = metadata["original_md5"]
        chunk_count = metadata["chunk_count"]
        
        print(f"Merging file: {original_filename}")
        print(f"Expected size: {format_size(original_size)}")
        print(f"Number of chunks: {chunk_count}")
        
        output_path = self.output_dir / original_filename
        
        # Check if output file already exists
        if output_path.exists():
            print(f"\nWarning: Output file already exists: {output_path}")
            response = input("Overwrite? (y/n): ").lower()
            if response != 'y':
                print("Merge cancelled.")
                return output_path
        
        # Verify all chunks exist
        print("\nVerifying chunks...")
        chunks_dir = self.metadata_file.parent
        missing_chunks = []
        
        for chunk_info in metadata["chunks"]:
            chunk_path = chunks_dir / chunk_info["filename"]
            if not chunk_path.exists():
                missing_chunks.append(chunk_info["filename"])
        
        if missing_chunks:
            raise FileNotFoundError(
                f"Missing chunk files: {', '.join(missing_chunks)}"
            )
        
        print("✓ All chunks found")
        
        # Merge chunks
        print("\nMerging chunks...")
        with open(output_path, 'wb') as output_f:
            with tqdm(total=original_size, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                for chunk_info in metadata["chunks"]:
                    chunk_path = chunks_dir / chunk_info["filename"]
                    
                    # Verify chunk MD5 if enabled
                    if self.verify:
                        chunk_md5 = MetadataManager.calculate_md5(chunk_path)
                        if chunk_md5 != chunk_info["md5"]:
                            raise ValueError(
                                f"Chunk MD5 mismatch: {chunk_info['filename']}\n"
                                f"Expected: {chunk_info['md5']}\n"
                                f"Got: {chunk_md5}"
                            )
                    
                    # Read and write chunk
                    with open(chunk_path, 'rb') as chunk_f:
                        data = chunk_f.read()
                        output_f.write(data)
                        pbar.update(len(data))
        
        # Verify merged file
        if self.verify:
            print("\nVerifying merged file...")
            merged_md5 = MetadataManager.calculate_md5(output_path)
            
            if merged_md5 != original_md5:
                raise ValueError(
                    f"Merged file MD5 mismatch!\n"
                    f"Expected: {original_md5}\n"
                    f"Got: {merged_md5}\n"
                    f"The merged file may be corrupted."
                )
            
            print("✓ MD5 verification passed")
        
        # Cleanup chunks if requested
        if self.cleanup:
            print("\nCleaning up chunk files...")
            for chunk_info in metadata["chunks"]:
                chunk_path = chunks_dir / chunk_info["filename"]
                try:
                    chunk_path.unlink()
                except Exception as e:
                    print(f"Warning: Failed to delete {chunk_info['filename']}: {e}")
            
            # Also delete metadata file
            try:
                self.metadata_file.unlink()
                print("✓ Cleanup complete")
            except Exception as e:
                print(f"Warning: Failed to delete metadata file: {e}")
        
        print(f"\n✓ Merge complete!")
        print(f"  Output file: {output_path}")
        print(f"  File size: {format_size(output_path.stat().st_size)}")
        
        return output_path

