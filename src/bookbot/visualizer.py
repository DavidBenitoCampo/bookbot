"""
BookBot Visualizer - Chart and visualization generation.

Creates visual representations of text analysis including
bar charts, word clouds, and statistical graphs.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .analyzer import AnalysisResult

logger = logging.getLogger(__name__)

# Try to import visualization libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("matplotlib not installed. Visualization features disabled.")

try:
    from wordcloud import WordCloud
    HAS_WORDCLOUD = True
except ImportError:
    HAS_WORDCLOUD = False
    logger.warning("wordcloud not installed. Word cloud generation disabled.")


class VisualizerError(Exception):
    """Raised when visualization fails."""
    pass


class Visualizer:
    """
    Generate visualizations from text analysis results.
    
    Creates various charts and graphs including:
    - Character frequency bar charts
    - Word frequency bar charts
    - Word clouds
    - Reading statistics pie charts
    
    Example:
        >>> from bookbot.analyzer import BookAnalyzer
        >>> from bookbot.visualizer import Visualizer
        >>> analyzer = BookAnalyzer("books/frankenstein.txt")
        >>> result = analyzer.analyze()
        >>> viz = Visualizer(result)
        >>> viz.save_all("output/")
    """
    
    # Color scheme for charts
    COLORS = {
        'primary': '#6366f1',
        'secondary': '#8b5cf6',
        'accent': '#06b6d4',
        'success': '#10b981',
        'warning': '#f59e0b',
        'background': '#0f172a',
        'card': '#1e293b',
        'text': '#e2e8f0',
        'muted': '#94a3b8',
    }
    
    # Gradient colors for bar charts
    GRADIENT = [
        '#6366f1', '#7c3aed', '#8b5cf6', '#a855f7', '#c084fc',
        '#d8b4fe', '#e9d5ff', '#f3e8ff', '#faf5ff', '#fefce8',
    ]
    
    def __init__(
        self,
        result: AnalysisResult,
        style: str = 'dark',
        figsize: Tuple[int, int] = (12, 6)
    ):
        """
        Initialize the visualizer.
        
        Args:
            result: Analysis result to visualize
            style: Chart style ('dark' or 'light')
            figsize: Default figure size (width, height)
        """
        self.result = result
        self.style = style
        self.figsize = figsize
        
        if not HAS_MATPLOTLIB:
            logger.warning("Matplotlib not available. Charts cannot be generated.")
    
    def _setup_style(self):
        """Configure matplotlib style for dark theme."""
        if not HAS_MATPLOTLIB:
            return
            
        if self.style == 'dark':
            plt.style.use('dark_background')
            plt.rcParams['figure.facecolor'] = self.COLORS['background']
            plt.rcParams['axes.facecolor'] = self.COLORS['card']
            plt.rcParams['text.color'] = self.COLORS['text']
            plt.rcParams['axes.labelcolor'] = self.COLORS['text']
            plt.rcParams['xtick.color'] = self.COLORS['muted']
            plt.rcParams['ytick.color'] = self.COLORS['muted']
        else:
            plt.style.use('seaborn-v0_8-whitegrid')
        
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.size'] = 11
    
    def char_frequency_chart(
        self,
        top_n: int = 15,
        save_path: Optional[str] = None,
        show: bool = False
    ) -> Optional[str]:
        """
        Generate a character frequency bar chart.
        
        Args:
            top_n: Number of characters to show
            save_path: Path to save the chart (optional)
            show: Display the chart interactively
            
        Returns:
            Path to saved file or None
        """
        if not HAS_MATPLOTLIB:
            raise VisualizerError("matplotlib is required for chart generation")
        
        self._setup_style()
        
        chars = list(self.result.char_frequency.keys())[:top_n]
        counts = list(self.result.char_frequency.values())[:top_n]
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create gradient bars
        colors = self.GRADIENT[:len(chars)]
        bars = ax.bar(chars, counts, color=colors, edgecolor='white', linewidth=0.5)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.annotate(
                f'{count:,}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=9,
                color=self.COLORS['text']
            )
        
        ax.set_xlabel('Character', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title(
            f'📊 Character Frequency in "{self.result.title}"',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        
        # Style improvements
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            logger.info(f"Saved character chart to: {path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return str(save_path) if save_path else None
    
    def word_frequency_chart(
        self,
        top_n: int = 15,
        save_path: Optional[str] = None,
        show: bool = False
    ) -> Optional[str]:
        """
        Generate a word frequency horizontal bar chart.
        
        Args:
            top_n: Number of words to show
            save_path: Path to save the chart (optional)
            show: Display the chart interactively
            
        Returns:
            Path to saved file or None
        """
        if not HAS_MATPLOTLIB:
            raise VisualizerError("matplotlib is required for chart generation")
        
        self._setup_style()
        
        words = [w for w, _ in self.result.top_words[:top_n]]
        counts = [c for _, c in self.result.top_words[:top_n]]
        
        # Reverse for horizontal bar chart (top word at top)
        words = words[::-1]
        counts = counts[::-1]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create gradient bars
        colors = self.GRADIENT[:len(words)][::-1]
        bars = ax.barh(words, counts, color=colors, edgecolor='white', linewidth=0.5)
        
        # Add value labels
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            ax.annotate(
                f'{count:,}',
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(5, 0),
                textcoords="offset points",
                ha='left', va='center',
                fontsize=9,
                color=self.COLORS['text']
            )
        
        ax.set_xlabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_ylabel('Word', fontsize=12, fontweight='bold')
        ax.set_title(
            f'📚 Top {top_n} Words in "{self.result.title}"',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            logger.info(f"Saved word chart to: {path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return str(save_path) if save_path else None
    
    def word_cloud(
        self,
        save_path: Optional[str] = None,
        show: bool = False,
        max_words: int = 100
    ) -> Optional[str]:
        """
        Generate a word cloud visualization.
        
        Args:
            save_path: Path to save the word cloud (optional)
            show: Display the word cloud interactively
            max_words: Maximum number of words to include
            
        Returns:
            Path to saved file or None
        """
        if not HAS_WORDCLOUD:
            raise VisualizerError("wordcloud package is required for word cloud generation")
        if not HAS_MATPLOTLIB:
            raise VisualizerError("matplotlib is required for visualization")
        
        self._setup_style()
        
        # Create word cloud
        wc = WordCloud(
            width=1200,
            height=600,
            max_words=max_words,
            background_color=self.COLORS['background'],
            colormap='viridis',
            prefer_horizontal=0.7,
            min_font_size=10,
            max_font_size=150,
        )
        
        # Generate from word frequencies
        wc.generate_from_frequencies(self.result.word_frequency)
        
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(
            f'☁️ Word Cloud: "{self.result.title}"',
            fontsize=16,
            fontweight='bold',
            pad=20,
            color=self.COLORS['text']
        )
        
        plt.tight_layout()
        
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=self.COLORS['background'])
            logger.info(f"Saved word cloud to: {path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return str(save_path) if save_path else None
    
    def statistics_chart(
        self,
        save_path: Optional[str] = None,
        show: bool = False
    ) -> Optional[str]:
        """
        Generate a summary statistics visualization.
        
        Creates a dashboard-style chart showing key metrics.
        
        Args:
            save_path: Path to save the chart (optional)
            show: Display the chart interactively
            
        Returns:
            Path to saved file or None
        """
        if not HAS_MATPLOTLIB:
            raise VisualizerError("matplotlib is required for chart generation")
        
        self._setup_style()
        
        r = self.result
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(
            f'📊 Analysis Dashboard: "{r.title}"',
            fontsize=16,
            fontweight='bold',
            y=0.98
        )
        
        # 1. Composition pie chart
        ax1 = axes[0, 0]
        sizes = [r.unique_word_count, r.word_count - r.unique_word_count]
        labels = ['Unique Words', 'Repeated Words']
        colors = [self.COLORS['primary'], self.COLORS['secondary']]
        explode = (0.05, 0)
        ax1.pie(
            sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=False, startangle=90,
            textprops={'color': self.COLORS['text']}
        )
        ax1.set_title('Word Composition', fontweight='bold')
        
        # 2. Key metrics bar
        ax2 = axes[0, 1]
        metrics = ['Words', 'Sentences', 'Paragraphs']
        values = [r.word_count, r.sentence_count, r.paragraph_count]
        bars = ax2.bar(metrics, values, color=[self.COLORS['primary'], self.COLORS['accent'], self.COLORS['success']])
        ax2.set_title('Document Structure', fontweight='bold')
        ax2.set_ylabel('Count')
        for bar, val in zip(bars, values):
            ax2.annotate(
                f'{val:,}',
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=10,
                fontweight='bold'
            )
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # 3. Complexity gauge (as horizontal bar)
        ax3 = axes[1, 0]
        complexity_metrics = ['Avg Word Length', 'Avg Sentence Length', 'Vocab Richness %']
        complexity_values = [
            r.average_word_length,
            r.average_sentence_length / 5,  # Normalize
            r.vocabulary_richness * 100
        ]
        colors = [self.COLORS['accent'], self.COLORS['warning'], self.COLORS['success']]
        bars = ax3.barh(complexity_metrics, complexity_values, color=colors)
        ax3.set_title('Complexity Metrics (normalized)', fontweight='bold')
        ax3.set_xlabel('Value')
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        
        # 4. Reading time comparison
        ax4 = axes[1, 1]
        time_labels = ['This Book', 'Avg Novel\n(80k words)', 'Short Story\n(7.5k words)']
        time_values = [r.reading_time_minutes, 336, 32]  # avg novel ~80k words
        colors = [self.COLORS['primary'], self.COLORS['muted'], self.COLORS['muted']]
        bars = ax4.bar(time_labels, time_values, color=colors)
        ax4.set_title('Reading Time Comparison', fontweight='bold')
        ax4.set_ylabel('Minutes')
        for bar, val in zip(bars, time_values):
            ax4.annotate(
                f'{val:.0f}m',
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=10
            )
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            logger.info(f"Saved statistics chart to: {path}")
        
        if show:
            plt.show()
        else:
            plt.close()
        
        return str(save_path) if save_path else None
    
    def save_all(
        self,
        output_dir: str,
        prefix: str = ""
    ) -> List[str]:
        """
        Generate and save all visualizations.
        
        Args:
            output_dir: Directory to save visualizations
            prefix: Optional filename prefix
            
        Returns:
            List of paths to saved files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        # Character frequency chart
        try:
            path = self.char_frequency_chart(
                save_path=output_path / f"{prefix}char_frequency.png"
            )
            if path:
                saved_files.append(path)
        except VisualizerError as e:
            logger.warning(f"Could not generate char chart: {e}")
        
        # Word frequency chart
        try:
            path = self.word_frequency_chart(
                save_path=output_path / f"{prefix}word_frequency.png"
            )
            if path:
                saved_files.append(path)
        except VisualizerError as e:
            logger.warning(f"Could not generate word chart: {e}")
        
        # Word cloud
        try:
            path = self.word_cloud(
                save_path=output_path / f"{prefix}wordcloud.png"
            )
            if path:
                saved_files.append(path)
        except VisualizerError as e:
            logger.warning(f"Could not generate word cloud: {e}")
        
        # Statistics dashboard
        try:
            path = self.statistics_chart(
                save_path=output_path / f"{prefix}statistics.png"
            )
            if path:
                saved_files.append(path)
        except VisualizerError as e:
            logger.warning(f"Could not generate statistics chart: {e}")
        
        logger.info(f"Saved {len(saved_files)} visualizations to: {output_path}")
        return saved_files
