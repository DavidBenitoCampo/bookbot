"""
BookBot Analyzer - Core text analysis engine.

Provides comprehensive text analysis capabilities for books and documents,
including word/character frequency, reading statistics, and vocabulary metrics.
"""

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Common English stop words to filter out for meaningful word analysis
STOP_WORDS = frozenset({
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
    'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
    'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
    'we', 'they', 'what', 'which', 'who', 'whom', 'when', 'where', 'why',
    'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'just', 'also', 'now', 'here', 'there', 'then', 'once',
    'if', 'because', 'until', 'while', 'about', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further',
    'him', 'his', 'her', 'their', 'my', 'your', 'our', 'me', 'us', 'them',
})

# Average reading speed in words per minute
AVERAGE_READING_SPEED = 238


class AnalyzerError(Exception):
    """Base exception for analyzer errors."""
    pass


class FileNotFoundError(AnalyzerError):
    """Raised when a book file cannot be found."""
    pass


class EmptyFileError(AnalyzerError):
    """Raised when a book file is empty."""
    pass


@dataclass
class AnalysisResult:
    """
    Container for all text analysis results.
    
    Attributes:
        file_path: Path to the analyzed file
        title: Extracted or inferred title of the book
        word_count: Total number of words
        unique_word_count: Number of unique words
        character_count: Total characters (including spaces)
        character_count_no_spaces: Characters excluding spaces
        sentence_count: Number of sentences
        paragraph_count: Number of paragraphs
        average_word_length: Mean word length
        average_sentence_length: Mean words per sentence
        vocabulary_richness: Unique words / total words ratio
        reading_time_minutes: Estimated reading time
        char_frequency: Character frequency distribution
        word_frequency: Word frequency distribution (excluding stop words)
        top_words: Most common meaningful words
        sentiment: Sentiment analysis results (if available)
    """
    file_path: str
    title: str = ""
    word_count: int = 0
    unique_word_count: int = 0
    character_count: int = 0
    character_count_no_spaces: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    average_word_length: float = 0.0
    average_sentence_length: float = 0.0
    vocabulary_richness: float = 0.0
    reading_time_minutes: float = 0.0
    char_frequency: Dict[str, int] = field(default_factory=dict)
    word_frequency: Dict[str, int] = field(default_factory=dict)
    top_words: List[Tuple[str, int]] = field(default_factory=list)
    sentiment: Optional[Dict] = None
    
    def to_dict(self) -> dict:
        """Convert the analysis result to a dictionary."""
        result = {
            'file_path': self.file_path,
            'title': self.title,
            'statistics': {
                'word_count': self.word_count,
                'unique_word_count': self.unique_word_count,
                'character_count': self.character_count,
                'character_count_no_spaces': self.character_count_no_spaces,
                'sentence_count': self.sentence_count,
                'paragraph_count': self.paragraph_count,
                'average_word_length': round(self.average_word_length, 2),
                'average_sentence_length': round(self.average_sentence_length, 2),
                'vocabulary_richness': round(self.vocabulary_richness, 4),
                'reading_time_minutes': round(self.reading_time_minutes, 1),
            },
            'char_frequency': dict(sorted(
                self.char_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )),
            'top_words': self.top_words,
        }
        if self.sentiment:
            result['sentiment'] = self.sentiment
        return result



class BookAnalyzer:
    """
    Comprehensive text analyzer for books and documents.
    
    Provides detailed statistical analysis including word frequency,
    character distribution, reading metrics, and vocabulary analysis.
    
    Example:
        >>> analyzer = BookAnalyzer("books/frankenstein.txt")
        >>> result = analyzer.analyze()
        >>> print(f"Words: {result.word_count}")
        >>> print(f"Reading time: {result.reading_time_minutes:.1f} min")
    """
    
    def __init__(
        self, 
        file_path: str,
        encoding: str = 'utf-8',
        include_stop_words: bool = False
    ):
        """
        Initialize the analyzer with a file path.
        
        Args:
            file_path: Path to the file to analyze (txt, pdf, epub)
            encoding: File encoding for text files (default: utf-8)
            include_stop_words: Include stop words in word frequency
        """
        self.file_path = Path(file_path)
        self.encoding = encoding
        self.include_stop_words = include_stop_words
        self._text: Optional[str] = None
        self._result: Optional[AnalysisResult] = None
        
        logger.info(f"Initialized analyzer for: {self.file_path}")
    
    def _load_text(self) -> str:
        """
        Load and cache the text from the file.
        
        Supports multiple file formats through the readers module.
        
        Returns:
            The file contents as a string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            EmptyFileError: If the file is empty
        """
        if self._text is not None:
            return self._text
            
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Cannot find book file: {self.file_path}"
            )
        
        # Use multi-format reader
        try:
            from bookbot.readers import read_file, UnsupportedFormatError
            self._text = read_file(str(self.file_path), encoding=self.encoding)
        except UnsupportedFormatError:
            # Fall back to direct text reading for unknown formats
            try:
                self._text = self.file_path.read_text(encoding=self.encoding)
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 decode failed, trying latin-1")
                self._text = self.file_path.read_text(encoding='latin-1')
        except ImportError:
            # readers module not available, use basic text reading
            try:
                self._text = self.file_path.read_text(encoding=self.encoding)
            except UnicodeDecodeError:
                logger.warning(f"UTF-8 decode failed, trying latin-1")
                self._text = self.file_path.read_text(encoding='latin-1')
        
        if not self._text.strip():
            raise EmptyFileError(
                f"Book file is empty: {self.file_path}"
            )
        
        logger.debug(f"Loaded {len(self._text)} characters from file")
        return self._text

    
    def _extract_title(self, text: str) -> str:
        """
        Attempt to extract the book title from the text.
        
        Looks for common title patterns or uses the filename.
        """
        # Try to find a title in the first few lines
        lines = text.split('\n')[:20]
        for line in lines:
            line = line.strip()
            # Skip empty lines and common header text
            if not line or line.lower().startswith(('the project', 'copyright', 'title:')):
                continue
            # Check if it looks like a title (short, capitalized)
            if len(line) < 100 and line[0].isupper():
                # Clean up the title
                title = re.sub(r'[_*#]', '', line).strip()
                if title:
                    return title
        
        # Fall back to filename
        return self.file_path.stem.replace('_', ' ').title()
    
    @lru_cache(maxsize=1)
    def _get_words(self) -> List[str]:
        """Get all words from the text (cached)."""
        text = self._load_text()
        # Extract words using regex (handles contractions properly)
        return re.findall(r"[a-zA-Z']+", text.lower())
    
    def _count_characters(self, text: str) -> Dict[str, int]:
        """
        Count the frequency of each alphabetic character.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary mapping characters to their counts
        """
        char_count: Dict[str, int] = {}
        for char in text.lower():
            if char.isalpha():
                char_count[char] = char_count.get(char, 0) + 1
        return dict(sorted(char_count.items(), key=lambda x: x[1], reverse=True))
    
    def _count_words(self, words: List[str]) -> Dict[str, int]:
        """
        Count word frequencies, optionally excluding stop words.
        
        Args:
            words: List of words to count
            
        Returns:
            Dictionary mapping words to their counts
        """
        if self.include_stop_words:
            return dict(Counter(words).most_common())
        else:
            filtered = [w for w in words if w not in STOP_WORDS and len(w) > 2]
            return dict(Counter(filtered).most_common())
    
    def _count_sentences(self, text: str) -> int:
        """Count the number of sentences in the text."""
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty sentences
        return len([s for s in sentences if s.strip()])
    
    def _count_paragraphs(self, text: str) -> int:
        """Count the number of paragraphs in the text."""
        # Paragraphs are separated by blank lines
        paragraphs = re.split(r'\n\s*\n', text)
        return len([p for p in paragraphs if p.strip()])
    
    def analyze(self, include_sentiment: bool = False) -> AnalysisResult:
        """
        Perform complete text analysis.
        
        Args:
            include_sentiment: Include sentiment analysis (requires textblob/nltk)
        
        Returns:
            AnalysisResult containing all computed metrics
        """
        if self._result is not None and not include_sentiment:
            return self._result
        
        logger.info(f"Starting analysis of {self.file_path}")
        
        text = self._load_text()
        words = self._get_words()
        
        # Basic counts
        word_count = len(words)
        unique_words = set(words)
        unique_word_count = len(unique_words)
        character_count = len(text)
        character_count_no_spaces = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
        sentence_count = self._count_sentences(text)
        paragraph_count = self._count_paragraphs(text)
        
        # Computed metrics
        average_word_length = sum(len(w) for w in words) / word_count if word_count else 0
        average_sentence_length = word_count / sentence_count if sentence_count else 0
        vocabulary_richness = unique_word_count / word_count if word_count else 0
        reading_time_minutes = word_count / AVERAGE_READING_SPEED
        
        # Frequency analysis
        char_frequency = self._count_characters(text)
        word_frequency = self._count_words(words)
        top_words = list(word_frequency.items())[:20]
        
        # Sentiment analysis (optional)
        sentiment_data = None
        if include_sentiment:
            try:
                from bookbot.sentiment import analyze_sentiment
                sentiment_result = analyze_sentiment(text, detailed=True)
                sentiment_data = sentiment_result.to_dict()
                logger.info(f"Sentiment: {sentiment_result.overall.label}")
            except ImportError:
                logger.warning("Sentiment analysis not available (install textblob)")
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")
        
        self._result = AnalysisResult(
            file_path=str(self.file_path),
            title=self._extract_title(text),
            word_count=word_count,
            unique_word_count=unique_word_count,
            character_count=character_count,
            character_count_no_spaces=character_count_no_spaces,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            average_word_length=average_word_length,
            average_sentence_length=average_sentence_length,
            vocabulary_richness=vocabulary_richness,
            reading_time_minutes=reading_time_minutes,
            char_frequency=char_frequency,
            word_frequency=word_frequency,
            top_words=top_words,
            sentiment=sentiment_data,
        )
        
        logger.info(f"Analysis complete: {word_count} words, {sentence_count} sentences")
        return self._result



def analyze_text(text: str, title: str = "Untitled") -> AnalysisResult:
    """
    Analyze text directly without reading from a file.
    
    This is a convenience function for analyzing text strings.
    
    Args:
        text: The text to analyze
        title: Optional title for the analysis result
        
    Returns:
        AnalysisResult containing all computed metrics
        
    Example:
        >>> result = analyze_text("Hello world! This is a test.")
        >>> print(result.word_count)
        6
    """
    # Create a temporary analyzer-like analysis
    if not text.strip():
        raise EmptyFileError("Cannot analyze empty text")
    
    words = re.findall(r"[a-zA-Z']+", text.lower())
    word_count = len(words)
    unique_words = set(words)
    unique_word_count = len(unique_words)
    
    # Character frequency
    char_count: Dict[str, int] = {}
    for char in text.lower():
        if char.isalpha():
            char_count[char] = char_count.get(char, 0) + 1
    char_frequency = dict(sorted(char_count.items(), key=lambda x: x[1], reverse=True))
    
    # Word frequency (excluding stop words)
    filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    word_frequency = dict(Counter(filtered_words).most_common())
    
    # Sentence and paragraph counts
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    paragraphs = re.split(r'\n\s*\n', text)
    paragraph_count = len([p for p in paragraphs if p.strip()])
    
    # Computed metrics
    average_word_length = sum(len(w) for w in words) / word_count if word_count else 0
    average_sentence_length = word_count / sentence_count if sentence_count else 0
    vocabulary_richness = unique_word_count / word_count if word_count else 0
    reading_time_minutes = word_count / AVERAGE_READING_SPEED
    
    character_count = len(text)
    character_count_no_spaces = len(text.replace(' ', '').replace('\n', '').replace('\t', ''))
    
    return AnalysisResult(
        file_path="<text>",
        title=title,
        word_count=word_count,
        unique_word_count=unique_word_count,
        character_count=character_count,
        character_count_no_spaces=character_count_no_spaces,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        average_word_length=average_word_length,
        average_sentence_length=average_sentence_length,
        vocabulary_richness=vocabulary_richness,
        reading_time_minutes=reading_time_minutes,
        char_frequency=char_frequency,
        word_frequency=word_frequency,
        top_words=list(word_frequency.items())[:20],
    )


def compare_books(results: List[AnalysisResult]) -> Dict:
    """
    Compare multiple book analysis results.
    
    Args:
        results: List of AnalysisResult objects to compare
        
    Returns:
        Dictionary with comparative statistics
    """
    if not results:
        return {}
    
    comparison = {
        'books': [],
        'rankings': {},
    }
    
    for result in results:
        comparison['books'].append({
            'title': result.title,
            'word_count': result.word_count,
            'vocabulary_richness': result.vocabulary_richness,
            'reading_time_minutes': result.reading_time_minutes,
            'average_word_length': result.average_word_length,
        })
    
    # Rankings
    by_length = sorted(results, key=lambda x: x.word_count, reverse=True)
    by_richness = sorted(results, key=lambda x: x.vocabulary_richness, reverse=True)
    by_complexity = sorted(results, key=lambda x: x.average_word_length, reverse=True)
    
    comparison['rankings'] = {
        'by_length': [r.title for r in by_length],
        'by_vocabulary_richness': [r.title for r in by_richness],
        'by_complexity': [r.title for r in by_complexity],
    }
    
    # Averages
    comparison['averages'] = {
        'word_count': sum(r.word_count for r in results) / len(results),
        'vocabulary_richness': sum(r.vocabulary_richness for r in results) / len(results),
        'average_word_length': sum(r.average_word_length for r in results) / len(results),
    }
    
    return comparison
