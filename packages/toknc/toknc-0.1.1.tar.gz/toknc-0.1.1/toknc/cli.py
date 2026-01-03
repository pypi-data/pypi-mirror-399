#!/usr/bin/env python3
"""
Token Counter CLI - Estimates token usage for files in a directory
"""

import os
import sys
import argparse
import mimetypes
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
import re


# Fallback token estimation when tiktoken is not available
class SimpleTokenizer:
    """Simple tokenizer for fallback token estimation"""

    def __init__(self):
        # Rough estimation: ~1 token per 4 characters for English text
        # This is a very rough approximation
        self.chars_per_token = 4

    def encode(self, text: str) -> List[int]:
        """Simple tokenization - just return dummy tokens"""
        # Estimate token count based on character count
        estimated_tokens = max(1, len(text) // self.chars_per_token)
        return list(range(estimated_tokens))

    def decode(self, tokens: List[int]) -> str:
        """Not implemented for fallback"""
        return ""


class TokenCounter:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize token counter with specific model encoding"""
        self.model = model
        self.using_fallback = False

        try:
            import tiktoken

            try:
                self.encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback to cl100k_base (most common encoding)
                self.encoding = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            print(
                "Warning: tiktoken not available. Using rough token estimation.",
                file=sys.stderr,
            )
            print(
                "Install with: pip install tiktoken for accurate results.",
                file=sys.stderr,
            )
            self.encoding = SimpleTokenizer()
            self.using_fallback = True

    def count_tokens(self, text: str) -> int:
        """Count tokens in a given text"""
        if not text:
            return 0
        if self.using_fallback:
            return len(self.encoding.encode(text))
        return len(self.encoding.encode(text))

    def is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file"""
        # Check extension first
        text_extensions = {
            ".txt",
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".html",
            ".css",
            ".json",
            ".xml",
            ".yaml",
            ".yml",
            ".md",
            ".rst",
            ".sql",
            ".sh",
            ".bash",
            ".zsh",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".java",
            ".go",
            ".rs",
            ".php",
            ".rb",
            ".swift",
            ".kt",
            ".scala",
            ".r",
            ".m",
            ".pl",
            ".lua",
            ".vim",
            ".dockerfile",
        }

        if file_path.suffix.lower() in text_extensions:
            return True

        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith("text/"):
            return True

        # Try to read a small portion to check if it's text
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                # Check if contains null bytes (binary indicator)
                if b"\x00" in chunk:
                    return False
                # Try to decode as UTF-8
                try:
                    chunk.decode("utf-8")
                    return True
                except UnicodeDecodeError:
                    return False
        except (IOError, OSError):
            return False

        return False

    def read_file_content(self, file_path: Path) -> str:
        """Read content from a text file"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except (IOError, OSError, UnicodeDecodeError):
            return ""

    def analyze_directory(
        self,
        directory: Path,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict:
        """Analyze directory and return token statistics"""

        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")

        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        total_tokens = 0
        file_stats = []
        total_files = 0
        total_size = 0

        # Default include patterns (all files)
        if include_patterns is None:
            include_patterns = ["*"]

        # Default exclude patterns
        if exclude_patterns is None:
            exclude_patterns = [
                "*.git/*",
                "*.svn/*",
                "*.hg/*",
                "node_modules/*",
                "__pycache__/*",
                "*.pyc",
                "*.pyo",
                "*.pyd",
                ".DS_Store",
                "Thumbs.db",
            ]

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                # Check exclude patterns
                if any(file_path.match(pattern) for pattern in exclude_patterns):
                    continue

                # Check include patterns
                if not any(file_path.match(pattern) for pattern in include_patterns):
                    continue

                # Check if it's a text file
                if not self.is_text_file(file_path):
                    continue

                try:
                    content = self.read_file_content(file_path)
                    file_size = file_path.stat().st_size
                    tokens = self.count_tokens(content)

                    file_stats.append(
                        {
                            "path": str(file_path.relative_to(directory)),
                            "tokens": tokens,
                            "size_bytes": file_size,
                            "size_chars": len(content),
                        }
                    )

                    total_tokens += tokens
                    total_files += 1
                    total_size += file_size

                except Exception as e:
                    print(
                        f"Warning: Could not process {file_path}: {e}", file=sys.stderr
                    )

        # Sort files by token count (descending)
        file_stats.sort(key=lambda x: x["tokens"], reverse=True)

        return {
            "directory": str(directory),
            "model": self.model,
            "total_tokens": total_tokens,
            "total_files": total_files,
            "total_size_bytes": total_size,
            "using_fallback": self.using_fallback,
            "file_stats": file_stats,
        }


def format_size(size_bytes: int) -> str:
    """Format bytes in human readable format"""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def print_results(
    analysis: Dict,
    show_details: bool = False,
    top_files: int = 10,
    output_format: str = "text",
):
    """Print analysis results"""

    if output_format == "json":
        print(json.dumps(analysis, indent=2))
        return

    print(f"\n📊 Token Analysis for: {analysis['directory']}")
    print(f"🤖 Model: {analysis['model']}")
    if analysis.get("using_fallback", False):
        print(f"⚠️  Using rough token estimation (install tiktoken for accuracy)")
    print(f"📁 Total files: {analysis['total_files']}")
    print(f"🪙 Total tokens: {analysis['total_tokens']:,}")
    print(f"💾 Total size: {format_size(analysis['total_size_bytes'])}")

    # Context window comparisons
    print(f"\n📏 Context Window Usage:")
    print(
        f"\n{'Category':<12} {'Model Name':<25} {'Developer':<15} {'Window':<15} {'Usage':<20}"
    )
    print("-" * 87)

    models = [
        ("Private", "Gemini 3 Pro", "Google", 1000000),
        ("Private", "GPT-5.1 Codex Max", "OpenAI", 400000),
        ("Private", "Grok 4.1", "xAI", 256000),
        ("Private", "Claude 4.5 Opus", "Anthropic", 200000),
        ("Private", "GPT-5.2", "OpenAI", 400000),
        ("Open Source", "GLM-4.7", "Zhipu AI", 200000),
        ("Open Source", "Kimi K2 Thinking", "Moonshot AI", 262000),
        ("Open Source", "GPT-OSS-120B", "OpenAI", 131000),
        ("Open Source", "DeepSeek-V3.2", "DeepSeek", 128000),
        ("Open Source", "Mistral Large 2", "Mistral AI", 128000),
    ]

    def format_context_window(tokens):
        if tokens >= 1000000:
            return f"{tokens // 1000000}M"
        elif tokens >= 1000:
            return f"{tokens // 1000}k"
        else:
            return str(tokens)

    for category, model_name, developer, window in models:
        percentage = (analysis["total_tokens"] / window) * 100
        bar_length = min(15, int(percentage / 6.67))
        bar = "█" * bar_length + "░" * (15 - bar_length)
        formatted_window = format_context_window(window)
        print(
            f"{category:<12} {model_name:<25} {developer:<15} {formatted_window:<15} {bar} {percentage:.1f}%"
        )

    if analysis["file_stats"]:
        print(
            f"\n🔝 Top {min(top_files, len(analysis['file_stats']))} files by tokens:"
        )
        for i, file_stat in enumerate(analysis["file_stats"][:top_files]):
            percentage = (file_stat["tokens"] / analysis["total_tokens"]) * 100
            print(f"  {i + 1:2d}. {file_stat['path']}")
            print(f"      Tokens: {file_stat['tokens']:,} ({percentage:.1f}%)")
            print(f"      Size: {format_size(file_stat['size_bytes'])}")

        if show_details and len(analysis["file_stats"]) > top_files:
            print(f"\n📋 All files ({len(analysis['file_stats'])} total):")
            for file_stat in analysis["file_stats"]:
                percentage = (file_stat["tokens"] / analysis["total_tokens"]) * 100
                print(
                    f"  {file_stat['path']}: {file_stat['tokens']:,} tokens ({percentage:.1f}%)"
                )


def main():
    parser = argparse.ArgumentParser(
        description="Estimate token usage for files in a directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Analyze current directory
  %(prog)s /path/to/project         # Analyze specific directory
  %(prog)s --model gpt-4            # Use GPT-4 encoding
  %(prog)s --include "*.py"         # Only Python files
  %(prog)s --exclude "test_*"       # Exclude files matching pattern
  %(prog)s --details                # Show all files
  %(prog)s --json                   # Output as JSON
        """,
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to analyze (default: current directory)",
    )

    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="OpenAI model for token encoding (default: gpt-3.5-turbo)",
    )

    parser.add_argument(
        "--include",
        action="append",
        help="File patterns to include (can be used multiple times)",
    )

    parser.add_argument(
        "--exclude",
        action="append",
        help="File patterns to exclude (can be used multiple times)",
    )

    parser.add_argument(
        "--top", type=int, default=10, help="Number of top files to show (default: 10)"
    )

    parser.add_argument(
        "--details", action="store_true", help="Show all files in detail"
    )

    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    try:
        directory = Path(args.directory).resolve()
        counter = TokenCounter(args.model)

        print(f"🔍 Analyzing {directory}...")
        analysis = counter.analyze_directory(directory, args.include, args.exclude)

        print_results(analysis, args.details, args.top, "json" if args.json else "text")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
