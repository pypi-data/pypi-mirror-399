"""Tests for core.search module"""
import unittest
from fileindex.core.search import Search


class TestSearch(unittest.TestCase):
    """Test cases for Search class"""

    def setUp(self):
        """Create test data"""
        self.records = [
            {
                'name': 'document.txt',
                'path': '/home/user/document.txt',
                'ext': 'txt',
                'size': 1024,
                'mtime': 1609459200.0,
                'hash': 'abc123def456'
            },
            {
                'name': 'script.py',
                'path': '/home/user/code/script.py',
                'ext': 'py',
                'size': 2048,
                'mtime': 1609459200.0,
                'hash': 'ghi789jkl012'
            },
            {
                'name': 'main.py',
                'path': '/home/user/code/main.py',
                'ext': 'py',
                'size': 4096,
                'mtime': 1609459200.0,
                'hash': 'mno345pqr678'
            },
            {
                'name': 'readme.md',
                'path': '/home/user/readme.md',
                'ext': 'md',
                'size': 512,
                'mtime': 1609459200.0,
                'hash': 'stu901vwx234'
            }
        ]

    def test_search_initialization(self):
        """Test Search class initialization"""
        search = Search(self.records)
        self.assertEqual(len(search.records), 4)
        self.assertEqual(search.records, self.records)

    def test_by_name_exact_match(self):
        """Test search by exact filename"""
        search = Search(self.records)
        results = search.by_name('document.txt')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'document.txt')

    def test_by_name_substring_match(self):
        """Test search by filename substring"""
        search = Search(self.records)
        results = search.by_name('main')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'main.py')

    def test_by_name_case_insensitive(self):
        """Test that search by name is case insensitive"""
        search = Search(self.records)
        results = search.by_name('SCRIPT')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'script.py')

    def test_by_name_no_match(self):
        """Test search by name with no matches"""
        search = Search(self.records)
        results = search.by_name('nonexistent')
        self.assertEqual(len(results), 0)

    def test_by_extension_exact_match(self):
        """Test search by file extension"""
        search = Search(self.records)
        results = search.by_extension('py')
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r['ext'], 'py')

    def test_by_extension_with_dot(self):
        """Test that extension search works with leading dot"""
        search = Search(self.records)
        results = search.by_extension('.txt')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ext'], 'txt')

    def test_by_extension_case_insensitive(self):
        """Test that extension search is case insensitive"""
        search = Search(self.records)
        results = search.by_extension('PY')
        self.assertEqual(len(results), 2)

    def test_by_extension_no_match(self):
        """Test extension search with no matches"""
        search = Search(self.records)
        results = search.by_extension('xyz')
        self.assertEqual(len(results), 0)

    def test_by_size_min_size(self):
        """Test search by minimum file size"""
        search = Search(self.records)
        results = search.by_size(min_size=2000)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertGreaterEqual(r['size'], 2000)

    def test_by_size_max_size(self):
        """Test search by maximum file size"""
        search = Search(self.records)
        results = search.by_size(max_size=2000)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertLessEqual(r['size'], 2000)

    def test_by_size_range(self):
        """Test search by size range"""
        search = Search(self.records)
        results = search.by_size(min_size=1000, max_size=3000)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertGreaterEqual(r['size'], 1000)
            self.assertLessEqual(r['size'], 3000)

    def test_by_size_no_match(self):
        """Test size search with no matches"""
        search = Search(self.records)
        results = search.by_size(min_size=10000, max_size=20000)
        self.assertEqual(len(results), 0)

    def test_by_path_substring_match(self):
        """Test search by path substring"""
        search = Search(self.records)
        results = search.by_path('code')
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertIn('code', r['path'])

    def test_by_path_case_insensitive(self):
        """Test that path search is case insensitive"""
        search = Search(self.records)
        results = search.by_path('HOME')
        self.assertEqual(len(results), 4)

    def test_by_path_no_match(self):
        """Test path search with no matches"""
        search = Search(self.records)
        results = search.by_path('nonexistent')
        self.assertEqual(len(results), 0)

    def test_find_duplicates_none(self):
        """Test find_duplicates when no duplicates exist"""
        search = Search(self.records)
        duplicates = search.find_duplicates()
        self.assertEqual(len(duplicates), 0)

    def test_find_duplicates_with_duplicates(self):
        """Test find_duplicates with duplicate content"""
        records = self.records + [
            {
                'name': 'copy.py',
                'path': '/home/user/copy.py',
                'ext': 'py',
                'size': 2048,
                'mtime': 1609459200.0,
                'hash': 'ghi789jkl012'  # Same hash as script.py
            }
        ]
        search = Search(records)
        duplicates = search.find_duplicates()

        self.assertEqual(len(duplicates), 1)
        self.assertIn('ghi789jkl012', duplicates)
        self.assertEqual(len(duplicates['ghi789jkl012']), 2)

    def test_find_duplicates_multiple_groups(self):
        """Test find_duplicates with multiple duplicate groups"""
        records = self.records + [
            {
                'name': 'copy.py',
                'path': '/home/user/copy.py',
                'ext': 'py',
                'size': 2048,
                'mtime': 1609459200.0,
                'hash': 'ghi789jkl012'
            },
            {
                'name': 'copy.txt',
                'path': '/home/user/copy.txt',
                'ext': 'txt',
                'size': 1024,
                'mtime': 1609459200.0,
                'hash': 'abc123def456'
            }
        ]
        search = Search(records)
        duplicates = search.find_duplicates()

        self.assertEqual(len(duplicates), 2)
        self.assertEqual(len(duplicates['ghi789jkl012']), 2)
        self.assertEqual(len(duplicates['abc123def456']), 2)

    def test_chained_search(self):
        """Test chaining multiple search filters"""
        search = Search(self.records)

        # First filter by extension
        results = search.by_extension('py')
        self.assertEqual(len(results), 2)

        # Chain another filter
        results = Search(results).by_name('main')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'main.py')

    def test_search_preserves_all_fields(self):
        """Test that search results preserve all record fields"""
        search = Search(self.records)
        results = search.by_name('document')

        self.assertEqual(len(results), 1)
        result = results[0]

        # All fields should be preserved
        self.assertIn('name', result)
        self.assertIn('path', result)
        self.assertIn('ext', result)
        self.assertIn('size', result)
        self.assertIn('mtime', result)
        self.assertIn('hash', result)


if __name__ == '__main__':
    unittest.main()
