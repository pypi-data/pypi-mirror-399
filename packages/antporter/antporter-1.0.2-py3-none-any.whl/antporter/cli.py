"""
Command-line interface for AntPorter.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from . import __version__
from .splitter import FileSplitter
from .merger import FileMerger
from .metadata import MetadataManager
from .utils import parse_size, format_size


def cmd_split(args) -> int:
    """
    Handle split command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        input_file = Path(args.file)
        output_dir = Path(args.output_dir) if args.output_dir else None
        
        # Parse chunk size
        chunk_size = parse_size(args.chunk_size)
        
        # Create splitter and split file
        splitter = FileSplitter(
            input_file=input_file,
            chunk_size=chunk_size,
            output_dir=output_dir,
            resume=not args.no_resume,
            remove_source=args.remove_source
        )
        
        splitter.split()
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_merge(args) -> int:
    """
    Handle merge command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        metadata_file = Path(args.metadata)
        output_dir = Path(args.output_dir) if args.output_dir else None
        
        # Create merger and merge chunks
        merger = FileMerger(
            metadata_file=metadata_file,
            output_dir=output_dir,
            verify=not args.no_verify,
            cleanup=args.cleanup
        )
        
        merger.merge()
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args) -> int:
    """
    Handle info command.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        metadata_file = Path(args.metadata)
        
        # Load and display metadata
        manager = MetadataManager(metadata_file)
        
        if not manager.validate():
            print("Error: Invalid metadata file", file=sys.stderr)
            return 1
        
        print("\n" + "=" * 60)
        print("FILE INFORMATION")
        print("=" * 60)
        print(manager)
        print("=" * 60)
        
        # Display chunk details if requested
        if args.chunks:
            print("\nCHUNK DETAILS")
            print("-" * 60)
            for chunk in manager.data["chunks"]:
                print(f"  [{chunk['index']:3d}] {chunk['filename']}")
                print(f"        Size: {format_size(chunk['size'])}")
                print(f"        MD5:  {chunk['md5']}")
            print("-" * 60)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """
    Main entry point for CLI.
    
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        prog='antporter',
        description='Split and merge files to bypass HPC cluster file size limits',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Split a large file into 100MB chunks
  antporter split large_file.tar.gz --chunk-size 100MB
  
  # Split with custom output directory
  antporter split data.zip --chunk-size 50MB --output-dir ./chunks
  
  # Split and remove source file
  antporter split data.zip --chunk-size 50MB --remove-source
  
  # Merge chunks back to original file
  antporter merge large_file.tar.gz.meta.json
  
  # Merge with cleanup (delete chunks after merge)
  antporter merge data.zip.meta.json --cleanup
  
  # Show metadata information
  antporter info large_file.tar.gz.meta.json
  
  # Show detailed chunk information
  antporter info large_file.tar.gz.meta.json --chunks
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Split command
    split_parser = subparsers.add_parser(
        'split',
        help='Split a file into chunks',
        description='Split a large file into smaller chunks'
    )
    split_parser.add_argument(
        'file',
        help='Path to file to split'
    )
    split_parser.add_argument(
        '--chunk-size', '-s',
        required=True,
        help='Size of each chunk (e.g., 100MB, 1GB)'
    )
    split_parser.add_argument(
        '--output-dir', '-o',
        help='Output directory for chunks (default: same as input file)'
    )
    split_parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Disable resume functionality (overwrite existing chunks)'
    )
    split_parser.add_argument(
        '--remove-source',
        action='store_true',
        help='Remove source file after successful split'
    )
    
    # Merge command
    merge_parser = subparsers.add_parser(
        'merge',
        help='Merge chunks back into original file',
        description='Merge file chunks back into the original file'
    )
    merge_parser.add_argument(
        'metadata',
        help='Path to metadata JSON file'
    )
    merge_parser.add_argument(
        '--output-dir', '-o',
        help='Output directory for merged file (default: same as metadata file)'
    )
    merge_parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip MD5 verification'
    )
    merge_parser.add_argument(
        '--cleanup', '-c',
        action='store_true',
        help='Delete chunk files after successful merge'
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Display metadata information',
        description='Display information about a split file from its metadata'
    )
    info_parser.add_argument(
        'metadata',
        help='Path to metadata JSON file'
    )
    info_parser.add_argument(
        '--chunks',
        action='store_true',
        help='Show detailed chunk information'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'split':
        return cmd_split(args)
    elif args.command == 'merge':
        return cmd_merge(args)
    elif args.command == 'info':
        return cmd_info(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())

