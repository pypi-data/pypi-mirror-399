
# txt2dir

Much of my workflow nowadays requires brainstorming and using LLMs to decide on project architecture and file structure. The final output is usually a textfile with a tree diagram for the project skeleton. This tool automates that workflow by turning those textfiles into actual directory structures.

This project also serves as my introduction to the process of turning Python projects into pip packages and working with build tools.

## Install

```bash
pip install txt2dir
```

Or install from source:
```bash
git clone https://github.com/Sycritz/txt2dir
cd txt2dir
pip install -e .
```

## Usage

```bash
txt2dir project_structure.txt -o ~/projects/new_project
```

Options:
- `-o, --output`: Specify output directory (defaults to current directory)
- `-d, --dry-run`: Preview what would be created without actually creating it

## Supported Formats

### Simple Indented Format

Uses indentation to define hierarchy. Directories end with `/`, files don't.

```
myproject/
  src/
    __init__.py
    main.py
    utils/
      __init__.py
      helpers.py
  tests/
    test_main.py
  README.md
  requirements.txt
```

The tool auto-detects indent size (2 spaces, 4 spaces, tabs, etc.) so you don't need to worry about consistency.

### Tree Format

Supports the standard tree diagram format with box-drawing characters.

```
project/
├── README.md
├── src/
│   ├── main.py
│   └── utils/
│       └── helpers.py
└── tests/
    └── test_main.py
```

Both formats can be mixed - use whatever your LLM outputs or whatever you prefer to write by hand.

## Features

- Auto-detects indentation size
- Handles both simple and tree diagram formats
- Creates nested directory structures
- Generates empty files with proper paths
- Dry-run mode to preview before creating
- Ignores comment lines (starting with `#`)

## Examples

Preview structure without creating:
```bash
txt2dir structure.txt -d
```

Create in specific directory:
```bash
txt2dir structure.txt -o ~/workspace/new-project
```

Create in current directory:
```bash
txt2dir structure.txt
```

## Notes

Lines starting with `#` are treated as comments and ignored. Empty lines are also ignored.

Directories must end with `/` to be recognized as directories. Everything else is treated as a file.
