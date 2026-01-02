"""
subxx.py - Core module for subtitle fetching

Provides fetch_subs() function wrapping yt-dlp for downloading subtitles.
Supports language selection, format conversion (VTT→SRT), and configuration.
"""

import sys
import re
import os
from pathlib import Path
from typing import Optional, List
import logging

# Exit codes
EXIT_SUCCESS = 0
EXIT_USER_CANCELLED = 1
EXIT_NO_SUBTITLES = 2
EXIT_NETWORK_ERROR = 3
EXIT_INVALID_URL = 4
EXIT_CONFIG_ERROR = 5
EXIT_FILE_ERROR = 6

# Text extraction constants
SENTENCES_PER_PARAGRAPH = 6  # Number of sentences to group per paragraph
SENTENCE_BOUNDARY_MARKER = (
    "<|||SENTENCE_BOUNDARY|||>"  # Unique marker for sentence breaks
)


def generate_file_hash(video_id: str) -> str:
    """Generate an 8-character hash from video ID for filename disambiguation.

    Args:
        video_id: YouTube video ID

    Returns:
        8-character hexadecimal hash string
    """
    import hashlib

    return hashlib.sha256(video_id.encode()).hexdigest()[:8]


# TOML support: tomllib (3.11+) or tomli (3.9-3.10)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


def load_config() -> dict:
    """Load config from TOML file (project then global).

    Config file locations checked in order:
    1. ./.subxx.toml (project-specific)
    2. ~/.subxx.toml (user global)

    Returns:
        Configuration dictionary (empty dict if no config found)
    """
    if tomllib is None:
        return {}

    config_files = [
        Path.cwd() / ".subxx.toml",  # Project config
        Path.home() / ".subxx.toml",  # Global config
    ]

    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file, "rb") as f:
                    return tomllib.load(f)
            except Exception as e:
                logging.warning(f"Failed to load config from {config_file}: {e}")
                continue

    return {}  # No config found


def get_default(config: dict, key: str, fallback: any) -> any:
    """Get value from config with fallback.

    Args:
        config: Configuration dictionary
        key: Key to look up in config['defaults']
        fallback: Default value if key not found

    Returns:
        Config value or fallback
    """
    return config.get("defaults", {}).get(key, fallback)


def parse_languages(langs: str) -> Optional[List[str]]:
    """Parse language parameter into list.

    Args:
        langs: Language string (e.g., "en", "en,de,fr", "all")

    Returns:
        List of language codes, or None for "all"
    """
    langs = langs.strip()

    if langs.lower() == "all":
        return None  # None means download all

    # Split by comma and strip whitespace
    lang_list = [lang.strip() for lang in langs.split(",")]
    return lang_list


def construct_output_path(output_dir: str, filename: str) -> Path:
    """Construct output path with home directory expansion.

    Args:
        output_dir: Output directory (may contain ~)
        filename: Filename to append

    Returns:
        Absolute Path object
    """
    output_path = Path(output_dir).expanduser()
    return output_path / filename


def safe_write_file(
    file_path: Path, content: str, force: bool = False, skip_existing: bool = False
) -> bool:
    """Safely write file with overwrite protection.

    Args:
        file_path: Path to write
        content: Content to write
        force: If True, overwrite without prompt
        skip_existing: If True, skip if exists

    Returns:
        True if file was written, False if skipped
    """
    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if file exists
    if file_path.exists():
        if skip_existing:
            return False

        if not force:
            # This would normally prompt, but for testing we'll just not overwrite
            # In real CLI implementation, this uses typer.confirm()
            return False

    # Write file
    try:
        file_path.write_text(content, encoding="utf-8")
        return True
    except IOError as e:
        logging.error(f"Failed to write file {file_path}: {e}")
        return False


def fetch_subs(
    url: str,
    langs: str = "en",
    fmt: str = "srt",
    auto: bool = True,
    output_dir: str = ".",
    out_template: str = "%(title)s.%(id)s.%(lang)s.%(ext)s",
    prompt_overwrite: bool = True,
    skip_existing: bool = False,
    dry_run: bool = False,
    verbosity: str = "normal",
    sanitize: str = "safe",
) -> int:
    """Fetch subtitles for a video URL.

    Args:
        url: Video URL to fetch subtitles from
        langs: Language codes (comma-separated, e.g., "en,de,fr" or "all")
        fmt: Output format ("srt" or "vtt")
        auto: Include auto-generated subtitles as fallback (default: True)
              IMPORTANT: Manual subtitles ALWAYS have priority over auto-generated.
              - auto=True: Download manual if available, fallback to auto-generated
              - auto=False: Download manual only, fail if none exist
        output_dir: Directory to save files (default: current directory ".")
        out_template: Filename template (default includes lang code)
        prompt_overwrite: If True (default), fail fast if file exists.
                         If False (--force), allow overwriting.
                         NOTE: Actual prompting not implemented, will fail immediately.
        skip_existing: Skip existing files silently without error
        dry_run: Preview without downloading
        verbosity: Output verbosity level:
                   - 'quiet': Errors only
                   - 'normal': Clean summary (default)
                   - 'verbose': All debug output
        sanitize: Filename sanitization strategy (via yt-dlp restrictfilenames):
                  - 'safe': Minimal sanitization (default, yt-dlp default behavior)
                  - 'nospaces': ASCII-safe, spaces→underscores (restrictfilenames=True)
                  - 'slugify': Same as nospaces (restrictfilenames=True)

    Returns:
        int: Exit code (0 = success, non-zero = error)
    """
    import yt_dlp

    logger = logging.getLogger("subxx")

    # Parse language parameter
    parsed_langs = parse_languages(langs)

    # Ensure output directory exists
    output_path_obj = Path(output_dir).expanduser()
    output_path_obj.mkdir(parents=True, exist_ok=True)

    # Construct full output path
    output_path = os.path.join(output_path_obj, out_template)

    # OVERWRITE PROTECTION: Check for existing files
    # - If neither --force nor --skip-existing: fail fast with error
    # - If --skip-existing: silently skip and return success
    if prompt_overwrite or skip_existing:
        # This is the default case - fail fast if file exists
        # We need to check what files would be created

        # Get video info to determine potential filenames
        try:
            with yt_dlp.YoutubeDL({"skip_download": True, "quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)

            video_id = info.get("id", "unknown")
            video_title = info.get("title", "video")

            # Determine which languages would be downloaded
            manual_subs = info.get("subtitles", {})
            auto_subs = info.get("automatic_captions", {}) if auto else {}

            available_langs = set(manual_subs.keys())
            if auto:
                available_langs.update(auto_subs.keys())

            # Determine target languages
            if parsed_langs:
                target_langs = [
                    lang for lang in parsed_langs if lang in available_langs
                ]
            else:
                target_langs = list(manual_subs.keys())[
                    :1
                ]  # Default: first manual subtitle

            # Check for existing files using glob patterns
            # yt-dlp may add additional fields to filename, so use glob
            existing_files = []
            for lang in target_langs:
                # Check for requested format with glob pattern
                # Pattern: *video_id*.lang.ext (accounts for yt-dlp additions like .NA)
                pattern = f"*{video_id}*.{lang}.{fmt}"
                matches = list(output_path_obj.glob(pattern))
                existing_files.extend(matches)

            # If any files exist, handle based on mode
            if existing_files:
                if skip_existing:
                    # Skip mode: silently skip and return success
                    logger.debug(f"Skipping {len(existing_files)} existing file(s)")
                    return EXIT_SUCCESS
                else:
                    # Default mode: fail fast with helpful message
                    logger.error("❌ Error: The following file(s) already exist:")
                    for f in existing_files[:5]:  # Show max 5 files
                        logger.error(f"   - {f.name}")
                    if len(existing_files) > 5:
                        logger.error(f"   ... and {len(existing_files) - 5} more")
                    logger.error("")
                    logger.error("Use one of these options:")
                    logger.error("  --force           Overwrite without prompting")
                    logger.error("  --skip-existing   Skip existing files silently")
                    return EXIT_FILE_ERROR

        except Exception as e:
            # If info fetch fails, log warning but continue
            logger.warning(f"Could not check for existing files: {e}")

    # CRITICAL: Subtitle priority logic
    # yt-dlp behavior with these flags:
    # 1. writesubtitles=True, writeautomaticsub=False
    #    → Download ONLY manual subtitles (fail if none exist)
    # 2. writesubtitles=True, writeautomaticsub=True
    #    → Download manual if available, FALLBACK to auto-generated
    # 3. Manual subtitles ALWAYS take priority when both exist

    # Set yt-dlp verbosity based on our verbosity level
    ydl_quiet = verbosity != "verbose"  # Show yt-dlp output only in verbose mode
    ydl_no_warnings = verbosity != "verbose"  # Suppress warnings except in verbose mode
    ydl_noprogress = verbosity != "verbose"  # Hide progress bar except in verbose mode

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,  # Always try manual subs first
        "writeautomaticsub": auto,  # Fallback to auto if manual don't exist
        "subtitleslangs": parsed_langs,
        "subtitlesformat": fmt,  # Let yt-dlp download in requested format (srt/vtt)
        "outtmpl": output_path,  # Full path including directory
        "nooverwrites": prompt_overwrite
        or skip_existing,  # Prevent overwrites unless --force
        "quiet": ydl_quiet,  # Hide yt-dlp output except in verbose mode
        "no_warnings": ydl_no_warnings,  # Suppress warnings in quiet mode
        "noprogress": ydl_noprogress,  # Hide progress bar except in verbose mode
        # Retry configuration for reliability
        "retries": 3,  # Number of retries for downloads
        "fragment_retries": 3,  # Retries for fragmented downloads
        "file_access_retries": 3,  # Retries for file access
        "sleep_interval": 10,  # Sleep between requests (avoid rate limiting)
        "max_sleep_interval": 30,  # Max sleep interval for exponential backoff
        "sleep_interval_requests": 2,  # Sleep between each request within the download process
    }

    # Apply filename sanitization via yt-dlp
    if sanitize in ["nospaces", "slugify"]:
        ydl_opts["restrictfilenames"] = (
            True  # Replaces spaces with underscores, ASCII-safe
        )

    # Dry run mode
    if dry_run:
        try:
            with yt_dlp.YoutubeDL({"skip_download": True, "quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)

                logger.info("🔍 Dry run: Would download subtitles for:")
                logger.info(f"   Video: {info.get('title', 'Unknown')}")
                logger.info(f"   URL: {url}\n")

                # Determine which languages would be downloaded
                requested_langs = parsed_langs if parsed_langs else []

                manual_subs = info.get("subtitles", {})
                auto_subs = info.get("automatic_captions", {})

                logger.info("Would create files:")
                langs_to_check = (
                    requested_langs if requested_langs else list(manual_subs.keys())
                )
                for lang in langs_to_check:
                    if lang in manual_subs or (auto and lang in auto_subs):
                        filename = f"{info.get('title', 'video')}.{info.get('id', 'unknown')}.{lang}.{fmt}"
                        output_file = Path(output_dir) / filename
                        logger.info(f"   ✓ {output_file}")

                logger.info("\n💡 Run without --dry-run to download")
                return EXIT_SUCCESS
        except Exception as e:
            logger.error(f"❌ Dry run failed: {e}")
            return EXIT_NETWORK_ERROR

    # Normal mode: Show clean summary before download
    video_title = "Unknown"
    if verbosity == "normal":
        try:
            with yt_dlp.YoutubeDL({"skip_download": True, "quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get("title", "Unknown")

            logger.info(f"📥 Downloading subtitles for: {video_title}")
            logger.info(f"🌐 Languages: {langs}")
        except Exception:
            pass  # If info fetch fails, continue with download

    # Execute yt-dlp
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            exit_code = ydl.download([url])

            if exit_code != 0:
                # Check what went wrong
                logger.error("❌ No subtitles found for requested languages")

                if not auto:
                    logger.info(
                        "💡 Tip: Try --auto to include auto-generated subtitles"
                    )
                else:
                    logger.info("💡 Tip: Use 'list' command to see available languages")

                return EXIT_NO_SUBTITLES

            # Success - yt-dlp handled the download
            # In normal mode, we already showed "📥 Downloading..." message

            # Fetch and save metadata (video + channel)
            try:
                _save_metadata(url, output_path_obj, logger)
            except Exception as e:
                logger.warning(f"⚠️  Could not save metadata: {e}")
                # Don't fail the entire operation if metadata fails

            # Silent success = success (following Unix philosophy)
            return EXIT_SUCCESS

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"❌ Download failed: {e}")
        logger.info("💡 Tip: Check your internet connection")
        return EXIT_NETWORK_ERROR

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return EXIT_NETWORK_ERROR


def _save_metadata(url: str, output_dir: Path, logger) -> None:
    """
    Fetch and save video metadata to JSON file.

    Fetches channel description via direct HTTP request to avoid yt-dlp's
    slow video enumeration.

    Args:
        url: Video URL
        output_dir: Directory where metadata file will be saved
        logger: Logger instance
    """
    import json
    import hashlib
    import yt_dlp

    try:
        import urllib.request
    except ImportError:
        import urllib2 as urllib

    # Create fresh YoutubeDL instance for metadata-only fetching
    with yt_dlp.YoutubeDL(
        {"quiet": True, "skip_download": True, "no_warnings": True}
    ) as ydl:
        # Fetch video metadata (already includes channel_follower_count and channel_is_verified)
        video_info = ydl.extract_info(url, download=False)
        if not video_info:
            raise ValueError("Could not fetch video metadata")

        # Generate file hash from video ID
        video_id = video_info.get("id", "unknown")
        file_hash = hashlib.sha256(video_id.encode()).hexdigest()[:8]

        # Fetch channel description via HTTP if channel URL is available
        # Version: Working as of 2025-11-01
        # Method: Parse HTML with BeautifulSoup to extract <meta name="description">
        # Location: Found in page <head> section
        channel_url = video_info.get("channel_url")
        if channel_url:
            try:
                logger.debug(f"Fetching channel description from: {channel_url}")

                # Make HTTP request to channel/about page
                req = urllib.request.Request(
                    channel_url + "/about",
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode("utf-8", errors="ignore")

                # Parse HTML with BeautifulSoup to extract meta description
                # HTML selector: <meta name="description" content="...">
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(html, "html.parser")
                meta_tag = soup.find("meta", attrs={"name": "description"})

                if meta_tag and meta_tag.get("content"):
                    description = meta_tag.get("content")
                    video_info["channel_description"] = description
                    logger.debug(
                        f"Fetched channel description ({len(description)} chars)"
                    )
                else:
                    logger.debug("Could not find meta description tag in HTML")

            except Exception as e:
                logger.warning(f"Could not fetch channel description: {e}")

        # Log available channel metadata
        if video_info.get("channel_follower_count"):
            logger.debug(
                f"Channel: {video_info.get('channel')}, followers={video_info.get('channel_follower_count')}, verified={video_info.get('channel_is_verified')}"
            )

    # Save to metadata-{hash}.json
    metadata_file = output_dir / f"metadata-{file_hash}.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(video_info, f, indent=2, ensure_ascii=False)

    logger.debug(f"Saved metadata to: {metadata_file}")


def setup_logging(
    verbose: bool = False, quiet: bool = False, log_file: Optional[str] = None
):
    """Configure logging based on verbosity settings.

    Args:
        verbose: Enable debug logging
        quiet: Show errors only
        log_file: Optional log file path

    Returns:
        Logger instance
    """
    # Determine log level
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # Create formatter
    formatter = logging.Formatter("%(message)s")  # Simple format for CLI

    # Setup handlers
    handlers = []

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, mode="a")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=level, handlers=handlers, force=True)

    return logging.getLogger("subxx")


def extract_text(
    subtitle_file: str,
    output_format: str = "txt",
    timestamp_interval: Optional[int] = None,
    output_file: Optional[str] = None,
    force: bool = False,
    use_chapters: bool = False,
    fallback_timestamps: Optional[int] = None,
    min_chapters: Optional[int] = None,
) -> int:
    """Extract text from SRT subtitle file.

    Args:
        subtitle_file: Path to subtitle file (.srt or .vtt)
        output_format: Output format ("txt", "md", or "pdf")
        timestamp_interval: Optional interval in seconds for timestamp markers
                           (e.g., 300 for every 5 minutes)
        output_file: Output file path (auto-generated if None)
        force: Overwrite existing output file without prompt
        use_chapters: Use chapter markers from metadata instead of timestamps
        fallback_timestamps: Fallback to virtual chapters with this interval if YouTube chapters unavailable/insufficient
        min_chapters: Minimum required chapters for YouTube chapters to be used (otherwise fall back)

    Returns:
        int: Exit code (0 = success, non-zero = error)
    """
    logger = logging.getLogger("subxx")

    # Check file format
    subtitle_path = Path(subtitle_file)
    if not subtitle_path.exists():
        logger.error(f"File not found: {subtitle_file}")
        return EXIT_FILE_ERROR

    # VTT not implemented
    if subtitle_path.suffix.lower() == ".vtt":
        logger.error("❌ VTT extraction not implemented yet")
        logger.info("💡 Tip: Convert to SRT first using the 'subs' command")
        return EXIT_FILE_ERROR

    # Load metadata if available (look for metadata-*.json or metadata.json)
    metadata = None
    metadata_files = list(subtitle_path.parent.glob("metadata-*.json"))
    if not metadata_files:
        # Fallback to old naming without hash
        metadata_files = [subtitle_path.parent / "metadata.json"]

    for metadata_file in metadata_files:
        if metadata_file.exists():
            try:
                import json

                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                logger.debug(f"Loaded metadata from: {metadata_file}")
                break
            except Exception as e:
                logger.warning(f"Could not load metadata from {metadata_file}: {e}")

    # Parse SRT file
    try:
        import srt

        with open(subtitle_path, encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))
    except ImportError:
        logger.error("❌ Missing 'srt' library")
        logger.info("💡 Install with: uv sync --extra extract")
        return EXIT_CONFIG_ERROR
    except Exception as e:
        logger.error(f"Failed to parse SRT file: {e}")
        return EXIT_FILE_ERROR

    # Extract text with fallback strategy
    structure_source = "plain"  # Track what structure we used
    extracted = None

    # STRATEGY 1: Try YouTube chapters if requested
    if use_chapters and metadata and "chapters" in metadata and metadata["chapters"]:
        chapters = metadata["chapters"]
        chapter_count = len(chapters)

        # Check if we have enough chapters (if min_chapters specified)
        if min_chapters and chapter_count < min_chapters:
            logger.warning(
                f"Only {chapter_count} YouTube chapters found (min {min_chapters} required); falling back"
            )
            if fallback_timestamps:
                # Fall back to virtual chapters
                logger.info(f"Generating virtual chapters every {fallback_timestamps}s")
                extracted = generate_virtual_chapters(subtitles, fallback_timestamps)
                structure_source = "virtual_chapters"
            else:
                # Fall back to plain paragraphs
                logger.info("Falling back to plain paragraph format")
                extracted = extract_with_timestamps(subtitles, None)
                structure_source = "plain"
        else:
            # Use YouTube chapters
            logger.info(f"Using {chapter_count} YouTube chapters from metadata")
            if timestamp_interval:
                logger.warning(
                    "Both --chapters and --timestamps specified; using --chapters (ignoring --timestamps)"
                )
            extracted = extract_with_chapters(subtitles, chapters)
            structure_source = "youtube_chapters"

    # STRATEGY 2: Try virtual chapters if fallback_timestamps specified
    elif use_chapters and fallback_timestamps:
        logger.warning("--chapters specified but no chapter data found in metadata")
        logger.info(f"Generating virtual chapters every {fallback_timestamps}s")
        extracted = generate_virtual_chapters(subtitles, fallback_timestamps)
        structure_source = "virtual_chapters"

    # STRATEGY 3: Use timestamp markers (old behavior)
    elif timestamp_interval:
        extracted = extract_with_timestamps(subtitles, timestamp_interval)
        structure_source = "timestamps"

    # STRATEGY 4: Plain paragraphs (no structure)
    else:
        extracted = extract_with_timestamps(subtitles, None)
        structure_source = "plain"

    # Warn if chapters requested but not available and no fallback
    if (
        use_chapters
        and (not metadata or "chapters" not in metadata)
        and not fallback_timestamps
    ):
        logger.warning(
            "--chapters specified but no chapter data or fallback found; using plain format"
        )

    # Determine output file
    if output_file is None:
        output_file_path = subtitle_path.with_suffix(f".{output_format}")
    else:
        output_file_path = Path(output_file)

    # Check overwrite
    if output_file_path.exists() and not force:
        logger.error(f"Output file exists: {output_file_path}")
        logger.error("Use --force to overwrite")
        return EXIT_FILE_ERROR

    # Write output based on format
    try:
        if output_format == "txt":
            write_txt(output_file_path, extracted)
        elif output_format == "md":
            write_markdown(output_file_path, extracted, subtitle_path.stem, metadata)
        elif output_format == "pdf":
            write_pdf(output_file_path, extracted, subtitle_path.stem)
        else:
            logger.error(f"Unknown format: {output_format}")
            return EXIT_FILE_ERROR
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.info("💡 Install with: uv sync --extra extract")
        return EXIT_CONFIG_ERROR
    except Exception as e:
        logger.error(f"Failed to write output: {e}")
        return EXIT_FILE_ERROR

    # Also write JSON for persistence
    try:
        import json

        json_output_path = output_file_path.with_suffix(".json")
        write_outputs(
            json_output_path,
            subtitles,
            extracted,
            metadata,
            timestamp_interval,
            structure_source=structure_source,
        )
        logger.debug(f"Saved structured data to: {json_output_path}")
    except Exception as e:
        logger.warning(f"Could not write JSON output: {e}")

    logger.info(f"✅ Extracted text to: {output_file_path}")
    return EXIT_SUCCESS


def format_timestamp(seconds: float) -> str:
    """Format seconds as [H:]MM:SS timestamp string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string like [5:30] or [1:05:30]
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"[{hours}:{minutes:02d}:{secs:02d}]"
    else:
        return f"[{minutes}:{secs:02d}]"


def extract_with_timestamps(
    subtitles: List, interval: Optional[int] = None
) -> List[str]:
    """Extract text with optional timestamp markers and smart paragraph breaks.

    Uses a two-pass approach:
    1. First pass: Build items list (text + timestamps + speaker markers)
    2. Second pass: Mark sentence boundaries and group into paragraphs

    Args:
        subtitles: List of parsed SRT subtitle objects
        interval: Interval in seconds for timestamp markers (None = no timestamps)

    Returns:
        List of text lines/paragraphs with optional timestamp markers
    """

    # PASS 1: Build sequence of items (text, timestamps, speakers)
    items = []  # List of (type, content) tuples
    last_marker = -1

    for sub in subtitles:
        content = sub.content.strip()
        if not content:
            continue

        # Check if we need a timestamp marker before this content
        if interval:
            current_time = sub.start.total_seconds()
            if last_marker == -1 or current_time - last_marker >= interval:
                timestamp = format_timestamp(current_time)
                items.append(("timestamp", timestamp))
                last_marker = current_time

        # Replace >> with 💬 for speaker changes
        if content.startswith(">>"):
            content = f"💬 {content[2:].strip()}"

        items.append(("text", content))

    # Safety check: verify marker doesn't exist in actual content
    full_text_sample = " ".join(item[1] for item in items if item[0] == "text")[:1000]
    if SENTENCE_BOUNDARY_MARKER in full_text_sample:
        # Fallback: use even more unique marker
        marker = f"<|||SENT_{id(items)}|||>"
    else:
        marker = SENTENCE_BOUNDARY_MARKER

    # PASS 2: Process items, marking sentence boundaries in text chunks
    result = []
    current_para = []
    sentence_count = 0

    for item_type, item_content in items:
        if item_type == "timestamp":
            # Flush current paragraph before timestamp
            if current_para:
                result.append(" ".join(current_para))
                current_para = []
                sentence_count = 0
            # Add timestamp
            result.append(item_content)
        else:  # text
            # Mark sentence boundaries in this text chunk
            text_with_markers = re.sub(
                r"([a-zA-Z])\.\s+([A-Z])", rf"\1.{marker}\2", item_content
            )

            # Split by sentence markers
            parts = text_with_markers.split(marker)

            for part in parts:
                part = part.strip()
                if not part:
                    continue

                # Check if this is a speaker change (starts new paragraph)
                if part.startswith("💬") and current_para:
                    # Flush current paragraph
                    result.append(" ".join(current_para))
                    current_para = [part]
                    sentence_count = 1 if part.endswith(".") else 0
                else:
                    # Add to current paragraph
                    current_para.append(part)

                    # Count as sentence if it ends with period
                    if part.endswith("."):
                        sentence_count += 1

                    # Break if we've accumulated enough sentences
                    if sentence_count >= SENTENCES_PER_PARAGRAPH:
                        result.append(" ".join(current_para))
                        current_para = []
                        sentence_count = 0

    # Flush any remaining paragraph
    if current_para:
        result.append(" ".join(current_para))

    return result


def extract_with_chapters(subtitles: List, chapters: List[dict]) -> List[dict]:
    """Extract text with chapter structure and smart paragraph breaks.

    Inserts chapter boundaries while maintaining the sentence-based
    paragraph splitting (6 sentences per paragraph).

    Args:
        subtitles: List of parsed SRT subtitle objects
        chapters: List of chapter dicts with 'start_time', 'title', 'end_time'

    Returns:
        List of chapter objects:
        [
            {
                "type": "chapter",
                "title": "Chapter Title",
                "content": ["paragraph1", "paragraph2", ...]
            },
            ...
        ]
    """

    # PASS 1: Build sequence of items (text, chapters, speakers)
    items = []  # List of (type, content) tuples
    chapter_idx = 0
    last_chapter_inserted = -1

    for sub in subtitles:
        content = sub.content.strip()
        if not content:
            continue

        # Check if we need a chapter marker before this content
        current_time = sub.start.total_seconds()

        # Find which chapter we're currently in
        while chapter_idx < len(chapters) and current_time >= chapters[chapter_idx].get(
            "end_time", float("inf")
        ):
            chapter_idx += 1

        # Insert chapter marker if we've moved to a new chapter
        if chapter_idx < len(chapters) and chapter_idx != last_chapter_inserted:
            if current_time >= chapters[chapter_idx]["start_time"]:
                chapter_title = chapters[chapter_idx].get(
                    "title", f"Chapter {chapter_idx + 1}"
                )
                items.append(("chapter", chapter_title))
                last_chapter_inserted = chapter_idx

        # Replace >> with 💬 for speaker changes
        if content.startswith(">>"):
            content = f"💬 {content[2:].strip()}"

        items.append(("text", content))

    # Safety check: verify marker doesn't exist in actual content
    full_text_sample = " ".join(item[1] for item in items if item[0] == "text")[:1000]
    if SENTENCE_BOUNDARY_MARKER in full_text_sample:
        # Fallback: use even more unique marker
        marker = f"<|||SENT_{id(items)}|||>"
    else:
        marker = SENTENCE_BOUNDARY_MARKER

    # PASS 2: Build chapter objects with content
    result = []
    current_chapter = None
    current_chapter_content = []
    current_para = []
    sentence_count = 0

    for item_type, item_content in items:
        if item_type == "chapter":
            # Close previous chapter
            if current_chapter is not None:
                # Flush any remaining paragraph
                if current_para:
                    current_chapter_content.append(" ".join(current_para))
                    current_para = []
                    sentence_count = 0

                # Save chapter object
                result.append(
                    {
                        "type": "chapter",
                        "title": current_chapter,
                        "content": current_chapter_content,
                    }
                )

            # Start new chapter
            current_chapter = item_content
            current_chapter_content = []
            current_para = []
            sentence_count = 0
        else:  # text
            # Mark sentence boundaries in this text chunk
            text_with_markers = re.sub(
                r"([a-zA-Z])\.\s+([A-Z])", rf"\1.{marker}\2", item_content
            )

            # Split by sentence markers
            parts = text_with_markers.split(marker)

            for part in parts:
                part = part.strip()
                if not part:
                    continue

                # Check if this is a speaker change (starts new paragraph)
                if part.startswith("💬") and current_para:
                    # Flush current paragraph
                    current_chapter_content.append(" ".join(current_para))
                    current_para = [part]
                    sentence_count = 1 if part.endswith(".") else 0
                else:
                    # Add to current paragraph
                    current_para.append(part)

                    # Count as sentence if it ends with period
                    if part.endswith("."):
                        sentence_count += 1

                    # Break if we've accumulated enough sentences
                    if sentence_count >= SENTENCES_PER_PARAGRAPH:
                        current_chapter_content.append(" ".join(current_para))
                        current_para = []
                        sentence_count = 0

    # Close final chapter
    if current_chapter is not None:
        # Flush any remaining paragraph
        if current_para:
            current_chapter_content.append(" ".join(current_para))

        # Save final chapter object
        result.append(
            {
                "type": "chapter",
                "title": current_chapter,
                "content": current_chapter_content,
            }
        )

    return result


def generate_virtual_chapters(subtitles: List, interval_seconds: int) -> List[dict]:
    """Generate virtual chapters based on timestamp intervals.

    Creates time-based chapters when YouTube chapter markers are not available.
    Uses the same smart paragraph grouping (6 sentences per paragraph) as real chapters.

    Args:
        subtitles: List of subtitle objects with start, end, content
        interval_seconds: Time interval for chapter breaks (e.g., 300 for 5 minutes)

    Returns:
        List of chapter objects:
        [
            {
                "type": "chapter",
                "title": "[0:00]",
                "content": ["paragraph1", "paragraph2", ...]
            },
            ...
        ]
    """
    if not subtitles:
        return []

    # PASS 1: Group subtitles into time-based chapters with smart paragraph breaks
    chapters = []
    current_chapter_start = 0
    current_chapter_content = []
    current_para = []
    sentence_count = 0

    for sub in subtitles:
        current_time = sub.start.total_seconds()
        text = sub.content.replace("\n", " ").strip()

        if not text:
            continue

        # Check if we need to start a new chapter
        if (
            current_time >= current_chapter_start + interval_seconds
            and current_chapter_content
        ):
            # Save current chapter
            if current_para:
                current_chapter_content.append(" ".join(current_para))

            chapters.append(
                {
                    "type": "chapter",
                    "title": format_timestamp(current_chapter_start),
                    "content": current_chapter_content,
                }
            )

            # Start new chapter
            current_chapter_start = (
                current_time // interval_seconds
            ) * interval_seconds
            current_chapter_content = []
            current_para = []
            sentence_count = 0

        # Add text to current paragraph
        current_para.append(text)

        # Count sentences (approximate: count sentence-ending punctuation)
        sentence_count += text.count(".") + text.count("!") + text.count("?")

        # Every 6 sentences, start a new paragraph
        if sentence_count >= 6:
            current_chapter_content.append(" ".join(current_para))
            current_para = []
            sentence_count = 0

    # Save final chapter
    if current_para:
        current_chapter_content.append(" ".join(current_para))

    if current_chapter_content:
        chapters.append(
            {
                "type": "chapter",
                "title": format_timestamp(current_chapter_start),
                "content": current_chapter_content,
            }
        )

    return chapters


def write_txt(output_file: Path, lines: List) -> None:
    """Write plain text output.

    Args:
        lines: List of strings (flat paragraphs) or list of chapter objects
    """
    with open(output_file, "w", encoding="utf-8") as f:
        if lines and isinstance(lines[0], dict) and lines[0].get("type") == "chapter":
            # Chapter objects - format with decorated headers
            formatted = []
            for chapter in lines:
                formatted.append(f"=== {chapter['title']} ===\n")
                formatted.extend(chapter["content"])
            f.write("\n\n".join(formatted))
        else:
            # Flat strings - existing behavior
            f.write("\n\n".join(lines))


def write_markdown(
    output_file: Path, lines: List, title: str, metadata: Optional[dict] = None
) -> None:
    """Write Markdown output with optional metadata, headings, channel bio, and citations.

    Args:
        lines: List of strings (flat paragraphs) or list of chapter objects
        title: Document title
        metadata: Optional video metadata
    """

    # Generate file hash from video ID if metadata available
    file_hash = None
    if metadata and metadata.get("id"):
        file_hash = generate_file_hash(metadata["id"])

    with open(output_file, "w", encoding="utf-8") as f:
        # If metadata provided, add YAML frontmatter and enhanced content
        if metadata:
            # YAML frontmatter
            f.write("---\n")
            f.write(f"title: \"{metadata.get('title', title)}\"\n")
            f.write(f"creator: {metadata.get('uploader', 'Unknown')}\n")
            if metadata.get("channel_id"):
                f.write(f"channel_id: {metadata['channel_id']}\n")
            if metadata.get("upload_date"):
                # Format: YYYYMMDD -> YYYY-MM-DD
                date_str = metadata["upload_date"]
                if len(date_str) == 8:
                    date_formatted = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    f.write(f"date: {date_formatted}\n")
            if metadata.get("duration"):
                duration = metadata["duration"]
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                f.write(f'duration: "{minutes}:{seconds:02d}"\n')
            f.write(f"source: {metadata.get('webpage_url', '')}\n")
            f.write(f"video_id: {metadata.get('id', '')}\n")
            f.write(f"language: {metadata.get('language', 'en')}\n")
            if metadata.get("view_count"):
                f.write(f"views: {metadata['view_count']}\n")
            # Reference thumbnail with hash suffix
            thumbnail_name = (
                f"thumbnail-{file_hash}.jpg" if file_hash else "thumbnail.jpg"
            )
            f.write(f"thumbnail: {thumbnail_name}\n")
            if metadata.get("description"):
                # Truncate and normalize description (replace newlines with spaces)
                desc = metadata["description"][:500].replace("\n", " ").strip()
                # Use folded scalar style for proper YAML multiline string
                f.write("description: >\n")
                f.write(f"  {desc}\n")
            if metadata.get("tags"):
                tags_str = ", ".join(metadata["tags"][:10])  # First 10 tags
                f.write(f"tags: [{tags_str}]\n")
            f.write("---\n\n")

            # Human-readable header
            video_title = metadata.get("title", title)
            f.write(f"# {video_title}\n\n")

            channel_name = metadata.get("uploader", "Unknown")
            channel_url = metadata.get("channel_url", metadata.get("uploader_url", ""))
            webpage_url = metadata.get("webpage_url", "")

            f.write(f"**📺 Source:** [Watch on YouTube]({webpage_url})  \n")
            if channel_url:
                f.write(f"**👤 Channel:** [{channel_name}]({channel_url})  \n")
            else:
                f.write(f"**👤 Channel:** {channel_name}  \n")

            if metadata.get("duration"):
                duration = metadata["duration"]
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                f.write(f"**⏱ Duration:** {minutes}:{seconds:02d}  \n")

            if metadata.get("upload_date"):
                date_str = metadata["upload_date"]
                if len(date_str) == 8:
                    date_formatted = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
                    f.write(f"**📅 Published:** {date_formatted}  \n")

            if metadata.get("view_count"):
                f.write(f"**👁 Views:** {metadata['view_count']:,}  \n")

            # Add thumbnail image if available (not clickable)
            f.write("\n")
            f.write(f"![Video thumbnail]({thumbnail_name})\n")

            f.write("\n---\n\n")
            f.write("## Transcript\n\n")
        else:
            # Fallback: simple title
            f.write(f"# {title}\n\n")

        # Content - handle both chapter objects and flat strings
        if lines and isinstance(lines[0], dict) and lines[0].get("type") == "chapter":
            # Chapter objects - format with H3 headers
            for chapter in lines:
                f.write(f"### {chapter['title']}\n\n")
                for paragraph in chapter["content"]:
                    f.write(f"{paragraph}\n\n")
        else:
            # Flat strings - existing behavior (timestamp markers or plain paragraphs)
            for line in lines:
                if line.startswith("[") and line.endswith("]"):
                    # Timestamp marker as bold text (not heading)
                    f.write(f"\n**{line}**\n\n")
                else:
                    f.write(f"{line}\n\n")

        # Add channel bio and citations if metadata available
        if metadata:
            write_channel_bio(f, metadata)
            write_citations(f, metadata)


def write_pdf(output_file: Path, lines: List, title: str) -> None:
    """Write PDF output.

    Args:
        lines: List of strings (flat paragraphs) or list of chapter objects
        title: Document title
    """
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)

    # Content
    pdf.set_font("Arial", "", 12)

    if lines and isinstance(lines[0], dict) and lines[0].get("type") == "chapter":
        # Chapter objects - format with section headings
        for chapter in lines:
            # Chapter title as heading
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, chapter["title"], ln=True)
            pdf.ln(5)
            pdf.set_font("Arial", "", 12)

            # Chapter content paragraphs
            for paragraph in chapter["content"]:
                pdf.multi_cell(0, 10, paragraph)
                pdf.ln(2)

            pdf.ln(5)  # Extra space between chapters
    else:
        # Flat strings - existing behavior
        for line in lines:
            if line.startswith("[") and line.endswith("]"):
                # Timestamp marker - bold
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, line, ln=True)
                pdf.set_font("Arial", "", 12)
            else:
                # Regular text
                pdf.multi_cell(0, 10, line)
                pdf.ln(2)

    pdf.output(str(output_file))


def write_channel_bio(f, metadata: dict) -> None:
    """Write channel bio section to markdown file."""
    f.write("\n---\n\n")
    f.write("## About the Channel\n\n")

    channel_name = metadata.get("uploader", metadata.get("channel", "Unknown"))
    f.write(f"**{channel_name}**\n\n")

    # Channel description if available
    channel_desc = metadata.get("channel_description", metadata.get("description", ""))
    if channel_desc:
        # Take first paragraph/500 chars
        desc_short = channel_desc.split("\n\n")[0][:500]
        f.write(f"{desc_short}\n\n")

    # Channel stats
    if metadata.get("channel_follower_count"):
        followers = metadata["channel_follower_count"]
        if followers >= 1000000:
            f.write(f"- **📊 Subscribers:** {followers/1000000:.1f}M\n")
        elif followers >= 1000:
            f.write(f"- **📊 Subscribers:** {followers/1000:.1f}K\n")
        else:
            f.write(f"- **📊 Subscribers:** {followers:,}\n")

    channel_url = metadata.get("channel_url", metadata.get("uploader_url", ""))
    if channel_url:
        f.write(f"- **🔗 Channel:** [{channel_url}]({channel_url})\n")

    f.write("\n")


def generate_citations(metadata: dict) -> dict:
    """Generate all citation formats as a dictionary."""
    import datetime

    title = metadata.get("title", "Unknown")
    creator = metadata.get("uploader", "Unknown")
    url = metadata.get("webpage_url", "")
    video_id = metadata.get("id", "")

    # Parse date
    year, month_name, day = "Unknown", "Unknown", "Unknown"
    if metadata.get("upload_date"):
        date_str = metadata["upload_date"]
        if len(date_str) == 8:
            year = date_str[0:4]
            month = date_str[4:6]
            day = date_str[6:8]
            month_names = [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]
            month_name = month_names[int(month) - 1]

    # Get today's date for access date
    today = datetime.date.today()
    access_date = today.strftime("%Y-%m-%d")

    # Duration string
    duration_str = ""
    if metadata.get("duration"):
        duration = metadata["duration"]
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        duration_str = f", {minutes}:{seconds:02d}"

    citations = {
        "apa": f"{creator}. ({year}, {month_name} {day}). *{title}* [Video]. YouTube. {url}",
        "mla": f'{creator}. "{title}." *YouTube*, {day} {month_name[:3]}. {year}, {url}.',
        "chicago": f'{creator}. "{title}." YouTube video{duration_str}. {month_name} {day}, {year}. {url}.',
        "bibtex": f"@misc{{{video_id},\n  author = {{{{{creator}}}}},\n  title = {{{title}}},\n  year = {{{year}}},\n  month = {{{month_name}}},\n  howpublished = {{\\url{{{url}}}}},\n  note = {{Accessed: {access_date}}}\n}}",
        "plain": f'{creator}. "{title}." YouTube, {month_name} {day}, {year}. Video{duration_str}. {url}. Accessed {access_date}.',
    }

    return citations


def write_citations(f, metadata: dict) -> None:
    """Write citation section with plain text format only (all formats available in JSON)."""
    citations = generate_citations(metadata)

    f.write("---\n\n")
    f.write("## Citation\n\n")
    f.write(f"{citations['plain']}\n\n")


# ============================================================================
# Output Formatter Architecture
# ============================================================================
"""
Multi-format output system for transcript generation.

DESIGN GOALS:
    - Support multiple output formats from the same transcript data
    - Preserve backward compatibility (default: single format)
    - Enable future extensibility without breaking existing code

CURRENT STATE (many==1):
    - Default format: 'sentence-chunked'
    - Single output file generated per transcript
    - Identical behavior to legacy write_json()

FUTURE EXTENSIBILITY:
    - Add new formatters by subclassing OutputFormatter
    - Register formatters in OUTPUT_FORMATTERS dict
    - Support multiple formats via formats parameter
    - Each format generates a separate output file

ADDING NEW FORMATTERS:
    1. Create a new class inheriting from OutputFormatter
    2. Implement format_paragraphs() method
    3. Implement write() method
    4. Register in OUTPUT_FORMATTERS dict

    Example:
        class RawConcatenatedFormatter(OutputFormatter):
            def __init__(self):
                super().__init__('raw-concatenated', 'Raw text without timestamps')

            def format_paragraphs(self, subtitles, timestamp_interval):
                return [' '.join(sub.content for sub in subtitles)]

            def write(self, output_file, subtitles, paragraphs, metadata, timestamp_interval):
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(paragraphs[0])

        OUTPUT_FORMATTERS['raw-concatenated'] = RawConcatenatedFormatter()

OUTPUT FILE NAMING:
    - Single format: transcript-HASH.json (backward compatible)
    - Multiple formats: transcript-HASH-{format-name}.json
"""


class OutputFormatter:
    """Base class for transcript output formatters.

    Formatters control how transcript data is structured and written.
    Each formatter produces a different representation of the same source data.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def format_paragraphs(
        self, subtitles: List, timestamp_interval: Optional[int]
    ) -> List[str]:
        """Format subtitle data into paragraph structure.

        Args:
            subtitles: List of subtitle objects with .start, .end, .content
            timestamp_interval: Interval in seconds for timestamp insertion

        Returns:
            List of formatted paragraph strings
        """
        raise NotImplementedError("Subclasses must implement format_paragraphs()")

    def write(
        self,
        output_file: Path,
        subtitles: List,
        paragraphs: List[str],
        metadata: Optional[dict],
        timestamp_interval: Optional[int],
        structure_source: str = "plain",
    ) -> None:
        """Write formatted output to file.

        Args:
            output_file: Path where output will be written
            subtitles: Raw subtitle data
            paragraphs: Formatted paragraphs from format_paragraphs()
            metadata: Video metadata
            timestamp_interval: Timestamp interval used
            structure_source: Source of structure ("youtube_chapters", "virtual_chapters", "timestamps", "plain")
        """
        raise NotImplementedError("Subclasses must implement write()")


class SentenceChunkedFormatter(OutputFormatter):
    """Sentence-chunked formatter (current default behavior).

    Produces paragraphs by:
    1. Concatenating subtitle text
    2. Splitting on sentence boundaries
    3. Grouping sentences into chunks
    4. Adding timestamps at intervals
    """

    def __init__(self):
        super().__init__(
            name="sentence-chunked",
            description="Sentence-based paragraphs with periodic timestamps",
        )

    def format_paragraphs(
        self, subtitles: List, timestamp_interval: Optional[int]
    ) -> List[str]:
        """Format subtitles into sentence-chunked paragraphs."""
        # Reuse existing extract_with_timestamps logic
        from io import StringIO

        buffer = StringIO()
        for sub in subtitles:
            buffer.write(sub.content)
            buffer.write(" ")

        text = buffer.getvalue()
        return extract_with_timestamps(text, subtitles, timestamp_interval)

    def write(
        self,
        output_file: Path,
        subtitles: List,
        paragraphs: List[str],
        metadata: Optional[dict],
        timestamp_interval: Optional[int],
        structure_source: str = "plain",
    ) -> None:
        """Write sentence-chunked JSON format."""
        import json
        import datetime

        # Convert subtitles to serializable format
        subtitles_data = []
        for sub in subtitles:
            subtitles_data.append(
                {
                    "index": sub.index,
                    "start": sub.start.total_seconds(),
                    "end": sub.end.total_seconds(),
                    "content": sub.content,
                }
            )

        # Generate citations if metadata available
        citations = generate_citations(metadata) if metadata else None

        # Count chapters if using chapter-based structure
        chapter_count = None
        if structure_source in ("youtube_chapters", "virtual_chapters"):
            # paragraphs is a list of chapter objects
            chapter_count = (
                len(paragraphs)
                if isinstance(paragraphs, list)
                and paragraphs
                and isinstance(paragraphs[0], dict)
                else None
            )

        # Build JSON structure
        output_data = {
            "metadata": metadata,
            "citations": citations,
            "subtitles": subtitles_data,
            "extracted_paragraphs": paragraphs,
            "extraction_info": {
                "format": self.name,
                "timestamp_interval": timestamp_interval,
                "structure_source": structure_source,
                "chapter_count": chapter_count,
                "extracted_at": datetime.datetime.now().isoformat(),
                "format_version": "1.0",
            },
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)


# Formatter registry
OUTPUT_FORMATTERS = {
    "sentence-chunked": SentenceChunkedFormatter(),
}


def write_outputs(
    output_file: Path,
    subtitles: List,
    extracted: List[str],
    metadata: Optional[dict],
    timestamp_interval: Optional[int],
    formats: Optional[List[str]] = None,
    structure_source: str = "plain",
) -> None:
    """Write transcript in multiple output formats.

    Args:
        output_file: Base output file path (will be modified per format)
        subtitles: Raw subtitle data
        extracted: Pre-extracted paragraphs (for backward compatibility)
        metadata: Video metadata
        timestamp_interval: Timestamp interval used
        formats: List of format names to output (default: ['sentence-chunked'])
        structure_source: Source of structure ("youtube_chapters", "virtual_chapters", "timestamps", "plain")
    """
    if formats is None:
        formats = ["sentence-chunked"]  # Default: current behavior

    for format_name in formats:
        if format_name not in OUTPUT_FORMATTERS:
            logging.warning(f"Unknown output format '{format_name}', skipping")
            continue

        formatter = OUTPUT_FORMATTERS[format_name]

        # For sentence-chunked, use pre-extracted paragraphs (backward compat)
        # For new formatters, call format_paragraphs()
        if format_name == "sentence-chunked" and extracted:
            paragraphs = extracted
        else:
            paragraphs = formatter.format_paragraphs(subtitles, timestamp_interval)

        # Generate format-specific filename if multiple formats
        if len(formats) > 1:
            stem = output_file.stem
            suffix = output_file.suffix
            format_output = output_file.parent / f"{stem}-{format_name}{suffix}"
        else:
            format_output = output_file

        formatter.write(
            format_output,
            subtitles,
            paragraphs,
            metadata,
            timestamp_interval,
            structure_source,
        )
        logging.info(f"✓ Wrote {format_name} format to {format_output.name}")


def write_json(
    output_file: Path,
    subtitles: List,
    extracted: List[str],
    metadata: Optional[dict],
    timestamp_interval: Optional[int],
) -> None:
    """Write structured JSON output for persistence and re-processing.

    DEPRECATED: Use write_outputs() instead for multi-format support.
    This function is kept for backward compatibility.
    """
    import json
    import datetime

    # Convert subtitles to serializable format
    subtitles_data = []
    for sub in subtitles:
        subtitles_data.append(
            {
                "index": sub.index,
                "start": sub.start.total_seconds(),
                "end": sub.end.total_seconds(),
                "content": sub.content,
            }
        )

    # Generate citations if metadata available
    citations = generate_citations(metadata) if metadata else None

    # Build JSON structure
    output_data = {
        "metadata": metadata,
        "citations": citations,
        "subtitles": subtitles_data,
        "extracted_paragraphs": extracted,
        "extraction_info": {
            "timestamp_interval": timestamp_interval,
            "extracted_at": datetime.datetime.now().isoformat(),
            "format_version": "1.0",
        },
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


def main():
    """Entry point for console script (setuptools/hatchling entry point)."""
    import runpy
    from pathlib import Path

    # Get the path to __main__.py in the same directory as subxx.py
    main_file = Path(__file__).parent / "__main__.py"

    if not main_file.exists():
        raise FileNotFoundError(f"Cannot find __main__.py at {main_file}")

    # Execute __main__.py directly
    runpy.run_path(str(main_file), run_name="__main__")
