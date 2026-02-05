"""
Tests for BookBot report module.
"""

import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bookbot.analyzer import analyze_text
from bookbot.report import ReportGenerator, generate_comparison_report


class TestReportGenerator:
    """Tests for the ReportGenerator class."""
    
    @pytest.fixture
    def sample_result(self):
        """Create a sample analysis result."""
        return analyze_text(
            "The quick brown fox jumps over the lazy dog. "
            "This is a sample text for testing reports. "
            "It should have enough content to generate meaningful statistics."
        )
    
    def test_generate_text(self, sample_result):
        """Test text report generation."""
        reporter = ReportGenerator(sample_result, use_color=False)
        text = reporter.generate_text()
        
        assert "BOOKBOT ANALYSIS REPORT" in text
        assert "Word Count" in text
        assert str(sample_result.word_count) in text
    
    def test_generate_json(self, sample_result):
        """Test JSON report generation."""
        reporter = ReportGenerator(sample_result)
        json_str = reporter.generate_json()
        
        # Should be valid JSON
        data = json.loads(json_str)
        
        assert 'statistics' in data
        assert data['statistics']['word_count'] == sample_result.word_count
    
    def test_generate_csv(self, sample_result):
        """Test CSV report generation."""
        reporter = ReportGenerator(sample_result)
        csv_str = reporter.generate_csv()
        
        assert "Metric,Value" in csv_str
        assert "Word Count" in csv_str
    
    def test_generate_html(self, sample_result):
        """Test HTML report generation."""
        reporter = ReportGenerator(sample_result)
        html = reporter.generate_html()
        
        assert "<!DOCTYPE html>" in html
        assert sample_result.title in html
        assert "Chart" in html  # Should include chart.js
    
    def test_save_report(self, sample_result, tmp_path):
        """Test saving reports to files."""
        reporter = ReportGenerator(sample_result)
        
        # Save as JSON
        json_path = tmp_path / "report.json"
        saved = reporter.save(str(json_path), format='json')
        
        assert saved.exists()
        data = json.loads(saved.read_text())
        assert data['statistics']['word_count'] == sample_result.word_count


class TestComparisonReport:
    """Tests for comparison report generation."""
    
    def test_comparison_report_text(self):
        """Test text comparison report."""
        result1 = analyze_text("Short text here")
        result1.title = "Book One"
        
        result2 = analyze_text("Another longer text with more words")
        result2.title = "Book Two"
        
        report = generate_comparison_report([result1, result2], 'text')
        
        assert "COMPARISON REPORT" in report
        assert "Book One" in report
        assert "Book Two" in report
    
    def test_comparison_report_json(self):
        """Test JSON comparison report."""
        result1 = analyze_text("First book content")
        result2 = analyze_text("Second book content")
        
        report = generate_comparison_report([result1, result2], 'json')
        data = json.loads(report)
        
        assert 'books' in data
        assert len(data['books']) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
