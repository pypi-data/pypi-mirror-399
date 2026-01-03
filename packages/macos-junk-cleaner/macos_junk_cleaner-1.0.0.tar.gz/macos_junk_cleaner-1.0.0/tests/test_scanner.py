import os

from macos_junk_cleaner.scanner import is_junk, scan_junk


def test_is_junk():
    assert is_junk(".DS_Store") is True
    assert is_junk("._foo") is True
    assert is_junk(".Spotlight-V100") is True
    assert is_junk("regular_file.txt") is False
    assert is_junk("Documents") is False


def test_scan_junk(tmp_path):
    # Create mock structure
    (tmp_path / "normal_dir").mkdir()
    (tmp_path / "normal_dir" / "file.txt").write_text("hello")
    (tmp_path / "normal_dir" / ".DS_Store").write_text("junk")
    (tmp_path / "normal_dir" / "._apple").write_text("junk")

    junk_dir = tmp_path / ".Spotlight-V100"
    junk_dir.mkdir()
    (junk_dir / "inside_junk").write_text("junk")

    others = tmp_path / "others"
    others.mkdir()
    (others / ".Trashes").mkdir()

    found = scan_junk(str(tmp_path))

    # Sort for consistent comparison
    found_basenames = sorted([os.path.basename(f) for f in found])
    expected_basenames = sorted([".DS_Store", "._apple", ".Spotlight-V100", ".Trashes"])

    assert found_basenames == expected_basenames
    assert len(found) == 4


def test_scan_junk_non_recursive(tmp_path):
    # Create mock structure
    (tmp_path / ".DS_Store").write_text("junk")

    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    (sub_dir / ".DS_Store").write_text("junk")

    # Recursive (default) should find 2
    assert len(scan_junk(str(tmp_path))) == 2

    # Non-recursive should find 1
    found = scan_junk(str(tmp_path), recursive=False)
    assert len(found) == 1
    assert os.path.basename(found[0]) == ".DS_Store"
