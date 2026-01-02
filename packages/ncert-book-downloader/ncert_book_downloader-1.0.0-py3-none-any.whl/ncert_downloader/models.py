"""
Data models for NCERT Book Downloader.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """
    Represents an NCERT book with its metadata and download URL.
    
    Attributes:
        class_num: The class/grade number (1-12)
        subject: The subject name (e.g., "Physics", "Maths")
        title: The book title (can be in English or Hindi)
        language: The language of the book ("English" or "Hindi")
        url: The direct download URL for the ZIP file
        part: Optional part number for multi-part books
    """
    class_num: int
    subject: str
    title: str
    language: str  # 'English' or 'Hindi'
    url: str
    part: Optional[int] = None

    def get_filename(self) -> str:
        """
        Generate a clean filename for the book.
        
        Returns:
            A filename in the format: Class_{num}_{Subject}[_Part_{n}]_{Language}.zip
        """
        part_str = f"_Part_{self.part}" if self.part else ""
        return f"Class_{self.class_num}_{self.subject}{part_str}_{self.language}.zip"
    
    def get_folder_path(self, base_dir: str) -> str:
        """
        Get the folder path for organizing the book.
        
        Args:
            base_dir: The base directory for downloads
            
        Returns:
            Path in the format: {base_dir}/Class_{num}/{Subject}
        """
        return os.path.join(base_dir, f"Class_{self.class_num}", self.subject)
    
    def get_safe_title(self) -> str:
        """
        Generate a filesystem-safe title for the book.
        
        Removes characters that are invalid in filenames while preserving
        Unicode characters (like Hindi text).
        
        Returns:
            A sanitized title safe for use in filenames
        """
        invalid_chars = '<>:"/\\|?*'
        return "".join(c for c in self.title if c not in invalid_chars).strip()

    def __str__(self) -> str:
        """Human-readable representation of the book."""
        part_str = f" Part {self.part}" if self.part else ""
        return f"Class {self.class_num} - {self.subject}{part_str} ({self.language})"
