# Code Extractor Documentation

## Overview

This Python utility extracts and collects code files from projects based on configurable rules, creating a consolidated Markdown document with syntax-highlighted code blocks. It's designed to help developers create organized documentation from their codebase, prepare code for sharing, or generate reports.

## Features

- Graphical user interface for intuitive operation
- Command-line interface for scripting and automation
- Flexible configuration through INI-style config files
- Support for different project types (web, Android, or custom configurations)
- File filtering by extension and directory
- Exclusion patterns for files and directories
- Support for specific file inclusion
- Markdown output with syntax highlighting
- Generation of file lists

## Installation

No special installation is required beyond standard Python libraries:
- os
- argparse
- datetime
- configparser
- tkinter (standard in most Python installations)
- threading

## Usage

### Graphical User Interface (GUI)

To launch the GUI:

```bash
python main.py -ui
```

The GUI provides a user-friendly way to:
1. Select a project directory
2. Choose a configuration
3. Scan files based on the configuration
4. Select/deselect specific files
5. Generate the output Markdown document

### Command Line Interface (CLI)

```bash
python main.py <directory> [-c CONFIG] [-o OUTPUT]
```

#### Arguments

- `directory`: Base directory of the project to scan (required in CLI mode)
- `-c`, `--config`: Configuration type to use (default: "extract")
- `-o`, `--output`: Output file path (default: "Extracts/{config}_collection.md")
- `-ui`, `--ui`: Launch with graphical user interface

## GUI Interface Guide

### Main Components

1. **Project Directory**: Select the root directory of your project
2. **Configuration**: Choose from available configuration files
3. **File Selection**: After scanning, select which files to include
4. **Output File**: Specify the output filename
5. **Control Buttons**: Scan files, select/deselect all, and extract code

### Step-by-Step Usage

1. **Launch the Application**: Run `python main.py -ui`
2. **Select Project Directory**: Click "Browse..." to select your project folder
3. **Choose Configuration**: Select the appropriate preset (web, android, etc.)
4. **Scan Files**: Click "Scan Files" to analyze your project
5. **Review and Select Files**: Use checkboxes to select which files to include
   - "Select All", "Deselect All", and "Toggle Selection" buttons help with file selection
6. **Set Output Filename**: Enter a name for the output file
7. **Extract Code**: Click "Extract Selected Files" to generate the Markdown document
8. **Check Results**: The status bar will show the extraction results

## Configuration Files

Configuration files use the INI format with sections representing directories and their scan rules.

### Location of Configuration Files

Configuration files are searched for in the following order:
1. `configs/` directory (relative to the script)
2. The same directory as the script (for backward compatibility)

### Naming Convention

Configuration files follow the naming pattern: `{config_type}_extract.config`

Example:
- `configs/web_extract.config` - for web projects
- `configs/android_extract.config` - for Android projects
- `configs/custom_extract.config` - for custom project types

### Configuration Structure

#### Global Section

The `global` section defines exclusion rules that apply to all directories:

```ini
[global]
excluded_dirs = node_modules, .git, dist, build, coverage
excluded_files = *.min.js, *.min.css, package-lock.json, yarn.lock
```

#### Directory Sections

Each section (except `global` and `specific_files`) represents a directory to scan, relative to the base directory. An empty section name (`.`) refers to the base directory itself.

```ini
[directory_path]
extensions = .ext1, .ext2, .ext3
include_subdirs = true|false
excluded_dirs = dir1, dir2
excluded_files = file1, file2, *pattern1, pattern2*
```

- `extensions`: File extensions to include (with or without leading dot)
- `include_subdirs`: Whether to scan subdirectories recursively (default: true)
- `excluded_dirs`: Directories to skip (in addition to global exclusions)
- `excluded_files`: Files to skip (in addition to global exclusions)

#### Specific Files Section

The `specific_files` section allows explicitly including specific files regardless of other rules:

```ini
[specific_files]
files = file1.ext, path/to/file2.ext
```

### Exclusion Pattern Formats

- Exact name: `filename.ext`
- Prefix match: `prefix*` (matches any file starting with "prefix")
- Suffix match: `*suffix` (matches any file ending with "suffix")

## Output

### Markdown File

The tool generates a Markdown file with:
- Title and timestamp
- Each file as a section with a heading showing its relative path
- Code blocks with appropriate syntax highlighting based on file extension

Example output:
```markdown
# Project Code Collection

Generated on: 2025-04-12 12:34:56

## path/to/file1.js

```javascript
// File content here
function example() {
  return "Hello world";
}
```

## path/to/file2.css

```css
/* File content here */
body {
  margin: 0;
  padding: 0;
}
```
```

### Files List

The tool also generates a `files.txt` file in the current directory listing all extracted files (using paths relative to the base directory).

## Example Configurations

### Web Project Configuration

```ini
[global]
excluded_dirs = node_modules, .git, dist, build, coverage, .next
excluded_files = *.min.js, *.min.css, package-lock.json, yarn.lock

[.]
extensions = .json, .mjs, .yaml, .yml, .config, .tsx, .ts, .jsx, .js, .html, .css
include_subdirs = true
excluded_dirs = test, __tests__, e2e

[src]
extensions = .json, .mjs, .yaml, .yml, .config, .tsx, .ts, .jsx, .js, .html, .css
include_subdirs = true

[public]
extensions = .json, .mjs, .yaml, .yml, .config, .tsx, .ts, .jsx, .js, .html, .css
include_subdirs = true

[config]
extensions = .json, .mjs, .yaml, .yml, .config, .tsx, .ts, .jsx, .js, .html, .css
include_subdirs = true

[specific_files]
files = package.json, tsconfig.json, webpack.config.js, vite.config.js, .eslintrc.json, .prettierrc
```

### Android Project Configuration

```ini
[global]
excluded_dirs = .gradle, build, .idea
excluded_files = *.iml, local.properties

[app/src/main/java/com/example/cpplearner]
extensions = .kt, .java
include_subdirs = true
excluded_dirs = debug

[app/src/main/cpp]
extensions = .cpp, .h, .txt
include_subdirs = false
excluded_files = *.so, *.a

[app/src/main/res/layout]
extensions = .xml
include_subdirs = false

[app/src/main/res/menu]
extensions = .xml
include_subdirs = false

[app/src/main/res/navigation]
extensions = .xml
include_subdirs = false

[app/src/main/res/values]
extensions = .xml
include_subdirs = false
excluded_files = strings.xml

[specific_files]
files = build.gradle.kts, settings.gradle.kts, app/build.gradle.kts, app/src/main/AndroidManifest.xml
```

## Function Reference

### Main Functions

#### `main()`
Entry point that parses arguments and orchestrates the extraction process or launches the GUI.

#### `CodeExtractorUI` Class
The main class that implements the graphical user interface.

#### `find_config_file(config_name)`
Searches for configuration files in the `configs/` directory and falls back to the script directory.

#### `get_available_configs()`
Gets a list of available configuration files from the configs directory and script directory.

#### `collect_files_from_dir(directory, extensions, include_subdirs, excluded_dirs, excluded_files)`
Collects files from a directory based on specified filters.

#### `create_markdown_content(file_paths, base_directory)`
Creates markdown content from collected file paths.

#### `get_language_by_extension(extension)`
Maps file extensions to appropriate language identifiers for syntax highlighting.

### Helper Functions

#### `parse_list_from_config(config_text)`
Parses comma or newline separated lists from config.

#### `ensure_directory_exists(file_path)`
Creates directories as needed for output files.

## Examples

### Basic GUI Usage

```bash
# Launch the GUI
python main.py -ui
```

### Basic CLI Usage

```bash
# Use default web configuration
python main.py /path/to/project -c web

# Use custom configuration
python main.py /path/to/project -c my_custom

# Specify output file
python main.py /path/to/project -c web -o my_web_code.md

# Output to a specific directory
python main.py /path/to/project -c web -o reports/web_code.md
```

### Creating Custom Configurations

1. Create a file named `{your_config}_extract.config` in the `configs/` directory
2. Structure it with appropriate sections and rules
3. In the GUI, select your custom configuration from the dropdown
4. In the CLI, run the script with `-c {your_config}`

## Directory Structure

```
code-extractor/
├── main.py
├── configs/
│   ├── web_extract.config
│   ├── android_extract.config
│   └── ... (your custom configs)
├── Extracts/
│   └── ... (generated output files)
├── README.md
├── CONTRIBUTING.md
└── Documentation.md
```

## Limitations

- Binary files are not supported
- Non-UTF-8 text files may have character encoding issues (though the script attempts to handle this)
- Very large files might cause memory issues as the entire content is loaded into memory
- The GUI might be slower than the CLI for very large projects with many files

## Troubleshooting

- **Config file not found**: Ensure the config file follows the naming convention `{config}_extract.config` and is in the `configs/` directory
- **No files found**: Check your configuration for overly restrictive rules or exclusions
- **Directory not found**: Verify that section names in the config file match existing directories relative to the project root
- **GUI freezes during scan**: For very large projects, the scan might take some time. The threading implementation helps prevent freezing, but patience may be required
- **Checkbox selection issues**: If you have a large number of files, use the "Select All", "Deselect All", or "Toggle Selection" buttons for easier management
