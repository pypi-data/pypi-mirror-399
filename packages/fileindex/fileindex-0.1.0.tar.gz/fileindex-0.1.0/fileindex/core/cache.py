import json
import time
from pathlib import Path


class IndexCache:
    def __init__(self):
        self.cache_dir = Path.home()/".fileindex"
        self.cache_file = self.cache_dir/"index.json"

    def save(self, root, records):
        """
        Save scan results to disk
        Also remember this as last scanned root
        """
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "root": str(Path(root).resolve()),
            "scanned_at": time.time(),
            "file_count": len(records),
            "records": records,
        }

        with self.cache_file.open("w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self):
        """
        Load cached indexed file
        Returns dict or None
        """
        if not self.cache_file.exists():
            return None

        with self.cache_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def is_valid(self, root):
        """
        check whether cache matches requested root
        """
        data = self.load()
        if not data:
            return False

        return data.get("root") == str(Path(root).expanduser().resolve())

    def has_cache(self):
        """
        check if any cahce exists
        """
        return self.cache_file.exists()

    def get_last_root(self):
        """
        Return last scanned root, or None
        """
        data = self.load()
        if not data:
            return None

        return data.get("root")

    def get_records(self):
        """
        Return cached records or empty list
        Useful for incremental scans
        """
        data = self.load()
        if not data:
            return []
        return data.get("records", [])

    def clear(self):
        """
        clear cached index
        """
        if self.cache_file.exists():
            self.cache_file.unlink()
