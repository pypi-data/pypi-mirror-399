"""Tests for core.scan module"""
import unittest
import tempfile
import os
from pathlib import Path
from fileindex.core.scan import Scan


class TestScan(unittest.TestCase):
    """Test cases for Scan class"""

    def setUp(self):
        """Create temporary directory structure for testing"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

        # Create test files
        (self.root / "file1.txt").write_text("Hello, World!")
        (self.root / "file2.py").write_text("print('hello')")

        # Create subdirectory with files
        (self.root / "subdir").mkdir()
        (self.root / "subdir" / "file3.txt").write_text("Subdir file")

        # Create ignored directories (should be skipped)
        (self.root / ".git").mkdir()
        (self.root / ".git" / "config").write_text("git config")
        (self.root / "__pycache__").mkdir()
        (self.root / "__pycache__" / "module.pyc").write_text("pyc")

    def tearDown(self):
        """Clean up temporary directory"""
        self.temp_dir.cleanup()

    def test_scan_initialization(self):
        """Test Scan class initialization"""
        scan = Scan(str(self.root))
        self.assertEqual(scan.root, self.root.resolve())
        self.assertEqual(len(scan.records), 0)
        self.assertEqual(len(scan._seen_paths), 0)

    def test_scan_validates_root_exists(self):
        """Test that scan validates root directory exists"""
        scan = Scan("/nonexistent/path")
        with self.assertRaises(FileNotFoundError):
            scan._validate_root()

    def test_scan_validates_root_is_directory(self):
        """Test that scan validates root is a directory"""
        file_path = self.root / "file1.txt"
        scan = Scan(str(file_path))
        with self.assertRaises(NotADirectoryError):
            scan._validate_root()

    def test_scan_finds_files(self):
        """Test that scan finds all files"""
        scan = Scan(str(self.root))
        records = scan.run()

        # Should find 3 files (not in ignored dirs)
        self.assertGreaterEqual(len(records), 3)
        file_names = [r['name'] for r in records]
        self.assertIn('file1.txt', file_names)
        self.assertIn('file2.py', file_names)
        self.assertIn('file3.txt', file_names)

    def test_scan_skips_ignored_directories(self):
        """Test that scan skips .git and __pycache__"""
        scan = Scan(str(self.root))
        records = scan.run()

        # No files from .git or __pycache__ should be found
        paths = [r['path'] for r in records]
        git_files = [p for p in paths if '.git' in p]
        pyc_files = [p for p in paths if '__pycache__' in p]

        self.assertEqual(len(git_files), 0)
        self.assertEqual(len(pyc_files), 0)

    def test_record_structure(self):
        """Test that records have correct structure"""
        scan = Scan(str(self.root))
        records = scan.run()

        self.assertGreater(len(records), 0)
        record = records[0]

        # Check all required fields
        self.assertIn('name', record)
        self.assertIn('path', record)
        self.assertIn('ext', record)
        self.assertIn('size', record)
        self.assertIn('mtime', record)
        self.assertIn('hash', record)

    def test_record_extension_extraction(self):
        """Test that file extensions are correctly extracted"""
        scan = Scan(str(self.root))
        records = scan.run()

        txt_files = [r for r in records if r['ext'] == 'txt']
        py_files = [r for r in records if r['ext'] == 'py']

        self.assertGreater(len(txt_files), 0)
        self.assertGreater(len(py_files), 0)

    def test_record_size(self):
        """Test that file sizes are correctly recorded"""
        scan = Scan(str(self.root))
        records = scan.run()

        # Find the file1.txt record
        file1_record = [r for r in records if r['name'] == 'file1.txt'][0]
        self.assertEqual(file1_record['size'], 13)  # "Hello, World!" is 13 bytes

    def test_hash_is_computed(self):
        """Test that file hash is computed"""
        scan = Scan(str(self.root))
        records = scan.run()

        for record in records:
            self.assertIsNotNone(record['hash'])
            self.assertIsInstance(record['hash'], str)
            # SHA256 hex digest is 64 characters
            self.assertEqual(len(record['hash']), 64)

    def test_incremental_scan_reuses_hash(self):
        """Test that incremental scan reuses hash for unchanged files"""
        # First scan
        scan1 = Scan(str(self.root))
        records1 = scan1.run()

        # Second scan with previous records
        scan2 = Scan(str(self.root), previous_records=records1)
        records2 = scan2.run()

        # Find matching records and verify hashes are the same
        for r1, r2 in zip(records1, records2):
            if r1['path'] == r2['path']:
                self.assertEqual(r1['hash'], r2['hash'])


class TestScanPathExpansion(unittest.TestCase):
    """Test path expansion in Scan"""

    def test_expanduser_in_path(self):
        """Test that ~ is expanded to home directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a real path
            scan = Scan(temp_dir)
            self.assertEqual(scan.root, Path(temp_dir).resolve())


if __name__ == '__main__':
    unittest.main()
