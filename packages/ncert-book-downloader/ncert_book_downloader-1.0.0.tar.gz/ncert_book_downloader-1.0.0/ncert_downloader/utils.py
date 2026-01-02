"""
ANSI color codes and formatting utilities for terminal output.
"""


class Colors:
    """ANSI color codes for terminal output styling."""
    
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @classmethod
    def success(cls, text: str) -> str:
        """Format text as a success message (green)."""
        return f"{cls.GREEN}{text}{cls.END}"
    
    @classmethod
    def warning(cls, text: str) -> str:
        """Format text as a warning message (yellow)."""
        return f"{cls.YELLOW}{text}{cls.END}"
    
    @classmethod
    def error(cls, text: str) -> str:
        """Format text as an error message (red)."""
        return f"{cls.RED}{text}{cls.END}"
    
    @classmethod
    def info(cls, text: str) -> str:
        """Format text as an info message (blue)."""
        return f"{cls.BLUE}{text}{cls.END}"
    
    @classmethod
    def highlight(cls, text: str) -> str:
        """Format text as highlighted (cyan)."""
        return f"{cls.CYAN}{text}{cls.END}"
    
    @classmethod
    def bold(cls, text: str) -> str:
        """Format text as bold."""
        return f"{cls.BOLD}{text}{cls.END}"


def print_banner() -> None:
    """Display the script banner."""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   {Colors.BOLD}📚 NCERT Book Downloader{Colors.CYAN}                                      ║
║   {Colors.END}{Colors.CYAN}Download all NCERT textbooks (Classes 1-12)                    ║
║   English & Hindi Medium | PDF Format                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(banner)


def print_separator(char: str = "=", width: int = 60) -> None:
    """Print a separator line."""
    print(f"{Colors.CYAN}{char * width}{Colors.END}")
