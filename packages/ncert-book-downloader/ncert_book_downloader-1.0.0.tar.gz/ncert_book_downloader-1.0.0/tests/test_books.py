"""Tests for the book catalog."""

import pytest

from ncert_downloader.books import (
    NCERT_BOOKS,
    get_books_by_class,
    get_books_by_subject,
    get_books_by_language,
    get_total_books_count,
)


class TestBookCatalog:
    """Tests for the book catalog and helper functions."""

    def test_catalog_not_empty(self):
        """Test that the book catalog is not empty."""
        assert len(NCERT_BOOKS) > 0

    def test_catalog_has_expected_count(self):
        """Test that we have a reasonable number of books."""
        # Should have at least 150 books
        assert len(NCERT_BOOKS) >= 150

    def test_all_books_have_required_fields(self):
        """Test that all books have the required fields."""
        for book in NCERT_BOOKS:
            assert book.class_num >= 1
            assert book.class_num <= 12
            assert book.subject
            assert book.title
            assert book.language in ("English", "Hindi")
            assert book.url.startswith("https://")

    def test_get_books_by_class(self):
        """Test filtering books by class."""
        class_10_books = get_books_by_class(10)
        assert len(class_10_books) > 0
        assert all(b.class_num == 10 for b in class_10_books)

    def test_get_books_by_class_invalid(self):
        """Test filtering by non-existent class."""
        books = get_books_by_class(99)
        assert len(books) == 0

    def test_get_books_by_subject(self):
        """Test filtering books by subject."""
        physics_books = get_books_by_subject("Physics")
        assert len(physics_books) > 0
        assert all(b.subject.lower() == "physics" for b in physics_books)

    def test_get_books_by_subject_case_insensitive(self):
        """Test that subject filtering is case-insensitive."""
        books1 = get_books_by_subject("physics")
        books2 = get_books_by_subject("PHYSICS")
        books3 = get_books_by_subject("Physics")
        assert len(books1) == len(books2) == len(books3)

    def test_get_books_by_language_english(self):
        """Test filtering English books."""
        english_books = get_books_by_language("English")
        assert len(english_books) > 0
        assert all(b.language == "English" for b in english_books)

    def test_get_books_by_language_hindi(self):
        """Test filtering Hindi books."""
        hindi_books = get_books_by_language("Hindi")
        assert len(hindi_books) > 0
        assert all(b.language == "Hindi" for b in hindi_books)

    def test_get_total_books_count(self):
        """Test getting total book count."""
        count = get_total_books_count()
        assert count == len(NCERT_BOOKS)

    def test_each_class_has_books(self):
        """Test that each class from 1-12 has at least one book."""
        for class_num in range(1, 13):
            books = get_books_by_class(class_num)
            assert len(books) > 0, f"Class {class_num} has no books"

    def test_books_have_valid_urls(self):
        """Test that all book URLs are valid NCERT URLs."""
        for book in NCERT_BOOKS:
            assert "ncert.nic.in" in book.url
            assert book.url.endswith(".zip")
