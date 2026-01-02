#!/usr/bin/env python3
"""CLI tool to generate directory structures from text files."""

import re
from pathlib import Path
from typing import Iterator
import click


def detect_indent_size(lines: list[str]) -> int:
    """Detect the indentation size used in the file."""
    indents = []
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        if any(c in line for c in '│├└─'):
            continue
        
        stripped = line.lstrip()
        if stripped and line[0] == ' ':
            indent = len(line) - len(stripped)
            if indent > 0:
                indents.append(indent)
    
    if not indents:
        return 4
    
    from math import gcd
    from functools import reduce
    return reduce(gcd, indents)


def parse_tree_line(line: str) -> tuple[str, int]:
    """Parse a tree-format line and return (name, depth).
    
    Depth is calculated by counting tree structure groups:
    ├── item       -> depth 1
    │   ├── sub    -> depth 2 (one │ group + one ├)
    │   │   └── x  -> depth 3 (two │ groups + one └)
    """
    # Split by branch characters to get prefix and name
    match = re.match(r'^((?:[│\s]*[├└]─+\s+)|(?:[│\s]+))', line)
    
    if not match:
        # No tree characters, probably root
        return line.strip(), 0
    
    prefix = match.group(1)
    name = line[len(prefix):].strip()
    
    # Count depth by counting vertical bars and branch chars
    # Each │ followed by spaces is one level, final ├ or └ is the item level
    depth = prefix.count('│') + prefix.count('├') + prefix.count('└')
    
    return name, depth


def parse_structure(lines: Iterator[str]) -> list[tuple[int, str, bool]]:
    """Parse text (plain or tree format) into (depth, name, is_file) tuples."""
    lines_list = list(lines)
    items = []
    
    # Check if it's tree format
    has_tree_chars = any(any(c in line for c in '│├└─') for line in lines_list)
    
    if not has_tree_chars:
        indent_size = detect_indent_size(lines_list)
    
    for line in lines_list:
        if not line.strip() or line.strip().startswith('#'):
            continue
        
        # Skip pure connector lines (only │ and whitespace)
        if re.match(r'^[│\s]*$', line):
            continue
        
        if has_tree_chars:
            # Check if line has actual tree branch characters
            if any(c in line for c in '├└'):
                name, depth = parse_tree_line(line)
            else:
                # Root level item (no tree chars)
                name = line.strip()
                depth = 0
        else:
            # Plain indented format
            leading_spaces = len(line) - len(line.lstrip())
            depth = leading_spaces // indent_size
            name = line.strip()
        
        if not name:
            continue
            
        is_file = not name.endswith('/')
        name = name.rstrip('/')
        
        if name:
            items.append((depth, name, is_file))
    
    return items


def create_structure(base: Path, items: list[tuple[int, str, bool]]) -> None:
    """Create directories and files from parsed structure."""
    if not items:
        return
    
    min_depth = min(d for d, _, _ in items)
    items = [(d - min_depth, n, f) for d, n, f in items]
    
    path_stack = [base]
    
    for depth, name, is_file in items:
        path_stack = path_stack[:depth + 1]
        
        current_path = path_stack[-1] / name
        
        if is_file:
            current_path.parent.mkdir(parents=True, exist_ok=True)
            current_path.touch()
        else:
            current_path.mkdir(parents=True, exist_ok=True)
            path_stack.append(current_path)


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('-o', '--output', type=click.Path(path_type=Path), 
              help='Output directory (default: current directory)')
@click.option('-d', '--dry-run', is_flag=True, 
              help='Show what would be created without creating it')
def main(input_file: Path, output: Path | None, dry_run: bool) -> None:
    """Generate directory structure from text file.
    
    Supports both plain indented format and tree format with │├└─ characters.
    Auto-detects indent size (2 spaces, 4 spaces, tabs, etc.)
    
    Format:
      - Directories end with /
      - Files don't end with /
      - Indentation or tree chars define nesting
      - Lines starting with # are ignored
    """
    output = output or Path.cwd()
    
    with input_file.open(encoding='utf-8') as f:
        items = parse_structure(f)
    
    if not items:
        click.echo("No valid structure found in file")
        return
    
    if dry_run:
        click.echo(f"Would create in {output}:")
        for depth, name, is_file in items:
            indent = "  " * depth
            icon = "📄" if is_file else "📁"
            click.echo(f"{indent}{icon} {name}")
    else:
        create_structure(output, items)
        click.echo(f"✓ Created structure in {output}")


if __name__ == '__main__':
    main()
