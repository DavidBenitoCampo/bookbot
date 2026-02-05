"""
Tests for BookBot analyzer module.

Comprehensive test suite covering:
- Basic text analysis
- Character frequency counting
- Word frequency counting
- Edge cases and error handling
- Performance tests
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from bookbot.analyzer import (
    BookAnalyzer,
    AnalysisResult,
    analyze_text,
    compare_books,
    AnalyzerError,
    EmptyFileError,
)


class TestAnalyzeText:
    """Tests for the analyze_text function."""
    
    def test_basic_analysis(self):
        """Test basic text analysis."""
        text = "Hello world. This is a test."
        result = analyze_text(text)
        
        assert result.word_count == 6
        assert result.sentence_count == 2
        assert result.character_count == len(text)
    
    def test_word_count(self):
        """Test accurate word counting."""
        text = "one two three four five"
        result = analyze_text(text)
        
        assert result.word_count == 5
    
    def test_character_frequency(self):
        """Test character frequency counting."""
        text = "aaa bb c"
        result = analyze_text(text)
        
        assert result.char_frequency['a'] == 3
        assert result.char_frequency['b'] == 2
        assert result.char_frequency['c'] == 1
    
    def test_character_frequency_case_insensitive(self):
        """Test that character counting is case-insensitive."""
        text = "AaAa BbBb"
        result = analyze_text(text)
        
        assert result.char_frequency['a'] == 4
        assert result.char_frequency['b'] == 4
    
    def test_unique_word_count(self):
        """Test unique word counting."""
        text = "hello hello world world world"
        result = analyze_text(text)
        
        assert result.word_count == 5
        assert result.unique_word_count == 2
    
    def test_vocabulary_richness(self):
        """Test vocabulary richness calculation."""
        text = "unique words every single one"
        result = analyze_text(text)
        
        # All words are unique, richness should be 1.0
        assert result.vocabulary_richness == 1.0
    
    def test_average_word_length(self):
        """Test average word length calculation."""
        text = "aa bbbb cccccc"  # lengths: 2, 4, 6 -> avg = 4
        result = analyze_text(text)
        
        assert result.average_word_length == 4.0
    
    def test_sentence_count(self):
        """Test sentence counting."""
        text = "First sentence. Second sentence! Third sentence?"
        result = analyze_text(text)
        
        assert result.sentence_count == 3
    
    def test_paragraph_count(self):
        """Test paragraph counting."""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        result = analyze_text(text)
        
        assert result.paragraph_count == 3
    
    def test_reading_time(self):
        """Test reading time estimation."""
        # 238 words = ~1 minute at average reading speed
        words = " ".join(["word"] * 238)
        result = analyze_text(words)
        
        assert 0.9 < result.reading_time_minutes < 1.1
    
    def test_empty_text_raises_error(self):
        """Test that empty text raises an error."""
        with pytest.raises(EmptyFileError):
            analyze_text("")
    
    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only text raises an error."""
        with pytest.raises(EmptyFileError):
            analyze_text("   \n\t  ")
    
    def test_special_characters_ignored_in_char_count(self):
        """Test that special characters are not counted in char frequency."""
        text = "hello! world? test."
        result = analyze_text(text)
        
        assert '!' not in result.char_frequency
        assert '?' not in result.char_frequency
        assert '.' not in result.char_frequency
    
    def test_contractions_handled(self):
        """Test that contractions are handled correctly."""
        text = "I'm can't won't don't"
        result = analyze_text(text)
        
        # Contractions should be counted as words
        assert result.word_count == 4
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = analyze_text("Hello world")
        data = result.to_dict()
        
        assert 'statistics' in data
        assert 'char_frequency' in data
        assert 'top_words' in data
        assert data['statistics']['word_count'] == 2


class TestBookAnalyzer:
    """Tests for the BookAnalyzer class."""
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a sample text file for testing."""
        content = """The Project Gutenberg EBook of Frankenstein

This is a sample text for testing the BookBot analyzer.
It contains multiple sentences and paragraphs.

This is the second paragraph. It has more content.
The analyzer should correctly count words, sentences, and paragraphs.

Here is the third paragraph with some repeated words.
Words like the, and, is are common stop words.
"""
        file_path = tmp_path / "sample.txt"
        file_path.write_text(content)
        return file_path
    
    @pytest.fixture
    def empty_file(self, tmp_path):
        """Create an empty file for testing."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")
        return file_path
    
    def test_analyze_file(self, sample_file):
        """Test analyzing a file."""
        analyzer = BookAnalyzer(str(sample_file))
        result = analyzer.analyze()
        
        assert result.word_count > 0
        assert result.sentence_count > 0
        assert result.paragraph_count >= 3
    
    def test_file_not_found(self):
        """Test error handling for missing files."""
        analyzer = BookAnalyzer("nonexistent_file.txt")
        
        with pytest.raises(Exception):  # FileNotFoundError
            analyzer.analyze()
    
    def test_empty_file_error(self, empty_file):
        """Test error handling for empty files."""
        analyzer = BookAnalyzer(str(empty_file))
        
        with pytest.raises(EmptyFileError):
            analyzer.analyze()
    
    def test_title_extraction(self, sample_file):
        """Test title extraction from text."""
        analyzer = BookAnalyzer(str(sample_file))
        result = analyzer.analyze()
        
        # Should extract title from first line or use filename
        assert result.title != ""
    
    def test_caching(self, sample_file):
        """Test that results are cached."""
        analyzer = BookAnalyzer(str(sample_file))
        
        result1 = analyzer.analyze()
        result2 = analyzer.analyze()
        
        # Should return the same cached result
        assert result1 is result2
    
    def test_include_stop_words(self, sample_file):
        """Test including stop words in analysis."""
        analyzer_with = BookAnalyzer(str(sample_file), include_stop_words=True)
        analyzer_without = BookAnalyzer(str(sample_file), include_stop_words=False)
        
        result_with = analyzer_with.analyze()
        result_without = analyzer_without.analyze()
        
        # Word frequency should be different
        assert len(result_with.word_frequency) >= len(result_without.word_frequency)


class TestCompareBooks:
    """Tests for book comparison functionality."""
    
    def test_compare_single_book(self):
        """Test comparison with single book."""
        result = analyze_text("Single book content here")
        comparison = compare_books([result])
        
        assert len(comparison['books']) == 1
    
    def test_compare_multiple_books(self):
        """Test comparison with multiple books."""
        result1 = analyze_text("Short book with few words")
        result1.title = "Short Book"
        
        result2 = analyze_text("Longer book with many more words to increase the count significantly")
        result2.title = "Long Book"
        
        comparison = compare_books([result1, result2])
        
        assert len(comparison['books']) == 2
        assert 'rankings' in comparison
        assert comparison['rankings']['by_length'][0] == "Long Book"
    
    def test_compare_empty_list(self):
        """Test comparison with empty list."""
        comparison = compare_books([])
        
        assert comparison == {}
    
    def test_comparison_averages(self):
        """Test that comparison includes averages."""
        result1 = analyze_text("One two three four five")
        result2 = analyze_text("Six seven eight nine ten eleven twelve")
        
        comparison = compare_books([result1, result2])
        
        assert 'averages' in comparison
        assert comparison['averages']['word_count'] == 6.0  # (5 + 7) / 2


class TestEdgeCases:
    """Tests for edge cases and unusual inputs."""
    
    def test_unicode_text(self):
        """Test handling of unicode text."""
        text = "Café résumé naïve 日本語 中文"
        result = analyze_text(text)
        
        # Should handle unicode without errors
        assert result.word_count > 0
    
    def test_very_long_word(self):
        """Test handling of very long words."""
        long_word = "a" * 1000
        text = f"Short words and {long_word} mixed"
        result = analyze_text(text)
        
        assert result.word_count == 5
    
    def test_numbers_in_text(self):
        """Test that numbers are not counted as words."""
        text = "There are 100 apples and 50 oranges"
        result = analyze_text(text)
        
        # Numbers should not be in word frequency
        assert '100' not in result.word_frequency
        assert '50' not in result.word_frequency
    
    def test_hyphenated_words(self):
        """Test handling of hyphenated words."""
        text = "well-known self-esteem twenty-one"
        result = analyze_text(text)
        
        # Hyphenated words may be split or kept whole depending on implementation
        assert result.word_count >= 3


class TestAnalysisResult:
    """Tests for the AnalysisResult dataclass."""
    
    def test_default_values(self):
        """Test default values in AnalysisResult."""
        result = AnalysisResult(file_path="test.txt")
        
        assert result.word_count == 0
        assert result.char_frequency == {}
        assert result.top_words == []
    
    def test_to_dict_structure(self):
        """Test the structure of to_dict output."""
        result = analyze_text("Test content here")
        data = result.to_dict()
        
        # Check required keys
        assert 'file_path' in data
        assert 'title' in data
        assert 'statistics' in data
        assert 'char_frequency' in data
        assert 'top_words' in data
        
        # Check statistics structure
        stats = data['statistics']
        assert 'word_count' in stats
        assert 'unique_word_count' in stats
        assert 'vocabulary_richness' in stats


# Performance tests (marked for optional running)
class TestPerformance:
    """Performance tests for large texts."""
    
    @pytest.mark.slow
    def test_large_text_performance(self):
        """Test performance with large text."""
        # Generate a large text (~100k words)
        large_text = " ".join(["word"] * 100000)
        
        import time
        start = time.time()
        result = analyze_text(large_text)
        elapsed = time.time() - start
        
        assert result.word_count == 100000
        assert elapsed < 5.0  # Should complete in under 5 seconds


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
