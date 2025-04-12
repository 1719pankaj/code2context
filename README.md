![Logo](https://github.com/1719pankaj/Utilities/blob/main/Code2Context_Logo.jpg)

A simple yet powerful tool for extracting code files from projects and combining them into a single Markdown document - perfect for feeding code context into LLMs!

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

Code Extractor scans your project directories, collecting files based on configurable rules, and compiles them into a single, well-formatted Markdown document with proper syntax highlighting. This makes it ideal for:

- Creating comprehensive context for LLM prompts
- Generating code documentation
- Sharing code snippets with collaborators
- Creating code samples for tutorials

## Quick Start

### Installation

No dependencies beyond standard Python libraries:

```bash
# Clone the repository
git clone https://github.com/yourusername/code-extractor.git
cd code-extractor

# Ready to use!
python main.py /path/to/your/project
```

### Basic Usage

**Graphical User Interface (GUI)**:
```bash
# Launch with the GUI
python main.py -ui
```

**Command Line Interface (CLI)**:
```bash
# For web projects
python main.py /path/to/web/project -c web

# For Android projects
python main.py /path/to/android/project -c android

# Custom output file
python main.py /path/to/project -c web -o my-context-file.md
```

The extracted code will be saved to an `Extracts` folder by default (automatically created if needed).

## Features at a Glance

- **User-friendly GUI** for interactive file selection and extraction
- **Battery-included configurations** for web and Android projects
- **Flexible file selection** based on directories, extensions, and patterns
- **Markdown output** with proper syntax highlighting
- **Exclusion filters** for node_modules, build directories, and more
- **Specific file inclusion** regardless of other rules
- **Files list generation** for quick reference

## Project Structure

```
code-extractor/
├── main.py              # Main script with CLI and GUI functionality
├── configs/             # Directory for configuration files
│   ├── web_extract.config
│   ├── android_extract.config
│   └── ...              # Your custom configurations
├── Extracts/            # Generated output (created when needed)
│   └── ...
├── README.md
├── CONTRIBUTING.md
└── Documentation.md
```

## Using the GUI

1. Launch the application with the `-ui` flag
2. Select your project directory using the "Browse..." button
3. Choose a configuration from the dropdown
4. Click "Scan Files" to analyze your project
5. Select/deselect files for extraction using the checkboxes
6. Enter an output filename (or use the default)
7. Click "Extract Selected Files" to generate the markdown document

## Example: Using with LLMs

When using the output with LLMs like Claude, GPT-4, or others:

1. Run the extractor on your project (using GUI or CLI)
2. Upload the generated Markdown file to your LLM interface
3. Ask questions about your codebase with full context!

```
"Here's my project code. Can you explain how the authentication flow works?"
```

## Included Configurations

- **Web Projects**: Configured for JavaScript, TypeScript, React, HTML, CSS, etc.
- **Android Projects**: Configured for Kotlin, Java, XML layouts, etc.

## Contributing

We welcome contributions! Whether it's adding new configurations for different project types (Python, Rust, Go, etc.), improving existing ones, or enhancing the core functionality.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.

## Documentation

For more detailed information on configuration options, custom setups, and advanced usage, see [Documentation.md](Documentation.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
