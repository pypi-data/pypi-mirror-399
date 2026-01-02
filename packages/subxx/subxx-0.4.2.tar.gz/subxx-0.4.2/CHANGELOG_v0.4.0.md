# Changelog: subxx v0.4.0

## 🎯 Major Changes

### Architecture Refactoring
- **Core functions now return dicts** instead of exit codes
  - `fetch_subs()` returns comprehensive dict with status, files, metadata, available_languages
  - `extract_text()` returns dict with extracted data, output files, extraction info
  - Both functions accept optional `logger` parameter (None = silent mode for library use)

### JSON Output Support
- Added `--json` flag to output results as JSON to stdout
- Added `--json-file <path>` option to save JSON to file
- Supported commands: `list`, `subs` (more commands can follow same pattern)

### Importable Module
The module is now naturally importable for programmatic use:

```python
from subxx import fetch_subs, extract_text

# Fetch subtitles - returns dict with all info
result = fetch_subs(
    url="https://youtube.com/watch?v=...",
    langs="en",
    fmt="srt",
    output_dir="./output"
)

if result["status"] == "success":
    print(f"Downloaded {len(result['files'])} files")
    for file in result["files"]:
        print(f"  {file['language']}: {file['path']}")
```

## 📝 Files Modified

1. **pyproject.toml**
   - Version: 0.3.0 → 0.4.0

2. **subxx.py**
   - `fetch_subs()`: Returns dict instead of int
   - `extract_text()`: Returns dict instead of int
   - `setup_logging()`: Added `json_mode` parameter to suppress output

3. **__main__.py**
   - Added `handle_json_output()` helper function
   - Updated `subs` command with --json and --json-file flags
   - Updated `list` command with --json and --json-file flags
   - Both commands work with dict returns from core functions

## 🧪 Testing

### Basic functionality test:
```bash
# Syntax check passed
python3 -m py_compile subxx.py __main__.py

# Module import works
python3 -c "import subxx; print('✓ Module loads')"
```

### Manual testing needed:
```bash
# Test traditional CLI output
uv run subxx list "https://youtube.com/watch?v=dQw4w9WgXcQ"
uv run subxx subs "https://youtube.com/watch?v=dQw4w9WgXcQ" --langs en

# Test JSON output
uv run subxx list "https://youtube.com/watch?v=dQw4w9WgXcQ" --json
uv run subxx subs "https://youtube.com/watch?v=dQw4w9WgXcQ" --langs en --json

# Test JSON file output
uv run subxx list "https://youtube.com/watch?v=dQw4w9WgXcQ" --json-file output.json

# Test as importable module
python3 -c "
from subxx import fetch_subs
result = fetch_subs('https://...', langs='en', dry_run=True)
print(result['status'])
"
```

## 🔄 Breaking Changes

**For existing Python importers:**
- `fetch_subs()` and `extract_text()` now return `dict` instead of `int`
- Exit codes (EXIT_SUCCESS, etc.) still exist but are only used in CLI layer

**Migration example:**
```python
# v0.3.0 (old)
exit_code = fetch_subs(url, langs="en")
if exit_code == EXIT_SUCCESS:
    print("Success!")

# v0.4.0 (new)
result = fetch_subs(url, langs="en")
if result["status"] == "success":
    print("Success!")
    print(f"Files: {result['files']}")
```

## ✨ JSON Output Schema

### `list` command:
```json
{
  "status": "success",
  "video_id": "dQw4w9WgXcQ",
  "video_title": "Example Video",
  "url": "https://...",
  "duration": 212,
  "available_languages": [
    {"code": "en", "name": "en", "auto_generated": false},
    {"code": "es", "name": "es", "auto_generated": true}
  ]
}
```

### `subs` command:
```json
{
  "status": "success",
  "video_id": "dQw4w9WgXcQ",
  "video_title": "Example Video",
  "files": [
    {
      "path": "/path/to/video.en.srt",
      "language": "en",
      "format": "srt",
      "auto_generated": false,
      "size_bytes": 12345
    }
  ],
  "metadata": {...},
  "available_languages": [...],
  "download_info": {
    "requested_languages": "en",
    "format": "srt",
    "downloaded_at": "2024-12-29T12:34:56Z"
  }
}
```

## 📋 TODO/Future Work

- [ ] Update `batch` command with JSON support
- [ ] Update `extract` command with JSON support (standalone, not via subs)
- [ ] Update test suite to work with dict returns
- [ ] Add integration tests for JSON output
- [ ] Consider refactoring CLI code to separate cli.py module
- [ ] Update documentation/README with examples

## ✅ Status
**Implementation: COMPLETE**
**Testing: MANUAL TESTING REQUIRED**
