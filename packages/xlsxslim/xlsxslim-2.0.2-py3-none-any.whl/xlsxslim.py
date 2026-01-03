#!/usr/bin/env python3
# ==============================
# xlsxslim - Reduce Excel file size by removing empty rows and columns
# Author: Vladyslav V. Prodan
# Contact: github.com/click0
# Phone: +38(099)6053340
# Version: 2.0.2
# License: BSD 3-Clause "New" or "Revised" License
# Year: 2025
# ==============================
"""
xlsxslim - Reduce Excel file size by removing empty rows and columns.

Uses direct XML manipulation for memory-efficient processing of large files.
No need to load entire workbook into memory.
"""

__version__ = "2.0.2"
__author__ = "Vladyslav V. Prodan"

import gc
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, List
from zipfile import ZipFile, ZIP_DEFLATED

import click

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# Exit codes
EXIT_SUCCESS = 0
EXIT_FILE_NOT_FOUND = 1
EXIT_MULTIPLE_FILES = 2
EXIT_IO_ERROR = 3
EXIT_ALREADY_OPTIMIZED = 4


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def get_memory_usage() -> int:
    """Get current process memory usage in bytes."""
    if HAS_PSUTIL:
        process = psutil.Process()
        return process.memory_info().rss
    return 0


def get_available_memory() -> int:
    """Get available system memory in bytes."""
    if HAS_PSUTIL:
        return psutil.virtual_memory().available
    return 0


def col_letter(col_idx: int) -> str:
    """Convert column index to Excel letter (1=A, 27=AA, etc.)."""
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result


def col_index(col_str: str) -> int:
    """Convert column letter to index (A=1, AA=27, etc.)."""
    result = 0
    for c in col_str.upper():
        result = result * 26 + (ord(c) - ord('A') + 1)
    return result


def parse_cell_ref(cell_ref: str) -> Tuple[int, int]:
    """Parse cell reference like 'B5' to (row, col) tuple."""
    match = re.match(r'^([A-Z]+)(\d+)$', cell_ref.upper())
    if not match:
        return 0, 0
    col_str, row_str = match.groups()
    return int(row_str), col_index(col_str)


def print_memory_info(quiet: bool = False):
    """Print current memory usage info."""
    if quiet or not HAS_PSUTIL:
        return
    mem_used = get_memory_usage()
    mem_avail = get_available_memory()
    click.echo(f"Memory:  {format_size(mem_used)} used, {format_size(mem_avail)} available")


def get_sheet_paths(zf: ZipFile) -> Dict[str, str]:
    """
    Get mapping of sheet names to their XML paths in the xlsx archive.
    Uses regex to avoid XML parsing issues.
    """
    # Read workbook.xml
    workbook_xml = zf.read('xl/workbook.xml').decode('utf-8')
    
    # Extract sheet names and rIds using regex
    # Handles: <sheet ... name="Sheet1" ... r:id="rId1" ...>
    # or: <sheet ... r:id="rId1" ... name="Sheet1" ...>
    sheets = {}
    
    # Find all sheet elements
    sheet_pattern = r'<sheet\s+[^>]*?name="([^"]+)"[^>]*?r:id="([^"]+)"'
    for match in re.finditer(sheet_pattern, workbook_xml):
        name, rid = match.groups()
        sheets[rid] = name
    
    # Also try with reversed order
    sheet_pattern2 = r'<sheet\s+[^>]*?r:id="([^"]+)"[^>]*?name="([^"]+)"'
    for match in re.finditer(sheet_pattern2, workbook_xml):
        rid, name = match.groups()
        if rid not in sheets:
            sheets[rid] = name
    
    # Read relationships
    rels_xml = zf.read('xl/_rels/workbook.xml.rels').decode('utf-8')
    
    # Extract relationships - handle different attribute orders
    result = {}
    
    # Pattern 1: Target before Id
    rel_pattern1 = r'<Relationship[^>]+Target="([^"]+)"[^>]+Id="([^"]+)"'
    for match in re.finditer(rel_pattern1, rels_xml):
        target, rid = match.groups()
        if rid in sheets:
            if target.startswith('/'):
                target = target.lstrip('/')
            elif not target.startswith('xl/'):
                target = 'xl/' + target.lstrip('./')
            result[sheets[rid]] = target
    
    # Pattern 2: Id before Target
    rel_pattern2 = r'<Relationship[^>]+Id="([^"]+)"[^>]+Target="([^"]+)"'
    for match in re.finditer(rel_pattern2, rels_xml):
        rid, target = match.groups()
        if rid in sheets and sheets[rid] not in result:
            if target.startswith('/'):
                target = target.lstrip('/')
            elif not target.startswith('xl/'):
                target = 'xl/' + target.lstrip('./')
            result[sheets[rid]] = target
    
    return result


def analyze_sheet_xml(zf: ZipFile, sheet_path: str) -> dict:
    """
    Analyze sheet XML to find actual data bounds using regex.
    Memory efficient - doesn't build full DOM.
    """
    sheet_xml = zf.read(sheet_path).decode('utf-8')
    
    # Get original dimension
    dim_match = re.search(r'<dimension[^>]+ref="([^"]+)"', sheet_xml)
    original_range = dim_match.group(1) if dim_match else "A1"
    
    # Parse original range to get max row/col
    if ':' in original_range:
        _, end_ref = original_range.split(':')
        orig_max_row, orig_max_col = parse_cell_ref(end_ref)
    else:
        orig_max_row, orig_max_col = parse_cell_ref(original_range)
    
    # Find actual data bounds by scanning cells
    # Look for cells with values (<v>), formulas (<f>), or inline strings (<is>)
    data_max_row = 0
    data_max_col = 0
    
    # Pattern for rows: <row r="123" ...>...</row>
    row_pattern = r'<row[^>]+r="(\d+)"[^>]*>(.*?)</row>'
    
    for row_match in re.finditer(row_pattern, sheet_xml, re.DOTALL):
        row_num = int(row_match.group(1))
        row_content = row_match.group(2)
        
        # Check if row has any cells with data
        # Pattern for cells: <c r="A1" ...>...<v>...</v>...</c> or <f>...</f> or <is>...</is>
        cell_pattern = r'<c[^>]+r="([A-Z]+\d+)"[^>]*>(.*?)</c>'
        
        row_has_data = False
        for cell_match in re.finditer(cell_pattern, row_content, re.DOTALL):
            cell_ref = cell_match.group(1)
            cell_content = cell_match.group(2)
            
            # Check if cell has value, formula, or inline string
            if '<v>' in cell_content or '<v/>' in cell_content or \
               '<f>' in cell_content or '<f ' in cell_content or \
               '<is>' in cell_content:
                row_has_data = True
                _, cell_col = parse_cell_ref(cell_ref)
                if cell_col > data_max_col:
                    data_max_col = cell_col
        
        if row_has_data and row_num > data_max_row:
            data_max_row = row_num
    
    # Handle empty sheet
    if data_max_row == 0:
        data_max_row = 1
        data_max_col = 1
    
    return {
        'path': sheet_path,
        'original_range': original_range,
        'original_max_row': orig_max_row if orig_max_row > 0 else 1,
        'original_max_col': orig_max_col if orig_max_col > 0 else 1,
        'data_max_row': data_max_row,
        'data_max_col': data_max_col,
        'new_range': f"A1:{col_letter(data_max_col)}{data_max_row}",
        'rows_deleted': max(0, orig_max_row - data_max_row),
        'cols_deleted': max(0, orig_max_col - data_max_col),
        'optimized': orig_max_row > data_max_row or orig_max_col > data_max_col,
    }


def optimize_sheet_xml(sheet_xml: bytes, max_row: int, max_col: int) -> bytes:
    """
    Optimize sheet XML by removing rows/cells beyond data bounds.
    Uses regex to preserve original XML structure exactly.
    """
    xml_str = sheet_xml.decode('utf-8')
    
    # 1. Update dimension
    new_range = f"A1:{col_letter(max_col)}{max_row}"
    xml_str = re.sub(
        r'(<dimension[^>]+ref=")[^"]+(")',
        rf'\g<1>{new_range}\g<2>',
        xml_str
    )
    
    # 2. Reset selection to A1 (prevents focus on deleted rows)
    # Pattern: <selection activeCell="XYZ123" sqref="XYZ123"/>
    xml_str = re.sub(
        r'(<selection[^>]+activeCell=")[^"]+(")',
        r'\g<1>A1\g<2>',
        xml_str
    )
    xml_str = re.sub(
        r'(<selection[^>]+sqref=")[^"]+(")',
        r'\g<1>A1\g<2>',
        xml_str
    )
    
    # 3. Reset topLeftCell in sheetView to A1 (prevents scroll to deleted area)
    xml_str = re.sub(
        r'(<sheetView[^>]+)topLeftCell="[^"]+"',
        r'\g<1>topLeftCell="A1"',
        xml_str
    )
    
    # 4. Remove rows beyond max_row
    def filter_row(match):
        row_num = int(match.group(1))
        if row_num > max_row:
            return ''  # Remove entire row
        return match.group(0)  # Keep row as-is
    
    # Match entire row elements
    xml_str = re.sub(
        r'<row[^>]+r="(\d+)"[^>]*>.*?</row>',
        filter_row,
        xml_str,
        flags=re.DOTALL
    )
    
    # Also handle self-closing rows: <row r="123" ... />
    xml_str = re.sub(
        r'<row[^>]+r="(\d+)"[^/]*/>\s*',
        filter_row,
        xml_str
    )
    
    # 5. Update <cols> section if present - truncate max column
    def update_col(match):
        full_match = match.group(0)
        col_min = int(match.group(1))
        col_max = int(match.group(2))
        
        if col_min > max_col:
            return ''  # Remove column definition entirely
        elif col_max > max_col:
            # Truncate max
            return re.sub(r'max="\d+"', f'max="{max_col}"', full_match)
        return full_match
    
    xml_str = re.sub(
        r'<col[^>]+min="(\d+)"[^>]+max="(\d+)"[^>]*/?>',
        update_col,
        xml_str
    )
    
    # 6. Clean up any double whitespace/newlines left by removals
    xml_str = re.sub(r'\n\s*\n', '\n', xml_str)
    
    return xml_str.encode('utf-8')


def optimize_xlsx(input_path: Path, output_path: Path, sheets_stats: List[dict], 
                  verbose: bool = False, quiet: bool = False) -> bool:
    """
    Create optimized xlsx by modifying XML directly.
    Memory efficient - processes one file at a time.
    """
    path_to_stats = {s['path']: s for s in sheets_stats}
    
    with ZipFile(input_path, 'r') as zf_in:
        with ZipFile(output_path, 'w', ZIP_DEFLATED) as zf_out:
            for item in zf_in.namelist():
                data = zf_in.read(item)
                
                # Check if this is a sheet that needs optimization
                if item in path_to_stats:
                    stats = path_to_stats[item]
                    if stats['optimized']:
                        if verbose and not quiet:
                            click.echo(f"  Optimizing: {item}")
                        data = optimize_sheet_xml(
                            data, 
                            stats['data_max_row'], 
                            stats['data_max_col']
                        )
                
                # Write to output (preserving original structure)
                zf_out.writestr(item, data)
    
    return True


def find_excel_files(directory: Path) -> list:
    """Find all Excel files in directory."""
    patterns = ["*.xlsx", "*.xlsm"]
    files = []
    for pattern in patterns:
        files.extend(directory.glob(pattern))
    files = [f for f in files if not f.name.startswith("~$")]
    return sorted(files)


def generate_output_path(input_path: Path, suffix: str) -> Path:
    """Generate output path with suffix."""
    return input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"


@click.command()
@click.argument("input_file", type=click.Path(exists=False), required=False)
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option("-i", "--inplace", is_flag=True, help="Overwrite original file")
@click.option("-n", "--dry-run", is_flag=True, help="Analyze only, don't save")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("-q", "--quiet", is_flag=True, help="Minimal output")
@click.option("-s", "--suffix", default="_slim", help="Output file suffix (default: _slim)")
@click.version_option(__version__, prog_name="xlsxslim")
def main(
    input_file: Optional[str],
    output: Optional[str],
    inplace: bool,
    dry_run: bool,
    verbose: bool,
    quiet: bool,
    suffix: str,
):
    """
    Reduce Excel file size by removing empty rows and columns.
    
    Uses direct XML manipulation - memory efficient for ANY file size.
    
    \b
    Examples:
        xlsxslim                     # Auto-detect single xlsx
        xlsxslim report.xlsx         # Optimize specific file
        xlsxslim report.xlsx -i      # Overwrite original
        xlsxslim report.xlsx -n      # Analyze only (dry run)
    """
    if not quiet:
        click.echo(f"xlsxslim v{__version__}\n")
    
    # Determine input file
    if input_file:
        input_path = Path(input_file)
        if not input_path.exists():
            click.echo(f"Error: File not found: {input_file}", err=True)
            sys.exit(EXIT_FILE_NOT_FOUND)
    else:
        cwd = Path.cwd()
        excel_files = find_excel_files(cwd)
        
        if len(excel_files) == 0:
            click.echo("Error: No Excel files found in current directory", err=True)
            sys.exit(EXIT_FILE_NOT_FOUND)
        elif len(excel_files) > 1:
            click.echo("Error: Multiple Excel files found:", err=True)
            for f in excel_files:
                click.echo(f"  - {f.name}", err=True)
            click.echo("\nPlease specify a file explicitly.", err=True)
            sys.exit(EXIT_MULTIPLE_FILES)
        else:
            input_path = excel_files[0]
            if not quiet:
                click.echo(f"Auto-detected: {input_path.name}\n")
    
    # Determine output path
    if output:
        output_path = Path(output)
    elif inplace:
        output_path = input_path
    else:
        output_path = generate_output_path(input_path, suffix)
    
    input_size = input_path.stat().st_size
    
    if not quiet:
        click.echo(f"Input:  {input_path.name} ({format_size(input_size)})")
        if HAS_PSUTIL:
            print_memory_info(quiet)
        click.echo()
        click.echo("Analyzing...")
        click.echo()
    
    # Analyze sheets
    try:
        with ZipFile(input_path, 'r') as zf:
            sheet_paths = get_sheet_paths(zf)
            
            sheets_stats = []
            for name, path in sheet_paths.items():
                stats = analyze_sheet_xml(zf, path)
                stats['name'] = name
                sheets_stats.append(stats)
    except Exception as e:
        click.echo(f"Error: Failed to analyze file: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(EXIT_IO_ERROR)
    
    if not quiet:
        click.echo(f"Sheets: {len(sheets_stats)}\n")
    
    # Print stats
    any_optimized = False
    total_rows_deleted = 0
    total_cols_deleted = 0
    
    for stats in sheets_stats:
        if stats.get("optimized"):
            any_optimized = True
        
        total_rows_deleted += stats.get("rows_deleted", 0)
        total_cols_deleted += stats.get("cols_deleted", 0)
        
        if not quiet:
            click.echo(f'Sheet "{stats["name"]}":')
            
            if verbose or stats.get("rows_deleted", 0) > 0 or stats.get("cols_deleted", 0) > 0:
                click.echo(f'  Used range:  {stats["original_range"]} → {stats["new_range"]}')
                
                if stats.get("rows_deleted", 0) > 0:
                    click.echo(
                        f'  Rows:        {stats["original_max_row"]:,} → '
                        f'{stats["data_max_row"]:,} '
                        f'(-{stats["rows_deleted"]:,})'
                    )
                
                if stats.get("cols_deleted", 0) > 0:
                    click.echo(
                        f'  Columns:     {stats["original_max_col"]:,} → '
                        f'{stats["data_max_col"]:,} '
                        f'(-{stats["cols_deleted"]:,})'
                    )
            else:
                click.echo("  Already optimized")
            
            click.echo()
    
    if verbose and HAS_PSUTIL:
        print_memory_info(quiet)
        click.echo()
    
    if not any_optimized:
        if not quiet:
            click.echo("File is already optimized. No changes needed.")
        sys.exit(EXIT_ALREADY_OPTIMIZED)
    
    if dry_run:
        if not quiet:
            click.echo("Dry run - no changes saved.")
            click.echo(f"\nWould delete {total_rows_deleted:,} rows and {total_cols_deleted:,} columns.")
        sys.exit(EXIT_SUCCESS)
    
    if not quiet:
        click.echo("Optimizing...")
    
    try:
        if inplace:
            temp_path = input_path.with_suffix('.tmp.xlsx')
            optimize_xlsx(input_path, temp_path, sheets_stats, verbose, quiet)
            temp_path.replace(input_path)
        else:
            optimize_xlsx(input_path, output_path, sheets_stats, verbose, quiet)
    except Exception as e:
        click.echo(f"Error: Failed to save file: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(EXIT_IO_ERROR)
    
    gc.collect()
    
    output_size = output_path.stat().st_size
    saved_bytes = input_size - output_size
    saved_percent = (saved_bytes / input_size * 100) if input_size > 0 else 0
    
    if not quiet:
        click.echo()
        click.echo(f"Output: {output_path.name} ({format_size(output_size)})")
        click.echo(f"Saved:  {format_size(saved_bytes)} ({saved_percent:.1f}%)")
        if HAS_PSUTIL:
            print_memory_info(quiet)
    elif saved_bytes > 0:
        click.echo(f"{output_path.name}: {format_size(saved_bytes)} saved ({saved_percent:.1f}%)")
    
    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
