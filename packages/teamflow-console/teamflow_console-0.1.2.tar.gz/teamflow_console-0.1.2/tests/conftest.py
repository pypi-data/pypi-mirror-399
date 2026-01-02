"""Pytest configuration and fixtures for TeamFlow Console App."""

import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest
from rich.console import Console


@pytest.fixture
def mock_console():
    """Fixture providing a Rich Console with string buffer for testing."""
    return Console(file=StringIO(), force_terminal=True)


@pytest.fixture
def capture_output():
    """Fixture to capture stdout and stderr during tests."""

    class CapturedOutput:
        def __init__(self):
            self.stdout = StringIO()
            self.stderr = StringIO()

        def __enter__(self):
            self.redirect_stdout = redirect_stdout(self.stdout)
            self.redirect_stderr = redirect_stderr(self.stderr)
            self.redirect_stdout.__enter__()
            self.redirect_stderr.__enter__()
            return self

        def __exit__(self, *args):
            self.redirect_stdout.__exit__(*args)
            self.redirect_stderr.__exit__(*args)

        def get_stdout(self) -> str:
            return self.stdout.getvalue()

        def get_stderr(self) -> str:
            return self.stderr.getvalue()

    return CapturedOutput


@pytest.fixture
def storage_mocks():
    """Fixture providing mock storage instances for testing."""

    class StorageMocks:
        def __init__(self):
            self.tasks = {}
            self.users = {}
            self.teams = {}
            self.task_next_id = 1
            self.user_next_id = 1
            self.team_next_id = 1

    return StorageMocks()
