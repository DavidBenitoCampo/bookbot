"""
BookBot Exporter - Export analysis results to various formats.

Handles file export operations including JSON, CSV, HTML, and
batch export for multiple analyses.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .analyzer import AnalysisResult, compare_books
from .report import ReportGenerator, generate_comparison_report

logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Raised when export operations fail."""
    pass


class Exporter:
    """
    Export analysis results to various file formats.
    
    Supports exporting individual analyses and comparative
    reports in multiple formats.
    
    Example:
        >>> from bookbot.analyzer import BookAnalyzer
        >>> from bookbot.exporter import Exporter
        >>> result = BookAnalyzer("books/frankenstein.txt").analyze()
        >>> exporter = Exporter(result)
        >>> exporter.to_json("output/analysis.json")
    """
    
    SUPPORTED_FORMATS = ['json', 'csv', 'html', 'text', 'md']
    
    def __init__(self, result: Optional[AnalysisResult] = None):
        """
        Initialize the exporter.
        
        Args:
            result: Analysis result to export (optional for comparison exports)
        """
        self.result = result
    
    def _ensure_result(self) -> AnalysisResult:
        """Ensure we have a result to export."""
        if self.result is None:
            raise ExportError("No analysis result provided")
        return self.result
    
    def to_json(
        self, 
        path: str,
        indent: int = 2,
        include_frequencies: bool = True
    ) -> Path:
        """
        Export to JSON format.
        
        Args:
            path: Output file path
            indent: JSON indentation
            include_frequencies: Include full frequency data
            
        Returns:
            Path to exported file
        """
        result = self._ensure_result()
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = result.to_dict()
        data['exported_at'] = datetime.now().isoformat()
        data['bookbot_version'] = '1.0.0'
        
        if not include_frequencies:
            # Trim frequency data to reduce file size
            data['char_frequency'] = dict(list(data['char_frequency'].items())[:26])
            data['top_words'] = data['top_words'][:20]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        logger.info(f"Exported JSON to: {output_path}")
        return output_path
    
    def to_csv(self, path: str) -> Path:
        """
        Export to CSV format.
        
        Args:
            path: Output file path
            
        Returns:
            Path to exported file
        """
        result = self._ensure_result()
        report = ReportGenerator(result)
        
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        csv_content = report.generate_csv()
        output_path.write_text(csv_content, encoding='utf-8')
        
        logger.info(f"Exported CSV to: {output_path}")
        return output_path
    
    def to_html(
        self, 
        path: str,
        include_charts: bool = True
    ) -> Path:
        """
        Export to interactive HTML format.
        
        Args:
            path: Output file path
            include_charts: Include Chart.js visualizations
            
        Returns:
            Path to exported file
        """
        result = self._ensure_result()
        report = ReportGenerator(result)
        
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = report.generate_html(include_charts=include_charts)
        output_path.write_text(html_content, encoding='utf-8')
        
        logger.info(f"Exported HTML to: {output_path}")
        return output_path
    
    def to_markdown(self, path: str) -> Path:
        """
        Export to Markdown format.
        
        Args:
            path: Output file path
            
        Returns:
            Path to exported file
        """
        result = self._ensure_result()
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        r = result
        
        content = f'''# 📚 BookBot Analysis Report

## {r.title}

**File:** `{r.file_path}`  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📖 Reading Statistics

| Metric | Value |
|--------|-------|
| Word Count | {r.word_count:,} |
| Unique Words | {r.unique_word_count:,} |
| Characters | {r.character_count:,} |
| Sentences | {r.sentence_count:,} |
| Paragraphs | {r.paragraph_count:,} |
| Reading Time | {r.reading_time_minutes:.1f} minutes |

---

## 📊 Complexity Metrics

| Metric | Value |
|--------|-------|
| Average Word Length | {r.average_word_length:.2f} characters |
| Average Sentence Length | {r.average_sentence_length:.1f} words |
| Vocabulary Richness | {r.vocabulary_richness:.2%} |

---

## 🔤 Top 10 Words

| Rank | Word | Count |
|------|------|-------|
'''
        for i, (word, count) in enumerate(r.top_words[:10], 1):
            content += f'| {i} | {word} | {count:,} |\n'
        
        content += '''
---

## 📈 Character Frequency (Top 10)

| Character | Count |
|-----------|-------|
'''
        for char, count in list(r.char_frequency.items())[:10]:
            content += f'| {char} | {count:,} |\n'
        
        content += f'''
---

*Generated by [BookBot](https://github.com/DavidBenitoCampo/bookbot) v1.0.0*
'''
        
        output_path.write_text(content, encoding='utf-8')
        
        logger.info(f"Exported Markdown to: {output_path}")
        return output_path
    
    def to_text(self, path: str, use_color: bool = False) -> Path:
        """
        Export to plain text format.
        
        Args:
            path: Output file path
            use_color: Include ANSI color codes
            
        Returns:
            Path to exported file
        """
        result = self._ensure_result()
        report = ReportGenerator(result, use_color=use_color)
        
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        text_content = report.generate_text()
        output_path.write_text(text_content, encoding='utf-8')
        
        logger.info(f"Exported text to: {output_path}")
        return output_path
    
    def export(self, path: str, format: Optional[str] = None) -> Path:
        """
        Export to any supported format.
        
        The format can be specified explicitly or inferred from
        the file extension.
        
        Args:
            path: Output file path
            format: Export format (optional, inferred from extension)
            
        Returns:
            Path to exported file
        """
        output_path = Path(path)
        
        if format is None:
            # Infer from extension
            ext = output_path.suffix.lower().lstrip('.')
            format = ext if ext in self.SUPPORTED_FORMATS else 'text'
        
        exporters = {
            'json': self.to_json,
            'csv': self.to_csv,
            'html': self.to_html,
            'md': self.to_markdown,
            'text': self.to_text,
            'txt': self.to_text,
        }
        
        if format not in exporters:
            raise ExportError(
                f"Unsupported format: {format}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )
        
        return exporters[format](str(output_path))


def batch_export(
    results: List[AnalysisResult],
    output_dir: str,
    formats: List[str] = None
) -> Dict[str, List[Path]]:
    """
    Export multiple analysis results.
    
    Args:
        results: List of analysis results
        output_dir: Output directory
        formats: List of formats to export (default: all)
        
    Returns:
        Dictionary mapping formats to exported file paths
    """
    if formats is None:
        formats = ['json', 'html', 'csv']
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    exported: Dict[str, List[Path]] = {fmt: [] for fmt in formats}
    
    for result in results:
        exporter = Exporter(result)
        safe_name = result.title.lower().replace(' ', '_')[:30]
        
        for fmt in formats:
            try:
                file_path = output_path / f"{safe_name}.{fmt}"
                exported[fmt].append(exporter.export(str(file_path), fmt))
            except ExportError as e:
                logger.error(f"Failed to export {result.title} to {fmt}: {e}")
    
    logger.info(f"Batch exported {len(results)} files to {output_path}")
    return exported


def export_comparison(
    results: List[AnalysisResult],
    path: str,
    format: str = 'json'
) -> Path:
    """
    Export a comparison of multiple books.
    
    Args:
        results: List of analysis results to compare
        path: Output file path
        format: Export format
        
    Returns:
        Path to exported file
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if format == 'json':
        comparison = compare_books(results)
        comparison['exported_at'] = datetime.now().isoformat()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)
    else:
        content = generate_comparison_report(results, format)
        output_path.write_text(content, encoding='utf-8')
    
    logger.info(f"Exported comparison to: {output_path}")
    return output_path
