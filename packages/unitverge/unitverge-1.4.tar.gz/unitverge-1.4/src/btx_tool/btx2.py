"""
Bytex2 CLI Tool (btx2)
=======================

A command-line interface for the Bytex2 transpiler system. This tool provides
functionality to transpile, compile, and execute Bytex2 code, as well as work
with Python bytecode files.

Usage:
    btx2 <command> [arguments]

Commands:
    exec     - Transpile and immediately execute a Bytex2 file
    build    - Transpile Bytex2 to Python source code (.bx/.btx -> .py)
    compile  - Transpile Bytex2 to Python bytecode (.bx/.btx -> .pyc)
    expyc    - Execute a Python bytecode (.pyc) file directly
    repl     - Start an interactive Bytex2 REPL session

Examples:
    btx2 exec program.bx
    btx2 build program.bx program.py
    btx2 compile program.bx program.pyc
    btx2 expyc compiled.pyc
    btx2 repl

Dependencies:
    - UnitVerge.Bytex (bytex2 transpiler)
    - Python standard library modules

Author: pt
Version: As defined in UnitVerge.Bytex.bx2.translator.__version__
Repo: https://github.com/pt-main/unitverge
"""

import argparse
from UnitVerge import Bytex
import marshal
import os
import py_compile
from UnitVerge.Bytex.bx2.translator import __version__
import sys


class PycCompiler:
    """Handle Python bytecode compilation and execution operations.
    
    This class provides static methods for compiling Python code to .pyc files,
    compiling existing .py files, and executing .pyc files directly.
    
    Methods:
        compile_code_to_pyc: Compile string code to .pyc file
        compile_file_to_pyc: Compile .py file to .pyc file
        execute_pyc: Execute .pyc file directly
    """
    
    @staticmethod
    def compile_code_to_pyc(code: str, output_file: str, source_file: str = '<string>') -> None:
        """Compile Python source code from a string to a .pyc file.
        
        Args:
            code: Python source code as string
            output_file: Path for output .pyc file
            source_file: Original source filename for error messages
            
        Returns:
            None
            
        Raises:
            Various compilation and I/O exceptions
        """
        try:
            # Create temporary file for compilation
            temp_py = "temp_compile.py"
            with open(temp_py, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Compile to bytecode
            py_compile.compile(temp_py, cfile=output_file)
            os.remove(temp_py)
            
            print(f"✓ {output_file} compiled")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            # Cleanup temporary file on error
            if os.path.exists("temp_compile.py"):
                os.remove("temp_compile.py")
    
    @staticmethod
    def compile_file_to_pyc(source_file: str, output_file: str = None) -> None:
        """Compile an existing .py file to .pyc bytecode.
        
        Args:
            source_file: Path to source .py file
            output_file: Optional output path for .pyc file
                         Defaults to source_file with .pyc extension
            
        Returns:
            None
            
        Raises:
            FileNotFoundError: If source_file doesn't exist
            Various compilation exceptions
        """
        try:
            # Default output filename
            if output_file is None:
                output_file = source_file.replace('.py', '.pyc')
                if output_file == source_file:
                    output_file = source_file + 'c'
            
            # Perform compilation
            py_compile.compile(source_file, cfile=output_file)
            print(f"✓ Compiled {source_file} -> {output_file}")
            
        except FileNotFoundError:
            print(f"✗ File not found: {source_file}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    @staticmethod
    def execute_pyc(pyc_file: str) -> None:
        """Execute a .pyc bytecode file directly.
        
        Args:
            pyc_file: Path to .pyc file to execute
            
        Returns:
            None
            
        Raises:
            FileNotFoundError: If pyc_file doesn't exist
            Various execution and marshalling exceptions
        """
        try:
            # Validate file existence
            if not os.path.exists(pyc_file):
                print(f"✗ File not found: {pyc_file}")
                return     
            
            print(f"\nExecuting pyc file: {pyc_file}")
            print("-" * 40)
            
            # Load and execute bytecode
            with open(pyc_file, 'rb') as f:
                f.seek(16)  # Skip pyc header (magic number + timestamp)
                code = marshal.load(f)
            
            exec(code)
            print("-" * 40)
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()


# ============================================================================
# CLI Argument Parser Setup
# ============================================================================

parser = argparse.ArgumentParser(
    prog='btx2',
    description='''
╔══════════════════════════════════════════════════════════════╗
║                    Bytex2 CLI Tool (btx2)                    ║
║    Transpiler for Bytex2 language to Python bytecode         ║
╚══════════════════════════════════════════════════════════════╝

Bytex2 is a transpiler that converts Bytex2 code to Python. This CLI tool
provides multiple ways to work with Bytex2 files:

  • Execute Bytex2 code directly
  • Convert to Python source files
  • Compile to Python bytecode (.pyc)
  • Execute compiled bytecode
  • Interactive REPL environment

Supported file extensions: .bx, .btx, .py, .pyc

Common Workflow:
  1. Write Bytex2 code in .bx/.btx file
  2. Test with: btx2 exec program.bx
  3. Build to Python: btx2 build program.bx program.py
  4. Compile to bytecode: btx2 compile program.bx program.pyc
  5. Distribute compiled version

Note: Bytex2 files are transpiled to Python, then compiled to bytecode.''',
    epilog='''═══════════════════════════════════════════════════════════════
Examples:
  Quick test:           btx2 exec demo.bx
  Convert to Python:    btx2 build source.bx output.py
  Create bytecode:      btx2 compile app.bx app.pyc
  Run bytecode:         btx2 expyc app.pyc
  Interactive mode:     btx2 repl

  Advanced:
    btx2 compile input.btx - (dash for stdout)
    btx2 exec /path/to/file.bx

Troubleshooting:
  • Ensure Bytex2 syntax is correct
  • Check file permissions
  • Verify Python version compatibility
  • Use 'btx2 repl' to test snippets

Exit Codes:
  0 - Success
  1 - File not found
  2 - Bytex method error
  3 - General error

Repo: https://github.com/pt-main/unitverge, By Pt.''',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    usage='btx2 <command> [options] [arguments]\n       btx2 -h for detailed help'
)

# Parent parser for common arguments
common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument('--verbose', '-v', action='store_true', 
                          help='Enable verbose output for debugging')
common_parser.add_argument('--version', action='version', 
                          version=f'Bytex2 CLI v{__version__}')

subparsers = parser.add_subparsers(
    dest='command',
    title='Available Commands',
    description='''Choose one of the following commands to perform specific operations.
Each command has its own set of options and arguments.''',
    required=True,
    metavar='command'
)

# exec command: Transpile and execute Bytex2 file
exec_parser = subparsers.add_parser(
    'exec',
    help='Execute a Bytex2 file immediately',
    description='''
╔══════════════════════════════════════════════════════════════╗
║                        EXEC Command                          ║
╚══════════════════════════════════════════════════════════════╝

Transpiles a Bytex2 file to Python and executes it immediately.
Useful for testing and running Bytex2 scripts directly.

The file is transpiled in memory and executed without creating
intermediate files. Ideal for development and testing.''',
    epilog='''Example: btx2 exec script.bx
         btx2 exec --verbose app.btx''',
    parents=[common_parser],
    formatter_class=argparse.RawDescriptionHelpFormatter
)
exec_parser.add_argument(
    'input_file',
    help='''Path to Bytex2 source file.
Supported extensions: .bx, .btx

Examples:
  script.bx    - Standard Bytex2 file
  /path/app.btx - Full path to file
  ./local.bx   - Relative path'''
)

# build command: Transpile Bytex2 to Python source
build_parser = subparsers.add_parser(
    'build',
    help='Convert Bytex2 to Python source code',
    description='''
╔══════════════════════════════════════════════════════════════╗
║                        BUILD Command                         ║
╚══════════════════════════════════════════════════════════════╝

Transpiles a Bytex2 file to human-readable Python source code.
Creates a .py file that can be:
  • Edited further
  • Imported as module
  • Run with python interpreter
  • Compiled with other tools

The output is standard Python 3.x syntax.''',
    epilog='''Example: btx2 build source.bx output.py
         btx2 build --verbose input.btx module.py''',
    parents=[common_parser],
    formatter_class=argparse.RawDescriptionHelpFormatter
)
build_parser.add_argument(
    'input_file',
    help='''Source Bytex2 file to transpile.
Must have .bx or .btx extension.

If file doesn't exist, operation fails with error.'''
)
build_parser.add_argument(
    'output_file',
    help='''Output Python file path.
Recommended extension: .py

If file exists, it will be overwritten.
Use - for stdout output.'''
)

# compile command: Transpile Bytex2 to Python bytecode
compile_parser = subparsers.add_parser(
    'compile',
    help='Compile Bytex2 to Python bytecode (.pyc)',
    description='''
╔══════════════════════════════════════════════════════════════╗
║                      COMPILE Command                         ║
╚══════════════════════════════════════════════════════════════╝

Compiles Bytex2 code directly to Python bytecode (.pyc file).
Two-step process:
  1. Transpile Bytex2 → Python source
  2. Compile Python → Bytecode (.pyc)

Benefits:
  • Faster execution (no transpilation at runtime)
  • Code obfuscation
  • Distribution without source
  • Python version specific

Note: .pyc files are Python version dependent.''',
    epilog='''Example: btx2 compile app.bx app.pyc
         btx2 compile --verbose script.btx /output/compiled.pyc''',
    parents=[common_parser],
    formatter_class=argparse.RawDescriptionHelpFormatter
)
compile_parser.add_argument(
    'input_file',
    help='''Bytex2 source file to compile.
File must exist and be readable.'''
)
compile_parser.add_argument(
    'output_file',
    help='''Output .pyc file path.
Extension should be .pyc for clarity.

The file contains Python bytecode and can be executed
with 'btx2 expyc' or 'python' command.'''
)

# expyc command: Execute Python bytecode file
expyc_parser = subparsers.add_parser(
    'expyc',
    help='Execute compiled Python bytecode (.pyc)',
    description='''
╔══════════════════════════════════════════════════════════════╗
║                       EXPYC Command                          ║
╚══════════════════════════════════════════════════════════════╝

Executes a pre-compiled Python bytecode (.pyc) file directly.
Bypasses Python source interpretation for faster execution.

The .pyc file must be compatible with:
  • Current Python version
  • Platform architecture
  • Bytecode format

Useful for:
  • Running distributed applications
  • Testing compiled output
  • Performance-sensitive code''',
    epilog='''Example: btx2 expyc compiled.pyc
         btx2 expyc --verbose /path/to/app.pyc''',
    parents=[common_parser],
    formatter_class=argparse.RawDescriptionHelpFormatter
)
expyc_parser.add_argument(
    'input_file',
    help='''Python bytecode file (.pyc) to execute.
File must be a valid .pyc compiled with compatible
Python version.'''
)

# repl command: Start interactive REPL
repl_parser = subparsers.add_parser(
    'repl',
    help='Start interactive Bytex2 REPL',
    description='''
╔══════════════════════════════════════════════════════════════╗
║                        REPL Command                          ║
╚══════════════════════════════════════════════════════════════╝

Starts an interactive Read-Eval-Print Loop for Bytex2.
Features:
  • Immediate code execution
  • Line-by-line transpilation
  • Variable persistence
  • Syntax testing
  • Debugging aid

Commands in REPL:
  exit      - Exit REPL
  Ctrl+C    - Keyboard interrupt
  Ctrl+D    - End of file (exit)

Each line is transpiled to Python and executed immediately.''',
    epilog='''Example: btx2 repl
         btx2 repl --verbose

REPL Example Session:
  >>> x = 10
  >>> y = x * 2
  >>> print(y)
  20
  >>> exit''',
    parents=[common_parser],
    formatter_class=argparse.RawDescriptionHelpFormatter
)
repl_parser.add_argument(
    '--history-size',
    type=int,
    default=100,
    help='Number of commands to keep in history (default: 100)'
)

version_parser = subparsers.add_parser(
    'version',
    help='Show cli version',
    parents=[common_parser],
    formatter_class=argparse.RawDescriptionHelpFormatter
)


def main() -> None:
    """Main entry point for the Bytex2 CLI tool.
    
    Parses command-line arguments and routes to appropriate functionality.
    
    Returns:
        None
        
    Raises:
        SystemExit: On invalid arguments or critical errors
    """
    args = parser.parse_args()
    
    try:
        if args.command == 'exec':
            if args.verbose:
                print(f"[VERBOSE] Reading file: {args.input_file}")
            with open(args.input_file, 'r', encoding='utf-8') as file:
                code = file.read()
            if args.verbose:
                print(f"[VERBOSE] Executing {len(code)} characters of Bytex2 code")
            Bytex('2.0').current['ex'](code)
            
        elif args.command == 'build':
            if args.verbose:
                print(f"[VERBOSE] Building: {args.input_file} -> {args.output_file}")
            with open(args.input_file, 'r', encoding='utf-8') as file:
                code = file.read()
            if args.output_file == '-':
                python_code = Bytex('2.0').current['bu'](code)
                print(python_code)
            else:
                Bytex('2.0').current['bi'](code, args.output_file)
                print(f"✓ Built {args.input_file} -> {args.output_file}")
        
        elif args.command == 'compile':
            if args.verbose:
                print(f"[VERBOSE] Compiling: {args.input_file} -> {args.output_file}")
            with open(args.input_file, 'r', encoding='utf-8') as file:
                code = file.read()
            python_code = Bytex('2.0').current['bu'](code)
            if args.output_file == '-':
                print("[INFO] Cannot output .pyc to stdout, use 'build' for Python source")
                sys.exit(1)
            compiler = PycCompiler()
            compiler.compile_code_to_pyc(python_code, args.output_file, args.input_file)
        
        elif args.command == 'expyc':
            if args.verbose:
                print(f"[VERBOSE] Executing bytecode: {args.input_file}")
            compiler = PycCompiler()
            compiler.execute_pyc(args.input_file)
        
        elif args.command == 'repl':
            if args.verbose:
                print(f"[VERBOSE] Starting REPL with history size: {args.history_size}")
            localscope = locals()
            print(f'''Bytex2 REPL [v{__version__}] (by pt)
Type 'exit' to quit, Ctrl+C to interrupt.''')
            print('=' * 60)
            
            history = []
            while True:
                try:
                    inp = input('>>> ')
                    if inp.strip().lower() == 'exit':
                        print("Goodbye!")
                        break
                    
                    history.append(inp)
                    if len(history) > args.history_size:
                        history.pop(0)
                    
                    code = Bytex('2.0').translator().translate(inp)
                    if args.verbose:
                        print(f"[VERBOSE] Transpiled to Python: {'\n'.join(code)}")
                    try:
                        exec('\n'.join(code), localscope, localscope)
                    except Exception as e:
                        print(f'✗ Error: {e}')
                        
                except KeyboardInterrupt:
                    print('\n[Interrupted]')
                    continue
                except EOFError:
                    print('\n[EOF] Exiting...')
                    break
        
        elif args.command == 'version':
            print(f'Bytex2 CLI toolkit [v{__version__}] (by pt) - licence MIT')
        
        else:
            print('Unknown command. Use [btx2 -h] for help.')
            
    except FileNotFoundError as e:
        print(f"✗ File not found: {e}")
        print("  Check if file exists and path is correct.")
        sys.exit(1)
    except KeyError as e:
        print(f"✗ Method not found in Bytex: {e}")
        print("  Bytex2 installation may be corrupted.")
        sys.exit(2)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        if args.verbose:
            traceback.print_exc()
        else:
            print("  Use --verbose for detailed error information.")
        sys.exit(3)


if __name__ == '__main__':
    main()