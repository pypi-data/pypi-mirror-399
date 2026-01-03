# Token Counter CLI

A Python CLI application that estimates token usage for files in a directory, helping you understand how much context window space your codebase would consume.

## Features

- 📊 Analyzes token usage for all text files in a directory
- 🤖 Supports multiple OpenAI model encodings
- 📏 Shows context window usage percentages for popular models
- 🔝 Ranks files by token consumption
- 🚫 Automatically excludes binary files and common build/cache directories
- 📋 Supports file inclusion/exclusion patterns
- 📄 JSON output option for integration
- ⚠️ Fallback token estimation when tiktoken is not available

## Installation

```bash
# Install via pip
pip install toknc

# For accurate token counting, install tiktoken:
pip install toknc[tiktoken]
```

Note: The tool will work without tiktoken using rough estimation (≈1 token per 4 characters).

## Usage

```bash
# Analyze current directory
tokenc

# Analyze specific directory
tokenc /path/to/project

# Use specific model encoding
tokenc --model gpt-4

# Only analyze Python files
tokenc --include "*.py"

# Exclude test files
tokenc --exclude "test_*" --exclude "*_test.py"

# Show all files in detail
tokenc --details

# Output as JSON
tokenc --json

# Show top 20 files
tokenc --top 20
```

## Options

- `directory`: Directory to analyze (default: current directory)
- `--model`: OpenAI model for token encoding (default: gpt-3.5-turbo)
- `--include`: File patterns to include (can be used multiple times)
- `--exclude`: File patterns to exclude (can be used multiple times)
- `--top`: Number of top files to show (default: 10)
- `--details`: Show all files in detail
- `--json`: Output results as JSON

## Example Output

```
📊 Token Analysis for: /Users/adminx/test
🤖 Model: gpt-3.5-turbo
📁 Total files: 4
🪙 Total tokens: 2,897
💾 Total size: 11.4 KB

📏 Context Window Usage:
  GPT-3.5 Turbo     4096 tokens: ██████████████░░░░░░ 70.7%
  GPT-4             8192 tokens: ███████░░░░░░░░░░░░░ 35.4%
  GPT-4 Turbo     128000 tokens: ░░░░░░░░░░░░░░░░░░░░ 2.3%
  Claude 3        200000 tokens: ░░░░░░░░░░░░░░░░░░░░ 1.4%
  Gemini Pro       32768 tokens: █░░░░░░░░░░░░░░░░░░░ 8.8%

🔝 Top 4 files by tokens:
   1. token_counter.py
      Tokens: 2,877 (99.3%)
      Size: 11.3 KB
```

## Supported File Types

The tool automatically detects text files and includes common source code extensions:
- Python (.py), JavaScript (.js, .jsx), TypeScript (.ts, .tsx)
- Web files (.html, .css)
- Config files (.json, .xml, .yaml, .yml)
- Documentation (.md, .rst)
- Shell scripts (.sh, .bash, .zsh)
- C/C++ (.c, .cpp, .h, .hpp)
- Java (.go, .rs, .php, .rb)
- And many more...

## Automatically Excluded

- Version control: .git/, .svn/, .hg/
- Dependencies: node_modules/, __pycache__/
- Compiled files: .pyc, .pyo, .pyd
- System files: .DS_Store, Thumbs.db