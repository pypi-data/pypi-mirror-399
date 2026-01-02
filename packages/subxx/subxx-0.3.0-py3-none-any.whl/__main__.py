"""
__main__.py - CLI and HTTP API entry point for subxx

Provides typer-based CLI commands and optional FastAPI HTTP server.
"""

import sys
from pathlib import Path
from typing import Optional
import typer

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    try:

        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass  # If reconfigure fails, continue with default encoding
from subxx import (
    fetch_subs,
    load_config,
    get_default,
    setup_logging,
    generate_file_hash,
    EXIT_SUCCESS,
    EXIT_USER_CANCELLED,
    EXIT_NO_SUBTITLES,
    EXIT_NETWORK_ERROR,
    EXIT_INVALID_URL,
    EXIT_CONFIG_ERROR,
    EXIT_FILE_ERROR,
)

app = typer.Typer(
    name="subxx",
    help="Subtitle fetching toolkit - Download subtitles from video URLs",
    add_completion=True,
)


@app.command()
def version():
    """Show version information."""
    try:
        import importlib.metadata

        ver = importlib.metadata.version("subxx")
    except importlib.metadata.PackageNotFoundError:
        ver = "0.1.0"

    typer.echo(f"subxx {ver}")
    typer.echo("Subtitle fetching toolkit")
    typer.echo("https://gist.github.com/cprima/subxx")


@app.command()
def list(
    url: str,
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Errors only"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Debug output"),
):
    """List available subtitles for a video without downloading.

    Examples:
      uv run subxx list https://youtu.be/VIDEO_ID
    """
    import yt_dlp

    # Load config for log file
    config = load_config()
    log_file = config.get("logging", {}).get("log_file")

    # Setup logging
    logger = setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    ydl_opts = {
        "skip_download": True,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            typer.echo(f"\n📹 Video: {info.get('title', 'Unknown')}")
            duration = info.get("duration", 0)
            typer.echo(f"🕒 Duration: {duration // 60}:{duration % 60:02d}\n")

            # Manual subtitles
            manual_subs = info.get("subtitles", {})
            if manual_subs:
                typer.echo("✅ Manual subtitles:")
                for lang in sorted(manual_subs.keys()):
                    typer.echo(f"   - {lang}")

            # Auto-generated subtitles
            auto_subs = info.get("automatic_captions", {})
            if auto_subs:
                if manual_subs:
                    typer.echo("")
                typer.echo("🤖 Auto-generated subtitles:")
                for lang in sorted(auto_subs.keys()):
                    typer.echo(f"   - {lang}")

            if not manual_subs and not auto_subs:
                typer.echo("❌ No subtitles available")
                raise typer.Exit(code=EXIT_NO_SUBTITLES)

    except typer.Exit:
        raise  # Re-raise typer.Exit without catching
    except Exception as e:
        logger.error(f"Failed to list subtitles: {e}")
        raise typer.Exit(code=EXIT_NETWORK_ERROR)


@app.command()
def subs(
    url: str,
    langs: Optional[str] = typer.Option(
        None, "--langs", "-l", help="Language codes (en,de,fr or all)"
    ),
    # Format selection (one of these)
    fmt: Optional[str] = typer.Option(
        None, "--fmt", "-f", help="Output format (srt/vtt/txt/md/pdf)"
    ),
    srt: bool = typer.Option(
        False, "--srt", help="Download SRT subtitle file (default)"
    ),
    vtt: bool = typer.Option(False, "--vtt", help="Download VTT subtitle file"),
    txt: bool = typer.Option(False, "--txt", help="Extract to plain text"),
    md: bool = typer.Option(False, "--md", help="Extract to Markdown"),
    pdf: bool = typer.Option(False, "--pdf", help="Extract to PDF"),
    # Other options
    auto: Optional[bool] = typer.Option(
        None, "--auto/--no-auto", help="Include auto-generated subs"
    ),
    output_dir: Optional[str] = typer.Option(
        None, "--output-dir", "-o", help="Output directory"
    ),
    output_folder: Optional[str] = typer.Option(
        None,
        "--output-folder",
        help="Subfolder name for organized output (creates folder with original.srt and transcript.md)",
    ),
    sanitize: Optional[str] = typer.Option(
        None, "--sanitize", help="Filename sanitization (safe/nospaces/slugify)"
    ),
    timestamps: Optional[int] = typer.Option(
        None,
        "--timestamps",
        "-t",
        help="Add timestamp markers every N seconds (for txt/md/pdf)",
    ),
    chapters: bool = typer.Option(
        False,
        "--chapters",
        help="Use chapter markers from metadata (YouTube chapters, for txt/md/pdf)",
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite without prompting"),
    skip_existing: bool = typer.Option(
        False, "--skip-existing", help="Skip existing files"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview without downloading"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Errors only"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Debug output"),
):
    """Fetch subtitles for a video URL.

    Format determines behavior:
      srt/vtt: Download subtitle file
      txt/md/pdf: Download SRT → Extract text → Delete SRT

    Examples:
      Subtitle file:   uv run subxx subs <url>
      Plain text:      uv run subxx subs <url> --txt
      Markdown:        uv run subxx subs <url> --md
      With timestamps: uv run subxx subs <url> --md --timestamps 300
      With chapters:   uv run subxx subs <url> --md --chapters
      PDF:             uv run subxx subs <url> --pdf
    """
    # Load config
    config = load_config()

    # Get log file from config
    log_file = config.get("logging", {}).get("log_file")

    # Determine verbosity level
    if quiet:
        verbosity = "quiet"
    elif verbose:
        verbosity = "verbose"
    else:
        verbosity = "normal"

    # Setup logging with appropriate level
    logger = setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    # Determine format from flags (priority: specific flag > --fmt > config > default)
    if md:
        fmt = "md"
    elif txt:
        fmt = "txt"
    elif pdf:
        fmt = "pdf"
    elif vtt:
        fmt = "vtt"
    elif srt:
        fmt = "srt"
    elif fmt:
        # Use --fmt value
        pass
    else:
        # Use config or default
        fmt = get_default(config, "fmt", "srt")

    # Apply other config defaults
    langs = langs or get_default(config, "langs", "en")
    auto = auto if auto is not None else get_default(config, "auto", True)
    output_dir = output_dir or get_default(config, "output_dir", ".")
    sanitize = sanitize or get_default(config, "sanitize", "safe")

    # Determine if we need extraction
    text_formats = {"txt", "md", "pdf"}
    need_extraction = fmt in text_formats
    download_fmt = (
        "srt" if need_extraction else fmt
    )  # Always download SRT for extraction

    # Handle prompting logic
    prompt_overwrite = not force and not skip_existing

    # Call fetch_subs with verbosity parameter
    exit_code = fetch_subs(
        url=url,
        langs=langs,
        fmt=download_fmt,
        auto=auto,
        output_dir=output_dir,
        prompt_overwrite=prompt_overwrite,
        skip_existing=skip_existing,
        dry_run=dry_run,
        verbosity=verbosity,
        sanitize=sanitize,
    )

    # If download successful and extraction needed, extract text
    if exit_code == EXIT_SUCCESS and need_extraction and not dry_run:
        try:
            # Check if extract dependencies are available
            try:
                import srt  # noqa: F401
                from fpdf import FPDF  # noqa: F401
            except ImportError:
                logger.error("❌ Error: Missing dependencies for text extraction")
                logger.info("💡 Install with: uv sync --extra extract")
                raise typer.Exit(code=EXIT_CONFIG_ERROR)

            # Import extract function
            from subxx import extract_text
            import yt_dlp

            # Extract video ID from URL to generate hash for filenames
            video_id = None
            file_hash = None
            try:
                with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_id = info.get("id")
                    if video_id:
                        file_hash = generate_file_hash(video_id)
                        logger.debug(
                            f"Generated file hash: {file_hash} from video ID: {video_id}"
                        )
            except Exception as e:
                logger.warning(f"Could not extract video ID for hash generation: {e}")
                # Continue without hash

            # Find downloaded subtitle files for this video
            output_path_obj = Path(output_dir).expanduser()
            # Get all subtitle files (SRT, since we always download SRT for extraction)
            # sorted by modification time (most recent first)
            all_subtitle_files = sorted(
                output_path_obj.glob(
                    f"*.{download_fmt}"
                ),  # Use download_fmt (srt), not final fmt (md/txt/pdf)
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            # Take only the most recent file(s) - assume they're from this download
            subtitle_files = all_subtitle_files[:1] if all_subtitle_files else []
            logger.debug(f"Found {len(subtitle_files)} recent subtitle file(s)")

            if not subtitle_files:
                logger.error("No subtitle files found to extract")
                raise typer.Exit(code=EXIT_FILE_ERROR)

            # Extract text from each subtitle file
            extract_failed = []
            for subtitle_file in subtitle_files:
                logger.info(f"📄 Extracting text from: {subtitle_file.name}")

                # Handle output_folder if specified
                if output_folder:
                    # Create organized folder structure
                    folder_path = output_path_obj / output_folder
                    folder_path.mkdir(parents=True, exist_ok=True)

                    # Generate filenames with hash suffix if available
                    if file_hash:
                        original_name = f"original-{file_hash}.{download_fmt}"
                        transcript_name = f"transcript-{file_hash}.{fmt}"
                    else:
                        original_name = f"original.{download_fmt}"
                        transcript_name = f"transcript.{fmt}"

                    # Move SRT to folder as original-{hash}.srt
                    original_srt = folder_path / original_name
                    import shutil

                    shutil.move(str(subtitle_file), str(original_srt))
                    logger.debug(f"Moved {subtitle_file.name} to {original_srt}")

                    # Set output file as transcript-{hash}.{fmt}
                    output_file = str(folder_path / transcript_name)
                    # Update subtitle_file to new location
                    subtitle_file = original_srt
                else:
                    output_file = None  # Auto-generate

                extract_exit = extract_text(
                    subtitle_file=str(subtitle_file),
                    output_format=fmt,  # Use the final format (txt/md/pdf)
                    timestamp_interval=timestamps,
                    output_file=output_file,
                    force=force,
                    use_chapters=chapters,
                )

                if extract_exit != EXIT_SUCCESS:
                    extract_failed.append(subtitle_file)
                else:
                    # Only delete SRT file if NOT using output_folder (keep original for re-processing)
                    if not output_folder:
                        subtitle_file.unlink()
                        logger.debug(
                            f"Deleted intermediate SRT file: {subtitle_file.name}"
                        )

            if extract_failed:
                logger.error(f"Failed to extract {len(extract_failed)} file(s)")
                raise typer.Exit(code=EXIT_FILE_ERROR)
        except typer.Exit:
            raise  # Re-raise typer.Exit
        except Exception as e:
            import traceback

            logger.error(f"❌ Extraction failed: {e}")
            logger.debug(f"Traceback: {traceback.format_exc()}")
            raise typer.Exit(code=EXIT_FILE_ERROR)

    raise typer.Exit(code=exit_code)


@app.command()
def batch(
    urls_file: str,
    langs: str = typer.Option("en", "--langs", "-l", help="Language codes"),
    fmt: str = typer.Option("srt", "--fmt", "-f", help="Output format"),
    auto: bool = typer.Option(True, "--auto/--no-auto", help="Include auto-generated"),
    output_dir: str = typer.Option(".", "--output-dir", "-o", help="Output directory"),
    sanitize: str = typer.Option(
        "safe", "--sanitize", help="Filename sanitization (safe/nospaces/slugify)"
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Errors only"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Debug output"),
):
    """Download subtitles for multiple URLs from a file.

    URL file format (yt-dlp standard):
      One URL per line
      Lines starting with # are comments
      Empty lines are ignored

    Example:
      uv run subxx batch urls.txt --langs en,de
    """
    # Load config
    config = load_config()
    log_file = config.get("logging", {}).get("log_file")

    # Determine verbosity level
    if quiet:
        verbosity = "quiet"
    elif verbose:
        verbosity = "verbose"
    else:
        verbosity = "normal"

    # Setup logging
    logger = setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    # Read URLs from file (yt-dlp format)
    urls_path = Path(urls_file).expanduser()
    if not urls_path.exists():
        logger.error(f"File not found: {urls_file}")
        raise typer.Exit(code=EXIT_FILE_ERROR)

    urls = []
    with open(urls_path) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines (yt-dlp standard)
            if line and not line.startswith("#"):
                urls.append(line)

    if not urls:
        logger.error("No URLs found in file")
        raise typer.Exit(code=EXIT_INVALID_URL)

    logger.info(f"Processing {len(urls)} URLs from {urls_file}")

    # Process each URL
    failed = []
    for i, url in enumerate(urls, 1):
        logger.info(f"[{i}/{len(urls)}] {url}")

        exit_code = fetch_subs(
            url=url,
            langs=langs,
            fmt=fmt,
            auto=auto,
            output_dir=output_dir,
            prompt_overwrite=False,  # No prompts in batch mode
            skip_existing=True,  # Skip existing by default
            verbosity=verbosity,
            sanitize=sanitize,
        )

        if exit_code != 0:
            failed.append(url)

    # Summary
    if failed:
        logger.error(f"❌ Failed to download {len(failed)}/{len(urls)} URLs")
        for url in failed:
            logger.error(f"  - {url}")
        raise typer.Exit(code=EXIT_NETWORK_ERROR)
    else:
        logger.info(f"✅ Successfully downloaded {len(urls)} subtitle sets")
        raise typer.Exit(code=EXIT_SUCCESS)


@app.command()
def extract(
    subtitle_file: str = typer.Argument(..., help="Subtitle file (.srt or .vtt)"),
    output_format: str = typer.Option(
        "txt", "--format", "-f", help="Output format (txt, md, pdf)"
    ),
    timestamp_interval: Optional[int] = typer.Option(
        None,
        "--timestamps",
        "-t",
        help="Add timestamp every N seconds (e.g., 300 for 5min)",
    ),
    chapters: bool = typer.Option(
        False, "--chapters", help="Use chapter markers from metadata (YouTube chapters)"
    ),
    auto_structure: bool = typer.Option(
        False,
        "--auto-structure",
        help="Auto-detect best structure (YouTube chapters → virtual chapters → plain)",
    ),
    fallback_timestamps: Optional[int] = typer.Option(
        None,
        "--fallback-timestamps",
        help="Fallback to virtual chapters with this interval if YouTube chapters unavailable/insufficient",
    ),
    min_chapters: Optional[int] = typer.Option(
        None,
        "--min-chapters",
        help="Minimum required YouTube chapters (triggers fallback if fewer)",
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite existing output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Extract text from subtitle files.

    Removes timestamps and formatting to create readable text documents.

    Examples:
      Basic:                uv run subxx extract video.srt
      Markdown:             uv run subxx extract video.srt -f md
      Auto-structure:       uv run subxx extract video.srt --auto-structure -f md
      With timestamps:      uv run subxx extract video.srt -t 300
      With chapters:        uv run subxx extract video.srt --chapters -f md
      With fallback:        uv run subxx extract video.srt --chapters --fallback-timestamps 300 -f md
      Minimum chapters:     uv run subxx extract video.srt --chapters --min-chapters 5 --fallback-timestamps 300 -f md
      PDF output:           uv run subxx extract video.srt -f pdf
    """

    # Check if extract dependencies are installed
    try:
        import srt  # noqa: F401
        from fpdf import FPDF  # noqa: F401
    except ImportError:
        typer.echo("❌ Error: Missing dependencies for text extraction")
        typer.echo("Install with: uv sync --extra extract")
        typer.echo("Or run with: uv run --extra extract subxx extract <file>")
        raise typer.Exit(code=EXIT_CONFIG_ERROR)

    # Load config
    config = load_config()
    log_file = config.get("logging", {}).get("log_file")

    # Setup logging
    logger = setup_logging(verbose=verbose, quiet=quiet, log_file=log_file)

    # Apply auto-structure defaults
    if auto_structure:
        chapters = True
        if fallback_timestamps is None:
            fallback_timestamps = 300  # Default: 5-minute virtual chapters
        logger.info(
            "Auto-structure mode: will try YouTube chapters → virtual chapters (5min) → plain"
        )

    # Import and call extract function
    from subxx import extract_text

    exit_code = extract_text(
        subtitle_file=subtitle_file,
        output_format=output_format,
        timestamp_interval=timestamp_interval,
        output_file=output_file,
        force=force,
        use_chapters=chapters,
        fallback_timestamps=fallback_timestamps,
        min_chapters=min_chapters,
    )

    raise typer.Exit(code=exit_code)


@app.command()
def serve(
    host: str = typer.Option(
        "127.0.0.1", "--host", help="Bind address (ALWAYS use 127.0.0.1)"
    ),
    port: int = typer.Option(8000, "--port", help="Port to listen on"),
):
    """Start HTTP API server (requires fastapi, uvicorn).

    ⚠️  WARNING: API has NO authentication. ONLY run on localhost!

    Example:
      uv run --extra api subxx serve --host 127.0.0.1 --port 8000
    """
    try:
        import uvicorn
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import PlainTextResponse
        from pydantic import BaseModel
        import anyio
        import tempfile
        from pathlib import Path
    except ImportError:
        typer.echo("❌ Error: API dependencies not installed")
        typer.echo("Install with: uv sync --extra api")
        typer.echo("Or run with: uv run --extra api subxx serve")
        raise typer.Exit(code=EXIT_CONFIG_ERROR)

    # Security check
    if host != "127.0.0.1" and host != "localhost":
        typer.echo(f"⚠️  WARNING: Binding to {host} exposes API to network!")
        typer.echo("The API has NO authentication and should ONLY run on localhost.")
        if not typer.confirm("Continue anyway?", default=False):
            raise typer.Exit(code=EXIT_USER_CANCELLED)

    class SubsRequest(BaseModel):
        url: str
        langs: str = "en"
        fmt: str = "srt"
        auto: bool = True
        sanitize: str = "safe"

    api = FastAPI(
        title="subxx API", description="Subtitle fetching HTTP API", version="0.1.0"
    )

    @api.post("/subs", response_class=PlainTextResponse)
    async def fetch_subs_endpoint(req: SubsRequest):
        """Fetch subtitles and return content directly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Download to temp directory
            exit_code = await anyio.to_thread.run_sync(
                fetch_subs,
                url=req.url,
                langs=req.langs,
                fmt=req.fmt,
                auto=req.auto,
                output_dir=tmpdir,
                out_template="%(title)s.%(id)s.%(lang)s.%(ext)s",
                prompt_overwrite=False,
                skip_existing=False,
                dry_run=False,
                verbosity="quiet",
                sanitize=req.sanitize,
            )

            if exit_code != 0:
                raise HTTPException(status_code=500, detail="Subtitle fetch failed")

            # Find downloaded file(s) and return content
            subtitle_files = list(Path(tmpdir).glob(f"*.{req.fmt}"))
            if not subtitle_files:
                raise HTTPException(status_code=404, detail="No subtitles found")

            # Return first subtitle
            return subtitle_files[0].read_text(encoding="utf-8")

    @api.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "ok", "service": "subxx"}

    typer.echo(f"🚀 Starting subxx API server on http://{host}:{port}")
    typer.echo(f"📖 API docs: http://{host}:{port}/docs")
    typer.echo("⚠️  Security: NO authentication - localhost only!")
    typer.echo("")

    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    app()
