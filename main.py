#!/usr/bin/env python3
"""
BookBot - Professional Text Analysis Tool

A command-line application for analyzing books and documents,
providing comprehensive statistics, visualizations, and reports.

Usage:
    bookbot books/frankenstein.txt
    bookbot books/*.txt --compare
    bookbot book.txt -f html -o report.html --visualize

Author: David Benito Campo
Version: 1.0.0
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from bookbot.analyzer import BookAnalyzer, AnalysisResult, compare_books
from bookbot.report import ReportGenerator, generate_comparison_report
from bookbot.exporter import Exporter, batch_export, export_comparison
from bookbot.visualizer import Visualizer
from bookbot.utils import setup_logging, find_books, format_duration

__version__ = "1.0.0"


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='bookbot',
        description='📚 BookBot - Professional Text Analysis Tool',
        epilog='Example: bookbot books/frankenstein.txt -f html -o report.html',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Positional arguments
    parser.add_argument(
        'files',
        nargs='*',
        help='Book files to analyze (supports glob patterns)'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '-o', '--output',
        metavar='PATH',
        help='Output file or directory path'
    )
    output_group.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'csv', 'html', 'md'],
        default='text',
        help='Output format (default: text)'
    )
    output_group.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored terminal output'
    )
    
    # Analysis options
    analysis_group = parser.add_argument_group('Analysis Options')
    analysis_group.add_argument(
        '--compare',
        action='store_true',
        help='Compare multiple books'
    )
    analysis_group.add_argument(
        '--sentiment', '-S',
        action='store_true',
        help='Include sentiment analysis (requires textblob)'
    )
    analysis_group.add_argument(
        '--include-stopwords',
        action='store_true',
        help='Include stop words in word frequency'
    )
    analysis_group.add_argument(
        '--top-words',
        type=int,
        default=20,
        metavar='N',
        help='Number of top words to show (default: 20)'
    )

    
    # Visualization options
    viz_group = parser.add_argument_group('Visualization Options')
    viz_group.add_argument(
        '--visualize', '-V',
        action='store_true',
        help='Generate visualization charts'
    )
    viz_group.add_argument(
        '--wordcloud',
        action='store_true',
        help='Generate word cloud image'
    )
    
    # Other options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress output (only errors)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interactive mode'
    )
    
    return parser


def analyze_single_file(
    file_path: str,
    args: argparse.Namespace
) -> Optional[AnalysisResult]:
    """
    Analyze a single file and handle output.
    
    Args:
        file_path: Path to the file to analyze
        args: Command line arguments
        
    Returns:
        Analysis result or None on error
    """
    try:
        analyzer = BookAnalyzer(
            file_path,
            include_stop_words=args.include_stopwords
        )
        result = analyzer.analyze(include_sentiment=args.sentiment)
        
        if args.verbose:
            print(f"✓ Analyzed: {result.title}")
            print(f"  Words: {result.word_count:,}")
            print(f"  Reading time: {format_duration(result.reading_time_minutes)}")
            if result.sentiment:
                print(f"  Sentiment: {result.sentiment['overall']['label']}")
        
        return result

        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return None


def handle_output(
    results: List[AnalysisResult],
    args: argparse.Namespace
) -> None:
    """
    Handle output generation based on arguments.
    
    Args:
        results: List of analysis results
        args: Command line arguments
    """
    if not results:
        return
    
    # Comparison mode
    if args.compare and len(results) > 1:
        if args.output:
            export_comparison(results, args.output, args.format)
            print(f"✓ Saved comparison to: {args.output}")
        else:
            report = generate_comparison_report(results, args.format)
            print(report)
        return
    
    # Single or multiple files without comparison
    for result in results:
        reporter = ReportGenerator(
            result,
            use_color=not args.no_color,
            verbose=args.verbose
        )
        
        if args.output:
            output_path = Path(args.output)
            
            # Check if output is a directory or file
            if output_path.is_dir() or (not output_path.suffix and len(results) > 1):
                # Output is a directory
                output_path.mkdir(parents=True, exist_ok=True)
                safe_name = result.title.lower().replace(' ', '_')[:30]
                file_path = output_path / f"{safe_name}.{args.format}"
            else:
                file_path = output_path
                file_path.parent.mkdir(parents=True, exist_ok=True)
            
            exporter = Exporter(result)
            exporter.export(str(file_path), args.format)
            print(f"✓ Saved report to: {file_path}")
        else:
            # Print to stdout
            if args.format == 'text':
                print(reporter.generate_text())
            elif args.format == 'json':
                print(reporter.generate_json())
            elif args.format == 'csv':
                print(reporter.generate_csv())
            elif args.format == 'html':
                print(reporter.generate_html())
            elif args.format == 'md':
                # Use exporter for markdown
                exporter = Exporter(result)
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                    exporter.to_markdown(f.name)
                    print(Path(f.name).read_text())
        
        # Generate visualizations if requested
        if args.visualize or args.wordcloud:
            if args.output:
                output_path = Path(args.output)
                if output_path.is_dir():
                    viz_dir = output_path
                else:
                    viz_dir = output_path.parent
            else:
                viz_dir = Path('.')
            
            viz = Visualizer(result)
            
            try:
                if args.visualize:
                    saved = viz.save_all(viz_dir / 'visualizations')
                    for path in saved:
                        print(f"✓ Generated: {path}")
                elif args.wordcloud:
                    safe_title = result.title.lower().replace(' ', '_')[:20]
                    path = viz.word_cloud(
                        save_path=viz_dir / f"{safe_title}_wordcloud.png"
                    )
                    print(f"✓ Generated word cloud: {path}")
            except Exception as e:
                print(f"⚠ Visualization error: {e}", file=sys.stderr)



def interactive_mode() -> None:
    """Run in interactive mode."""
    print("📚 BookBot Interactive Mode")
    print("=" * 40)
    print("Commands: analyze <file>, compare <files>, quit")
    print()
    
    while True:
        try:
            user_input = input("bookbot> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        parts = user_input.split()
        command = parts[0].lower()
        
        if command in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break
        elif command == 'analyze' and len(parts) > 1:
            file_path = parts[1]
            try:
                analyzer = BookAnalyzer(file_path)
                result = analyzer.analyze()
                reporter = ReportGenerator(result, use_color=True)
                print(reporter.generate_text())
            except Exception as e:
                print(f"Error: {e}")
        elif command == 'compare' and len(parts) > 2:
            results = []
            for fp in parts[1:]:
                try:
                    analyzer = BookAnalyzer(fp)
                    results.append(analyzer.analyze())
                except Exception as e:
                    print(f"Error with {fp}: {e}")
            if results:
                print(generate_comparison_report(results, 'text'))
        elif command == 'help':
            print("Commands:")
            print("  analyze <file>      - Analyze a book file")
            print("  compare <f1> <f2>   - Compare multiple books")
            print("  quit                - Exit interactive mode")
        else:
            print(f"Unknown command: {command}")
            print("Type 'help' for available commands")


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    if args.quiet:
        log_level = logging.ERROR
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING
    
    setup_logging(level=log_level)
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return 0
    
    # Check for files
    if not args.files:
        parser.print_help()
        print("\n❌ Error: No files specified")
        return 1
    
    # Expand glob patterns and find files
    files: List[str] = []
    for pattern in args.files:
        path = Path(pattern)
        if path.is_file():
            files.append(str(path))
        elif path.is_dir():
            # Find text files in directory
            found = find_books(path)
            files.extend(str(f) for f in found)
        else:
            # Try glob pattern
            from glob import glob
            matches = glob(pattern)
            files.extend(matches)
    
    if not files:
        print(f"❌ Error: No files found matching: {args.files}")
        return 1
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    files = unique_files
    
    if not args.quiet:
        print(f"📚 BookBot v{__version__}")
        print(f"   Analyzing {len(files)} file(s)...")
        print()
    
    # Analyze files
    results: List[AnalysisResult] = []
    for file_path in files:
        result = analyze_single_file(file_path, args)
        if result:
            results.append(result)
    
    if not results:
        print("❌ No files were successfully analyzed")
        return 1
    
    # Handle output
    handle_output(results, args)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
