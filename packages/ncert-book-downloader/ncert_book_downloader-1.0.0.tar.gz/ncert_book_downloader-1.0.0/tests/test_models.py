"""Tests for the Book model."""

import pytest

from ncert_downloader.models import Book


class TestBook:
    """Tests for the Book dataclass."""

    def test_book_creation(self):
        """Test creating a Book instance."""
        book = Book(
            class_num=10,
            subject="Science",
            title="Science",
            language="English",
            url="https://example.com/book.zip"
        )
        
        assert book.class_num == 10
        assert book.subject == "Science"
        assert book.title == "Science"
        assert book.language == "English"
        assert book.url == "https://example.com/book.zip"
        assert book.part is None

    def test_book_with_part(self):
        """Test creating a Book with a part number."""
        book = Book(
            class_num=12,
            subject="Physics",
            title="Physics Part 1",
            language="English",
            url="https://example.com/physics1.zip",
            part=1
        )
        
        assert book.part == 1

    def test_get_filename(self):
        """Test generating the download filename."""
        book = Book(10, "Science", "Science", "English", "https://example.com/book.zip")
        assert book.get_filename() == "Class_10_Science_English.zip"

    def test_get_filename_with_part(self):
        """Test generating filename for multi-part books."""
        book = Book(12, "Physics", "Physics Part 1", "English", "https://example.com/book.zip", 1)
        assert book.get_filename() == "Class_12_Physics_Part_1_English.zip"

    def test_get_folder_path(self):
        """Test generating the folder path."""
        book = Book(10, "Science", "Science", "English", "https://example.com/book.zip")
        path = book.get_folder_path("/downloads")
        assert path == "/downloads/Class_10/Science"

    def test_get_safe_title_english(self):
        """Test safe title generation for English titles."""
        book = Book(12, "Physics", "Physics Part 1", "English", "https://example.com/book.zip")
        assert book.get_safe_title() == "Physics Part 1"

    def test_get_safe_title_hindi(self):
        """Test safe title generation preserves Hindi characters."""
        book = Book(10, "Science", "विज्ञान", "Hindi", "https://example.com/book.zip")
        assert book.get_safe_title() == "विज्ञान"

    def test_get_safe_title_removes_invalid_chars(self):
        """Test that invalid filesystem characters are removed."""
        book = Book(10, "Science", "Book: Title?", "English", "https://example.com/book.zip")
        assert ":" not in book.get_safe_title()
        assert "?" not in book.get_safe_title()

    def test_str_representation(self):
        """Test string representation of a Book."""
        book = Book(10, "Science", "Science", "English", "https://example.com/book.zip")
        assert str(book) == "Class 10 - Science (English)"

    def test_str_representation_with_part(self):
        """Test string representation with part number."""
        book = Book(12, "Physics", "Physics Part 1", "English", "https://example.com/book.zip", 1)
        assert str(book) == "Class 12 - Physics Part 1 (English)"
