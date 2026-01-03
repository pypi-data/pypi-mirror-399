# xlsxslim

[![PyPI version](https://badge.fury.io/py/xlsxslim.svg)](https://badge.fury.io/py/xlsxslim)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

**Reduce Excel file size by removing empty rows, columns, and excess formatting.**

🇺🇦 [Документація українською](README_uk.md)

v2.0.2 uses direct XML/regex manipulation — works with files of **any size** without memory issues.

## Features

- 🚀 **Memory efficient** — processes 100+ MB files with < 100 MB RAM
- 📊 **Direct XML** — no openpyxl dependency for processing
- 📁 **Auto-detect** — finds single xlsx in current directory
- 💾 **Safe** — creates `_slim` copy by default

## Installation

```bash
pip install xlsxslim
```

## Quick Start

```bash
# Auto-detect single xlsx in current directory
xlsxslim

# Optimize specific file
xlsxslim report.xlsx

# Analyze only (dry run)
xlsxslim report.xlsx --dry-run

# Overwrite original file
xlsxslim report.xlsx --inplace
```

## Example Output

```
xlsxslim v2.0.0

Input:  report.xlsx (68.64 MB)
Memory:  45.00 MB used, 16.00 GB available

Analyzing...

Sheets: 2

Sheet "Data":
  Used range:  A1:J1047716 → A1:I82
  Rows:        1,047,716 → 82 (-1,047,634)
  Columns:     10 → 9 (-1)

Sheet "Summary":
  Used range:  A1:K1047713 → A1:K76
  Rows:        1,047,713 → 76 (-1,047,637)

Optimizing...

Output: report_slim.xlsx (156.00 KB)
Saved:  68.49 MB (99.8%)
Memory:  48.00 MB used, 16.00 GB available
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output FILE` | `-o` | Custom output path |
| `--inplace` | `-i` | Overwrite original file |
| `--dry-run` | `-n` | Analyze only, don't save |
| `--verbose` | `-v` | Detailed output |
| `--quiet` | `-q` | Minimal output |
| `--suffix TEXT` | `-s` | Output suffix (default: `_slim`) |
| `--version` | | Show version |
| `--help` | `-h` | Show help |

## How It Works

xlsx files are ZIP archives containing XML. xlsxslim:

1. **Analyzes** — Scans XML to find actual data bounds
2. **Removes** — Strips rows/columns/cells beyond data range
3. **Rebuilds** — Creates new ZIP with optimized XML

No need to load entire workbook into memory.

## Why Files Get Bloated

Excel tracks a "used range" that includes any cell ever formatted:

- Ctrl+Shift+End → format applied to row 1,048,576
- Copy-paste brings invisible formatting
- Conditional formatting on entire columns
- Deleted data leaves formatted empty cells

## v2.0 vs v1.x

| Feature | v1.x (openpyxl) | v2.0 (XML) |
|---------|-----------------|------------|
| 68 MB file | 46+ GB RAM, crashes | < 100 MB RAM |
| Speed | Slow | Fast |
| Dependencies | openpyxl | None (stdlib) |

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | File not found |
| 2 | Multiple files (specify explicitly) |
| 3 | Read/write error |
| 4 | Already optimized |

## Testing

```bash
# Install dev dependencies (includes openpyxl for creating test fixtures)
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with verbose output
pytest -v
```

## License

BSD 3-Clause License

## Copyright

Copyright (c) 2025, Vladyslav V. Prodan

## Contact

- GitHub: [github.com/click0](https://github.com/click0)
- Phone: +38(099)6053340
