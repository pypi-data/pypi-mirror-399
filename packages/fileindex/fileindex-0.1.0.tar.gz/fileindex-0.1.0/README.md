# fileindex

A fast, efficient command-line tool for local file indexing and searching with intelligent caching and duplicate detection.

## Features

- **Lightning-fast indexing**: Recursively scans directories and creates a comprehensive file index
- **Smart caching**: Caches results locally for instant searches without re-scanning
- **Incremental updates**: Re-scan only modified files using timestamps and sizes
- **Content-based deduplication**: Detect duplicate files using SHA256 hashing
- **Advanced filtering**: Search by name, extension, size range, and path
- **Chained filters**: Combine multiple filters to refine search results
- **Beautiful CLI**: Color-coded output with clear status messages
- **Zero dependencies**: Pure Python implementation using only standard library
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Easy installation**: Single command to install as a system command

## Installation

### Quick Start - Using pip (Recommended)

```bash
pip install fileindex
```

That's it! You can now use `fileindex` from anywhere:

```bash
fileindex scan ~/projects
fileindex search main
```

### Other Installation Methods

**Using uv (fastest project add):**
```bash
uv add fileindex
uv run fileindex scan .
```

**Using uv as a global tool:**
```bash
uv tool install fileindex
# ensure uv's bin dir is on PATH, then
fileindex scan .
```

**Using pipx (isolated CLI tool):**
```bash
pipx install fileindex
fileindex scan ~/projects
```

**From source (development):**
```bash
git clone https://github.com/Dhritikrishna123/file-index.git
cd fileindex
pip install -e .
```

### System Requirements
- **Python:** 3.8 or higher
- **OS:** Windows, macOS, or Linux
- **Disk:** ~100 KB for the package

After install, running `fileindex` should show the welcome screen with commands.

## Quick Start

```bash
# Index a directory
fileindex scan ~/projects

# Search files
fileindex search main
fileindex search document --ext pdf

# View cache status
fileindex status

# Find duplicates
fileindex dup

# Clear cache
fileindex cache clear
```

## Commands Reference

### `scan <path>`
Index a directory and cache the results.

```bash
fileindex scan ~/my_project
```

Features:
- Recursively walks directory tree
- Skips: `.git`, `__pycache__`, `node_modules`
- Computes SHA256 hash for each file
- Incremental scanning: reuses cached hashes

### `search <query>`
Search indexed files.

```bash
fileindex search main
fileindex search config --ext json
fileindex search . --ext py --path src --min-size 1000 --limit 20
```

**Filters:**
- `--ext <ext>` - Filter by extension
- `--path <substring>` - Filter by path
- `--min-size <bytes>` - Minimum file size
- `--max-size <bytes>` - Maximum file size
- `--limit <n>` - Limit output (default: 10)

### `status`
Display cache information.

```bash
fileindex status
```

### `dup`
Find all duplicate files based on content hash.

```bash
fileindex dup
```

### `cache clear`
Clear the cached index.

```bash
fileindex cache clear
```

## Usage Examples

```bash
# Find all Python files
fileindex scan ~/projects
fileindex search . --ext py --limit 100

# Locate large log files
fileindex search log --min-size 10000000

# Search in specific directory
fileindex search config --path /etc

# Find duplicates
fileindex scan ~/projects && fileindex dup

# Combined search
fileindex search . --ext py --path src --min-size 5000
```

## Cache Location

- **Linux/macOS**: `~/.fileindex/index.json`
- **Windows**: `C:\Users\<YourUser>\AppData\Roaming\.fileindex\index.json`

## Performance

- **Scanning**: ~1000-5000 files/second
- **Searching**: Instant (<100ms for cached index)
- **Memory**: Minimal, streaming operations
- **Incremental scan**: 50-90% faster than full scan

## Architecture

### Core Modules

- **`fileindex.core.scan`** - Directory scanning with SHA256 hashing
- **`fileindex.core.search`** - Advanced search and filtering
- **`fileindex.core.cache`** - Persistent JSON caching
- **`fileindex.cli.style`** - Terminal styling and colors
- **`fileindex.cli.welcome`** - Welcome screen and help

### Data Structure

Each file record contains:
```python
{
    "name": "file.txt",
    "path": "/full/path/file.txt",
    "ext": "txt",
    "size": 2048,
    "mtime": 1609459200.0,
    "hash": "abc123def456..."  # SHA256
}
```

## Testing

Run the comprehensive test suite:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Support & Issues

- Report bugs or feature requests: https://github.com/Dhritikrishna123/file-index/issues
- Repository: https://github.com/Dhritikrishna123/file-index

61+ tests covering:
- Directory scanning
- Search functionality
- Caching systems
- CLI styling
- Integration workflows

## Project Structure

```
fileindex/
├── fileindex/              # Main package
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py
│   ├── cli/
│   │   ├── style.py
│   │   └── welcome.py
│   └── core/
│       ├── scan.py
│       ├── search.py
│       └── cache.py
├── tests/                  # Test suite (61+ tests)
├── README.md
├── (dist/ created when you build)
├── LICENSE
├── setup.py
└── pyproject.toml
```

## Platform Support

- ✅ Linux
- ✅ macOS
- ✅ Windows

The `fileindex` command works identically across all platforms.

## Troubleshooting

### Command Not Found

```bash
# Check installation
pip list | grep fileindex

# Check PATH
echo $PATH  # Linux/Mac
echo %PATH%  # Windows

# Reinstall
pip uninstall fileindex
pip install fileindex
```

### Permission Issues (Linux/Mac)

```bash
pip install --user fileindex
```

## License

MIT License - See LICENSE file

## Roadmap

- Config file support for custom ignore patterns
- Regex-based search
- SQLite database backend
- Watch mode for real-time indexing
- CSV/JSON export
- Parallel scanning
- Fuzzy matching

## Notes

- All file paths are absolute
- Search is case-insensitive
- File hashing uses SHA256
- Supports Python 3.8+
- Zero external dependencies
