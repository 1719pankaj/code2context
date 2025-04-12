# Contributing to Code Extractor

Thank you for your interest in contributing to Code Extractor! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Guidelines](#development-guidelines)
  - [Adding New Configuration Types](#adding-new-configuration-types)
  - [Adding Support for New Languages](#adding-support-for-new-languages)
  - [Improving Exclusion Patterns](#improving-exclusion-patterns)
  - [GUI Enhancements](#gui-enhancements)
- [Internal Architecture](#internal-architecture)
  - [Core Components](#core-components)
  - [Configuration Processing](#configuration-processing)
  - [File Collection Logic](#file-collection-logic)
  - [Markdown Generation](#markdown-generation)
  - [GUI Architecture](#gui-architecture)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

Please be respectful and inclusive in all interactions within this project community. We aim to foster an open and welcoming environment.

## How to Contribute

### Reporting Bugs

If you find a bug:

1. Check the [Issues](https://github.com/yourusername/code-extractor/issues) to see if it's already reported
2. If not, create a new issue with:
   - A clear title and description
   - Steps to reproduce the issue
   - Expected behavior and what actually happened
   - Your environment (OS, Python version, etc.)
   - Whether the issue occurs in GUI mode, CLI mode, or both

### Suggesting Enhancements

Have an idea to improve Code Extractor?

1. Check if it's already suggested in [Issues](https://github.com/yourusername/code-extractor/issues)
2. If not, create a new issue labeled as "enhancement" with:
   - A clear description of your proposed feature
   - The problem it solves
   - Any implementation ideas you have
   - Whether it affects the GUI, CLI, or both

### Pull Requests

1. Fork the repository
2. Create a branch from `main` with a descriptive name
3. Make your changes
4. Run tests if applicable
5. Submit a pull request:
   - Reference any related issues
   - Describe your changes and the problem they solve
   - Mention any breaking changes

## Development Guidelines

### Adding New Configuration Types

To add a new project type configuration (e.g., Python, Ruby, etc.):

1. Create a new config file named `{type}_extract.config` (e.g., `python_extract.config`) in the `configs/` directory
2. Structure your configuration following this template:

```ini
[global]
excluded_dirs = directory1, directory2
excluded_files = pattern1, pattern2

[directory_path1]
extensions = .ext1, .ext2
include_subdirs = true
excluded_dirs = special_dir1, special_dir2
excluded_files = special_pattern1, special_pattern2

[directory_path2]
extensions = .ext3, .ext4
include_subdirs = false

[specific_files]
files = file1.ext, path/to/file2.ext
```

3. Add typical excluded directories and files for the project type in the `[global]` section
4. Define directory sections with appropriate extensions and exclusion rules
5. Add common config files to the `[specific_files]` section
6. Test your configuration with a sample project (using both GUI and CLI modes)
7. Document your new configuration in the README.md

Example for Python projects:

```ini
[global]
excluded_dirs = venv, __pycache__, .pytest_cache, .coverage, dist, build, .eggs
excluded_files = *.pyc, *.pyo, .DS_Store

[.]
extensions = .py, .pyw, .pyx, .pxi, .pxd
include_subdirs = true
excluded_dirs = tests

[src]
extensions = .py, .pyw, .pyx, .pxi, .pxd
include_subdirs = true

[specific_files]
files = setup.py, requirements.txt, pyproject.toml, setup.cfg, .flake8, pytest.ini
```

### Adding Support for New Languages

To add syntax highlighting support for new file types:

1. Open `main.py`
2. Find the `get_language_by_extension()` function
3. Add your new extension mapping to the `language_map` dictionary:

```python
def get_language_by_extension(extension):
    language_map = {
        # Existing mappings...
        '.py': 'python',
        '.pyw': 'python',
        '.rb': 'ruby',
        '.go': 'go',
        # Your new extension
        '.rs': 'rust',
    }
    return language_map.get(extension, 'text')
```

Make sure to use the correct language identifier for markdown syntax highlighting.

### Improving Exclusion Patterns

The current pattern matching supports:
- Exact matches
- Prefix matching with trailing asterisk (`prefix*`)
- Suffix matching with leading asterisk (`*suffix`)

To add more complex patterns:

1. Modify the pattern matching logic in the `collect_files_from_dir()` function
2. Consider adding support for glob patterns or regular expressions
3. Update the documentation to reflect the new capabilities

### GUI Enhancements

When modifying the GUI:

1. Use Tkinter's standard widgets and follow their design patterns
2. Keep the interface intuitive and user-friendly
3. For long-running operations, use threading to avoid freezing the UI
4. Update status messages to keep users informed of progress
5. Add tooltips or help text for complex features
6. Ensure all actions have clear visual feedback
7. Keep the design responsive to different window sizes

## Internal Architecture

For those interested in modifying the core functionality, here's how Code Extractor works internally.

### Core Components

The main script (`main.py`) consists of several key components:

1. **Argument Parsing**: Uses `argparse` to handle command-line arguments
2. **Configuration Parsing**: Uses `configparser` to read and parse config files
3. **File Collection**: Finds and filters files based on configuration rules
4. **Content Extraction**: Reads file contents
5. **Markdown Generation**: Creates formatted markdown output
6. **Graphical User Interface**: Implements a user-friendly UI using Tkinter

### Configuration Processing

Configuration files (.config) use the INI format. The processing flow:

1. The script searches for config files in the `configs/` directory, then falls back to the script directory
2. It parses global exclusions (applied to all sections)
3. For each directory section, it:
   - Resolves the full path
   - Determines which extensions to collect
   - Combines global and section-specific exclusions
4. Special handling for `specific_files` section to include individual files

The `parse_list_from_config()` function handles both comma-separated and newline-separated lists for flexibility.

### File Collection Logic

The `collect_files_from_dir()` function is responsible for gathering files that match criteria:

1. It either scans a single directory or walks the directory tree recursively
2. For each file, it checks:
   - If the extension matches those specified
   - If the file matches any exclusion pattern
   - If the directory is in the excluded list
3. Pattern matching uses three approaches:
   - Exact match: `filename.ext`
   - Prefix match: `prefix*` matches anything starting with "prefix"
   - Suffix match: `*suffix` matches anything ending with "suffix"

This is the logical flow of the exclusion check:
```python
if any(file == excluded_file or
       (excluded_file.startswith('*') and file.endswith(excluded_file[1:])) or
       (excluded_file.endswith('*') and file.startswith(excluded_file[:-1])) for excluded_file in excluded_files):
    continue
```

### Markdown Generation

The `create_markdown_content()` function builds the output markdown:

1. Creates a header with title and timestamp
2. For each file:
   - Determines the appropriate language for syntax highlighting
   - Creates a section heading with the relative file path
   - Includes the file content in a code block with language specifier
3. Handles encoding issues with the `errors='replace'` parameter

### GUI Architecture

The GUI is implemented through the `CodeExtractorUI` class:

1. **Initialization**: Sets up the main window, frames, and controls
2. **Directory Selection**: Allows browsing for the project directory
3. **Config Selection**: Populates a dropdown with available configs
4. **File Scanning**: Executes in a separate thread to avoid UI freezing
5. **File Display**: Shows checkboxes for each discovered file
6. **File Selection**: Provides buttons to select, deselect, or toggle files
7. **Extraction**: Generates markdown content in a separate thread
8. **Status Updates**: Shows progress and results in a status bar

The UI follows the Model-View-Controller pattern:
- **Model**: File data and configuration information
- **View**: Tkinter widgets and layout
- **Controller**: Event handlers and processing logic

Threading is used for potentially long-running operations to maintain UI responsiveness.

## Testing

When contributing changes:

1. Test your changes with at least one real project
2. Ensure the output markdown is correctly formatted
3. Verify that file collection works as expected with your changes
4. If modifying the GUI, test on different operating systems if possible
5. Check both GUI and CLI modes to ensure neither is broken

## Documentation

When making changes, please update:

1. The main `README.md` for user-facing changes
2. `Documentation.md` for detailed functionality changes
3. Comments in the code for implementation details
4. This `CONTRIBUTING.md` file if contribution process changes
5. Include information about GUI-specific changes if applicable
