"""Observed German competitor registrations and dated price/range research."""
from pathlib import Path
import re


def source_path(root, filename):
    """Catalog entries are single filenames; never follow an escape from cache."""
    if not isinstance(filename, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', filename):
        raise ValueError('Noncanonical source filename')
    base = Path(root).resolve()
    path = (base / filename).resolve()
    if not path.is_relative_to(base):
        raise ValueError('Source path escapes cache')
    return path
