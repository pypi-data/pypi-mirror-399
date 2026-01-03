"""Tests for core.cache module"""
import unittest
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch
from fileindex.core.cache import IndexCache


class TestIndexCache(unittest.TestCase):
    """Test cases for IndexCache class"""

    def setUp(self):
        """Set up temporary cache directory"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up temporary directory"""
        self.temp_dir.cleanup()

    def test_cache_initialization(self):
        """Test IndexCache initialization"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            self.assertEqual(cache.cache_dir, self.cache_dir / ".fileindex")
            self.assertEqual(cache.cache_file, self.cache_dir / ".fileindex" / "index.json")

    def test_has_cache_false_when_empty(self):
        """Test has_cache returns False when no cache exists"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            self.assertFalse(cache.has_cache())

    def test_save_creates_cache_file(self):
        """Test that save creates cache file"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            records = [
                {
                    'name': 'test.txt',
                    'path': '/test.txt',
                    'ext': 'txt',
                    'size': 100,
                    'mtime': 123456.0,
                    'hash': 'abc123'
                }
            ]

            cache.save('/test/root', records)

            self.assertTrue(cache.has_cache())
            self.assertTrue(cache.cache_file.exists())

    def test_save_stores_correct_data(self):
        """Test that save stores correct data structure"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            records = [
                {
                    'name': 'file.txt',
                    'path': '/root/file.txt',
                    'ext': 'txt',
                    'size': 256,
                    'mtime': 789012.0,
                    'hash': 'def456'
                }
            ]

            before_save = time.time()
            cache.save('/root', records)
            after_save = time.time()

            # Load and verify
            with open(cache.cache_file) as f:
                data = json.load(f)

            self.assertIn('root', data)
            self.assertIn('scanned_at', data)
            self.assertIn('file_count', data)
            self.assertIn('records', data)

            self.assertEqual(data['root'], str(Path('/root').resolve()))
            self.assertEqual(data['file_count'], 1)
            self.assertEqual(len(data['records']), 1)
            self.assertGreaterEqual(data['scanned_at'], before_save)
            self.assertLessEqual(data['scanned_at'], after_save)

    def test_load_returns_none_when_no_cache(self):
        """Test that load returns None when no cache exists"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            result = cache.load()
            self.assertIsNone(result)

    def test_load_returns_cached_data(self):
        """Test that load returns previously saved data"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            records = [
                {
                    'name': 'test.txt',
                    'path': '/test.txt',
                    'ext': 'txt',
                    'size': 100,
                    'mtime': 123456.0,
                    'hash': 'abc123'
                }
            ]

            cache.save('/test/root', records)
            data = cache.load()

            self.assertIsNotNone(data)
            self.assertEqual(data['file_count'], 1)
            self.assertEqual(data['records'][0]['name'], 'test.txt')

    def test_get_records_empty_when_no_cache(self):
        """Test get_records returns empty list when no cache"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            records = cache.get_records()
            self.assertEqual(records, [])

    def test_get_records_returns_records(self):
        """Test get_records returns saved records"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            test_records = [
                {
                    'name': 'file1.txt',
                    'path': '/file1.txt',
                    'ext': 'txt',
                    'size': 100,
                    'mtime': 123456.0,
                    'hash': 'abc123'
                },
                {
                    'name': 'file2.py',
                    'path': '/file2.py',
                    'ext': 'py',
                    'size': 200,
                    'mtime': 123457.0,
                    'hash': 'def456'
                }
            ]

            cache.save('/root', test_records)
            records = cache.get_records()

            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]['name'], 'file1.txt')
            self.assertEqual(records[1]['name'], 'file2.py')

    def test_get_last_root_none_when_no_cache(self):
        """Test get_last_root returns None when no cache"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            root = cache.get_last_root()
            self.assertIsNone(root)

    def test_get_last_root_returns_root(self):
        """Test get_last_root returns previously saved root"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            cache.save('/home/user/projects', [])

            root = cache.get_last_root()
            self.assertEqual(root, str(Path('/home/user/projects').resolve()))

    def test_is_valid_true_for_matching_root(self):
        """Test is_valid returns True when cache matches root"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            cache.save('/test/root', [])

            is_valid = cache.is_valid('/test/root')
            self.assertTrue(is_valid)

    def test_is_valid_false_for_different_root(self):
        """Test is_valid returns False when cache doesn't match root"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            cache.save('/test/root1', [])

            is_valid = cache.is_valid('/test/root2')
            self.assertFalse(is_valid)

    def test_is_valid_false_when_no_cache(self):
        """Test is_valid returns False when no cache exists"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            is_valid = cache.is_valid('/test/root')
            self.assertFalse(is_valid)

    def test_clear_removes_cache_file(self):
        """Test that clear removes cache file"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            cache.save('/root', [])
            self.assertTrue(cache.has_cache())

            cache.clear()
            self.assertFalse(cache.has_cache())

    def test_clear_when_no_cache_does_nothing(self):
        """Test that clear doesn't fail when no cache exists"""
        with patch.object(Path, 'home', return_value=self.cache_dir):
            cache = IndexCache()
            # Should not raise error
            cache.clear()
            self.assertFalse(cache.has_cache())


if __name__ == '__main__':
    unittest.main()
