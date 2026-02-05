"""
BookBot Sentiment Analysis - Text sentiment and emotion analysis.

Provides sentiment analysis capabilities using TextBlob or NLTK VADER,
including polarity, subjectivity, and chapter-by-chapter analysis.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Try importing sentiment analysis libraries
try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    logger.debug("TextBlob not installed. Sentiment analysis limited.")

try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
    # Try to ensure vader_lexicon is downloaded
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
        HAS_VADER = True
    except LookupError:
        try:
            nltk.download('vader_lexicon', quiet=True)
            HAS_VADER = True
        except:
            HAS_VADER = False
except ImportError:
    HAS_VADER = False
    logger.debug("NLTK VADER not installed. VADER sentiment analysis disabled.")


class SentimentError(Exception):
    """Base exception for sentiment analysis errors."""
    pass


class SentimentUnavailableError(SentimentError):
    """Raised when no sentiment analysis library is available."""
    pass


@dataclass
class SentimentScore:
    """
    Container for sentiment analysis scores.
    
    Attributes:
        polarity: Score from -1 (negative) to 1 (positive)
        subjectivity: Score from 0 (objective) to 1 (subjective)
        compound: VADER compound score (-1 to 1) if available
        positive: Proportion of positive sentiment
        negative: Proportion of negative sentiment
        neutral: Proportion of neutral sentiment
        label: Human-readable sentiment label
    """
    polarity: float = 0.0
    subjectivity: float = 0.0
    compound: Optional[float] = None
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 0.0
    label: str = "neutral"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            'polarity': round(self.polarity, 4),
            'subjectivity': round(self.subjectivity, 4),
            'positive': round(self.positive, 4),
            'negative': round(self.negative, 4),
            'neutral': round(self.neutral, 4),
            'label': self.label,
        }
        if self.compound is not None:
            result['compound'] = round(self.compound, 4)
        return result


@dataclass
class SentimentResult:
    """
    Complete sentiment analysis result for a text.
    
    Attributes:
        overall: Overall sentiment scores for the entire text
        by_section: Sentiment scores by section/chapter
        emotional_arc: Sentiment progression through the text
        key_phrases: Most positive and negative phrases found
    """
    overall: SentimentScore = field(default_factory=SentimentScore)
    by_section: List[Dict] = field(default_factory=list)
    emotional_arc: List[float] = field(default_factory=list)
    key_phrases: Dict[str, List[str]] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'overall': self.overall.to_dict(),
            'by_section': self.by_section,
            'emotional_arc': [round(x, 4) for x in self.emotional_arc],
            'key_phrases': self.key_phrases,
        }


class SentimentAnalyzer:
    """
    Sentiment analyzer using TextBlob and/or NLTK VADER.
    
    TextBlob provides polarity (-1 to 1) and subjectivity (0 to 1).
    VADER provides positive, negative, neutral, and compound scores.
    
    Example:
        >>> analyzer = SentimentAnalyzer()
        >>> result = analyzer.analyze("I love this book! It's amazing.")
        >>> print(f"Sentiment: {result.overall.label}")
        Sentiment: positive
    """
    
    def __init__(self, use_vader: bool = True, use_textblob: bool = True):
        """
        Initialize the sentiment analyzer.
        
        Args:
            use_vader: Use NLTK VADER if available
            use_textblob: Use TextBlob if available
        """
        self.use_vader = use_vader and HAS_VADER
        self.use_textblob = use_textblob and HAS_TEXTBLOB
        
        if not self.use_vader and not self.use_textblob:
            logger.warning("No sentiment analysis library available")
        
        # Initialize VADER if available
        self._vader = None
        if self.use_vader:
            try:
                self._vader = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"Failed to initialize VADER: {e}")
                self.use_vader = False
    
    def is_available(self) -> bool:
        """Check if sentiment analysis is available."""
        return self.use_textblob or self.use_vader
    
    def _get_label(self, polarity: float) -> str:
        """Get human-readable sentiment label from polarity score."""
        if polarity >= 0.5:
            return "very positive"
        elif polarity >= 0.1:
            return "positive"
        elif polarity >= -0.1:
            return "neutral"
        elif polarity >= -0.5:
            return "negative"
        else:
            return "very negative"
    
    def _analyze_textblob(self, text: str) -> Tuple[float, float]:
        """Analyze sentiment using TextBlob."""
        if not self.use_textblob:
            return 0.0, 0.0
        
        blob = TextBlob(text)
        return blob.sentiment.polarity, blob.sentiment.subjectivity
    
    def _analyze_vader(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER."""
        if not self.use_vader or not self._vader:
            return {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0}
        
        return self._vader.polarity_scores(text)
    
    def analyze_text(self, text: str) -> SentimentScore:
        """
        Analyze sentiment of a text string.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentScore with polarity and subjectivity
        """
        if not self.is_available():
            return SentimentScore(label="unavailable")
        
        polarity = 0.0
        subjectivity = 0.0
        compound = None
        positive = 0.0
        negative = 0.0
        neutral = 1.0
        
        # TextBlob analysis
        if self.use_textblob:
            polarity, subjectivity = self._analyze_textblob(text)
        
        # VADER analysis
        if self.use_vader:
            vader_scores = self._analyze_vader(text)
            compound = vader_scores['compound']
            positive = vader_scores['pos']
            negative = vader_scores['neg']
            neutral = vader_scores['neu']
            
            # If no TextBlob, use VADER compound as polarity
            if not self.use_textblob:
                polarity = compound
        
        label = self._get_label(polarity)
        
        return SentimentScore(
            polarity=polarity,
            subjectivity=subjectivity,
            compound=compound,
            positive=positive,
            negative=negative,
            neutral=neutral,
            label=label,
        )
    
    def analyze_by_sections(
        self, 
        text: str, 
        section_size: int = 1000
    ) -> List[Dict]:
        """
        Analyze sentiment by text sections.
        
        Args:
            text: Full text to analyze
            section_size: Approximate words per section
            
        Returns:
            List of sentiment scores by section
        """
        words = text.split()
        sections = []
        
        for i in range(0, len(words), section_size):
            section_text = ' '.join(words[i:i + section_size])
            score = self.analyze_text(section_text)
            sections.append({
                'section': len(sections) + 1,
                'start_word': i,
                'end_word': min(i + section_size, len(words)),
                **score.to_dict()
            })
        
        return sections
    
    def get_emotional_arc(
        self, 
        text: str, 
        num_points: int = 20
    ) -> List[float]:
        """
        Get the emotional arc (sentiment progression) of the text.
        
        Args:
            text: Full text to analyze
            num_points: Number of points in the arc
            
        Returns:
            List of polarity scores representing emotional progression
        """
        words = text.split()
        section_size = max(100, len(words) // num_points)
        
        arc = []
        for i in range(0, len(words), section_size):
            section_text = ' '.join(words[i:i + section_size])
            score = self.analyze_text(section_text)
            arc.append(score.polarity)
            
            if len(arc) >= num_points:
                break
        
        return arc
    
    def find_key_phrases(
        self, 
        text: str, 
        num_phrases: int = 5
    ) -> Dict[str, List[str]]:
        """
        Find the most positive and negative sentences.
        
        Args:
            text: Text to analyze
            num_phrases: Number of phrases to return for each category
            
        Returns:
            Dictionary with 'positive' and 'negative' phrase lists
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Analyze each sentence
        scored = []
        for sentence in sentences[:500]:  # Limit for performance
            score = self.analyze_text(sentence)
            scored.append((sentence, score.polarity))
        
        # Sort and get extremes
        scored.sort(key=lambda x: x[1])
        
        return {
            'positive': [s for s, _ in scored[-num_phrases:][::-1]],
            'negative': [s for s, _ in scored[:num_phrases]],
        }
    
    def analyze(self, text: str, detailed: bool = True) -> SentimentResult:
        """
        Perform complete sentiment analysis on text.
        
        Args:
            text: Text to analyze
            detailed: Include section analysis and emotional arc
            
        Returns:
            SentimentResult with all analysis data
        """
        if not self.is_available():
            return SentimentResult(
                overall=SentimentScore(label="unavailable")
            )
        
        logger.info("Starting sentiment analysis...")
        
        # Overall sentiment
        overall = self.analyze_text(text)
        
        result = SentimentResult(overall=overall)
        
        if detailed:
            # Section-by-section analysis
            result.by_section = self.analyze_by_sections(text)
            
            # Emotional arc
            result.emotional_arc = self.get_emotional_arc(text)
            
            # Key phrases
            result.key_phrases = self.find_key_phrases(text)
        
        logger.info(f"Sentiment analysis complete: {overall.label}")
        return result


def analyze_sentiment(text: str, detailed: bool = False) -> SentimentResult:
    """
    Convenience function to analyze text sentiment.
    
    Args:
        text: Text to analyze
        detailed: Include detailed analysis (sections, arc, phrases)
        
    Returns:
        SentimentResult with analysis data
        
    Example:
        >>> result = analyze_sentiment("This is a wonderful day!")
        >>> print(f"Polarity: {result.overall.polarity:.2f}")
        Polarity: 0.75
    """
    analyzer = SentimentAnalyzer()
    return analyzer.analyze(text, detailed=detailed)


def get_sentiment_availability() -> Dict[str, bool]:
    """
    Check which sentiment analysis libraries are available.
    
    Returns:
        Dictionary mapping library names to availability
    """
    return {
        'textblob': HAS_TEXTBLOB,
        'vader': HAS_VADER,
        'any': HAS_TEXTBLOB or HAS_VADER,
    }
