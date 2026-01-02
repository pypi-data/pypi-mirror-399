"""
conftest.py - pytest configuration and fixtures
"""

import pytest
from pathlib import Path
import importlib.util


@pytest.fixture
def cli_app():
    """Fixture providing the Typer CLI app."""
    # Load our __main__.py module explicitly to avoid conflict with pytest's __main__
    main_path = Path(__file__).parent / "__main__.py"
    spec = importlib.util.spec_from_file_location("subxx_main", main_path)
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    return main_module.app
