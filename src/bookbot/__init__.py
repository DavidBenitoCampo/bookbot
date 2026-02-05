"""
Bookbot - A professional text analysis tool for books and documents.

This package provides comprehensive text analysis capabilities including:
- Word and character frequency analysis
- Reading statistics and metrics
- Visualization generation
- Multiple export formats
"""

__version__ = "1.0.0"
__author__ = "David Benito Campo"

from .analyzer import BookAnalyzer, analyze_text
from .report import ReportGenerator
from .visualizer import Visualizer
from .exporter import Exporter

__all__ = [
    "BookAnalyzer",
    "analyze_text",
    "ReportGenerator",
    "Visualizer",
    "Exporter",
]
