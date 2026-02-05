"""
BookBot CLI module.

This module provides the command-line interface entry point for the bookbot package.
It's used when bookbot is installed as a package via pip.
"""

import sys
from pathlib import Path

# Handle both installed package and development mode
try:
    from bookbot.analyzer import BookAnalyzer, AnalysisResult, compare_books
    from bookbot.report import ReportGenerator, generate_comparison_report
    from bookbot.exporter import Exporter, batch_export, export_comparison
    from bookbot.visualizer import Visualizer
    from bookbot.utils import setup_logging, find_books, format_duration
except ImportError:
    # Development mode - add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
    from bookbot.analyzer import BookAnalyzer, AnalysisResult, compare_books
    from bookbot.report import ReportGenerator, generate_comparison_report
    from bookbot.exporter import Exporter, batch_export, export_comparison
    from bookbot.visualizer import Visualizer
    from bookbot.utils import setup_logging, find_books, format_duration


def main():
    """Main entry point for the CLI."""
    # Import and run main from the main module
    import importlib.util
    
    # Try to find main.py in the expected locations
    possible_paths = [
        Path(__file__).parent.parent.parent.parent / 'main.py',  # From src/bookbot/cli.py
        Path.cwd() / 'main.py',
    ]
    
    for main_path in possible_paths:
        if main_path.exists():
            spec = importlib.util.spec_from_file_location("main_module", main_path)
            if spec and spec.loader:
                main_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main_module)
                return main_module.main()
    
    # Fallback: run a simple version
    print("BookBot CLI - use 'python main.py' for full functionality")
    return 1


if __name__ == '__main__':
    sys.exit(main())
