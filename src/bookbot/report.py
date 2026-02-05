"""
BookBot Report Generator - Professional report formatting.

Generates analysis reports in multiple formats including
plain text, JSON, CSV, and HTML.
"""

import csv
import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .analyzer import AnalysisResult

logger = logging.getLogger(__name__)

# Try to import colorama for colored terminal output
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    
# Try to import tabulate for pretty tables
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


class ReportGenerator:
    """
    Generate formatted reports from analysis results.
    
    Supports multiple output formats:
    - text: Formatted plain text with optional colors
    - json: Structured JSON data
    - csv: Tabular CSV format
    - html: Interactive HTML report
    
    Example:
        >>> from bookbot.analyzer import BookAnalyzer
        >>> analyzer = BookAnalyzer("books/frankenstein.txt")
        >>> result = analyzer.analyze()
        >>> reporter = ReportGenerator(result)
        >>> print(reporter.generate_text())
    """
    
    def __init__(
        self, 
        result: AnalysisResult,
        use_color: bool = True,
        verbose: bool = False
    ):
        """
        Initialize the report generator.
        
        Args:
            result: The analysis result to generate reports for
            use_color: Enable colored terminal output
            verbose: Include detailed frequency data
        """
        self.result = result
        self.use_color = use_color and HAS_COLOR
        self.verbose = verbose
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if not self.use_color:
            return text
        colors = {
            'cyan': Fore.CYAN,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'red': Fore.RED,
            'white': Fore.WHITE,
            'bold': Style.BRIGHT,
            'reset': Style.RESET_ALL,
        }
        return f"{colors.get(color, '')}{text}{Style.RESET_ALL}"
    
    def generate_text(self) -> str:
        """
        Generate a formatted plain text report.
        
        Returns:
            Formatted text report string
        """
        r = self.result
        lines = []
        
        # Header
        header = f"═══ BOOKBOT ANALYSIS REPORT ═══"
        lines.append(self._colorize(header, 'cyan'))
        lines.append("")
        
        # Title and file info
        lines.append(self._colorize(f"📚 {r.title}", 'bold'))
        lines.append(f"   File: {r.file_path}")
        lines.append(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Reading Statistics
        lines.append(self._colorize("─── Reading Statistics ───", 'yellow'))
        lines.append(f"  📖 Word Count:        {r.word_count:,}")
        lines.append(f"  🔤 Unique Words:      {r.unique_word_count:,}")
        lines.append(f"  📝 Characters:        {r.character_count:,}")
        lines.append(f"  📄 Sentences:         {r.sentence_count:,}")
        lines.append(f"  📃 Paragraphs:        {r.paragraph_count:,}")
        lines.append(f"  ⏱️  Reading Time:      {r.reading_time_minutes:.1f} minutes")
        lines.append("")
        
        # Complexity Metrics
        lines.append(self._colorize("─── Complexity Metrics ───", 'green'))
        lines.append(f"  📏 Avg Word Length:   {r.average_word_length:.2f} characters")
        lines.append(f"  📐 Avg Sentence Len:  {r.average_sentence_length:.1f} words")
        lines.append(f"  🎯 Vocabulary Rich:   {r.vocabulary_richness:.2%}")
        lines.append("")
        
        # Top Words
        lines.append(self._colorize("─── Top 10 Words ───", 'magenta'))
        if HAS_TABULATE:
            table_data = [(word, count) for word, count in r.top_words[:10]]
            table = tabulate(table_data, headers=['Word', 'Count'], tablefmt='simple')
            for line in table.split('\n'):
                lines.append(f"  {line}")
        else:
            for i, (word, count) in enumerate(r.top_words[:10], 1):
                lines.append(f"  {i:2}. {word:<15} {count:,}")
        lines.append("")
        
        # Character Frequency (top 10)
        lines.append(self._colorize("─── Character Frequency ───", 'blue'))
        char_items = list(r.char_frequency.items())[:10]
        if HAS_TABULATE:
            table = tabulate(char_items, headers=['Char', 'Count'], tablefmt='simple')
            for line in table.split('\n'):
                lines.append(f"  {line}")
        else:
            for char, count in char_items:
                bar_length = int(count / max(r.char_frequency.values()) * 20)
                bar = '█' * bar_length
                lines.append(f"  '{char}': {count:>6,} {bar}")
        lines.append("")
        
        # Sentiment Analysis (if available)
        if r.sentiment:
            lines.append(self._colorize("─── Sentiment Analysis ───", 'red'))
            overall = r.sentiment.get('overall', {})
            polarity = overall.get('polarity', 0)
            subjectivity = overall.get('subjectivity', 0)
            label = overall.get('label', 'unknown')
            
            # Sentiment emoji based on label
            sentiment_emoji = {
                'very positive': '😊',
                'positive': '🙂',
                'neutral': '😐',
                'negative': '😕',
                'very negative': '😔',
            }.get(label, '❓')
            
            lines.append(f"  {sentiment_emoji} Overall:       {label.title()}")
            lines.append(f"  📊 Polarity:       {polarity:+.3f} (-1 to +1)")
            lines.append(f"  💭 Subjectivity:   {subjectivity:.3f} (0=objective, 1=subjective)")
            
            # Show positive/negative proportions if available
            if 'positive' in overall:
                lines.append(f"  ✅ Positive:       {overall['positive']:.1%}")
                lines.append(f"  ❌ Negative:       {overall['negative']:.1%}")
                lines.append(f"  ⚪ Neutral:        {overall['neutral']:.1%}")
            lines.append("")
        
        # Footer
        lines.append(self._colorize("═" * 35, 'cyan'))
        
        return '\n'.join(lines)
    
    def generate_json(self, indent: int = 2) -> str:
        """
        Generate a JSON report.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON formatted string
        """
        data = self.result.to_dict()
        data['generated_at'] = datetime.now().isoformat()
        data['generator'] = 'BookBot v1.0.0'
        return json.dumps(data, indent=indent, ensure_ascii=False)
    
    def generate_csv(self) -> str:
        """
        Generate a CSV report.
        
        Returns:
            CSV formatted string with statistics
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Statistics section
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Title', self.result.title])
        writer.writerow(['File Path', self.result.file_path])
        writer.writerow(['Word Count', self.result.word_count])
        writer.writerow(['Unique Words', self.result.unique_word_count])
        writer.writerow(['Character Count', self.result.character_count])
        writer.writerow(['Sentence Count', self.result.sentence_count])
        writer.writerow(['Paragraph Count', self.result.paragraph_count])
        writer.writerow(['Average Word Length', f"{self.result.average_word_length:.2f}"])
        writer.writerow(['Average Sentence Length', f"{self.result.average_sentence_length:.1f}"])
        writer.writerow(['Vocabulary Richness', f"{self.result.vocabulary_richness:.4f}"])
        writer.writerow(['Reading Time (min)', f"{self.result.reading_time_minutes:.1f}"])
        writer.writerow([])
        
        # Character frequency section
        writer.writerow(['Character', 'Frequency'])
        for char, count in self.result.char_frequency.items():
            writer.writerow([char, count])
        writer.writerow([])
        
        # Word frequency section
        writer.writerow(['Word', 'Frequency'])
        for word, count in self.result.top_words:
            writer.writerow([word, count])
        
        return output.getvalue()
    
    def generate_html(self, include_charts: bool = True) -> str:
        """
        Generate an interactive HTML report.
        
        Args:
            include_charts: Include Chart.js visualizations
            
        Returns:
            Complete HTML document string
        """
        r = self.result
        
        # Prepare chart data
        char_labels = [f"'{c}'" for c, _ in list(r.char_frequency.items())[:15]]
        char_values = [v for _, v in list(r.char_frequency.items())[:15]]
        word_labels = [w for w, _ in r.top_words[:10]]
        word_values = [v for _, v in r.top_words[:10]]
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BookBot Analysis: {r.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --accent: #06b6d4;
            --bg: #0f172a;
            --card: #1e293b;
            --text: #e2e8f0;
            --muted: #94a3b8;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 1rem;
        }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        .subtitle {{
            color: rgba(255,255,255,0.8);
            font-size: 1.1rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background: var(--card);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .card h3 {{
            color: var(--accent);
            margin-bottom: 1rem;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .stat:last-child {{
            border-bottom: none;
        }}
        .stat-label {{
            color: var(--muted);
        }}
        .stat-value {{
            font-weight: 600;
            color: var(--accent);
        }}
        .chart-container {{
            background: var(--card);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .chart-container h3 {{
            color: var(--accent);
            margin-bottom: 1rem;
        }}
        .chart-wrapper {{
            position: relative;
            height: 300px;
        }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--muted);
        }}
        .badge {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 {r.title}</h1>
            <p class="subtitle">Generated by BookBot on {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        </header>
        
        <div class="grid">
            <div class="card">
                <h3>📖 Reading Statistics</h3>
                <div class="stat">
                    <span class="stat-label">Total Words</span>
                    <span class="stat-value">{r.word_count:,}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Unique Words</span>
                    <span class="stat-value">{r.unique_word_count:,}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Characters</span>
                    <span class="stat-value">{r.character_count:,}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Sentences</span>
                    <span class="stat-value">{r.sentence_count:,}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Paragraphs</span>
                    <span class="stat-value">{r.paragraph_count:,}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>⏱️ Reading Time</h3>
                <div class="stat">
                    <span class="stat-label">Estimated Time</span>
                    <span class="stat-value">{r.reading_time_minutes:.0f} min</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Pages (est.)</span>
                    <span class="stat-value">{r.word_count // 250}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Hours</span>
                    <span class="stat-value">{r.reading_time_minutes / 60:.1f}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 Complexity Metrics</h3>
                <div class="stat">
                    <span class="stat-label">Avg Word Length</span>
                    <span class="stat-value">{r.average_word_length:.2f}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Avg Sentence Length</span>
                    <span class="stat-value">{r.average_sentence_length:.1f}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Vocabulary Richness</span>
                    <span class="stat-value">{r.vocabulary_richness:.2%}</span>
                </div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>🔤 Top 10 Words</h3>
            <div class="chart-wrapper">
                <canvas id="wordChart"></canvas>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📈 Character Frequency</h3>
            <div class="chart-wrapper">
                <canvas id="charChart"></canvas>
            </div>
        </div>
        
        <footer>
            <span class="badge">BookBot v1.0.0</span>
            <p style="margin-top: 1rem;">Text Analysis Report • {r.file_path}</p>
        </footer>
    </div>
    
    <script>
        const chartColors = {{
            primary: 'rgba(99, 102, 241, 0.8)',
            secondary: 'rgba(139, 92, 246, 0.8)',
            accent: 'rgba(6, 182, 212, 0.8)',
            border: 'rgba(99, 102, 241, 1)'
        }};
        
        // Word frequency chart
        new Chart(document.getElementById('wordChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(word_labels)},
                datasets: [{{
                    label: 'Word Count',
                    data: {json.dumps(word_values)},
                    backgroundColor: chartColors.primary,
                    borderColor: chartColors.border,
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ color: '#94a3b8' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        ticks: {{ color: '#94a3b8' }},
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        
        // Character frequency chart
        new Chart(document.getElementById('charChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(char_labels)},
                datasets: [{{
                    label: 'Character Count',
                    data: {json.dumps(char_values)},
                    backgroundColor: chartColors.accent,
                    borderColor: 'rgba(6, 182, 212, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ color: '#94a3b8' }},
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        ticks: {{ color: '#94a3b8' }},
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def save(
        self, 
        output_path: str, 
        format: str = 'text'
    ) -> Path:
        """
        Save the report to a file.
        
        Args:
            output_path: Path to save the report
            format: Report format (text, json, csv, html)
            
        Returns:
            Path to the saved file
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        generators = {
            'text': self.generate_text,
            'json': self.generate_json,
            'csv': self.generate_csv,
            'html': self.generate_html,
        }
        
        if format not in generators:
            raise ValueError(f"Unknown format: {format}. Use: {list(generators.keys())}")
        
        content = generators[format]()
        path.write_text(content, encoding='utf-8')
        
        logger.info(f"Saved {format} report to: {path}")
        return path


def generate_comparison_report(
    results: List[AnalysisResult],
    format: str = 'text'
) -> str:
    """
    Generate a comparison report for multiple books.
    
    Args:
        results: List of analysis results to compare
        format: Output format
        
    Returns:
        Formatted comparison report
    """
    if not results:
        return "No books to compare."
    
    if format == 'json':
        from .analyzer import compare_books
        data = compare_books(results)
        return json.dumps(data, indent=2)
    
    # Text format comparison
    lines = []
    lines.append("═══ BOOKBOT COMPARISON REPORT ═══")
    lines.append("")
    lines.append(f"Comparing {len(results)} books:")
    lines.append("")
    
    # Table of statistics
    headers = ['Book', 'Words', 'Unique', 'Richness', 'Avg Word', 'Read Time']
    rows = []
    for r in results:
        rows.append([
            r.title[:25] + '...' if len(r.title) > 25 else r.title,
            f"{r.word_count:,}",
            f"{r.unique_word_count:,}",
            f"{r.vocabulary_richness:.2%}",
            f"{r.average_word_length:.2f}",
            f"{r.reading_time_minutes:.0f}m",
        ])
    
    if HAS_TABULATE:
        lines.append(tabulate(rows, headers=headers, tablefmt='grid'))
    else:
        # Simple text table
        lines.append(' | '.join(headers))
        lines.append('-' * 80)
        for row in rows:
            lines.append(' | '.join(row))
    
    lines.append("")
    lines.append("═" * 35)
    
    return '\n'.join(lines)
