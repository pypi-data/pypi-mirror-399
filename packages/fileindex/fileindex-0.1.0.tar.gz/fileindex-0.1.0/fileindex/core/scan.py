from pathlib import Path
import os
import hashlib


class Scan:
    def __init__(self, root, previous_records=None):
        """
        root: directory to scan
        previous_records: optional list of records from cache
        """
        self.root = Path(root).expanduser().resolve()
        self.records = []

        # Build quick lookup for incremental scan
        self._previous = {}
        if previous_records:
            self._previous = {
                r["path"]: r
                for r in previous_records
            }

        # Track paths seen during scan
        self._seen_paths = set()

        # hardcoded ignore for now
        self.ignore_dirs = {
            ".git",
            "__pycache__",
            "node_modules"
        }

    def run(self):
        """
        Entry Point.
        Returns a list of file records
        """
        self._validate_root()
        self._walk()
        return self.records

    def _validate_root(self):
        """
        Ensure root exists and is a directory
        """
        if not self.root.exists():
            raise FileNotFoundError(f"Path does not exists: {self.root}")

        if not self.root.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.root}")

    def _walk(self):
        """
        Walk directory tree and collect file records
        """
        for current_dir, dirnames, filenames in os.walk(self.root):
            # modify dirnames in-place to skip ignored directories
            dirnames[:] = [
                d for d in dirnames
                if not self._should_ignore_dir(d)
            ]

            for filename in filenames:
                filepath = Path(current_dir)/filename
                path_str = str(filepath.resolve())

                self._seen_paths.add(path_str)

                try:
                    record = self._build_record(filepath)
                except (OSError, PermissionError):
                    # skip files we can't access
                    continue

                self.records.append(record)

    def _should_ignore_dir(self, dirname):
        """
        Decide whether to skip a directory
        """
        return dirname in self.ignore_dirs

    def _build_record(self, filepath):
        """
        Extract metadata for a single file
        """
        stat = filepath.stat()
        path_str = str(filepath.resolve())

        prev = self._previous.get(path_str)

        # Reuse hash if unchanged
        if prev and prev["size"] == stat.st_size and prev["mtime"] == stat.st_mtime:
            file_hash = prev.get("hash")
        else:
            file_hash = self._hash_file(filepath)

        return {
            "name": filepath.name,
            "path": str(filepath.resolve()),
            "ext": filepath.suffix.lstrip("."),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "hash": file_hash,
        }

    def _hash_file(self, filepath, chunk_size=8192):
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()
