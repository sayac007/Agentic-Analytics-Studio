"""Deterministic serialization and exclusive, atomic artifact publication."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile


def json_bytes(document):
    return (json.dumps(document, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def csv_bytes(header, rows):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(header)
    writer.writerows(rows)
    return stream.getvalue().encode()


def write_once(path, raw):
    """Publish a read-only file without overwriting an existing file or symlink."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o444)
        os.link(temporary, path)  # atomic no-clobber, including pre-existing symlinks
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def store(path, document):
    write_once(path, json_bytes(document))


def artifact(root, relative):
    return {'path': relative, 'sha256': hashlib.sha256((root / relative).read_bytes()).hexdigest()}
