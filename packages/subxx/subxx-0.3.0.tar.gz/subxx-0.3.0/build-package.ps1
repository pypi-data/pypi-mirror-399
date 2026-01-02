#!/usr/bin/env pwsh
# build-package.ps1 - Build subxx package for PyPI
# Handles temporary README.md creation from !README.md

param(
    [switch]$Test,      # Upload to test.pypi.org instead of pypi.org
    [switch]$Upload,    # Upload after building
    [switch]$Clean      # Clean dist/ before building
)

$ErrorActionPreference = "Stop"

Write-Host "🔨 Building subxx package..." -ForegroundColor Cyan

# Use uv run python to ensure we use the venv
$pythonCmd = "uv", "run", "python3"

# Check if build module is available
uv run python3 -c "import build" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Build tools not installed." -ForegroundColor Yellow
    Write-Host "   Run: uv sync --extra dev" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Configuration
$SourceReadme = "!README.md"
$TempReadme = "README.md"
$DistDir = "dist"

# Step 1: Clean if requested
if ($Clean -and (Test-Path $DistDir)) {
    Write-Host "🧹 Cleaning $DistDir..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $DistDir
}

# Step 2: Check source README exists
if (-not (Test-Path $SourceReadme)) {
    Write-Error "❌ Source file $SourceReadme not found!"
    exit 1
}

# Step 3: Create temporary README.md
Write-Host "📝 Copying $SourceReadme → $TempReadme..." -ForegroundColor Green
Copy-Item $SourceReadme $TempReadme -Force

try {
    # Step 4: Update pyproject.toml temporarily
    Write-Host "📝 Updating pyproject.toml..." -ForegroundColor Green
    $pyprojectContent = Get-Content "pyproject.toml" -Raw
    $originalContent = $pyprojectContent
    $pyprojectContent = $pyprojectContent -replace 'readme = "!README.md"', 'readme = "README.md"'
    Set-Content "pyproject.toml" $pyprojectContent -NoNewline

    try {
        # Step 5: Build package
        Write-Host "🔧 Building distribution..." -ForegroundColor Cyan
        uv run python3 -m build

        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ Build failed!"
            exit $LASTEXITCODE
        }

        # Step 6: Check package
        Write-Host "✅ Checking package..." -ForegroundColor Green
        uv run python3 -m twine check dist/*

        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ Package check failed!"
            exit $LASTEXITCODE
        }

        # Step 7: Upload if requested
        if ($Upload) {
            if ($Test) {
                Write-Host "📤 Uploading to test.pypi.org..." -ForegroundColor Magenta
                uv run python3 -m twine upload --repository testpypi dist/*
            } else {
                Write-Host "📤 Uploading to pypi.org..." -ForegroundColor Magenta
                uv run python3 -m twine upload dist/*
            }

            if ($LASTEXITCODE -ne 0) {
                Write-Error "❌ Upload failed!"
                exit $LASTEXITCODE
            }

            Write-Host "✅ Upload complete!" -ForegroundColor Green
        }

        Write-Host ""
        Write-Host "✅ Build complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📦 Package files:" -ForegroundColor Cyan
        Get-ChildItem dist/*.whl, dist/*.tar.gz | ForEach-Object {
            Write-Host "   - $($_.Name)" -ForegroundColor White
        }

        if (-not $Upload) {
            Write-Host ""
            Write-Host "To upload to TestPyPI:" -ForegroundColor Yellow
            Write-Host "  .\build-package.ps1 -Upload -Test" -ForegroundColor White
            Write-Host ""
            Write-Host "To upload to PyPI:" -ForegroundColor Yellow
            Write-Host "  .\build-package.ps1 -Upload" -ForegroundColor White
        }

    } finally {
        # Restore pyproject.toml
        Write-Host "🔄 Restoring pyproject.toml..." -ForegroundColor Yellow
        Set-Content "pyproject.toml" $originalContent -NoNewline
    }

} finally {
    # Step 8: Always remove temporary README.md
    if (Test-Path $TempReadme) {
        Write-Host "🔄 Removing temporary $TempReadme..." -ForegroundColor Yellow
        Remove-Item $TempReadme -Force
    }
}

Write-Host ""
Write-Host "✅ Done! Repository files unchanged." -ForegroundColor Green
