"""
NCERT Book Downloader

A Python package to download all NCERT textbooks (Classes 1-12) in PDF format
from the official NCERT website. Books are available in both English and Hindi medium.
"""

__version__ = "1.0.0"
__author__ = "ncert-book-downloader contributors"

from ncert_downloader.models import Book
from ncert_downloader.books import NCERT_BOOKS
from ncert_downloader.downloader import download_book, download_all_books
from ncert_downloader.merger import merge_books

__all__ = [
    "Book",
    "NCERT_BOOKS",
    "download_book",
    "download_all_books",
    "merge_books",
]
