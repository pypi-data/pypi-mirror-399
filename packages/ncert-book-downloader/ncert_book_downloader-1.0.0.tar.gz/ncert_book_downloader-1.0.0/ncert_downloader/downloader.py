"""
Core download functionality for NCERT books.
"""

import os
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

import requests

from ncert_downloader.models import Book
from ncert_downloader.books import NCERT_BOOKS
from ncert_downloader.utils import Colors, print_banner, print_separator


# Default HTTP headers for requests
DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/zip, application/octet-stream, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
}

# Minimum expected file size (1KB) to validate downloads
MIN_FILE_SIZE = 1000


def download_book(
    book: Book,
    base_dir: str,
    extract: bool = True,
    max_retries: int = 3
) -> tuple[bool, str]:
    """
    Download a single book and optionally extract it.
    
    Implements retry logic with exponential backoff for handling connection issues.
    
    Args:
        book: The Book object to download
        base_dir: Base directory to save the book
        extract: Whether to extract the ZIP file after downloading
        max_retries: Maximum number of retry attempts
        
    Returns:
        A tuple of (success: bool, message: str)
    """
    folder_path = book.get_folder_path(base_dir)
    os.makedirs(folder_path, exist_ok=True)
    
    zip_path = os.path.join(folder_path, book.get_filename())
    
    # Skip if already downloaded
    if os.path.exists(zip_path):
        return True, f"Already exists: {book.title}"
    
    last_error: Optional[Exception] = None
    
    for attempt in range(max_retries):
        try:
            # Exponential backoff between retries
            if attempt > 0:
                delay = 2 ** attempt  # 2s, 4s, 8s
                time.sleep(delay)
            
            # Create a session for better connection handling
            session = requests.Session()
            response = session.get(
                book.url,
                headers=DEFAULT_HEADERS,
                timeout=120,
                stream=True
            )
            response.raise_for_status()
            
            # Validate response size
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) < MIN_FILE_SIZE:
                raise requests.exceptions.ContentDecodingError(
                    "Response too small, might be an error page"
                )
            
            # Save the zip file
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was written properly
            if os.path.getsize(zip_path) < MIN_FILE_SIZE:
                os.remove(zip_path)
                raise requests.exceptions.ContentDecodingError("Downloaded file too small")
            
            # Extract if requested
            if extract:
                _extract_zip(zip_path, folder_path, book.language)
            
            return True, f"Downloaded: {book.title}"
            
        except (requests.exceptions.RequestException, ConnectionError, OSError) as e:
            last_error = e
            # Clean up partial download
            if os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except OSError:
                    pass
            continue
        except Exception as e:
            last_error = e
            break
    
    return False, f"Failed: {book.title} - {str(last_error)} (after {max_retries} retries)"


def _extract_zip(zip_path: str, folder_path: str, language: str) -> None:
    """
    Extract a ZIP file to a language-specific subdirectory.
    
    Args:
        zip_path: Path to the ZIP file
        folder_path: Base folder path
        language: Language name for the subdirectory
    """
    try:
        extract_dir = os.path.join(folder_path, language)
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except zipfile.BadZipFile:
        pass  # Keep the zip file even if extraction fails


def download_all_books(
    base_dir: str = "NCERT_Books",
    classes: Optional[list[int]] = None,
    subjects: Optional[list[str]] = None,
    languages: Optional[list[str]] = None,
    max_workers: int = 5,
    extract: bool = True,
    quiet: bool = False
) -> dict[str, int]:
    """
    Download NCERT books with filtering options.
    
    Args:
        base_dir: Directory to save books
        classes: List of class numbers to download (None = all)
        subjects: List of subjects to download (None = all)
        languages: List of languages to download (None = all)
        max_workers: Number of parallel downloads
        extract: Whether to extract zip files
        quiet: Suppress banner and detailed output
        
    Returns:
        A dictionary with download statistics
    """
    if not quiet:
        print_banner()
    
    # Filter books based on criteria
    books_to_download = _filter_books(NCERT_BOOKS, classes, subjects, languages)
    
    if not books_to_download:
        if not quiet:
            print(f"{Colors.RED}No books match the specified criteria.{Colors.END}")
        return {"success": 0, "skipped": 0, "failed": 0}
    
    total_books = len(books_to_download)
    
    if not quiet:
        print(f"{Colors.BLUE}📥 Preparing to download {Colors.BOLD}{total_books}{Colors.END}"
              f"{Colors.BLUE} books...{Colors.END}")
        print(f"{Colors.BLUE}📁 Download directory: {Colors.BOLD}{os.path.abspath(base_dir)}{Colors.END}")
        print(f"{Colors.BLUE}🔧 Parallel downloads: {Colors.BOLD}{max_workers}{Colors.END}")
        print(f"{Colors.BLUE}📦 Extract ZIP files: {Colors.BOLD}{'Yes' if extract else 'No'}{Colors.END}\n")
    
    # Create base directory
    os.makedirs(base_dir, exist_ok=True)
    
    # Track progress
    success_count = 0
    failed_count = 0
    skipped_count = 0
    failed_books: list[Book] = []
    
    start_time = time.time()
    
    # Download books in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_book = {
            executor.submit(download_book, book, base_dir, extract): book 
            for book in books_to_download
        }
        
        for i, future in enumerate(as_completed(future_to_book), 1):
            book = future_to_book[future]
            success, message = future.result()
            
            # Update counters
            if success:
                if "Already exists" in message:
                    skipped_count += 1
                    status = f"{Colors.YELLOW}⏭️  {message}{Colors.END}"
                else:
                    success_count += 1
                    status = f"{Colors.GREEN}✅ {message}{Colors.END}"
            else:
                failed_count += 1
                failed_books.append(book)
                status = f"{Colors.RED}❌ {message}{Colors.END}"
            
            # Print progress
            if not quiet:
                progress = f"[{i}/{total_books}]"
                print(f"{Colors.CYAN}{progress}{Colors.END} {status}")
    
    # Print summary
    elapsed_time = time.time() - start_time
    
    if not quiet:
        print_separator()
        print(f"{Colors.BOLD}📊 Download Summary:{Colors.END}")
        print_separator()
        print(f"  {Colors.GREEN}✅ Successfully downloaded: {success_count}{Colors.END}")
        print(f"  {Colors.YELLOW}⏭️  Already existed (skipped): {skipped_count}{Colors.END}")
        print(f"  {Colors.RED}❌ Failed: {failed_count}{Colors.END}")
        print(f"  ⏱️  Time elapsed: {elapsed_time:.1f} seconds")
        print_separator()
        
        if failed_books:
            print(f"\n{Colors.RED}Failed downloads:{Colors.END}")
            for book in failed_books:
                print(f"  - Class {book.class_num} {book.subject} ({book.language}): {book.title}")
        
        print(f"\n{Colors.GREEN}📚 Books saved to: {Colors.BOLD}{os.path.abspath(base_dir)}{Colors.END}")
    
    return {
        "success": success_count,
        "skipped": skipped_count,
        "failed": failed_count
    }


def _filter_books(
    books: list[Book],
    classes: Optional[list[int]],
    subjects: Optional[list[str]],
    languages: Optional[list[str]]
) -> list[Book]:
    """
    Filter books based on class, subject, and language criteria.
    
    Args:
        books: List of all books
        classes: Class numbers to include (None = all)
        subjects: Subjects to include (None = all)
        languages: Languages to include (None = all)
        
    Returns:
        Filtered list of books
    """
    result = books.copy()
    
    if classes:
        result = [b for b in result if b.class_num in classes]
    
    if subjects:
        subjects_lower = [s.lower() for s in subjects]
        result = [b for b in result if b.subject.lower() in subjects_lower]
    
    if languages:
        languages_lower = [lang.lower() for lang in languages]
        result = [b for b in result if b.language.lower() in languages_lower]
    
    return result


def list_available_books() -> None:
    """Display a summary of available books grouped by class."""
    from collections import defaultdict
    
    print_banner()
    print(f"{Colors.BOLD}Available NCERT Books:{Colors.END}\n")
    
    # Group by class
    books_by_class: dict[int, dict[str, list[Book]]] = defaultdict(lambda: defaultdict(list))
    
    for book in NCERT_BOOKS:
        books_by_class[book.class_num][book.subject].append(book)
    
    for class_num in sorted(books_by_class.keys(), reverse=True):
        subjects = books_by_class[class_num]
        print(f"{Colors.CYAN}Class {class_num}:{Colors.END}")
        for subject, books in sorted(subjects.items()):
            english_count = len([b for b in books if b.language == "English"])
            hindi_count = len([b for b in books if b.language == "Hindi"])
            print(f"  • {subject}: {english_count} English, {hindi_count} Hindi")
        print()
