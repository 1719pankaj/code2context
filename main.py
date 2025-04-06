import os
import argparse
import datetime
import configparser

def collect_files_from_dir(directory, extensions, include_subdirs, excluded_dirs=None, excluded_files=None):
    """
    Collect files with specified extensions, respecting exclusion patterns
    """
    if excluded_dirs is None:
        excluded_dirs = []
    if excluded_files is None:
        excluded_files = []

    # Convert excluded_dirs to absolute paths for more reliable comparison
    abs_excluded_dirs = [os.path.abspath(os.path.join(directory, d)) for d in excluded_dirs]

    file_paths = []
    if include_subdirs:
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            abs_root = os.path.abspath(root)
            if any(abs_root == d or abs_root.startswith(d + os.sep) for d in abs_excluded_dirs):
                continue

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    # Check if file matches any exclusion pattern
                    if any(file == excluded_file or
                           (excluded_file.startswith('*') and file.endswith(excluded_file[1:])) or
                           (excluded_file.endswith('*') and file.startswith(excluded_file[:-1])) for excluded_file in excluded_files):
                        continue

                    file_paths.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and any(file.endswith(ext) for ext in extensions):
                # Check exclusion patterns
                if any(file == excluded_file or
                       (excluded_file.startswith('*') and file.endswith(excluded_file[1:])) or
                       (excluded_file.endswith('*') and file.startswith(excluded_file[:-1])) for excluded_file in excluded_files):
                    continue

                file_paths.append(file_path)
    return file_paths

def create_markdown_content(file_paths, base_directory):
    markdown_content = f"# Project Code Collection\n\n"
    markdown_content += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    for file_path in sorted(file_paths):
        try:
            # Determine language for syntax highlighting
            file_ext = os.path.splitext(file_path)[1].lower()
            lang = get_language_by_extension(file_ext)

            relative_path = os.path.relpath(file_path, base_directory)
            markdown_content += f"## {relative_path}\n\n"
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
                markdown_content += f"```{lang}\n{content}\n```\n\n"
        except Exception as e:
            markdown_content += f"Error reading {file_path}: {str(e)}\n\n"
    return markdown_content

def get_language_by_extension(extension):
    language_map = {
        '.kt': 'kotlin',
        '.java': 'java',
        '.cpp': 'cpp',
        '.h': 'cpp',
        '.xml': 'xml',
        '.json': 'json',
        '.mjs': 'javascript',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.config': 'ini',
        '.tsx': 'tsx',
        '.ts': 'typescript',
        '.jsx': 'jsx',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
    }
    return language_map.get(extension, 'text')

def parse_list_from_config(config_text):
    """Parse a comma or newline separated list from config"""
    if not config_text:
        return []
    if ',' in config_text:
        return [item.strip() for item in config_text.split(',') if item.strip()]
    return [item.strip() for item in config_text.split('\n') if item.strip()]

def ensure_directory_exists(file_path):
    """Ensure directory exists for the given file path"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def find_config_file(config_name):
    """
    Find the configuration file by searching in the following locations:
    1. configs/ directory relative to the script
    2. Current script directory
    """
    # Define the config filename
    if not config_name.endswith('_extract.config') and not config_name.endswith('.config'):
        config_filename = f"{config_name}_extract.config"
    else:
        config_filename = config_name if config_name.endswith('.config') else f"{config_name}.config"

    # Search paths: configs/ directory first, then script directory
    script_dir = os.path.dirname(__file__)
    configs_dir = os.path.join(script_dir, "configs")

    search_paths = [
        os.path.join(configs_dir, config_filename),  # configs/xxx_extract.config
        os.path.join(script_dir, config_filename)    # ./xxx_extract.config (fallback)
    ]

    for path in search_paths:
        if os.path.exists(path):
            return path

    return None

def main():
    parser = argparse.ArgumentParser(description='Collect code based on config file and save as markdown.')
    parser.add_argument('directory', help='Base directory of the project')
    parser.add_argument('-c', '--config', help='Config type to use (e.g., android, web)', default='extract')
    parser.add_argument('-o', '--output', help='Output file path (default: code_collection.txt)')

    args = parser.parse_args()

    # Find the configuration file
    config_path = find_config_file(args.config)
    if not config_path:
        print(f"Error: Config file for '{args.config}' not found in 'configs/' directory or script directory.")
        return

    config = configparser.ConfigParser()
    config.read(config_path)

    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' not found.")
        return

    # Set output path - determine if we need to use Extracts folder
    if args.output:
        # Check if the output is just a filename or a path with directories
        if os.path.dirname(args.output):
            # User specified a path with directories
            output_path = args.output
        else:
            # User specified only a filename, place it in Extracts folder
            output_path = os.path.join("Extracts", args.output)
    else:
        # No output specified, use default in Extracts folder
        filename = f"{args.config}_collection.md"
        output_path = os.path.join("Extracts", filename)

    # Make sure the output directory exists
    ensure_directory_exists(output_path)

    print(f"Using config: {os.path.basename(config_path)}")
    print(f"Scanning base directory: {args.directory}")
    print(f"Output will be saved to: {output_path}")

    # Parse global exclusions if present
    global_excluded_dirs = []
    global_excluded_files = []

    if 'global' in config:
        if 'excluded_dirs' in config['global']:
            global_excluded_dirs = parse_list_from_config(config['global']['excluded_dirs'])
            print(f"Global excluded directories: {global_excluded_dirs}")

        if 'excluded_files' in config['global']:
            global_excluded_files = parse_list_from_config(config['global']['excluded_files'])
            print(f"Global excluded files: {global_excluded_files}")

    file_paths = []

    for section in config.sections():
        if section in ['specific_files', 'global']:
            continue  # Handle these sections separately

        # Handle relative directories from the base
        dir_path = os.path.join(args.directory, section)
        if not os.path.exists(dir_path):
            print(f"Warning: Directory '{dir_path}' does not exist. Skipping...")
            continue

        # Parse section-specific configurations
        extensions = parse_list_from_config(config.get(section, 'extensions'))
        extensions = [f'.{ext}' if not ext.startswith('.') else ext for ext in extensions]
        include_subdirs = config.getboolean(section, 'include_subdirs', fallback=True)

        # Section-specific exclusions combine with global exclusions
        excluded_dirs = global_excluded_dirs.copy()
        excluded_files = global_excluded_files.copy()

        if 'excluded_dirs' in config[section]:
            section_excluded_dirs = parse_list_from_config(config[section]['excluded_dirs'])
            excluded_dirs.extend(section_excluded_dirs)

        if 'excluded_files' in config[section]:
            section_excluded_files = parse_list_from_config(config[section]['excluded_files'])
            excluded_files.extend(section_excluded_files)

        collected = collect_files_from_dir(
            dir_path,
            extensions,
            include_subdirs,
            excluded_dirs,
            excluded_files
        )
        file_paths.extend(collected)
        print(f"Found {len(collected)} files in {dir_path}")

    # Handle specific files
    if 'specific_files' in config.sections():
        specific_files_text = config.get('specific_files', 'files')
        specific_files = parse_list_from_config(specific_files_text)

        # Process the specific files
        for specific_file in specific_files:
            full_path = os.path.join(args.directory, specific_file)
            if os.path.isfile(full_path):
                # Check if this file is excluded globally
                filename = os.path.basename(specific_file)
                if any(filename == excluded_file or
                       (excluded_file.startswith('*') and filename.endswith(excluded_file[1:])) or
                       (excluded_file.endswith('*') and filename.startswith(excluded_file[:-1]))
                       for excluded_file in global_excluded_files):
                    print(f"Skipping excluded specific file: {specific_file}")
                    continue

                if full_path not in file_paths:
                    file_paths.append(full_path)
                print(f"Added specific file: {specific_file}")
            else:
                print(f"Warning: Specific file '{specific_file}' not found. Skipping...")

    if not file_paths:
        print("No matching files found. Exiting.")
        return

    markdown_content = create_markdown_content(file_paths, args.directory)

    # Ensure the output directory exists before writing
    ensure_directory_exists(output_path)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(markdown_content)

    print(f"Successfully wrote content to {output_path}")
    print(f"Total size: {len(markdown_content):,} characters")

    # Generate files.txt in the current directory
    files_txt_path = "files.txt"
    file_names = [os.path.relpath(file, args.directory) for file in file_paths]

    with open(files_txt_path, 'w') as f:
        for name in file_names:
            f.write(f"{name}\n")
    print(f"Generated {files_txt_path} listing all extracted files.")

if __name__ == "__main__":
    main()
