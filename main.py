import os
import argparse
import datetime
import configparser
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading

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

def get_available_configs():
    """Get a list of available configuration files"""
    script_dir = os.path.dirname(__file__)
    configs_dir = os.path.join(script_dir, "configs")

    config_files = []

    # Check configs directory
    if os.path.exists(configs_dir):
        for file in os.listdir(configs_dir):
            if file.endswith('.config'):
                # Extract the config name without extension
                config_name = os.path.splitext(file)[0]
                if config_name.endswith('_extract'):
                    config_name = config_name[:-8]  # Remove _extract suffix
                config_files.append(config_name)

    # Check script directory
    for file in os.listdir(script_dir):
        if file.endswith('.config'):
            config_name = os.path.splitext(file)[0]
            if config_name.endswith('_extract'):
                config_name = config_name[:-8]  # Remove _extract suffix
            if config_name not in config_files:
                config_files.append(config_name)

    return config_files

class CodeExtractorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Extractor")
        self.root.geometry("900x700")

        # Initialize variables
        self.directory_var = tk.StringVar()
        self.config_var = tk.StringVar()
        self.output_var = tk.StringVar(value="code.txt")
        self.status_var = tk.StringVar(value="Ready")

        # Dictionary to store file checkboxes and their variables
        # Key: file path, Value: (BooleanVar, relative path)
        self.file_checkboxes = {}

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Directory selection
        ttk.Label(self.main_frame, text="Project Directory:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(self.main_frame, textvariable=self.directory_var, width=50).grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Button(self.main_frame, text="Browse...", command=self.browse_directory).grid(row=0, column=2, padx=5, pady=5)

        # Config selection
        ttk.Label(self.main_frame, text="Configuration:").grid(row=1, column=0, sticky="w", pady=5)
        self.config_combo = ttk.Combobox(self.main_frame, textvariable=self.config_var, width=30)
        self.config_combo.grid(row=1, column=1, sticky="w", pady=5)
        ttk.Button(self.main_frame, text="Scan Files", command=self.scan_files).grid(row=1, column=2, padx=5, pady=5)

        # File list with checkboxes
        ttk.Label(self.main_frame, text="Select Files to Extract:").grid(row=2, column=0, columnspan=3, sticky="w", pady=5)

        # Create a frame for the file list with scrollbar
        self.file_frame = ttk.Frame(self.main_frame, relief="sunken", borderwidth=1)
        self.file_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=5)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Scrollbars
        self.file_scroll_y = ttk.Scrollbar(self.file_frame, orient=tk.VERTICAL)
        self.file_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_scroll_x = ttk.Scrollbar(self.file_frame, orient=tk.HORIZONTAL)
        self.file_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas for scrolling
        self.file_canvas = tk.Canvas(self.file_frame)
        self.file_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        self.file_scroll_y.config(command=self.file_canvas.yview)
        self.file_scroll_x.config(command=self.file_canvas.xview)
        self.file_canvas.config(yscrollcommand=self.file_scroll_y.set, xscrollcommand=self.file_scroll_x.set)

        # Inner frame for file checkboxes
        self.file_list_frame = ttk.Frame(self.file_canvas)
        self.file_canvas.create_window((0, 0), window=self.file_list_frame, anchor=tk.NW)

        # Selection controls
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)

        ttk.Button(self.controls_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.controls_frame, text="Toggle Selection", command=self.toggle_selection).pack(side=tk.LEFT, padx=5)

        # Output file name
        ttk.Label(self.main_frame, text="Output File:").grid(row=5, column=0, sticky="w", pady=5)
        ttk.Entry(self.main_frame, textvariable=self.output_var).grid(row=5, column=1, sticky="ew", pady=5)

        # Extract button
        ttk.Button(self.main_frame, text="Extract Selected Files", command=self.extract_files).grid(row=6, column=0, columnspan=3, pady=10)

        # Status bar
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=7, column=0, columnspan=3, sticky="ew")

        # Populate the config combobox
        self.populate_configs()

        # Configure the canvas resize
        self.file_list_frame.bind("<Configure>", self.on_frame_configure)
        self.file_canvas.bind("<Configure>", self.on_canvas_configure)

    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Update the inner frame's width to fill the canvas"""
        canvas_width = event.width
        self.file_canvas.itemconfig(1, width=canvas_width)

    def populate_configs(self):
        """Populate the config combobox with available configs"""
        configs = get_available_configs()
        self.config_combo['values'] = configs
        if configs:
            self.config_var.set(configs[0])

    def browse_directory(self):
        """Browse for a directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.directory_var.set(directory)

    def scan_files(self):
        """Scan for files based on selected directory and config"""
        directory = self.directory_var.get()
        config_name = self.config_var.get()

        if not directory:
            messagebox.showwarning("Missing Directory", "Please select a project directory.")
            return

        if not config_name:
            messagebox.showwarning("Missing Config", "Please select a configuration.")
            return

        # Find the config file
        config_path = find_config_file(config_name)
        if not config_path:
            messagebox.showerror("Config Error", f"Config file for '{config_name}' not found.")
            return

        # Clear previous file list
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        self.file_checkboxes.clear()

        # Update status
        self.status_var.set(f"Scanning files with config: {os.path.basename(config_path)}...")
        self.root.update_idletasks()

        # Start scanning in a separate thread
        threading.Thread(target=self.perform_scan, args=(directory, config_path)).start()

    def perform_scan(self, directory, config_path):
        """Perform the file scan in a separate thread"""
        try:
            config = configparser.ConfigParser()
            config.read(config_path)

            # Parse global exclusions if present
            global_excluded_dirs = []
            global_excluded_files = []

            if 'global' in config:
                if 'excluded_dirs' in config['global']:
                    global_excluded_dirs = parse_list_from_config(config['global']['excluded_dirs'])

                if 'excluded_files' in config['global']:
                    global_excluded_files = parse_list_from_config(config['global']['excluded_files'])

            file_paths = []

            # Process each section
            for section in config.sections():
                if section in ['specific_files', 'global']:
                    continue  # Handle these sections separately

                # Handle relative directories from the base
                dir_path = os.path.join(directory, section)
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

            # Handle specific files
            if 'specific_files' in config.sections():
                specific_files_text = config.get('specific_files', 'files')
                specific_files = parse_list_from_config(specific_files_text)

                # Process the specific files
                for specific_file in specific_files:
                    full_path = os.path.join(directory, specific_file)
                    if os.path.isfile(full_path):
                        # Check if this file is excluded globally
                        filename = os.path.basename(specific_file)
                        if any(filename == excluded_file or
                               (excluded_file.startswith('*') and filename.endswith(excluded_file[1:])) or
                               (excluded_file.endswith('*') and filename.startswith(excluded_file[:-1]))
                               for excluded_file in global_excluded_files):
                            continue

                        if full_path not in file_paths:
                            file_paths.append(full_path)
                    else:
                        print(f"Warning: Specific file '{specific_file}' not found. Skipping...")

            # Update the UI with the file list
            self.root.after(0, lambda: self.update_file_list(file_paths, directory))

        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Error: {str(e)}"))

    def update_file_list(self, file_paths, base_directory):
        """Update the UI with the file list"""
        # Clear any existing file list
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        self.file_checkboxes.clear()

        # Sort file paths by relative path
        rel_paths = [(path, os.path.relpath(path, base_directory)) for path in file_paths]
        rel_paths.sort(key=lambda x: x[1])

        # Create checkboxes for each file
        for i, (full_path, rel_path) in enumerate(rel_paths):
            var = tk.BooleanVar(value=True)

            # Store the checkbox variable and relative path keyed by the full path
            self.file_checkboxes[full_path] = (var, rel_path)

            checkbox = ttk.Checkbutton(self.file_list_frame, text=rel_path, variable=var)
            checkbox.grid(row=i, column=0, sticky="w", padx=5, pady=2)

        # Update the scroll region
        self.file_list_frame.update_idletasks()
        self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all"))

        # Update status
        self.update_status(f"Found {len(file_paths)} files. Select files to extract.")

    def update_status(self, message):
        """Update the status bar"""
        self.status_var.set(message)

    def select_all(self):
        """Select all files"""
        for var, _ in self.file_checkboxes.values():
            var.set(True)

    def deselect_all(self):
        """Deselect all files"""
        for var, _ in self.file_checkboxes.values():
            var.set(False)

    def toggle_selection(self):
        """Toggle selection of all files"""
        for var, _ in self.file_checkboxes.values():
            var.set(not var.get())

    def extract_files(self):
        """Extract selected files"""
        # Get the selected files - only include files where the checkbox is checked
        selected_files = [path for path, (var, _) in self.file_checkboxes.items() if var.get()]

        if not selected_files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to extract.")
            return

        # Get the output file name
        output_filename = self.output_var.get()
        if not output_filename:
            messagebox.showwarning("Missing Output", "Please provide an output file name.")
            return

        # Add .md extension if not present
        if not output_filename.endswith('.md'):
            output_filename += '.md'

        # Set output path
        output_path = os.path.join("Extracts", output_filename)

        # Update status
        self.update_status(f"Extracting {len(selected_files)} files...")
        self.root.update_idletasks()

        # Start extraction in a separate thread
        base_directory = self.directory_var.get()
        threading.Thread(target=self.perform_extraction, args=(selected_files, base_directory, output_path)).start()

    def perform_extraction(self, file_paths, base_directory, output_path):
        """Perform the extraction in a separate thread"""
        try:
            # Generate markdown content
            markdown_content = create_markdown_content(file_paths, base_directory)

            # Ensure output directory exists
            ensure_directory_exists(output_path)

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(markdown_content)

            # Generate files.txt
            files_txt_path = "files.txt"
            file_names = [os.path.relpath(file, base_directory) for file in file_paths]

            with open(files_txt_path, 'w') as f:
                for name in file_names:
                    f.write(f"{name}\n")

            # Update status
            self.root.after(0, lambda: self.extraction_complete(output_path, len(file_paths)))

        except Exception as e:
            self.root.after(0, lambda: self.update_status(f"Error: {str(e)}"))

    def extraction_complete(self, output_path, num_files):
        """Show completion message and update status"""
        self.update_status(f"Extraction complete: {num_files} files extracted to {output_path}")
        messagebox.showinfo("Extraction Complete", f"Successfully extracted {num_files} files to:\n{output_path}\n\nAlso generated files.txt listing all extracted files.")

def main():
    parser = argparse.ArgumentParser(description='Collect code based on config file and save as markdown.')
    parser.add_argument('directory', nargs='?', help='Base directory of the project')
    parser.add_argument('-c', '--config', help='Config type to use (e.g., android, web)', default='extract')
    parser.add_argument('-o', '--output', help='Output file path (default: code_collection.txt)')
    parser.add_argument('-ui', '--ui', action='store_true', help='Launch with graphical user interface')

    args = parser.parse_args()

    # Check if UI mode is requested
    if args.ui or (not args.directory and len(os.sys.argv) > 1 and os.sys.argv[1] == '-ui'):
        root = tk.Tk()
        app = CodeExtractorUI(root)
        root.mainloop()
        return

    # Continue with CLI mode if UI is not requested
    if not args.directory:
        print("Error: Directory argument is required in CLI mode.")
        parser.print_help()
        return

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
