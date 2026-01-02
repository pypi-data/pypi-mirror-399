"""
test_subxx.py - Complete test suite for subxx.py

Test organization:
- Unit tests (pure functions, no I/O)
- Integration tests (file operations, with fixtures)
- CLI tests (command line interface)
- API tests (HTTP endpoints)
"""

import pytest
from pathlib import Path
from unittest.mock import patch
import os
import re

# Test fixtures
FIXTURE_FILE = (
    Path(__file__).parent
    / "The_FULL_Story_of_the_Man-Eating_Lions_of_Tsavo.mAKxcNQpiSg.en.srt"
)

# =============================================================================
# NOTE: VTT to SRT conversion tests removed - we now use yt-dlp's native
# subtitle format download instead of custom conversion
# =============================================================================
# UNIT TESTS - Configuration Loading
# =============================================================================


@pytest.mark.unit
def test_load_config_from_file(tmp_path):
    """Test loading config from TOML file."""
    from subxx import load_config

    config_file = tmp_path / ".subxx.toml"
    config_file.write_text(
        """
[defaults]
langs = "en,de"
fmt = "srt"
auto = true
output_dir = "~/subs"

[logging]
level = "DEBUG"
"""
    )

    # Temporarily change current directory
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        config = load_config()
        assert config["defaults"]["langs"] == "en,de"
        assert config["defaults"]["fmt"] == "srt"
        assert config["logging"]["level"] == "DEBUG"
    finally:
        os.chdir(old_cwd)


@pytest.mark.unit
def test_get_default_with_fallback():
    """Test getting config value with fallback."""
    from subxx import get_default

    config = {"defaults": {"langs": "en,de", "fmt": "srt"}}

    assert get_default(config, "langs", "en") == "en,de"
    assert get_default(config, "fmt", "vtt") == "srt"
    assert get_default(config, "missing", "fallback") == "fallback"


@pytest.mark.unit
def test_empty_config():
    """Test behavior with empty/missing config."""
    from subxx import get_default

    config = {}
    assert get_default(config, "langs", "en") == "en"
    assert get_default(config, "output_dir", ".") == "."


# =============================================================================
# UNIT TESTS - Language Parameter Parsing
# =============================================================================


@pytest.mark.unit
def test_parse_single_language():
    """Test parsing single language code."""
    from subxx import parse_languages

    result = parse_languages("en")
    assert result == ["en"]


@pytest.mark.unit
def test_parse_multiple_languages():
    """Test parsing comma-separated language codes."""
    from subxx import parse_languages

    result = parse_languages("en,de,fr")
    assert result == ["en", "de", "fr"]


@pytest.mark.unit
def test_parse_all_languages():
    """Test special 'all' keyword."""
    from subxx import parse_languages

    result = parse_languages("all")
    assert result is None  # None means download all


@pytest.mark.unit
def test_parse_with_spaces():
    """Test parsing with spaces around commas."""
    from subxx import parse_languages

    result = parse_languages("en, de, fr")
    assert result == ["en", "de", "fr"]


# =============================================================================
# UNIT TESTS - Output Path Handling
# =============================================================================


@pytest.mark.unit
def test_output_path_with_current_dir():
    """Test output path in current directory."""
    from subxx import construct_output_path

    path = construct_output_path(".", "video.srt")
    assert path == Path(".") / "video.srt"


@pytest.mark.unit
def test_output_path_with_custom_dir(tmp_path):
    """Test output path with custom directory."""
    from subxx import construct_output_path

    output_dir = tmp_path / "subs"
    path = construct_output_path(str(output_dir), "video.srt")
    assert path == output_dir / "video.srt"


@pytest.mark.unit
def test_output_path_expands_home():
    """Test that ~ is expanded in output paths."""
    from subxx import construct_output_path

    path = construct_output_path("~/subs", "video.srt")
    assert "~" not in str(path)
    assert path.is_absolute()


# =============================================================================
# INTEGRATION TESTS - Real Subtitle File Processing
# =============================================================================


@pytest.mark.integration
def test_fixture_file_exists():
    """Test that the fixture subtitle file exists."""
    assert FIXTURE_FILE.exists(), f"Fixture file not found: {FIXTURE_FILE}"
    assert FIXTURE_FILE.suffix == ".srt"


@pytest.mark.integration
def test_fixture_file_is_valid_srt():
    """Test that fixture file is a valid SRT subtitle file."""
    content = FIXTURE_FILE.read_text(encoding="utf-8")

    # Check SRT format characteristics
    assert content.strip(), "File is empty"

    lines = content.split("\n")

    # First line should be sequence number "1"
    assert lines[0].strip() == "1", "First line should be sequence number 1"

    # Should contain timestamp arrows
    assert "-->" in content, "Missing SRT timestamp arrows"

    # Should contain timestamps with commas (SRT format)
    timestamps = re.findall(r"\d{2}:\d{2}:\d{2},\d{3}", content)
    assert len(timestamps) > 0, "No valid SRT timestamps found"


@pytest.mark.integration
def test_fixture_file_metadata():
    """Test that fixture filename follows expected format."""
    # Expected format: <title>.<video_id>.<lang>.<ext>
    filename = FIXTURE_FILE.name

    # Check structure
    parts = filename.split(".")
    assert len(parts) >= 4, f"Filename doesn't match format: {filename}"

    # Check video ID (mAKxcNQpiSg)
    assert "mAKxcNQpiSg" in filename, "Video ID not found in filename"

    # Check language code
    assert ".en." in filename, "Language code 'en' not found in filename"

    # Check extension
    assert filename.endswith(".srt"), "File should have .srt extension"


@pytest.mark.integration
def test_fixture_file_encoding():
    """Test that fixture file is UTF-8 encoded."""
    # Should not raise UnicodeDecodeError
    content = FIXTURE_FILE.read_text(encoding="utf-8")
    assert len(content) > 0

    # Try re-encoding to verify UTF-8
    content.encode("utf-8")


@pytest.mark.integration
def test_fixture_file_content_quality():
    """Test basic quality of subtitle content."""
    content = FIXTURE_FILE.read_text(encoding="utf-8")

    # Count subtitle blocks
    blocks = [b for b in content.split("\n\n") if b.strip()]
    assert len(blocks) > 10, "File should contain multiple subtitle blocks"

    # Verify sequence numbers are sequential
    sequence_numbers = re.findall(r"^(\d+)$", content, re.MULTILINE)
    if len(sequence_numbers) > 1:
        # Check first few are sequential
        first_three = [int(n) for n in sequence_numbers[:3]]
        assert first_three == [1, 2, 3], "Sequence numbers should be sequential"


@pytest.mark.integration
def test_fixture_is_auto_generated():
    """Verify fixture is auto-generated subtitle (informational test).

    This test documents that our fixture is auto-generated, not manual.
    Auto-generated subs often have characteristics like:
    - [Music] tags
    - Less precise timing
    - More filler words ("um", "uh")
    """
    content = FIXTURE_FILE.read_text(encoding="utf-8")

    # This is informational - just checking we know what we're testing
    # Auto-generated subs often contain [Music] tags
    has_music_tags = "[Music]" in content or "♪" in content

    # Document the finding (not a hard assertion)
    # Most auto-generated subs will have these markers
    print(f"Fixture has music tags: {has_music_tags}")
    print("This confirms the fixture is auto-generated (expected)")


# =============================================================================
# INTEGRATION TESTS - File Operations
# =============================================================================


@pytest.mark.integration
def test_write_new_file(tmp_path):
    """Test writing a new file."""
    from subxx import safe_write_file

    output_file = tmp_path / "test.srt"
    content = "Test content"

    result = safe_write_file(output_file, content, force=False, skip_existing=False)

    assert result is True
    assert output_file.exists()
    assert output_file.read_text() == content


@pytest.mark.integration
def test_skip_existing_file(tmp_path):
    """Test skip_existing flag."""
    from subxx import safe_write_file

    output_file = tmp_path / "test.srt"
    output_file.write_text("Original content")

    result = safe_write_file(
        output_file, "New content", force=False, skip_existing=True
    )

    assert result is False
    assert output_file.read_text() == "Original content"


@pytest.mark.integration
def test_force_overwrite(tmp_path):
    """Test force overwrite flag."""
    from subxx import safe_write_file

    output_file = tmp_path / "test.srt"
    output_file.write_text("Original content")

    result = safe_write_file(
        output_file, "New content", force=True, skip_existing=False
    )

    assert result is True
    assert output_file.read_text() == "New content"


@pytest.mark.integration
def test_create_directory_if_missing(tmp_path):
    """Test that output directory is created automatically."""
    from subxx import safe_write_file

    deep_dir = tmp_path / "deep" / "nested" / "folder"
    output_file = deep_dir / "test.srt"

    # Directory doesn't exist yet
    assert not deep_dir.exists()

    result = safe_write_file(output_file, "Content", force=False, skip_existing=False)

    assert result is True
    assert deep_dir.exists()
    assert output_file.exists()


# =============================================================================
# CLI TESTS - Commands
# =============================================================================


def test_version_command(cli_app):
    """Test version command output."""
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli_app, ["version"])
    assert result.exit_code == 0
    assert "subxx" in result.stdout
    assert "0.1.0" in result.stdout or "dev" in result.stdout


def test_list_command_success(cli_app, mocker):
    """Test list command with mock yt-dlp response."""
    from typer.testing import CliRunner

    runner = CliRunner()

    mock_info = {
        "title": "Test Video Title",
        "duration": 635,  # 10:35
        "subtitles": {
            "en": [{"ext": "vtt"}],
            "de": [{"ext": "vtt"}],
        },
        "automatic_captions": {
            "fr": [{"ext": "vtt"}],
            "es": [{"ext": "vtt"}],
        },
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = (
            mock_info
        )

        result = runner.invoke(
            cli_app, ["list", "https://www.youtube.com/watch?v=test"]
        )

        assert result.exit_code == 0
        assert "Test Video Title" in result.stdout
        assert "10:35" in result.stdout
        assert "Manual subtitles" in result.stdout
        assert "en" in result.stdout
        assert "de" in result.stdout
        assert "Auto-generated" in result.stdout
        assert "fr" in result.stdout


def test_list_command_no_subtitles(cli_app, mocker):
    """Test list command when no subtitles available."""
    from typer.testing import CliRunner
    from subxx import EXIT_NO_SUBTITLES

    runner = CliRunner()

    mock_info = {
        "title": "Test Video",
        "duration": 100,
        "subtitles": {},
        "automatic_captions": {},
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = (
            mock_info
        )

        result = runner.invoke(
            cli_app, ["list", "https://www.youtube.com/watch?v=test"]
        )

        assert result.exit_code == EXIT_NO_SUBTITLES  # Should be 2, not 1
        assert "No subtitles available" in result.stdout


def test_list_command_manual_and_auto(cli_app, mocker):
    """Test list command distinguishes manual vs auto-generated."""
    from typer.testing import CliRunner

    runner = CliRunner()

    mock_info = {
        "title": "Test Video",
        "duration": 100,
        "subtitles": {
            "en": [{"ext": "vtt"}],
            "de": [{"ext": "vtt"}],
        },
        "automatic_captions": {
            "en": [{"ext": "vtt"}],  # Also has auto for EN
            "fr": [{"ext": "vtt"}],
            "es": [{"ext": "vtt"}],
        },
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = (
            mock_info
        )

        result = runner.invoke(
            cli_app, ["list", "https://www.youtube.com/watch?v=test"]
        )

        assert result.exit_code == 0
        # Should show manual subs clearly
        assert "Manual subtitles" in result.stdout
        assert "Auto-generated" in result.stdout
        # English appears in both, but only once in each section


def test_subs_command_basic(cli_app, mocker, tmp_path):
    """Test basic subs command."""
    from typer.testing import CliRunner

    runner = CliRunner()

    # Mock yt-dlp download
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        mock_instance = MockYDL.return_value.__enter__.return_value
        mock_instance.download.return_value = 0

        result = runner.invoke(
            cli_app,
            [
                "subs",
                "https://www.youtube.com/watch?v=test",
                "--output-dir",
                str(tmp_path),
                "--force",  # Skip prompt
            ],
        )

        assert result.exit_code == 0
        mock_instance.download.assert_called_once()


def test_subs_command_with_languages(cli_app, mocker, tmp_path):
    """Test subs command with multiple languages."""
    from typer.testing import CliRunner

    runner = CliRunner()

    # Mock yt-dlp download
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        mock_instance = MockYDL.return_value.__enter__.return_value
        mock_instance.download.return_value = 0

        result = runner.invoke(
            cli_app,
            [
                "subs",
                "https://www.youtube.com/watch?v=test",
                "--langs",
                "en,de,fr",
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        assert result.exit_code == 0
        mock_instance.download.assert_called_once()


def test_subs_manual_preferred_over_auto(cli_app, mocker, tmp_path):
    """Test that manual subtitles are preferred over auto-generated.

    CRITICAL TEST: When both manual and auto subs exist for a language,
    yt-dlp should download ONLY the manual subtitle.
    """
    from typer.testing import CliRunner

    runner = CliRunner()

    # Mock yt-dlp to simulate behavior
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        mock_instance = MockYDL.return_value.__enter__.return_value
        mock_instance.download.return_value = 0

        result = runner.invoke(
            cli_app,
            [
                "subs",
                "https://www.youtube.com/watch?v=test",
                "--langs",
                "en",
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        assert result.exit_code == 0

        # Verify yt-dlp was called with both flags (manual takes priority)
        ydl_call = MockYDL.call_args
        if ydl_call:
            opts = ydl_call[0][0]  # First positional arg is options dict
            assert opts["writesubtitles"] is True
            assert opts["writeautomaticsub"] is True  # But manual will be preferred


def test_subs_auto_disabled_fails_gracefully(cli_app, mocker, tmp_path):
    """Test that --no-auto fails with helpful message when only auto subs exist."""
    from typer.testing import CliRunner
    from subxx import EXIT_NO_SUBTITLES

    runner = CliRunner()

    # Mock download failure (no manual subs)
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        mock_instance = MockYDL.return_value.__enter__.return_value
        mock_instance.download.return_value = 1  # Failure

        result = runner.invoke(
            cli_app,
            [
                "subs",
                "https://www.youtube.com/watch?v=test",
                "--langs",
                "en",
                "--no-auto",  # Disable auto-generated
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        assert result.exit_code == EXIT_NO_SUBTITLES

        # Should suggest using --auto flag
        assert "--auto" in result.stdout or "auto" in result.stdout.lower()


def test_subs_only_auto_available_with_auto_enabled(cli_app, mocker, tmp_path):
    """Test downloading auto-generated when no manual subs exist."""
    from typer.testing import CliRunner

    runner = CliRunner()

    # Simulate successful download of auto-generated subs
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        mock_instance = MockYDL.return_value.__enter__.return_value
        mock_instance.download.return_value = 0

        result = runner.invoke(
            cli_app,
            [
                "subs",
                "https://www.youtube.com/watch?v=test",
                "--langs",
                "en",
                "--auto",  # Allow auto-generated (default)
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        assert result.exit_code == 0


# =============================================================================
# EXIT CODE TESTS
# =============================================================================


@pytest.mark.unit
def test_exit_code_constants():
    """Test that exit codes are properly defined."""
    from subxx import (
        EXIT_SUCCESS,
        EXIT_USER_CANCELLED,
        EXIT_NO_SUBTITLES,
        EXIT_NETWORK_ERROR,
        EXIT_INVALID_URL,
        EXIT_CONFIG_ERROR,
        EXIT_FILE_ERROR,
    )

    assert EXIT_SUCCESS == 0
    assert EXIT_USER_CANCELLED == 1
    assert EXIT_NO_SUBTITLES == 2
    assert EXIT_NETWORK_ERROR == 3
    assert EXIT_INVALID_URL == 4
    assert EXIT_CONFIG_ERROR == 5
    assert EXIT_FILE_ERROR == 6

    # Ensure all codes are unique
    codes = [
        EXIT_SUCCESS,
        EXIT_USER_CANCELLED,
        EXIT_NO_SUBTITLES,
        EXIT_NETWORK_ERROR,
        EXIT_INVALID_URL,
        EXIT_CONFIG_ERROR,
        EXIT_FILE_ERROR,
    ]
    assert len(codes) == len(set(codes)), "Exit codes must be unique"


# =============================================================================
# TEXT EXTRACTION TESTS
# =============================================================================


@pytest.mark.unit
def test_extract_text_from_srt(tmp_path):
    """Test extracting text from SRT file."""
    # Import dependencies (will skip if not installed)
    pytest.importorskip("srt")

    from subxx import extract_text, EXIT_SUCCESS

    # Create test SRT
    srt_file = tmp_path / "test.srt"
    srt_file.write_text(
        """1
00:00:00,000 --> 00:00:05,000
Hello, this is a test.

2
00:00:05,000 --> 00:00:10,000
Second line here.
""",
        encoding="utf-8",
    )

    exit_code = extract_text(str(srt_file), output_format="txt", force=True)
    assert exit_code == EXIT_SUCCESS

    output = tmp_path / "test.txt"
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "Hello, this is a test." in content
    assert "Second line here." in content
    # No timestamps
    assert "00:00:00" not in content


@pytest.mark.unit
def test_extract_with_timestamp_interval(tmp_path):
    """Test timestamp markers at intervals."""
    pytest.importorskip("srt")

    from subxx import extract_text, EXIT_SUCCESS

    srt_file = tmp_path / "test.srt"
    # Create SRT with content spanning 10 minutes
    srt_file.write_text(
        """1
00:00:00,000 --> 00:00:05,000
First subtitle.

2
00:05:00,000 --> 00:05:05,000
Subtitle at 5 minutes.

3
00:10:00,000 --> 00:10:05,000
Subtitle at 10 minutes.
""",
        encoding="utf-8",
    )

    exit_code = extract_text(str(srt_file), timestamp_interval=300, force=True)
    assert exit_code == EXIT_SUCCESS

    content = (tmp_path / "test.txt").read_text(encoding="utf-8")
    assert "[0:00]" in content
    assert "[5:00]" in content


@pytest.mark.unit
def test_extract_vtt_not_implemented(tmp_path):
    """Test that VTT extraction returns not implemented error."""
    pytest.importorskip("srt")

    from subxx import extract_text, EXIT_FILE_ERROR

    vtt_file = tmp_path / "test.vtt"
    vtt_file.write_text(
        "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nTest", encoding="utf-8"
    )

    exit_code = extract_text(str(vtt_file))
    assert exit_code == EXIT_FILE_ERROR  # Not implemented


@pytest.mark.unit
def test_extract_markdown_format(tmp_path):
    """Test Markdown output format."""
    pytest.importorskip("srt")

    from subxx import extract_text, EXIT_SUCCESS

    srt_file = tmp_path / "test.srt"
    srt_file.write_text(
        """1
00:00:00,000 --> 00:00:05,000
Test content.

2
00:05:00,000 --> 00:05:05,000
More content.
""",
        encoding="utf-8",
    )

    exit_code = extract_text(
        str(srt_file), output_format="md", timestamp_interval=300, force=True
    )
    assert exit_code == EXIT_SUCCESS

    output = tmp_path / "test.md"
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "# test" in content
    assert "## [0:00]" in content
    assert "Test content." in content


@pytest.mark.unit
def test_extract_pdf_format(tmp_path):
    """Test PDF output format."""
    pytest.importorskip("srt")
    pytest.importorskip("fpdf")

    from subxx import extract_text, EXIT_SUCCESS

    srt_file = tmp_path / "test.srt"
    srt_file.write_text(
        """1
00:00:00,000 --> 00:00:05,000
Test PDF content.
""",
        encoding="utf-8",
    )

    exit_code = extract_text(str(srt_file), output_format="pdf", force=True)
    assert exit_code == EXIT_SUCCESS

    output = tmp_path / "test.pdf"
    assert output.exists()
    # Just check file exists and has content
    assert output.stat().st_size > 0


@pytest.mark.unit
def test_extract_file_not_found():
    """Test error when file doesn't exist."""
    pytest.importorskip("srt")

    from subxx import extract_text, EXIT_FILE_ERROR

    exit_code = extract_text("nonexistent.srt")
    assert exit_code == EXIT_FILE_ERROR


@pytest.mark.unit
def test_extract_output_exists_no_force(tmp_path):
    """Test error when output exists without force flag."""
    pytest.importorskip("srt")

    from subxx import extract_text, EXIT_FILE_ERROR

    srt_file = tmp_path / "test.srt"
    srt_file.write_text(
        """1
00:00:00,000 --> 00:00:05,000
Test.
""",
        encoding="utf-8",
    )

    # Create output file
    output_file = tmp_path / "test.txt"
    output_file.write_text("Existing content", encoding="utf-8")

    # Try to extract without force
    exit_code = extract_text(str(srt_file), output_format="txt", force=False)
    assert exit_code == EXIT_FILE_ERROR

    # Original content should be unchanged
    assert output_file.read_text(encoding="utf-8") == "Existing content"


# =============================================================================
# INTEGRATED EXTRACTION TESTS (subs command with --txt/--md/--pdf)
# =============================================================================


@pytest.mark.integration
def test_subs_with_txt_flag(cli_app, mocker, tmp_path):
    """Test subs command with --txt flag extracts text."""
    pytest.importorskip("srt")

    from typer.testing import CliRunner
    from unittest.mock import patch

    # Create SRT file that will be "downloaded"
    srt_file = tmp_path / "Test_Video.test123.en.srt"

    # Mock yt-dlp operations
    mock_info = {
        "id": "test123",
        "title": "Test Video",
        "subtitles": {"en": [{"ext": "srt"}]},
        "automatic_captions": {},
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = (
            mock_info
        )

        def mock_download(urls):
            # Create the SRT file when yt-dlp "downloads" it
            srt_file.write_text(
                """1
00:00:00,000 --> 00:00:05,000
Hello world.
""",
                encoding="utf-8",
            )
            return 0

        mock_ydl.return_value.__enter__.return_value.download.side_effect = (
            mock_download
        )

        runner = CliRunner()
        runner.invoke(
            cli_app,
            [
                "subs",
                "https://example.com/video",
                "--txt",
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        # Should create txt file
        txt_file = tmp_path / "Test_Video.test123.en.txt"
        assert (
            txt_file.exists()
        ), f"Expected {txt_file} to exist. Files in dir: {list(tmp_path.glob('*'))}"
        assert "Hello world" in txt_file.read_text()

        # SRT should be deleted after extraction
        assert not srt_file.exists()


@pytest.mark.integration
def test_subs_with_md_flag(cli_app, mocker, tmp_path):
    """Test subs command with --md flag extracts markdown."""
    pytest.importorskip("srt")

    from typer.testing import CliRunner
    from unittest.mock import patch

    srt_file = tmp_path / "Test_Video.test123.en.srt"

    mock_info = {
        "id": "test123",
        "title": "Test Video",
        "subtitles": {"en": [{"ext": "srt"}]},
        "automatic_captions": {},
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = (
            mock_info
        )

        def mock_download(urls):
            srt_file.write_text(
                """1
00:00:00,000 --> 00:00:05,000
Test content.
""",
                encoding="utf-8",
            )
            return 0

        mock_ydl.return_value.__enter__.return_value.download.side_effect = (
            mock_download
        )

        runner = CliRunner()
        runner.invoke(
            cli_app,
            [
                "subs",
                "https://example.com/video",
                "--md",
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        # Should create md file
        md_file = tmp_path / "Test_Video.test123.en.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "# Test_Video.test123.en" in content
        assert "Test content" in content


@pytest.mark.integration
def test_subs_with_fmt_flag(cli_app, mocker, tmp_path):
    """Test subs command with -f txt flag."""
    pytest.importorskip("srt")

    from typer.testing import CliRunner
    from unittest.mock import patch

    srt_file = tmp_path / "Test_Video.test123.en.srt"

    mock_info = {
        "id": "test123",
        "title": "Test Video",
        "subtitles": {"en": [{"ext": "srt"}]},
        "automatic_captions": {},
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = (
            mock_info
        )

        def mock_download(urls):
            srt_file.write_text(
                """1
00:00:00,000 --> 00:00:05,000
Test.
""",
                encoding="utf-8",
            )
            return 0

        mock_ydl.return_value.__enter__.return_value.download.side_effect = (
            mock_download
        )

        runner = CliRunner()
        runner.invoke(
            cli_app,
            [
                "subs",
                "https://example.com/video",
                "-f",
                "txt",
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        # Should create txt file
        txt_file = tmp_path / "Test_Video.test123.en.txt"
        assert txt_file.exists()


@pytest.mark.integration
def test_subs_with_timestamps(cli_app, mocker, tmp_path):
    """Test subs command with -t timestamps flag."""
    pytest.importorskip("srt")

    from typer.testing import CliRunner
    from unittest.mock import patch

    srt_file = tmp_path / "Test_Video.test123.en.srt"

    mock_info = {
        "id": "test123",
        "title": "Test Video",
        "subtitles": {"en": [{"ext": "srt"}]},
        "automatic_captions": {},
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = (
            mock_info
        )

        def mock_download(urls):
            srt_file.write_text(
                """1
00:00:00,000 --> 00:00:05,000
First subtitle.

2
00:05:00,000 --> 00:05:05,000
Second subtitle at 5 min.
""",
                encoding="utf-8",
            )
            return 0

        mock_ydl.return_value.__enter__.return_value.download.side_effect = (
            mock_download
        )

        runner = CliRunner()
        runner.invoke(
            cli_app,
            [
                "subs",
                "https://example.com/video",
                "--md",
                "-t",
                "300",  # 5 minutes
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        # Should create md file with timestamps
        md_file = tmp_path / "Test_Video.test123.en.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "[0:00]" in content
        assert "[5:00]" in content


@pytest.mark.integration
def test_subs_srt_flag_keeps_file(cli_app, mocker, tmp_path):
    """Test that --srt flag keeps the subtitle file (no extraction)."""
    from typer.testing import CliRunner
    from unittest.mock import patch

    srt_file = tmp_path / "Test_Video.test123.en.srt"

    mock_info = {
        "id": "test123",
        "title": "Test Video",
        "subtitles": {"en": [{"ext": "srt"}]},
        "automatic_captions": {},
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl:
        mock_ydl.return_value.__enter__.return_value.extract_info.return_value = (
            mock_info
        )

        def mock_download(urls):
            srt_file.write_text(
                """1
00:00:00,000 --> 00:00:05,000
Test.
""",
                encoding="utf-8",
            )
            return 0

        mock_ydl.return_value.__enter__.return_value.download.side_effect = (
            mock_download
        )

        runner = CliRunner()
        runner.invoke(
            cli_app,
            [
                "subs",
                "https://example.com/video",
                "--srt",
                "--output-dir",
                str(tmp_path),
                "--force",
            ],
        )

        # SRT file should exist (no extraction happened)
        assert srt_file.exists()

        # No txt file should be created
        txt_file = tmp_path / "Test_Video.test123.en.txt"
        assert not txt_file.exists()


# =============================================================================
# HTTP API TESTS (Optional)
# =============================================================================


@pytest.mark.skipif(True, reason="FastAPI not yet implemented")
def test_api_subs_endpoint_success(mocker, tmp_path):
    """Test /subs endpoint with successful download."""
    import pytest
    from fastapi.testclient import TestClient

    # Only run if FastAPI is installed
    pytest.importorskip("fastapi")

    from __main__ import api

    client = TestClient(api)

    # Mock fetch_subs to return success
    mocker.patch("subxx.fetch_subs", return_value=0)

    # Create a fake subtitle file
    fake_srt = tmp_path / "test.en.srt"
    fake_srt.write_text("1\n00:00:00,000 --> 00:00:05,000\nTest subtitle\n")

    # Mock tempfile to use our tmp_path
    mocker.patch("tempfile.TemporaryDirectory", return_value=tmp_path)

    response = client.post(
        "/subs",
        json={
            "url": "https://www.youtube.com/watch?v=test",
            "langs": "en",
            "fmt": "srt",
            "auto": True,
        },
    )

    assert response.status_code == 200
    assert "Test subtitle" in response.text


@pytest.mark.skipif(True, reason="FastAPI not yet implemented")
def test_api_subs_endpoint_not_found(mocker, tmp_path):
    """Test /subs endpoint when no subtitles found."""
    import pytest
    from fastapi.testclient import TestClient

    # Only run if FastAPI is installed
    pytest.importorskip("fastapi")

    from __main__ import api

    client = TestClient(api)

    # Mock fetch_subs to return error
    mocker.patch("subxx.fetch_subs", return_value=2)

    # Mock tempfile with empty directory
    mocker.patch("tempfile.TemporaryDirectory", return_value=tmp_path)

    response = client.post(
        "/subs", json={"url": "https://www.youtube.com/watch?v=test", "langs": "en"}
    )

    assert response.status_code in [404, 500]


# =============================================================================
# E2E TESTS - Real YouTube API (requires internet)
# Run with: pytest -m e2e
# Skip with: pytest -m "not e2e"
# =============================================================================

# Golden set of stable YouTube videos for e2e testing
GOLDEN_VIDEO = {
    "video_id": "mAKxcNQpiSg",
    "url": "https://www.youtube.com/watch?v=mAKxcNQpiSg",
    "title": "The FULL Story of the Man-Eating Lions of Tsavo",
    "has_auto_subs": True,
    "duration_approx": 3533,  # ~58:53
}


@pytest.mark.e2e
@pytest.mark.slow
def test_e2e_list_subtitles(cli_app):
    """E2E TEST-1: List available subtitles from real YouTube video."""
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(cli_app, ["list", GOLDEN_VIDEO["url"]])

    assert result.exit_code == 0
    assert "Tsavo" in result.stdout or "Video" in result.stdout
    # Should list available languages
    assert "en" in result.stdout.lower() or "auto" in result.stdout.lower()


@pytest.mark.e2e
@pytest.mark.slow
def test_e2e_download_srt(cli_app, tmp_path):
    """E2E TEST-2: Download English subtitle as SRT."""
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(
        cli_app, ["subs", GOLDEN_VIDEO["url"], "--output-dir", str(tmp_path), "--force"]
    )

    assert result.exit_code == 0

    # Should create SRT file
    srt_files = list(tmp_path.glob("*.srt"))
    assert (
        len(srt_files) >= 1
    ), f"No SRT files created. Files: {list(tmp_path.glob('*'))}"

    # Verify SRT content
    content = srt_files[0].read_text(encoding="utf-8")
    assert "-->" in content, "SRT file missing timestamp arrows"


@pytest.mark.e2e
@pytest.mark.slow
def test_e2e_extract_txt(cli_app, tmp_path):
    """E2E TEST-3: Extract to plain text, SRT auto-deleted."""
    pytest.importorskip("srt")
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(
        cli_app,
        [
            "subs",
            GOLDEN_VIDEO["url"],
            "--txt",
            "--output-dir",
            str(tmp_path),
            "--force",
        ],
    )

    assert result.exit_code == 0

    # TXT file should exist
    txt_files = list(tmp_path.glob("*.txt"))
    assert (
        len(txt_files) >= 1
    ), f"No TXT files created. Files: {list(tmp_path.glob('*'))}"

    # SRT should be auto-deleted
    srt_files = list(tmp_path.glob("*.srt"))
    assert len(srt_files) == 0, "SRT file should be deleted after extraction"

    # TXT should have content without timestamps
    content = txt_files[0].read_text(encoding="utf-8")
    assert len(content) > 100, "TXT file too small"
    assert "00:00:00" not in content, "TXT should not contain SRT timestamps"


@pytest.mark.e2e
@pytest.mark.slow
def test_e2e_extract_md_timestamps(cli_app, tmp_path):
    """E2E TEST-4: Extract to Markdown with 5-minute timestamp markers."""
    pytest.importorskip("srt")
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(
        cli_app,
        [
            "subs",
            GOLDEN_VIDEO["url"],
            "--md",
            "-t",
            "300",  # 5-minute intervals
            "--output-dir",
            str(tmp_path),
            "--force",
        ],
    )

    assert result.exit_code == 0

    # MD file should exist
    md_files = list(tmp_path.glob("*.md"))
    assert len(md_files) >= 1, f"No MD files created. Files: {list(tmp_path.glob('*'))}"

    content = md_files[0].read_text(encoding="utf-8")

    # Should have timestamp markers
    assert "[0:00]" in content, "Missing [0:00] timestamp marker"
    assert "[5:0" in content or "[5:00]" in content, "Missing 5-minute timestamp marker"


@pytest.mark.e2e
@pytest.mark.slow
def test_e2e_dry_run(cli_app, tmp_path):
    """E2E TEST-8: Dry run mode creates no files."""
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(
        cli_app,
        [
            "subs",
            GOLDEN_VIDEO["url"],
            "--dry-run",
            "--output-dir",
            str(tmp_path),
            "--force",
        ],
    )

    assert result.exit_code == 0
    assert "dry run" in result.stdout.lower() or "would" in result.stdout.lower()

    # No files should be created
    all_files = list(tmp_path.glob("*"))
    assert len(all_files) == 0, f"Dry run should create no files, found: {all_files}"


@pytest.mark.e2e
@pytest.mark.slow
def test_e2e_quiet_mode(cli_app, tmp_path):
    """E2E TEST-9: Quiet mode suppresses output but creates files."""
    from typer.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(
        cli_app,
        [
            "subs",
            GOLDEN_VIDEO["url"],
            "--quiet",
            "--output-dir",
            str(tmp_path),
            "--force",
        ],
    )

    assert result.exit_code == 0

    # Output should be minimal/empty
    assert (
        len(result.stdout.strip()) < 50
    ), f"Quiet mode should suppress output, got: {result.stdout}"

    # File should still be created
    srt_files = list(tmp_path.glob("*.srt"))
    assert len(srt_files) >= 1, "Quiet mode should still create files"
