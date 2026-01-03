"""Integration tests for fileindex"""
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from fileindex.core.scan import Scan
from fileindex.core.search import Search
from fileindex.core.cache import IndexCache


class TestIntegration(unittest.TestCase):
    """Integration tests for complete fileindex workflow"""

    def setUp(self):
        """Create test directory structure"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create test files
        (self.root / "README.md").write_text("# Project")
        (self.root / "main.py").write_text("import sys\nprint('hello')")
        (self.root / "utils.py").write_text("def helper():\n    pass")

        # Create subdirectory
        (self.root / "src").mkdir()
        (self.root / "src" / "module.py").write_text("class Module:\n    pass")
        (self.root / "src" / "config.json").write_text('{"key": "value"}')

        # Create test subdirectory
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_main.py").write_text("import unittest\n")

    def tearDown(self):
        """Clean up temporary directory"""
        self.temp_dir.cleanup()

    def test_scan_and_search_workflow(self):
        """Test scanning and searching files"""
        # Step 1: Scan directory
        scan = Scan(str(self.root))
        records = scan.run()

        # Should find 6 files
        self.assertEqual(len(records), 6)

        # Step 2: Search by name
        search = Search(records)
        py_files = search.by_extension('py')
        self.assertEqual(len(py_files), 4)

        # Step 3: Chain filters - find main (could be main.py or test_main.py)
        main_files = Search(py_files).by_name('main')
        self.assertGreaterEqual(len(main_files), 1)
        names = {f['name'] for f in main_files}
        self.assertTrue('main.py' in names or 'test_main.py' in names)

    def test_scan_and_cache_workflow(self):
        """Test scanning and caching"""
        temp_cache = tempfile.TemporaryDirectory()
        cache_root = Path(temp_cache.name)

        try:
            with patch.object(Path, 'home', return_value=cache_root):
                # Step 1: Scan directory
                scan = Scan(str(self.root))
                records = scan.run()
                self.assertEqual(len(records), 6)

                # Step 2: Cache results
                cache = IndexCache()
                cache.save(str(self.root), records)
                self.assertTrue(cache.has_cache())

                # Step 3: Load from cache
                loaded_data = cache.load()
                self.assertIsNotNone(loaded_data)
                self.assertEqual(len(loaded_data['records']), 6)
                self.assertEqual(loaded_data['file_count'], 6)

                # Step 4: Search cached records
                search = Search(loaded_data['records'])
                md_files = search.by_extension('md')
                self.assertEqual(len(md_files), 1)
                self.assertEqual(md_files[0]['name'], 'README.md')
        finally:
            temp_cache.cleanup()

    def test_incremental_scan_and_cache(self):
        """Test incremental scanning with cache"""
        temp_cache = tempfile.TemporaryDirectory()
        cache_root = Path(temp_cache.name)

        try:
            with patch.object(Path, 'home', return_value=cache_root):
                cache = IndexCache()

                # First scan
                scan1 = Scan(str(self.root))
                records1 = scan1.run()
                cache.save(str(self.root), records1)

                # Get cached records
                cached_records = cache.get_records()

                # Second scan with previous records
                scan2 = Scan(str(self.root), previous_records=cached_records)
                records2 = scan2.run()

                # Both scans should find same number of files
                self.assertEqual(len(records1), len(records2))

                # Hashes should be same
                for r1, r2 in zip(records1, records2):
                    if r1['path'] == r2['path']:
                        self.assertEqual(r1['hash'], r2['hash'])
        finally:
            temp_cache.cleanup()

    def test_search_filters_combined(self):
        """Test combining multiple search filters"""
        scan = Scan(str(self.root))
        records = scan.run()

        # Start with all records
        search = Search(records)

        # Filter by extension
        py_files = search.by_extension('py')
        self.assertGreater(len(py_files), 0)

        # Filter by path
        src_files = Search(py_files).by_path('src')
        self.assertEqual(len(src_files), 1)
        self.assertIn('src', src_files[0]['path'])

        # Filter by size
        large_files = Search(py_files).by_size(min_size=10)
        self.assertGreater(len(large_files), 0)

    def test_duplicate_detection(self):
        """Test duplicate file detection"""
        # Create duplicate file
        (self.root / "copy_main.py").write_text("import sys\nprint('hello')")

        scan = Scan(str(self.root))
        records = scan.run()

        search = Search(records)
        duplicates = search.find_duplicates()

        # Should find one duplicate group
        self.assertEqual(len(duplicates), 1)

        # The duplicate group should have 2 files
        for files in duplicates.values():
            self.assertEqual(len(files), 2)
            names = {f['name'] for f in files}
            self.assertIn('main.py', names)
            self.assertIn('copy_main.py', names)

    def test_empty_directory_scan(self):
        """Test scanning empty directory"""
        empty_dir = Path(tempfile.mkdtemp())
        try:
            scan = Scan(str(empty_dir))
            records = scan.run()
            self.assertEqual(len(records), 0)
        finally:
            empty_dir.rmdir()

    def test_file_metadata_accuracy(self):
        """Test that file metadata is accurate"""
        scan = Scan(str(self.root))
        records = scan.run()

        # Find README.md
        readme = [r for r in records if r['name'] == 'README.md'][0]

        # Verify metadata
        self.assertEqual(readme['name'], 'README.md')
        self.assertEqual(readme['ext'], 'md')
        self.assertGreater(readme['size'], 0)
        self.assertGreater(readme['mtime'], 0)
        self.assertEqual(len(readme['hash']), 64)  # SHA256 hex is 64 chars


if __name__ == '__main__':
    unittest.main()
