"""
PDF merging functionality for NCERT books.

Merges individual chapter PDFs into complete book files.
"""

import os
import re
import zipfile
from pathlib import Path
from typing import Optional

from ncert_downloader.models import Book
from ncert_downloader.books import NCERT_BOOKS
from ncert_downloader.utils import Colors, print_banner, print_separator


# Check if pypdf is available
try:
    from pypdf import PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def get_chapter_sort_key(filename: str) -> int:
    """
    Generate a sort key for NCERT chapter PDFs to ensure correct order.
    
    Expected order:
    - Prelims (ps) -> -10
    - Introduction (intro) -> -5
    - Chapters (01, 02..) -> chapter number
    - Answers (an) -> 1000
    - Appendix (a1, a2..) -> 1001, 1002
    
    Args:
        filename: The PDF filename
        
    Returns:
        An integer sort key
    """
    stem = Path(filename).stem.lower()
    
    if "ps" in stem:
        return -10  # Prelims
    if "intro" in stem:
        return -5   # Introduction
    if "an" in stem:
        return 1000  # Answers
    
    # Try to find numeric part at end
    match = re.search(r'(\d+)$', stem)
    if match:
        return int(match.group(1))
    
    # Check for appendix variations
    if stem.endswith("a1") or "app1" in stem:
        return 1001
    if stem.endswith("a2") or "app2" in stem:
        return 1002
    
    return 100  # Default middle


def merge_books(
    base_dir: str = "NCERT_Books",
    classes: Optional[list[int]] = None,
    quiet: bool = False
) -> dict[str, int]:
    """
    Merge PDF chapters into single book files.
    
    Args:
        base_dir: Base directory containing downloaded books
        classes: Optional list of class numbers to process
        quiet: Suppress banner and detailed output
        
    Returns:
        Dictionary with merge statistics
    """
    if not PYPDF_AVAILABLE:
        if not quiet:
            print(f"{Colors.RED}❌ pypdf is not installed. Cannot merge books.{Colors.END}")
            print(f"Run: {Colors.BOLD}pip install pypdf{Colors.END} to enable this feature.")
        return {"merged": 0, "skipped": 0, "failed": 0}
    
    if not quiet:
        print_banner()
        print(f"{Colors.BLUE}🔄 Starting PDF Merge Process...{Colors.END}\n")
    
    books_to_process = NCERT_BOOKS.copy()
    if classes:
        books_to_process = [b for b in books_to_process if b.class_num in classes]
    
    success_count = 0
    skipped_count = 0
    failed_count = 0
    
    for book in books_to_process:
        result = _merge_single_book(book, base_dir, quiet)
        if result == "merged":
            success_count += 1
        elif result == "skipped":
            skipped_count += 1
        elif result == "failed":
            failed_count += 1
    
    if not quiet:
        print_separator()
        print(f"{Colors.BOLD}📊 Merge Summary:{Colors.END}")
        print(f"  {Colors.GREEN}✅ Books merged: {success_count}{Colors.END}")
        print(f"  {Colors.YELLOW}⏭️  Skipped (already merged): {skipped_count}{Colors.END}")
        if failed_count:
            print(f"  {Colors.RED}❌ Failed: {failed_count}{Colors.END}")
        print_separator()
    
    return {
        "merged": success_count,
        "skipped": skipped_count,
        "failed": failed_count
    }


def _merge_single_book(book: Book, base_dir: str, quiet: bool = False) -> str:
    """
    Merge a single book's chapters into one PDF.
    
    Args:
        book: The Book object to merge
        base_dir: Base directory containing downloaded books
        quiet: Suppress output
        
    Returns:
        "merged", "skipped", "failed", or "not_found"
    """
    folder_path = book.get_folder_path(base_dir)
    zip_path = os.path.join(folder_path, book.get_filename())
    
    # Generate safe output filename
    safe_title = book.get_safe_title()
    output_pdf_path = os.path.join(folder_path, f"{safe_title}.pdf")
    
    # Skip if already merged
    if os.path.exists(output_pdf_path):
        return "skipped"
    
    # Skip if source ZIP doesn't exist
    if not os.path.exists(zip_path):
        return "not_found"
    
    try:
        # Get list of PDFs from the ZIP
        chapter_files = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for name in zip_ref.namelist():
                if name.lower().endswith('.pdf'):
                    chapter_files.append(os.path.basename(name))
        
        if not chapter_files:
            return "not_found"
        
        # Sort files in correct order
        chapter_files.sort(key=get_chapter_sort_key)
        
        # Locate extracted files
        extract_dir = os.path.join(folder_path, book.language)
        merger = PdfWriter()
        pages_added = 0
        
        for filename in chapter_files:
            pdf_path = os.path.join(extract_dir, filename)
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    merger.append(f)
                pages_added += 1
        
        if pages_added > 0:
            with open(output_pdf_path, 'wb') as f_out:
                merger.write(f_out)
            if not quiet:
                print(f"{Colors.GREEN}✅ Merged: {book.title} "
                      f"({pages_added} chapters) -> {safe_title}.pdf{Colors.END}")
            return "merged"
        
        return "not_found"
        
    except Exception as e:
        if not quiet:
            print(f"{Colors.RED}❌ Failed to merge {book.title}: {e}{Colors.END}")
        return "failed"


def is_merge_available() -> bool:
    """Check if PDF merging functionality is available."""
    return PYPDF_AVAILABLE
