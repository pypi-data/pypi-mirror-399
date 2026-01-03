from io import StringIO

import pytest
from click.testing import CliRunner
from rich.console import Console

from macos_junk_cleaner.main import main


@pytest.fixture
def runner():
    return CliRunner()


def strip_formatting(text):
    """Helper to remove rich formatting/markup for easier testing."""
    # We use a very wide console to prevent table wrapping
    c = Console(file=StringIO(), force_terminal=False, width=1000, color_system=None)
    c.print(text, end="")
    return c.file.getvalue()


def test_cli_scan(runner, tmp_path):
    # Create mock junk files
    (tmp_path / ".DS_Store").write_text("junk")
    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (sub_dir / "._apple").write_text("junk")

    # Test scan with TESTING=1 to get simple output
    result = runner.invoke(main, ["scan", str(tmp_path)], env={"TESTING": "1"})
    assert result.exit_code == 0

    assert "Scanning" in result.output
    assert ".DS_Store" in result.output
    assert "._apple" in result.output


def test_cli_clean_interactive_abort(runner, tmp_path):
    (tmp_path / ".DS_Store").write_text("junk")

    # Test clean without flags, saying 'n' to prompt
    result = runner.invoke(main, ["clean", str(tmp_path)], input="n\n")
    assert result.exit_code == 0
    assert "Aborted" in result.output
    assert (tmp_path / ".DS_Store").exists()


def test_cli_clean_interactive_confirm(runner, tmp_path):
    (tmp_path / ".DS_Store").write_text("junk")

    # Test clean without flags, saying 'y' to prompt
    result = runner.invoke(main, ["clean", str(tmp_path)], input="y\n")
    assert result.exit_code == 0
    assert "Clean up complete" in result.output
    assert not (tmp_path / ".DS_Store").exists()


def test_cli_clean_yes_flag(runner, tmp_path):
    (tmp_path / ".DS_Store").write_text("junk")

    # Test clean with -y (no prompt should appear)
    result = runner.invoke(main, ["clean", "-y", str(tmp_path)])
    assert result.exit_code == 0
    assert "Proceeding with deletion" in result.output
    assert not (tmp_path / ".DS_Store").exists()


def test_cli_clean_force_flag(runner, tmp_path):
    (tmp_path / ".DS_Store").write_text("junk")

    # Test clean with --force (should skip list and prompt)
    result = runner.invoke(main, ["clean", "--force", str(tmp_path)])
    assert result.exit_code == 0
    assert "Forcing deletion" in result.output
    # The file path should still appear in the 'Removed:' output
    assert ".DS_Store" in result.output
    assert not (tmp_path / ".DS_Store").exists()


def test_cli_clean_no_junk(runner, tmp_path):
    # Test clean when no junk exists
    result = runner.invoke(main, ["clean", str(tmp_path)])
    assert result.exit_code == 0
    assert "No junk files found to clean" in result.output
