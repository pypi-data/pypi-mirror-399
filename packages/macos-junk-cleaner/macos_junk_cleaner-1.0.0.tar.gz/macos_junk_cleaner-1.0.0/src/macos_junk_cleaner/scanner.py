import os
import re

JUNK_PATTERNS = [
    r"\.DS_Store",
    r"\._.*",
    r"\.Spotlight-V100",
    r"\.Trashes",
    r"\.fseventsd",
    r"Network Trash Folder",
    r"Temporary Items",
]


def is_junk(name):
    for pattern in JUNK_PATTERNS:
        if re.fullmatch(pattern, name):
            return True
    return False


def scan_junk(root_path, recursive=True):
    junk_files = []

    if not recursive:
        try:
            for item in os.listdir(root_path):
                if is_junk(item):
                    junk_files.append(os.path.join(root_path, item))
        except Exception:
            pass
        return junk_files

    for root, dirs, files in os.walk(root_path):
        # Check directories
        for d in dirs[:]:
            if is_junk(d):
                junk_files.append(os.path.join(root, d))
                # Don't recurse into junk directories
                dirs.remove(d)

        # Check files
        for f in files:
            if is_junk(f):
                junk_files.append(os.path.join(root, f))

    return junk_files
