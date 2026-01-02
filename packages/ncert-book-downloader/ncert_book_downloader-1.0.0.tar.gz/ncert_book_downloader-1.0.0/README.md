# 📚 NCERT Book Downloader

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A Python tool to download all NCERT textbooks (Classes 1-12) in PDF format from the official NCERT website. Books are available in both **English** and **Hindi** medium.

## ✨ Features

- 📥 **Download all NCERT books** from Classes 1 to 12
- 🌐 **Both English and Hindi** medium supported
- 📁 **Organized folder structure** by class and subject
- ⚡ **Parallel downloads** for faster completion
- 🔄 **Resume support** - skips already downloaded files
- 📦 **Automatic ZIP extraction** to get PDF files
- 📄 **PDF merging** - combine chapters into single books (optional)
- 🎯 **Flexible filtering** by class, subject, or language

## 📋 Available Books

| Classes | Subjects |
|---------|----------|
| **Class 11-12** | Physics, Chemistry, Maths, Biology, Accountancy, Business Studies, Economics, Geography, History, Political Science, Psychology, Sociology, Hindi, English |
| **Class 9-10** | Science, Maths, Social Science, Hindi, English |
| **Class 6-8** | Science, Maths, Social Science, Hindi, English |
| **Class 3-5** | Maths, EVS (Environmental Studies), Hindi, English |
| **Class 1-2** | Maths, Hindi, English |

**Total: 180+ books covering all CBSE subjects!**

## 🚀 Quick Start

### Installation

#### Using pip (Recommended)

```bash
pip install ncert-book-downloader
```

#### From Source

```bash
# Clone the repository
git clone https://github.com/dpandey/ncert-book-downloader.git
cd ncert-book-downloader

# Install the package
pip install .

# Or install in development mode
pip install -e ".[dev,merge]"
```

### Basic Usage

```bash
# Download all books
ncert-download

# Or use Python directly
python -m ncert_downloader.cli
```

### Command Examples

```bash
# Download specific classes
ncert-download --classes 10 12

# Download specific subjects
ncert-download --subjects Maths Science

# Download specific language
ncert-download --language English

# Download and merge chapters into single PDFs
ncert-download --merge

# Combine filters
ncert-download --classes 12 --subjects Physics --language English

# Custom output directory
ncert-download --output /path/to/save/books

# List available books
ncert-download --list

# Fast download with more parallel connections
ncert-download --workers 10
```

## 📂 Folder Structure

Downloads are organized as follows:

```
NCERT_Books/
├── Class_12/
│   ├── Physics/
│   │   ├── English/
│   │   │   └── (PDF files)
│   │   └── Hindi/
│   │       └── (PDF files)
│   ├── Chemistry/
│   ├── Maths/
│   └── ...
├── Class_11/
├── Class_10/
├── ...
└── Class_1/
```

## ⚙️ Command Line Options

| Option | Description |
|--------|-------------|
| `-o, --output DIR` | Output directory (default: NCERT_Books) |
| `-c, --classes N [N ...]` | Download specific classes (1-12) |
| `-s, --subjects SUB [SUB ...]` | Download specific subjects |
| `-l, --language LANG` | Download specific language (English/Hindi) |
| `-w, --workers N` | Number of parallel downloads (default: 5) |
| `--no-extract` | Don't extract ZIP files after downloading |
| `--merge` | Merge chapters into single PDF books |
| `--list` | List all available books |
| `-q, --quiet` | Reduce output verbosity |
| `-v, --version` | Show version number |
| `-h, --help` | Show help message |

## 🐍 Python API

You can also use the library programmatically:

```python
from ncert_downloader import download_all_books, NCERT_BOOKS, Book

# Download all books
results = download_all_books()

# Download with filters
results = download_all_books(
    classes=[10, 12],
    subjects=["Physics", "Chemistry"],
    languages=["English"],
    max_workers=10
)

# Access book catalog
for book in NCERT_BOOKS:
    print(f"{book.class_num}: {book.subject} - {book.title}")
```

## 📌 Notes

- Books are downloaded from the **official NCERT website** (ncert.nic.in)
- Files are downloaded as ZIP archives containing PDF chapters
- The tool automatically extracts PDFs after downloading
- Already downloaded files are skipped on re-run
- PDF merging requires the optional `pypdf` dependency

## 🛠️ Development

```bash
# Clone and install in development mode
git clone https://github.com/dpandey/ncert-book-downloader.git
cd ncert-book-downloader
pip install -e ".[dev,merge]"

# Run linting
ruff check .

# Run tests
pytest

# Format code
ruff format .
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Disclaimer:** All NCERT books are copyrighted by NCERT and are provided free of charge for educational use. This tool simply facilitates downloading them from the official source.

## 🙏 Credits

- Book PDFs served by [NCERT Official Website](https://ncert.nic.in)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
