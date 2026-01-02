"""
Command-line interface for NCERT Book Downloader.
"""

import argparse
import sys
from typing import Optional

from ncert_downloader import __version__
from ncert_downloader.downloader import download_all_books, list_available_books
from ncert_downloader.merger import merge_books


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ncert-download",
        description="Download NCERT textbooks (Classes 1-12) in PDF format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ncert-download                         # Download all books
  ncert-download --classes 10 12         # Download Class 10 and 12 only
  ncert-download --subjects Maths Science  # Download Maths and Science only
  ncert-download --language English      # Download English medium only
  ncert-download --list                  # List all available books
  ncert-download --merge                 # Download and merge into single PDFs
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="NCERT_Books",
        metavar="DIR",
        help="Output directory for downloads (default: NCERT_Books)"
    )
    
    parser.add_argument(
        "-c", "--classes",
        nargs="+",
        type=int,
        choices=range(1, 13),
        metavar="N",
        help="Download specific classes only (1-12)"
    )
    
    parser.add_argument(
        "-s", "--subjects",
        nargs="+",
        metavar="SUBJECT",
        help="Download specific subjects only (e.g., Maths, Science, Physics)"
    )
    
    parser.add_argument(
        "-l", "--language",
        nargs="+",
        choices=["English", "Hindi", "english", "hindi"],
        metavar="LANG",
        help="Download specific language only (English/Hindi)"
    )
    
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=5,
        metavar="N",
        help="Number of parallel downloads (default: 5)"
    )
    
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="Don't extract ZIP files after downloading"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_books",
        help="List all available books without downloading"
    )
    
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge chapters into a single PDF book after downloading"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress banner and reduce output verbosity"
    )
    
    return parser


def main(args: Optional[list[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments (uses sys.argv if None)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    try:
        if parsed_args.list_books:
            list_available_books()
            return 0
        
        # Run the download
        results = download_all_books(
            base_dir=parsed_args.output,
            classes=parsed_args.classes,
            subjects=parsed_args.subjects,
            languages=parsed_args.language,
            max_workers=parsed_args.workers,
            extract=not parsed_args.no_extract,
            quiet=parsed_args.quiet
        )
        
        # Merge if requested
        if parsed_args.merge:
            merge_books(
                base_dir=parsed_args.output,
                classes=parsed_args.classes,
                quiet=parsed_args.quiet
            )
        
        # Return error code if any downloads failed
        return 1 if results["failed"] > 0 else 0
        
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
