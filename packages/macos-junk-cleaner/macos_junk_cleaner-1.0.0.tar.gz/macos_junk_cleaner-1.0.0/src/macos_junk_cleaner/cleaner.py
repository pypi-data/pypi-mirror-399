import os
import shutil


def remove_junk(paths, dry_run=True):
    removed = []
    errors = []

    for path in paths:
        if dry_run:
            removed.append(path)
            continue

        try:
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            removed.append(path)
        except Exception as e:
            errors.append((path, str(e)))

    return removed, errors
