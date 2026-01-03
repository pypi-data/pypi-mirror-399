"""
Bytex Language CLI - Project Management and Execution Tool
==========================================================

A command-line interface for managing Bytex projects and executing
Bytex2 code. Provides project scaffolding and integration with btx2.

Repo: https://github.com/pt-main/unitverge, By Pt.
"""

import argparse
import sys
import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional

LIBS = Path.home() / 'BTXLIBS'


class BytexCLI:
    """Main CLI handler for Bytex language operations."""
    
    def __init__(self):
        self.parser = self._create_parser()
        
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            prog='bytex',
            description='''╔══════════════════════════════════════════════════════════════╗
║                  Bytex Language CLI Tool                     ║
║         Project Management and Execution Interface           ║
╚══════════════════════════════════════════════════════════════╝

A comprehensive CLI for managing Bytex projects and executing
Bytex2 code. Simplifies project creation and integrates with
the btx2 transpiler for seamless development workflows.

This tool provides:
  • Project scaffolding with standard structure
  • Execution of Bytex2 files via btx2
  • Cross-platform build scripts
  • Easy integration with existing workflows''',
            epilog='''═══════════════════════════════════════════════════════════════
Examples:
  Run Bytex2 file:    bytex 2 program.btx
  Create project:     bytex project myapp main
  Install module:     bytex install module.btx utils
  Get help:           bytex --help
  Project help:       bytex project --help
  Bytex2 help:        bytex 2 --help

Project Structure Created:
  project-name/
  ├── src/           # Source files
  ├── build/         # Build output
  ├── build-win.bat  # Windows build script
  ├── build-unix.sh  # Unix/Linux build script
  └── README.md      # Project documentation

Dependencies:
  • Python 3.10+
  • btx2 CLI tool
  • UnitVerge package''',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False
        )
        
        # Main subparsers
        subparsers = parser.add_subparsers(
            dest='command',
            title='Available Commands',
            description='''Choose one of the following commands to perform operations.
For detailed help on any command, use: bytex <command> --help''',
            required=False,
            metavar='command'
        )
        
        # 2 command (btx2 integration)
        btx2_parser = subparsers.add_parser(
            '2',
            help='Execute Bytex2 files or use btx2 CLI',
            description='''╔══════════════════════════════════════════════════════════════╗
║                     Bytex2 Execution                         ║
╚══════════════════════════════════════════════════════════════╝

Execute Bytex2 files directly or pass commands to btx2 CLI.
This command provides seamless integration with the btx2 transpiler.

Auto-detection:
  • .btx files → btx2 exec <file>
  • .pyc files → btx2 expyc <file>
  • Other args → passed directly to btx2

Use this command to run Bytex2 code or access full btx2 functionality.''',
            epilog='''Examples:
  Execute .btx file:    bytex 2 app.btx
  Run .pyc bytecode:    bytex 2 compiled.pyc
  Use btx2 directly:    bytex 2 build source.btx output.py
  Get btx2 help:        bytex 2 --help''',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False
        )
        btx2_parser.add_argument(
            'btx2_args',
            nargs='*',
            help='''Arguments to pass to btx2. If a single .btx or .pyc file
is provided, it will be executed automatically.'''
        )
        btx2_parser.add_argument(
            '--help', '-h',
            action='store_true',
            help='Show btx2 help instead of executing'
        )
        
        # project command
        project_parser = subparsers.add_parser(
            'project',
            help='Create a new Bytex project structure',
            description='''╔══════════════════════════════════════════════════════════════╗
║                     Project Scaffolding                      ║
╚══════════════════════════════════════════════════════════════╝

Creates a complete Bytex project structure with:
  • Standard directory layout
  • Cross-platform build scripts
  • Basic configuration
  • Documentation template

This sets up a development environment ready for Bytex2
application development with proper build automation.''',
            epilog='''Examples:
  Create project:        bytex project myapp main
  With custom dir:       bytex project --output /path/to/project appname main

Project Structure:
  myapp/
  ├── src/              # Source code directory
  │   └── main.btx      # Main entry point
  ├── build/            # Build artifacts directory
  ├── build-win.bat     # Windows build automation
  ├── build-unix.sh     # Unix/Linux build automation
  └── README.md         # Project documentation''',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False
        )
        project_parser.add_argument(
            'name',
            help='''Project name (will be used for directory name).
Must be a valid directory name.'''
        )
        project_parser.add_argument(
            'mainfile',
            help='''Name of the main source file (without extension).
This will create src/<mainfile>.btx as the entry point.'''
        )
        project_parser.add_argument(
            '--output', '-o',
            default='.',
            help='Output directory for the project (default: current directory)'
        )
        project_parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Force creation even if directory exists (overwrites files)'
        )
        project_parser.add_argument(
            '--help', '-h',
            action='store_true',
            help='Show this help message and exit'
        )
        
        # install command
        install_parser = subparsers.add_parser(
            'install',
            help='Install a module into Bytex libraries',
            description='''╔══════════════════════════════════════════════════════════════╗
║                     Module Installation                      ║
╚══════════════════════════════════════════════════════════════╝

Install a Bytex module (.btx file) into the Bytex libraries directory.
This makes the module available for import in other Bytex projects.

The module will be copied to:
  • LIBS/ (global library directory) if no subdirectory specified
  • LIBS/<dir>/ if subdirectory specified

Default library location: ~/BTXLIBS/''',
            epilog='''Examples:
  Install to root:       bytex install mathlib.btx
  Install to utils dir:  bytex install utils.btx helpers
  Force overwrite:       bytex install module.btx --force

Usage in Bytex code:
  # After installation, you can import:
  import mathlib
  import helpers.utils as utils''',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False
        )
        install_parser.add_argument(
            'module',
            help='''Path to the module file (.btx) to install.
Must be a valid Bytex source file.'''
        )
        install_parser.add_argument(
            'directory',
            nargs='?',
            default='',
            help='''Optional subdirectory within LIBS to install the module.
If not specified, installs to LIBS root.'''
        )
        install_parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Force installation even if module already exists (overwrites)'
        )
        install_parser.add_argument(
            '--help', '-h',
            action='store_true',
            help='Show this help message and exit'
        )
        
        # Add help flag to main parser
        parser.add_argument(
            '--help', '-h',
            action='store_true',
            help='Show this help message and exit'
        )
        
        return parser
    
    def _run_btx2(self, args: List[str], show_help: bool = False) -> int:
        """Execute btx2 commands with appropriate arguments."""
        if show_help or not args:
            # Show btx2 help
            return subprocess.call(['btx2', '-h'])
        
        # Auto-detect file type for single argument
        if len(args) == 1:
            arg = args[0]
            if arg.endswith('.btx'):
                return subprocess.call(['btx2', 'exec', arg])
            elif arg.endswith('.pyc'):
                return subprocess.call(['btx2', 'expyc', arg])
        
        # Pass all arguments directly to btx2
        return subprocess.call(['btx2'] + args)
    
    def _create_project(self, name: str, mainfile: str, 
                       output_dir: str, force: bool = False) -> int:
        """Create a new Bytex project structure."""
        project_path = Path(output_dir) / name
        
        # Check if project already exists
        if project_path.exists() and not force:
            print(f"✗ Directory '{project_path}' already exists.")
            print("  Use --force to overwrite or choose a different name.")
            return 1
        
        try:
            # Create directory structure
            print(f"=== Creating project: {name} ===")
            
            if force and project_path.exists():
                print(f"⚠  Overwriting existing directory: {project_path}")
            
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            src_dir = project_path / 'src'
            build_dir = project_path / 'build'
            
            src_dir.mkdir(exist_ok=True)
            build_dir.mkdir(exist_ok=True)
            
            print("✓ Created directory structure")
            
            # Create main source file
            main_file_path = src_dir / f"{mainfile}.btx"
            with open(main_file_path, 'w', encoding='utf-8') as f:
                f.write(f'''# Main file: {mainfile}.btx
# Created by Bytex CLI

# Your Bytex2 code starts here
echoln "Hello from {name}!"

# Add your application logic below
# This file will be compiled to build/output.py
''')
            print(f"✓ Created main source file: src/{mainfile}.btx")
            
            # Create Windows build script
            win_build_script = project_path / 'build-win.bat'
            with open(win_build_script, 'w', encoding='utf-8') as f:
                f.write(f'''@echo off
REM Build script for {name} - Windows
REM Generated by Bytex CLI

echo Installing dependencies...
pip install unitverge

echo.
echo Building {mainfile}.btx...
bytex 2 build src\\{mainfile}.btx build\\output.py

if %errorlevel% equ 0 (
    echo.
    echo ✓ Build successful!
    echo Output: build\\output.py
) else (
    echo.
    echo ✗ Build failed!
    exit /b 1
)
''')
            print("✓ Created Windows build script: build-win.bat")
            
            # Create Unix build script
            unix_build_script = project_path / 'build-unix.sh'
            with open(unix_build_script, 'w', encoding='utf-8') as f:
                f.write(f'''#!/bin/bash
# Build script for {name} - Unix/Linux
# Generated by Bytex CLI

echo "Installing dependencies..."
pip3 install unitverge

echo
echo "Building {mainfile}.btx..."
bytex 2 build src/{mainfile}.btx build/output.py

if [ $? -eq 0 ]; then
    echo
    echo "✓ Build successful!"
    echo "Output: build/output.py"
else
    echo
    echo "✗ Build failed!"
    exit 1
fi
''')
            # Make Unix script executable
            unix_build_script.chmod(0o755)
            print("✓ Created Unix build script: build-unix.sh")
            
            # Create README
            readme_path = project_path / 'README.md'
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f'''# {name}

A Bytex2 project created with Bytex CLI.

## Project Structure

```
{name}/
├── src/                  # Source files
│   │                     # Main entry point
│   └── {mainfile}.btx 
├── build/                # Build output
├── build-win.bat         # Windows build automation
├── build-unix.sh         # Unix/Linux build automation
└── README.md             # This file
```

## Getting Started

### Prerequisites
- Python 3.10+
- btx2 CLI tool (`pip install unitverge`)

### Building the Project

**Windows:**
```cmd
build-win.bat
```

**Unix/Linux/Mac:**
```bash
./build-unix.sh
```

### Running the Application

```bash
bytex 2 exec src/{mainfile}.btx
```

Or build and run the Python output:

```bash
bytex 2 build src/{mainfile}.btx build/output.py
python build/output.py
```

### Installing Modules

You can install additional modules to ~/BTXLIBS/:

```bash
bytex install module.btx
bytex install utils.btx helpers
```
''')
            print("✓ Created documentation: README.md")
            
            # Create .gitignore
            gitignore_path = project_path / '.gitignore'
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write('''# Build artifacts
build/
*.pyc
__pycache__/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Virtual environments
venv/
env/
''')
            print("✓ Created .gitignore file")
            
            print("\n" + "="*40)
            print(f"✓ Project '{name}' created successfully!")
            print("="*40)
            print(f"\nLocation: {project_path.resolve()}")
            print("\nNext steps:")
            print(f"  1. cd {project_path}")
            print(f"  2. Review src/{mainfile}.btx")
            print(f"  3. Run build script (build-win.bat or ./build-unix.sh)")
            print(f"  4. Test with: bytex 2 exec src/{mainfile}.btx")
            print("\nHappy coding! 🚀")
            
            return 0
            
        except Exception as e:
            print(f"✗ Error creating project: {e}")
            return 1
    
    def _install_module(self, module_path: str, directory: str = '', 
                       force: bool = False) -> int:
        """Install a module into Bytex libraries."""
        try:
            # Check source file
            src_path = Path(module_path)
            if not src_path.exists():
                print(f"✗ Source file '{src_path}' not found.")
                return 1
            
            if not src_path.is_file():
                print(f"✗ '{src_path}' is not a file.")
                return 1
            
            # Ensure library directory exists
            LIBS.mkdir(parents=True, exist_ok=True)
            print(f"✓ Library directory: {LIBS}")
            
            # Determine target path
            if directory:
                target_dir = LIBS / directory
                target_dir.mkdir(parents=True, exist_ok=True)
                target_path = target_dir / src_path.name
                print(f"✓ Installing to subdirectory: {directory}/")
            else:
                target_path = LIBS / src_path.name
                print("✓ Installing to library root")
            
            # Check if file already exists
            if target_path.exists() and not force:
                print(f"\n⚠  Module '{target_path.name}' already exists at:")
                print(f"   {target_path}")
                
                # Interactive prompt
                try:
                    response = input("  Overwrite? [y/N]: ").strip().lower()
                    if response not in ['y', 'yes']:
                        print("✗ Installation cancelled.")
                        return 0
                except (KeyboardInterrupt, EOFError):
                    print("\n✗ Installation cancelled.")
                    return 0
            
            # Copy the file
            shutil.copy2(src_path, target_path)
            
            print(f"✓ Successfully installed '{src_path.name}'")
            print(f"  From: {src_path.resolve()}")
            print(f"  To:   {target_path.resolve()}")
            
            # Show usage example
            module_name = src_path.stem
            if directory:
                import_path = f"{directory}.{module_name}"
            else:
                import_path = module_name
            
            print("\n📦 Usage in Bytex code:")
            print(f"  #import {import_path}")
            
            if directory:
                print(f"  # or import {directory}.{module_name} as {module_name}")
            
            print(f"\nTotal modules in library: {len(list(LIBS.rglob('*.btx')))}")
            
            return 0
            
        except PermissionError:
            print(f"✗ Permission denied. Cannot write to {target_path}")
            print("  Try running with appropriate permissions.")
            return 1
        except Exception as e:
            print(f"✗ Installation failed: {e}")
            return 1
    
    def run(self) -> int:
        """Execute the CLI with parsed arguments."""
        # Parse arguments
        args = self.parser.parse_args()
        
        # Handle help
        if args.help or not hasattr(args, 'command'):
            self.parser.print_help()
            return 0
        
        # Dispatch to appropriate handler
        if args.command == '2':
            if hasattr(args, 'help') and args.help:
                return subprocess.call(['btx2', '-h'])
            return self._run_btx2(args.btx2_args)
        
        elif args.command == 'project':
            if hasattr(args, 'help') and args.help:
                # Re-parse with project parser to show help
                subparser = [sp for sp in self.parser._subparsers._actions 
                           if hasattr(sp, 'choices')][0]
                subparser.choices['project'].print_help()
                return 0
            
            return self._create_project(
                name=args.name,
                mainfile=args.mainfile,
                output_dir=args.output,
                force=args.force
            )
        
        elif args.command == 'install':
            if hasattr(args, 'help') and args.help:
                # Re-parse with install parser to show help
                subparser = [sp for sp in self.parser._subparsers._actions 
                           if hasattr(sp, 'choices')][0]
                subparser.choices['install'].print_help()
                return 0
            
            return self._install_module(
                module_path=args.module,
                directory=args.directory,
                force=args.force
            )
        
        else:
            print(f'Unknown command [{args.command}]. Use [--help] for help.')
            return 1


def main() -> None:
    """Main entry point for Bytex CLI."""
    cli = BytexCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
