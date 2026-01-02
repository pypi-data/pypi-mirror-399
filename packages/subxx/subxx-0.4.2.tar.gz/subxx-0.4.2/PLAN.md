# Implementation Plan: Refactor Chapter Structure + Implement All Feature Requests

**Status**: Planning
**Date**: 2025-11-06
**Goal**: Refactor chapter output to structured objects + implement all features from FEATURE_REQUESTS.md

---

## Phase 1: Refactor to Structured Chapter Objects

### 1.1 Change `extract_with_chapters()` Return Format

**Current**: Returns `List[str]` with hardcoded `### {title}` markers mixed with paragraphs

**New**: Returns `List[dict]` with chapter objects:
```python
[
    {
        "type": "chapter",
        "title": "Overview of my AI-First Tech Stack",
        "content": [
            "Paragraph 1 with 6 sentences...",
            "Paragraph 2 with 6 sentences...",
            "Paragraph 3 with 6 sentences..."
        ]
    },
    {
        "type": "chapter",
        "title": "The Core of the Tech Stack",
        "content": [
            "Paragraph 4...",
            "Paragraph 5..."
        ]
    }
]
```

**Changes needed**:
- Modify `extract_with_chapters()` (lines 769-873) to accumulate paragraphs per chapter
- When chapter boundary hit: close current chapter object, start new one
- Return list of chapter dicts instead of flat string list

**Algorithm**:
```python
def extract_with_chapters(subtitles, chapters):
    # PASS 1: Build items (unchanged)
    items = []  # (type, content) tuples

    # PASS 2: Group into chapter objects
    result = []
    current_chapter = None
    current_paragraphs = []
    current_para = []
    sentence_count = 0

    for item_type, item_content in items:
        if item_type == 'chapter':
            # Close previous chapter
            if current_chapter is not None:
                if current_para:
                    current_paragraphs.append(' '.join(current_para))
                result.append({
                    "type": "chapter",
                    "title": current_chapter,
                    "content": current_paragraphs
                })

            # Start new chapter
            current_chapter = item_content
            current_paragraphs = []
            current_para = []
            sentence_count = 0

        else:  # text
            # Same sentence processing logic
            # When paragraph complete:
            current_paragraphs.append(' '.join(current_para))
            current_para = []

    # Close final chapter
    if current_chapter is not None and current_paragraphs:
        result.append({
            "type": "chapter",
            "title": current_chapter,
            "content": current_paragraphs
        })

    return result
```

### 1.2 Update `extract_with_timestamps()` for Consistency

**Decision**: Keep returning flat `List[str]` for backward compatibility

**Rationale**:
- Simpler (timestamps don't need chapter structure)
- Writers can handle both formats
- Less breaking changes

### 1.3 Modify Writer Functions

**Pattern**: Detect input type, format accordingly

#### `write_txt()` (line 876)
```python
def write_txt(output_file: Path, lines: List) -> None:
    """Write plain text output."""
    with open(output_file, 'w', encoding='utf-8') as f:
        if lines and isinstance(lines[0], dict) and lines[0].get('type') == 'chapter':
            # Chapter objects - format with decorated headers
            formatted = []
            for chapter in lines:
                formatted.append(f"=== {chapter['title']} ===\n")
                formatted.extend(chapter['content'])
            f.write('\n\n'.join(formatted))
        else:
            # Flat strings - existing behavior
            f.write('\n\n'.join(lines))
```

#### `write_markdown()` (line 882)
```python
def write_markdown(output_file: Path, lines: List, title: str, metadata: Optional[dict] = None) -> None:
    """Write Markdown output with optional metadata, headings, channel bio, and citations."""
    # ... (existing frontmatter and header code) ...

    with open(output_file, 'w', encoding='utf-8') as f:
        # ... (write frontmatter and header) ...

        f.write("## Transcript\n\n")

        if lines and isinstance(lines[0], dict) and lines[0].get('type') == 'chapter':
            # Chapter objects - format with H3 headers
            for chapter in lines:
                f.write(f"### {chapter['title']}\n\n")
                f.write('\n\n'.join(chapter['content']))
                f.write('\n\n')
        else:
            # Flat strings - existing behavior
            f.write('\n\n'.join(lines))

        # ... (channel bio and citations) ...
```

#### `write_pdf()` (existing function)
```python
def write_pdf(output_file: Path, lines: List, title: str) -> None:
    """Write PDF output."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_font('Arial', '', 12)

    if lines and isinstance(lines[0], dict) and lines[0].get('type') == 'chapter':
        # Chapter objects - format with section headings
        for chapter in lines:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, chapter['title'], ln=True)
            pdf.set_font('Arial', '', 12)
            for paragraph in chapter['content']:
                pdf.multi_cell(0, 10, paragraph)
                pdf.ln(5)
    else:
        # Flat strings - existing behavior
        for line in lines:
            pdf.multi_cell(0, 10, line)
            pdf.ln(5)

    pdf.output(str(output_file))
```

---

## Phase 2: Implement `generate_virtual_chapters()`

**Location**: Add after `extract_with_chapters()` (after line 873)

**Function**:
```python
def generate_virtual_chapters(
    subtitles: List,
    interval: int
) -> List[dict]:
    """Generate virtual chapters from timestamp intervals.

    Creates chapter objects matching YouTube metadata format,
    allowing extract_with_chapters() to process them identically.

    Args:
        subtitles: List of parsed SRT subtitle objects
        interval: Seconds between each virtual chapter marker

    Returns:
        List of chapter dicts with 'start_time', 'title', 'end_time'
        Format identical to YouTube metadata['chapters']

    Example output:
        [
            {"start_time": 0.0, "title": "Section 1 (0:00-5:00)", "end_time": 300.0},
            {"start_time": 300.0, "title": "Section 2 (5:00-10:00)", "end_time": 600.0},
        ]
    """
    if not subtitles:
        return []

    # Get total duration from last subtitle
    total_duration = subtitles[-1].end.total_seconds()

    chapters = []
    start_time = 0.0
    section_num = 1

    while start_time < total_duration:
        end_time = min(start_time + interval, total_duration)

        # Format timestamps for title
        start_min = int(start_time // 60)
        start_sec = int(start_time % 60)
        end_min = int(end_time // 60)
        end_sec = int(end_time % 60)

        title = f"Section {section_num} ({start_min}:{start_sec:02d}-{end_min}:{end_sec:02d})"

        chapters.append({
            "start_time": start_time,
            "title": title,
            "end_time": end_time
        })

        start_time = end_time
        section_num += 1

    return chapters
```

**Test**:
```python
# Should generate chapters every 300s for a 20-minute video
subtitles = [...]  # 1200 seconds total
virtual = generate_virtual_chapters(subtitles, 300)
assert len(virtual) == 4
assert virtual[0]['title'] == "Section 1 (0:00-5:00)"
assert virtual[3]['title'] == "Section 4 (15:00-20:00)"
```

---

## Phase 3: Implement FR-001 (Fallback Strategy)

### 3.1 Add CLI Parameters

**In `extract` command** (`__main__.py` line ~418):
```python
@app.command()
def extract(
    subtitle_file: str = typer.Argument(..., help="Subtitle file (.srt or .vtt)"),
    output_format: str = typer.Option("txt", "--format", "-f", help="Output format (txt, md, pdf)"),
    timestamp_interval: Optional[int] = typer.Option(None, "--timestamps", "-t",
                                                     help="Add timestamp every N seconds (e.g., 300 for 5min)"),
    chapters: bool = typer.Option(False, "--chapters", help="Use chapter markers from metadata (YouTube chapters)"),
    fallback_timestamps: Optional[int] = typer.Option(None, "--fallback-timestamps",  # NEW
                                                       help="Fallback to N-second intervals if no chapters (use with --chapters)"),
    min_chapters: int = typer.Option(2, "--min-chapters",  # NEW
                                     help="Minimum chapters required to use chapter mode (default: 2)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
```

**In `subs` command** (`__main__.py` line ~134):
```python
@app.command()
def subs(
    url: str,
    # ... (existing parameters) ...
    chapters: bool = typer.Option(False, "--chapters", help="Use chapter markers from metadata (YouTube chapters, for txt/md/pdf)"),
    fallback_timestamps: Optional[int] = typer.Option(None, "--fallback-timestamps",  # NEW
                                                       help="Fallback to N-second intervals if no chapters"),
    min_chapters: int = typer.Option(2, "--min-chapters",  # NEW
                                     help="Minimum chapters required (default: 2)"),
    # ... (rest of parameters) ...
):
```

### 3.2 Update `extract_text()` Function

**New signature** (line 534):
```python
def extract_text(
    subtitle_file: str,
    output_format: str = "txt",
    timestamp_interval: Optional[int] = None,
    output_file: Optional[str] = None,
    force: bool = False,
    use_chapters: bool = False,
    fallback_timestamps: Optional[int] = None,  # NEW
    min_chapters: int = 2  # NEW
) -> int:
```

**New docstring**:
```python
"""Extract text from SRT subtitle file.

Args:
    subtitle_file: Path to subtitle file (.srt or .vtt)
    output_format: Output format ("txt", "md", or "pdf")
    timestamp_interval: Optional interval in seconds for timestamp markers
                       (e.g., 300 for every 5 minutes)
    output_file: Output file path (auto-generated if None)
    force: Overwrite existing output file without prompt
    use_chapters: Use chapter markers from metadata instead of timestamps
    fallback_timestamps: Fallback to N-second intervals if no chapters found
    min_chapters: Minimum number of chapters required (default: 2)

Returns:
    int: Exit code (0 = success, non-zero = error)
"""
```

**New logic** (replace lines 601-618):
```python
# Extract text with optional timestamps or chapters
structure_source = None
chapter_count = 0

if use_chapters:
    # Try to use real YouTube chapters
    chapters_list = None
    if metadata and 'chapters' in metadata:
        chapters_list = metadata['chapters']

        # Check chapter quality threshold
        if len(chapters_list) >= min_chapters:
            logger.info(f"Using {len(chapters_list)} chapters from YouTube metadata")
            extracted = extract_with_chapters(subtitles, chapters_list)
            structure_source = "youtube_metadata"
            chapter_count = len(chapters_list)
        else:
            logger.info(f"Only {len(chapters_list)} chapter(s) found (< min {min_chapters}); using fallback")
            chapters_list = None  # Force fallback

    # Fallback if no valid chapters
    if chapters_list is None:
        if fallback_timestamps:
            logger.info(f"Generating virtual chapters from {fallback_timestamps}s intervals")
            virtual_chapters = generate_virtual_chapters(subtitles, fallback_timestamps)
            extracted = extract_with_chapters(subtitles, virtual_chapters)
            structure_source = "timestamp_fallback"
            chapter_count = len(virtual_chapters)
        else:
            logger.warning("--chapters specified but no chapter data and no fallback; continuing without chapters")
            extracted = extract_with_timestamps(subtitles, None)
            structure_source = "none"

elif timestamp_interval:
    # Use timestamp-based extraction
    extracted = extract_with_timestamps(subtitles, timestamp_interval)
    structure_source = "timestamps"
else:
    # No markers
    extracted = extract_with_timestamps(subtitles, None)
    structure_source = "none"
```

### 3.3 Pass New Parameters in CLI Commands

**In `extract` command** (line 456):
```python
exit_code = extract_text(
    subtitle_file=subtitle_file,
    output_format=output_format,
    timestamp_interval=timestamp_interval,
    output_file=output_file,
    force=force,
    use_chapters=chapters,
    fallback_timestamps=fallback_timestamps,  # NEW
    min_chapters=min_chapters  # NEW
)
```

**In `subs` command** (line 297):
```python
extract_exit = extract_text(
    subtitle_file=str(subtitle_file),
    output_format=fmt,
    timestamp_interval=timestamps,
    output_file=output_file,
    force=force,
    use_chapters=chapters,
    fallback_timestamps=fallback_timestamps,  # NEW
    min_chapters=min_chapters  # NEW
)
```

---

## Phase 4: Implement Auto-Structure Mode (FR-002 Partial)

### 4.1 Add `--auto-structure` Flag

**In `extract` command** (line ~422):
```python
auto_structure: bool = typer.Option(False, "--auto-structure",
                                    help="Automatically choose best structure (chapters if available, else 5-min timestamps)"),
```

**In `subs` command** (line ~137):
```python
auto_structure: bool = typer.Option(False, "--auto-structure",
                                    help="Auto-select structure: chapters if available, else timestamps"),
```

### 4.2 Add Auto-Structure Logic in `extract` Command

**Before calling `extract_text()`** (insert after line 450, before line 454):
```python
# Auto-structure: detect best available structure
if auto_structure:
    try:
        import json
        from pathlib import Path

        subtitle_path = Path(subtitle_file)
        metadata_files = list(subtitle_path.parent.glob("metadata-*.json"))

        has_valid_chapters = False
        chapter_count_found = 0

        if metadata_files and metadata_files[0].exists():
            with open(metadata_files[0], 'r', encoding='utf-8') as f:
                meta = json.load(f)
                if 'chapters' in meta:
                    chapter_count_found = len(meta['chapters'])
                    if chapter_count_found >= min_chapters:
                        has_valid_chapters = True

        if has_valid_chapters:
            logger.info(f"Auto-structure: using {chapter_count_found} YouTube chapters")
            chapters = True
            timestamp_interval = None
        else:
            logger.info(f"Auto-structure: no valid chapters found, using 300s timestamp intervals")
            chapters = False
            timestamp_interval = 300
            fallback_timestamps = None

    except Exception as e:
        logger.warning(f"Auto-structure detection failed: {e}; using defaults")
```

### 4.3 Add Auto-Structure Logic in `subs` Command

**After metadata is saved** (insert after line 280, before extraction logic):
```python
# Auto-structure: detect best available structure
if auto_structure:
    try:
        has_valid_chapters = False
        chapter_count_found = 0

        # Check if we have metadata with chapters
        if metadata and 'chapters' in metadata:
            chapter_count_found = len(metadata['chapters'])
            if chapter_count_found >= min_chapters:
                has_valid_chapters = True

        if has_valid_chapters:
            logger.info(f"Auto-structure: using {chapter_count_found} YouTube chapters")
            chapters = True
            timestamps = None
        else:
            logger.info(f"Auto-structure: no valid chapters found, using 300s timestamp intervals")
            chapters = False
            timestamps = 300
            fallback_timestamps = None

    except Exception as e:
        logger.warning(f"Auto-structure detection failed: {e}; using defaults")
```

---

## Phase 5: Enhanced JSON Metadata

### 5.1 Update `write_outputs()` Function Signature

**Current** (around line 780):
```python
def write_outputs(output_file: Path, subtitles, extracted, metadata, timestamp_interval):
```

**New**:
```python
def write_outputs(
    output_file: Path,
    subtitles,
    extracted,
    metadata,
    timestamp_interval,
    structure_source: Optional[str] = None,  # NEW
    chapter_count: int = 0  # NEW
):
```

### 5.2 Add New Metadata Fields

**Update JSON structure**:
```python
def write_outputs(output_file, subtitles, extracted, metadata, timestamp_interval,
                  structure_source=None, chapter_count=0):
    """Write JSON output with extraction metadata."""
    import json
    import datetime

    # Determine structure type
    if structure_source in ["youtube_metadata", "timestamp_fallback"]:
        structure = "chapters"
    elif structure_source == "timestamps":
        structure = "timestamps"
    else:
        structure = "paragraphs"

    output = {
        "extraction_info": {
            "format": "sentence-chunked",
            "structure": structure,  # NEW: "chapters" | "timestamps" | "paragraphs"
            "structure_source": structure_source,  # NEW: "youtube_metadata" | "timestamp_fallback" | "timestamps" | "none"
            "timestamp_interval": timestamp_interval,
            "chapter_count": chapter_count,  # NEW: Number of chapters (real or virtual)
            "extracted_at": datetime.datetime.now().isoformat(),
            "format_version": "1.0"
        },
        "video_metadata": metadata if metadata else {},
        "paragraphs": extracted if isinstance(extracted, list) and all(isinstance(x, str) for x in extracted) else [],
        "chapters": extracted if isinstance(extracted, list) and extracted and isinstance(extracted[0], dict) else []
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
```

### 5.3 Update Calls to `write_outputs()`

**In `extract_text()` function** (around line 638):
```python
try:
    import json
    import datetime
    json_output_path = output_file_path.with_suffix('.json')
    write_outputs(
        json_output_path,
        subtitles,
        extracted,
        metadata,
        timestamp_interval,
        structure_source=structure_source,  # NEW
        chapter_count=chapter_count  # NEW
    )
    logger.debug(f"Saved structured data to: {json_output_path}")
except Exception as e:
    logger.warning(f"Could not write JSON output: {e}")
```

---

## Phase 6: Update Documentation

### 6.1 Update Command Examples in Docstrings

**In `extract` command**:
```python
"""Extract text from subtitle files.

Removes timestamps and formatting to create readable text documents.

Examples:
  Basic:                 uv run subxx extract video.srt
  Markdown:              uv run subxx extract video.srt -f md
  With timestamps:       uv run subxx extract video.srt -t 300
  With chapters:         uv run subxx extract video.srt --chapters -f md
  Chapter + fallback:    uv run subxx extract video.srt --chapters --fallback-timestamps 300 -f md
  Auto-structure:        uv run subxx extract video.srt --auto-structure -f md
  PDF output:            uv run subxx extract video.srt -f pdf
"""
```

**In `subs` command**:
```python
"""Fetch subtitles for a video URL.

Format determines behavior:
  srt/vtt: Download subtitle file
  txt/md/pdf: Download SRT → Extract text → Delete SRT

Examples:
  Subtitle file:         uv run subxx subs <url>
  Plain text:            uv run subxx subs <url> --txt
  Markdown:              uv run subxx subs <url> --md
  With timestamps:       uv run subxx subs <url> --md --timestamps 300
  With chapters:         uv run subxx subs <url> --md --chapters
  Chapter + fallback:    uv run subxx subs <url> --md --chapters --fallback-timestamps 300
  Auto-structure:        uv run subxx subs <url> --md --auto-structure
  PDF:                   uv run subxx subs <url> --pdf
"""
```

### 6.2 Update README.md

Add new sections:
- Document `--chapters` flag behavior
- Document `--fallback-timestamps` usage
- Document `--auto-structure` mode
- Document `--min-chapters` threshold
- Add examples showing fallback scenarios

---

## Testing Plan

### Test Case 1: Real YouTube Chapters
```bash
uv run python __main__.py extract \
  "D:\git.dhl.com\cg371p\agents-pub\workspace\transcripts\ai-tech-stack-2026\original-b61fce5c.srt" \
  --chapters -f md --force
```

**Expected**:
- Uses 9 real YouTube chapters
- Output has 9 H3 headers with real titles
- JSON metadata: `structure_source: "youtube_metadata"`, `chapter_count: 9`

### Test Case 2: Fallback to Virtual Chapters
```bash
# Remove metadata file temporarily or use file without metadata
uv run python __main__.py extract test-no-chapters.srt \
  --chapters --fallback-timestamps 300 -f md --force
```

**Expected**:
- Falls back to 300s intervals
- Output has virtual chapters: "Section 1 (0:00-5:00)", etc.
- JSON metadata: `structure_source: "timestamp_fallback"`
- H3 format identical to Test Case 1

### Test Case 3: No Fallback (Legacy Behavior)
```bash
uv run python __main__.py extract test-no-chapters.srt \
  --chapters -f md --force
```

**Expected**:
- Warning logged: "no chapter data and no fallback; continuing without chapters"
- Output has paragraphs only (no H3 markers)
- JSON metadata: `structure_source: "none"`

### Test Case 4: Min Chapters Threshold
```bash
# Use file with only 1 chapter
uv run python __main__.py extract video-1-chapter.srt \
  --chapters --min-chapters 2 --fallback-timestamps 300 -f md --force
```

**Expected**:
- Log: "Only 1 chapter(s) found (< min 2); using fallback"
- Falls back to virtual chapters
- JSON metadata: `structure_source: "timestamp_fallback"`

### Test Case 5: Auto-Structure with Chapters
```bash
uv run python __main__.py extract \
  "D:\git.dhl.com\cg371p\agents-pub\workspace\transcripts\ai-tech-stack-2026\original-b61fce5c.srt" \
  --auto-structure -f md --force
```

**Expected**:
- Log: "Auto-structure: using 9 YouTube chapters"
- Uses real chapters
- Output identical to Test Case 1

### Test Case 6: Auto-Structure without Chapters
```bash
uv run python __main__.py extract test-no-chapters.srt \
  --auto-structure -f md --force
```

**Expected**:
- Log: "Auto-structure: no valid chapters found, using 300s timestamp intervals"
- Uses 300s timestamps (not chapter objects, but timestamp markers like `[0:00]`)
- JSON metadata: `structure_source: "timestamps"`

### Test Case 7: TXT Format with Chapters
```bash
uv run python __main__.py extract \
  "D:\git.dhl.com\cg371p\agents-pub\workspace\transcripts\ai-tech-stack-2026\original-b61fce5c.srt" \
  --chapters -f txt --force
```

**Expected**:
- Output has decorated chapter headers: `=== Chapter Title ===`
- Same content as markdown but different formatting

### Test Case 8: PDF Format with Chapters
```bash
uv run python __main__.py extract \
  "D:\git.dhl.com\cg371p\agents-pub\workspace\transcripts\ai-tech-stack-2026\original-b61fce5c.srt" \
  --chapters -f pdf --force
```

**Expected**:
- PDF has chapter titles as section headings
- Proper paragraph formatting within each chapter

---

## Implementation Checklist

### Phase 1: Refactor Chapter Structure
- [ ] Modify `extract_with_chapters()` to return chapter objects
- [ ] Update `write_txt()` to detect and format chapter objects
- [ ] Update `write_markdown()` to detect and format chapter objects
- [ ] Update `write_pdf()` to detect and format chapter objects
- [ ] Test with existing test data (should produce same visual output)

### Phase 2: Virtual Chapters
- [ ] Implement `generate_virtual_chapters()` function
- [ ] Add unit tests for virtual chapter generation
- [ ] Test with various video lengths (5min, 20min, 1hr)

### Phase 3: Fallback Strategy
- [ ] Add `fallback_timestamps` parameter to `extract` command
- [ ] Add `min_chapters` parameter to `extract` command
- [ ] Add `fallback_timestamps` parameter to `subs` command
- [ ] Add `min_chapters` parameter to `subs` command
- [ ] Update `extract_text()` signature and logic
- [ ] Implement chapter quality check (`min_chapters`)
- [ ] Implement fallback logic (try chapters → try fallback → none)
- [ ] Pass new parameters through CLI to `extract_text()`
- [ ] Test TC-2, TC-3, TC-4

### Phase 4: Auto-Structure
- [ ] Add `auto_structure` flag to `extract` command
- [ ] Add `auto_structure` flag to `subs` command
- [ ] Implement auto-detection logic in `extract` command
- [ ] Implement auto-detection logic in `subs` command
- [ ] Test TC-5, TC-6

### Phase 5: Enhanced Metadata
- [ ] Update `write_outputs()` signature
- [ ] Add `structure_source` and `chapter_count` to JSON
- [ ] Update all calls to `write_outputs()`
- [ ] Verify JSON structure in all test cases

### Phase 6: Documentation
- [ ] Update `extract` command docstring
- [ ] Update `subs` command docstring
- [ ] Update README.md with new features
- [ ] Document fallback behavior and examples

### Phase 7: Final Testing
- [ ] Run all 8 test cases
- [ ] Verify backward compatibility (existing flags still work)
- [ ] Check JSON metadata in all scenarios
- [ ] Verify TXT, MD, and PDF outputs all correct
- [ ] Test with various video lengths and chapter counts

---

## Files to Modify

1. **subxx.py** (~400 lines modified):
   - Lines 769-873: Refactor `extract_with_chapters()`
   - After 873: Add `generate_virtual_chapters()` (~40 lines)
   - Lines 534-644: Update `extract_text()` signature and logic (~100 lines)
   - Lines 780+: Update `write_outputs()` (~30 lines)
   - Lines 876-880: Update `write_txt()` (~20 lines)
   - Lines 882-950: Update `write_markdown()` (~30 lines)
   - PDF writer: Update `write_pdf()` (~30 lines)

2. **__main__.py** (~100 lines modified):
   - Lines 418-434: Add flags to `extract` command (~10 lines)
   - After 450: Add auto-structure logic (~30 lines)
   - Lines 456-463: Pass new parameters (~5 lines)
   - Lines 134-153: Add flags to `subs` command (~10 lines)
   - After 280: Add auto-structure logic (~30 lines)
   - Lines 297-304: Pass new parameters (~5 lines)

**Total estimate**: ~500 lines modified/added

---

## Backward Compatibility

### Breaking Changes
- Chapter titles no longer have `###` prefix in data structure (but output looks the same)
- `extract_with_chapters()` now returns `List[dict]` instead of `List[str]`

### Compatible Changes
- Existing `--timestamps` behavior unchanged
- Existing paragraph-only output unchanged
- Writers handle both flat strings and chapter objects
- All existing CLI flags work as before

### Migration Path
If external code depends on `extract_with_chapters()`:
1. Check if result is list of dicts
2. If yes, iterate and format chapters
3. If no, use existing logic (flat strings)

---

## Success Criteria

- [ ] All 8 test cases pass
- [ ] Output format identical whether using real or virtual chapters
- [ ] Backward compatibility maintained (existing tests still pass)
- [ ] JSON metadata correctly tracks structure source
- [ ] TXT, MD, and PDF outputs all handle chapters correctly
- [ ] Fallback logic works seamlessly
- [ ] Auto-structure mode makes sensible decisions
- [ ] Documentation complete and accurate
- [ ] No regressions in existing functionality

---

## Related Files

- `FEATURE_REQUESTS.md` - Original feature request specification
- `subxx.py` - Core extraction logic
- `__main__.py` - CLI interface
- `test_subxx.py` - Test suite (update with new tests)
- `README.md` - User documentation (update with new features)
