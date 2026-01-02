# subxx

**YouTube transcript / subtitle fetching toolkit for Python** - Download, extract, and process subtitles from video URLs with a simple CLI or HTTP API.

[![Version](https://img.shields.io/badge/version-0.4.1-blue.svg)](https://gist.github.com/cprima/1ec077cb315295e349ee61dccf13f6b2)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Development Status](https://img.shields.io/badge/status-alpha-orange.svg)](https://github.com/cprima/subxx)

---

## Features

- **Download YouTube subtitles** from videos and channels (powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp))
- **Multiple output formats**: SRT, VTT, TXT, Markdown, PDF
- **JSON output**: Machine-readable output with `--json` and `--json-file` flags
- **Importable module**: Use as a Python library with dict-based return values
- **Text extraction** with automatic subtitle cleanup and optional timestamp markers
- **Language selection**: Download specific languages or all available subtitles
- **Batch processing**: Process multiple URLs from a file
- **Configuration files**: Project and global settings via TOML
- **HTTP API**: Optional FastAPI server for programmatic access
- **Dry-run mode**: Preview operations without downloading
- **Filename sanitization**: Safe, nospace, or slugify modes

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Module Usage (Python Library)](#module-usage-python-library)
- [Usage](#usage)
  - [List Available Subtitles](#list-available-subtitles)
  - [Download Subtitles](#download-subtitles)
  - [JSON Output](#json-output)
  - [Text Extraction](#text-extraction)
  - [Batch Processing](#batch-processing)
  - [Extract from Files](#extract-from-files)
- [Configuration](#configuration)
- [Makefile Shortcuts](#makefile-shortcuts)
- [HTTP API](#http-api)
- [Development](#development)
- [Testing](#testing)
- [License](#license)

---

## Installation

### Requirements

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Install with uv (recommended)

```bash
# Clone or download the project
git clone https://gist.github.com/cprima/subxx
cd subxx

# Install core dependencies
uv sync

# Install with optional features
uv sync --extra extract      # Text extraction (txt/md/pdf)
uv sync --extra api          # HTTP API server
uv sync --extra dev          # Development tools (pytest)

# Install all features
uv sync --extra extract --extra api --extra dev
```

### Using Make (Windows)

```bash
make install          # Core dependencies
make install-all      # All dependencies (extract + api + dev)
```

---

## Quick Start

### Basic Usage

```bash
# List available subtitles
uv run subxx list https://youtu.be/VIDEO_ID

# Download English subtitle (SRT format, default)
uv run subxx subs https://youtu.be/VIDEO_ID

# Extract to plain text
uv run subxx subs https://youtu.be/VIDEO_ID --txt

# Extract to Markdown with 5-minute timestamps
uv run subxx subs https://youtu.be/VIDEO_ID --md -t 300

# Extract to PDF
uv run subxx subs https://youtu.be/VIDEO_ID --pdf

# Get JSON output for automation
uv run subxx list https://youtu.be/VIDEO_ID --json
uv run subxx subs https://youtu.be/VIDEO_ID --json-file output.json
```

### With Makefile

```bash
# Quick Markdown extraction (just paste video ID)
make md VIDEO_ID=dQw4w9WgXcQ

# With timestamps
make md VIDEO_ID=dQw4w9WgXcQ TIMESTAMPS=300
```

---

## Module Usage (Python Library)

**New in v0.4.0+**: subxx can be imported and used as a Python library. Core functions now return structured data (dicts) instead of exit codes.

### Installation

```bash
# From test.pypi
pip install -i https://test.pypi.org/simple/ subxx==0.4.1

# Or with uv
uv add subxx==0.4.1 --index https://test.pypi.org/simple/
```

### Basic Example

```python
from subxx import fetch_subs, extract_text

# Download subtitles
result = fetch_subs(
    url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    langs="en",
    fmt="srt",
    output_dir="./subs",
    logger=None  # Silent mode
)

if result["status"] == "success":
    print(f"Downloaded: {result['video_title']}")
    for file_info in result["files"]:
        print(f"  {file_info['language']}: {file_info['path']}")
else:
    print(f"Error: {result['error']}")
```

### Return Structure

Functions return comprehensive dicts with all data:

```python
{
    "status": "success" | "error" | "skipped",
    "video_id": "dQw4w9WgXcQ",
    "video_title": "Rick Astley - Never Gonna Give You Up...",
    "files": [
        {
            "path": "/path/to/video.en.srt",
            "language": "en",
            "format": "srt",
            "auto_generated": false
        }
    ],
    "metadata": {...},
    "available_languages": [...],
    "download_info": {...},
    "error": null
}
```

### Complete Example

```python
from subxx import fetch_subs, extract_text

# 1. Download subtitle
result = fetch_subs(
    url="https://youtube.com/watch?v=...",
    langs="en",
    fmt="srt",
    auto=True,
    output_dir="./transcripts",
    logger=None
)

if result["status"] != "success":
    print(f"Error: {result['error']}")
    exit(1)

# 2. Extract to markdown
subtitle_file = result["files"][0]["path"]
extract_result = extract_text(
    subtitle_file=subtitle_file,
    output_format="md",
    use_chapters=True,
    logger=None
)

if extract_result["status"] == "success":
    print(f"Extracted to: {extract_result['output_files'][0]['path']}")
    print(f"Paragraphs: {len(extract_result['extracted_data']['paragraphs'])}")
```

### Available Functions

```python
from subxx import (
    fetch_subs,        # Download subtitles → dict
    extract_text,      # Extract text from srt/vtt → dict
    load_config,       # Load .subxx.toml config → dict
    get_default,       # Get config default value
    setup_logging,     # Configure logging
)
```

### Migration from CLI to Module

**v0.3.x (not supported as module)**:
- Functions returned exit codes (int)
- CLI-focused design

**v0.4.x (library-first)**:
- Functions return dicts with comprehensive data
- Optional `logger` parameter (None = silent)
- Clean separation: core functions vs CLI wrapper

---

## Usage

### List Available Subtitles

Preview available subtitle languages without downloading:

```bash
# Traditional output
uv run subxx list https://youtu.be/VIDEO_ID

# JSON output
uv run subxx list https://youtu.be/VIDEO_ID --json

# Save to file
uv run subxx list https://youtu.be/VIDEO_ID --json-file metadata.json
```

**Output:**
```
📹 Video: Example Video Title
🕒 Duration: 12:34

✅ Manual subtitles:
   - en
   - es

🤖 Auto-generated subtitles:
   - en, de, fr, ja, ko, pt, ru, zh-Hans, ...
```

**Options:**
- `-v, --verbose` - Debug output
- `-q, --quiet` - Errors only

---

### Download Subtitles

#### Format Selection

Download subtitle files in SRT or VTT format:

```bash
# Download SRT (default)
uv run subxx subs https://youtu.be/VIDEO_ID

# Download VTT
uv run subxx subs https://youtu.be/VIDEO_ID --vtt

# Using --fmt flag
uv run subxx subs https://youtu.be/VIDEO_ID -f srt
```

**Behavior**: Subtitle files (SRT/VTT) are downloaded and kept on disk.

#### Language Selection

```bash
# Download English (default)
uv run subxx subs https://youtu.be/VIDEO_ID

# Download specific language
uv run subxx subs https://youtu.be/VIDEO_ID -l de

# Download multiple languages
uv run subxx subs https://youtu.be/VIDEO_ID -l "en,de,fr"

# Download all available languages
uv run subxx subs https://youtu.be/VIDEO_ID -l all
```

#### Output Directory

```bash
# Save to specific directory
uv run python __main__.py subs https://youtu.be/VIDEO_ID -o ~/Downloads/subs

# Use current directory (default)
uv run python __main__.py subs https://youtu.be/VIDEO_ID -o .
```

#### Filename Sanitization

```bash
# Safe mode: Remove unsafe characters, keep spaces (default)
uv run python __main__.py subs URL --sanitize safe

# No spaces: Replace spaces with underscores
uv run python __main__.py subs URL --sanitize nospaces

# Slugify: Lowercase, hyphens, URL-safe
uv run python __main__.py subs URL --sanitize slugify
```

**Examples:**
- `safe`: `"My Video Title.srt"` → `"My Video Title.srt"`
- `nospaces`: `"My Video Title.srt"` → `"My_Video_Title.srt"`
- `slugify`: `"My Video Title.srt"` → `"my-video-title.srt"`

#### Overwrite Handling

```bash
# Prompt before overwriting (default)
uv run python __main__.py subs URL

# Force overwrite without prompting
uv run python __main__.py subs URL --force

# Skip existing files
uv run python __main__.py subs URL --skip-existing
```

#### Auto-Generated Subtitles

```bash
# Include auto-generated subtitles (default)
uv run python __main__.py subs URL --auto

# Only manual subtitles
uv run python __main__.py subs URL --no-auto
```

#### Dry Run

Preview what would be downloaded without actually downloading:

```bash
uv run python __main__.py subs URL --dry-run
```

**Output:**
```
[DRY RUN] Would download subtitle: en
```

---

### JSON Output

**New in v0.4.0**: Get machine-readable JSON output for automation and scripting.

#### Available Commands with JSON Support

- `list` - List available languages
- `subs` - Download subtitles

#### Output to stdout

```bash
# List command with JSON
uv run subxx list "https://youtu.be/dQw4w9WgXcQ" --json

# Subs command with JSON
uv run subxx subs "https://youtu.be/dQw4w9WgXcQ" --json
```

**Example JSON output**:
```json
{
  "status": "success",
  "video_id": "dQw4w9WgXcQ",
  "video_title": "Rick Astley - Never Gonna Give You Up...",
  "files": [
    {
      "path": "Rick Astley - Never Gonna Give You Up.dQw4w9WgXcQ.NA.en.srt",
      "language": "en",
      "format": "srt",
      "auto_generated": false
    }
  ],
  "available_languages": [
    {"code": "en", "name": "en", "auto_generated": false}
  ],
  "metadata": {...}
}
```

#### Save to file

```bash
# Save JSON to file
uv run subxx list URL --json-file metadata.json
uv run subxx subs URL --json-file result.json

# Both stdout and file
uv run subxx subs URL --json --json-file result.json
```

#### Use in Scripts

```bash
#!/bin/bash

# Get video metadata
metadata=$(uv run subxx list "$VIDEO_URL" --json)
video_title=$(echo "$metadata" | jq -r '.video_title')

echo "Downloading: $video_title"

# Download with JSON output
uv run subxx subs "$VIDEO_URL" --json-file download.json

# Check if successful
if [ "$(jq -r '.status' download.json)" == "success" ]; then
    echo "Success! Downloaded $(jq -r '.files | length' download.json) files"
fi
```

---

### Text Extraction

Extract clean, readable text from subtitles by automatically removing timestamps and formatting.

**Key behavior**: When using text formats (txt/md/pdf), subxx:
1. Downloads the subtitle as SRT
2. Extracts the text content
3. **Automatically deletes the SRT file**

#### Plain Text

```bash
# Extract to plain text
uv run python __main__.py subs URL --txt
```

**Output**: `Video_Title.VIDEO_ID.en.txt`

**Example content:**
```
Hello world.
This is a subtitle.
Welcome to the video.
```

#### Markdown

```bash
# Extract to Markdown
uv run python __main__.py subs URL --md

# Markdown with timestamp markers every 5 minutes
uv run python __main__.py subs URL --md -t 300

# Markdown with timestamp markers every 30 seconds
uv run python __main__.py subs URL --md -t 30
```

**Output**: `Video_Title.VIDEO_ID.en.md`

**Example content (with timestamps):**
```markdown
## [0:00]

Hello world.
This is a subtitle.

## [5:00]

Welcome to the next section.
More content here.

## [10:00]

Final section of the video.
```

#### PDF

```bash
# Extract to PDF
uv run python __main__.py subs URL --pdf

# PDF with timestamp markers
uv run python __main__.py subs URL --pdf -t 300
```

**Output**: `Video_Title.VIDEO_ID.en.pdf`

**Requirements**: Install extraction dependencies:
```bash
uv sync --extra extract
```

#### Timestamp Intervals

Add timestamp markers at regular intervals for long-form content:

```bash
# Every 5 minutes (300 seconds)
uv run python __main__.py subs URL --md -t 300

# Every 30 seconds
uv run python __main__.py subs URL --txt -t 30

# Every 10 minutes
uv run python __main__.py subs URL --pdf -t 600
```

**Format**: Timestamps appear as `## [0:00]`, `## [5:00]`, `## [10:00]`, etc.

---

### Batch Processing

Download subtitles for multiple URLs from a file:

```bash
# Create URLs file (one URL per line)
cat > urls.txt << EOF
https://youtu.be/VIDEO_ID_1
https://youtu.be/VIDEO_ID_2
# This is a comment
https://youtu.be/VIDEO_ID_3
EOF

# Process all URLs
uv run python __main__.py batch urls.txt

# With options
uv run python __main__.py batch urls.txt -l "en,de" -f srt -o ~/subs
```

**Options:**
- `-l, --langs` - Language codes (default: en)
- `-f, --fmt` - Output format (default: srt)
- `-o, --output-dir` - Output directory (default: .)
- `--sanitize` - Filename sanitization mode (default: safe)
- `-v, --verbose` - Verbose output
- `-q, --quiet` - Quiet mode

**URL File Format** (yt-dlp standard):
- One URL per line
- Lines starting with `#` are comments
- Empty lines are ignored

---

### Extract from Files

Extract text from existing subtitle files:

```bash
# Extract SRT to plain text
uv run python __main__.py extract video.srt

# Extract to Markdown
uv run python __main__.py extract video.srt -f md

# Extract to PDF
uv run python __main__.py extract video.srt -f pdf

# With timestamp markers every 5 minutes
uv run python __main__.py extract video.srt -f md -t 300

# Specify output file
uv run python __main__.py extract video.srt -o output.txt

# Force overwrite
uv run python __main__.py extract video.srt --force
```

**Supported input formats**: SRT, VTT

---

## Configuration

### Config File Locations

Configuration files are loaded in priority order:

1. `./.subxx.toml` (project-specific, current directory)
2. `~/.subxx.toml` (user global, home directory)

### Priority Chain

Settings are resolved in this order (highest to lowest):

1. **CLI flags** (e.g., `--langs en`, `--fmt srt`)
2. **Config file** (`.subxx.toml`)
3. **Hardcoded defaults**

### Example Configuration

Copy `.subxx.toml.example` to `.subxx.toml` or `~/.subxx.toml`:

```bash
cp .subxx.toml.example ~/.subxx.toml
```

**Example config:**

```toml
[defaults]
# Language codes (comma-separated or "all")
langs = "en"

# Output format: srt, vtt, txt, md, pdf
fmt = "md"

# Include auto-generated subtitles
auto = true

# Output directory (supports ~)
output_dir = "~/Downloads/subtitles"

# Filename sanitization: safe, nospaces, slugify
sanitize = "safe"

# Timestamp interval (seconds) for txt/md/pdf
timestamps = 300  # 5-minute intervals

[logging]
# Log level: DEBUG, INFO, WARNING, ERROR
level = "INFO"

# Log file (optional)
log_file = "~/.subxx/subxx.log"
```

### Use Case Configurations

**Configuration 1: Download SRT files to dedicated directory**
```toml
[defaults]
langs = "en"
fmt = "srt"
output_dir = "~/Downloads/subtitles"
```

**Configuration 2: Auto-extract to Markdown with timestamps**
```toml
[defaults]
langs = "en"
fmt = "md"
timestamps = 300
output_dir = "~/Documents/transcripts"
```

**Configuration 3: Multiple languages, plain text**
```toml
[defaults]
langs = "en,de,fr"
fmt = "txt"
sanitize = "slugify"
output_dir = "./subtitles"
```

---

## Makefile Shortcuts

### Available Targets

```bash
# Installation
make install          # Core dependencies
make install-all      # All dependencies (extract + api + dev)

# Testing
make test             # Run all tests
make test-unit        # Unit tests only
make test-integration # Integration tests only
make test-coverage    # Tests with coverage report

# Usage
make list VIDEO_URL=https://youtu.be/VIDEO_ID
make subs VIDEO_URL=https://youtu.be/VIDEO_ID
make md VIDEO_ID=VIDEO_ID                       # Quick Markdown extraction
make md VIDEO_ID=VIDEO_ID TIMESTAMPS=300        # With timestamps

# Utilities
make version          # Show version
make clean            # Clean cache files
make clean-all        # Clean everything including .venv
```

### Examples

```bash
# Quick Markdown extraction (just paste video ID)
make md VIDEO_ID=dQw4w9WgXcQ

# With 5-minute timestamps
make md VIDEO_ID=lHuxDMMkGJ8 TIMESTAMPS=300

# List subtitles
make list VIDEO_URL=https://youtu.be/dQw4w9WgXcQ

# Download with languages
make subs VIDEO_URL=https://youtu.be/dQw4w9WgXcQ LANGS=en,de
```

---

## HTTP API

Start an HTTP API server for programmatic access (requires API dependencies):

### Installation

```bash
# Install API dependencies
uv sync --extra api

# Or with Make
make install-api
```

### Start Server

```bash
# Start on localhost:8000 (default)
uv run python __main__.py serve

# Custom host/port
uv run python __main__.py serve --host 127.0.0.1 --port 8080
```

**Security Warning**: The API has NO authentication and should ONLY run on localhost (127.0.0.1).

### API Endpoints

#### POST /subs

Fetch subtitles and return content directly.

**Request:**
```json
{
  "url": "https://youtu.be/VIDEO_ID",
  "langs": "en",
  "fmt": "srt",
  "auto": true,
  "sanitize": "safe"
}
```

**Response:** Subtitle file content as plain text.

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/subs \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtu.be/dQw4w9WgXcQ",
    "langs": "en",
    "fmt": "srt"
  }'
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "subxx"
}
```

### API Documentation

Interactive API docs available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://gist.github.com/cprima/subxx
cd subxx

# Install all dependencies (core + extract + api + dev)
uv sync --extra extract --extra api --extra dev

# Or with Make
make install-all
```

### Project Structure

**Updated in v0.4.1** - Restructured for Python best practices:

```
subxx/
├── subxx.py                 # Core library functions (returns dicts)
├── cli.py                   # CLI + API implementation (Typer/FastAPI)
├── __main__.py              # Minimal entry point (3 lines)
├── test_subxx.py            # Test suite (pytest)
├── conftest.py              # Pytest configuration
├── pyproject.toml           # Project metadata and dependencies
├── Makefile                 # Build and test automation
├── .subxx.toml.example      # Example configuration file
└── !README.md               # This file
```

### Key Components

- **`subxx.py`**: Core library (library-first design)
  - `fetch_subs()` → dict - Download subtitles, return structured data
  - `extract_text()` → dict - Extract text from subtitles, return structured data
  - `load_config()` → dict - Configuration management
  - Helper functions for parsing, sanitization, logging
  - **Importable as Python module**

- **`cli.py`**: CLI + API implementation
  - Typer commands: `list`, `subs`, `batch`, `extract`, `serve`, `version`
  - FastAPI HTTP server
  - JSON output handling (`--json`, `--json-file`)
  - Traditional console output with emojis

- **`__main__.py`**: Minimal entry point (Python best practice)
  - 3 lines: import and run CLI
  - Enables `python -m subxx` usage

---

## Testing

### Run Tests

```bash
# All tests
make test

# Unit tests only (fast, no network)
make test-unit

# Integration tests only
make test-integration

# With coverage report
make test-coverage

# Verbose output
make test-verbose
```

### Test Categories

- **Unit tests** (`@pytest.mark.unit`): No external dependencies, mocked I/O
- **Integration tests** (`@pytest.mark.integration`): May use files/network
- **E2E tests** (`@pytest.mark.e2e`): Real YouTube API, requires internet
- **Slow tests** (`@pytest.mark.slow`): Network I/O, real downloads

### Running Specific Test Categories

```bash
# Run all tests except e2e (fast, for CI)
pytest -m "not e2e"

# Run only e2e tests (slow, requires internet)
pytest -m e2e

# Run unit tests only
pytest -m unit
```

### Test Coverage

Current coverage: **~50 tests** (unit, integration, and e2e)

Key areas tested:
- Configuration loading and defaults
- Language parsing
- Filename sanitization
- Text extraction (txt/md/pdf)
- Timestamp markers
- CLI commands
- Overwrite protection
- Real YouTube subtitle download (e2e)

---

## Exit Codes

- `0` - Success
- `1` - User cancelled
- `2` - No subtitles available
- `3` - Network error
- `4` - Invalid URL
- `5` - Configuration error
- `6` - File error

---

## Troubleshooting

### Missing Dependencies for Text Extraction

**Error:**
```
❌ Error: Missing dependencies for text extraction
```

**Solution:**
```bash
uv sync --extra extract
```

### Missing Dependencies for API

**Error:**
```
❌ Error: API dependencies not installed
```

**Solution:**
```bash
uv sync --extra api
```

### Windows Console Encoding Issues

If you see encoding errors on Windows, the tool automatically attempts to reconfigure stdout/stderr to UTF-8. If issues persist, use:

```bash
# Set console to UTF-8
chcp 65001
```

### yt-dlp Network Errors

If downloads fail with network errors:

1. Update yt-dlp:
   ```bash
   uv sync --upgrade
   ```

2. Check firewall/proxy settings

3. Try with `--verbose` for debug output:
   ```bash
   uv run python __main__.py subs URL --verbose
   ```

---

## Roadmap

### Completed (v0.4.x)
- [x] **JSON output support** (`--json`, `--json-file`)
- [x] **Importable Python module** (library-first architecture)
- [x] **Published package on test.pypi.org**
- [x] **Pythonic project structure** (cli.py, minimal __main__.py)

### Future Enhancements
- [ ] Publish to PyPI (production)
- [ ] Progress bars for downloads
- [ ] Retry logic for network failures
- [ ] Subtitle merging/combining
- [ ] Translation support
- [ ] Docker container
- [ ] GitHub Actions CI/CD
- [ ] SRT/VTT format conversion
- [ ] Subtitle editing/manipulation
- [ ] Batch command JSON support
- [ ] Extract command JSON support

---

## Contributing

Contributions welcome! This is an alpha project under active development.

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `make test`
6. Submit a pull request

### Guidelines

- Follow existing code style
- Add docstrings for new functions
- Update tests for changes
- Update README for new features
- Keep commits focused and atomic

---

## License

This project is licensed under **CC BY 4.0** (Creative Commons Attribution 4.0 International).

You are free to:
- **Share** - Copy and redistribute the material
- **Adapt** - Remix, transform, and build upon the material

Under the following terms:
- **Attribution** - You must give appropriate credit

See [LICENSE](https://creativecommons.org/licenses/by/4.0/) for full details.

---

## Credits

- Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp) for video subtitle extraction
- CLI powered by [Typer](https://typer.tiangolo.com/)
- API built with [FastAPI](https://fastapi.tiangolo.com/)
- Text extraction using [srt](https://github.com/cdown/srt) and [fpdf2](https://github.com/py-pdf/fpdf2)

---

## Author

**Christian Prior-Mamulyan**
- Email: cprior@gmail.com
- GitHub: [@cprima](https://github.com/cprima)

---

## Support

- Report issues: [GitHub Issues](https://gist.github.com/cprima/subxx/issues)
- Documentation: [GitHub Gist](https://gist.github.com/cprima/subxx)

---

**subxx** - Simple, powerful YouTube transcript / subtitle fetching for Python.
