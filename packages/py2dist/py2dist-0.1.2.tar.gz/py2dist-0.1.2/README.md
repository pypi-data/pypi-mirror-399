# py2dist

[中文文档](README_zh.md)

py2dist is a tool that uses Cython to compile Python source code into binary extension modules (`.so`/`.pyd`), primarily for source code protection.

## Features

- Compile single `.py` files or entire directories into binary files.
- Preserve directory structure.
- Support excluding specific files or directories.
- Automatically detect and use `ccache` to accelerate compilation.
- Provide both CLI and Python API.

## Installation

```bash
pip install py2dist
```

## Usage

### Command Line Interface (CLI)

Compile a single file:
```bash
py2dist -f myscript.py
```

Compile an entire directory:
```bash
py2dist -d myproject -o dist
```

Arguments:
- `-f, --file`: Specify a single `.py` file to compile.
- `-d, --directory`: Specify the directory to compile.
- `-o, --output`: Output directory (default is `dist`).
- `-m, --maintain`: Files or directories to exclude (comma-separated).
- `-x, --nthread`: Number of compilation threads (default is 1).
- `-q, --quiet`: Quiet mode.
- `-r, --release`: Release mode (cleans up temporary build files).
- `-c, --ccache`: Use ccache (auto-detect by default, or specify path).

### Python API

```python
from py2dist import compile_file, compile_dir

# Compile a single file
compile_file("myscript.py", output_dir="dist")

# Compile a directory
compile_dir(
    "myproject",
    output_dir="dist",
    exclude=["tests", "setup.py"],
    nthread=4
)
```

## ⚠️ Important Note: Python Version Consistency

The compiled binary extension modules (`.so`/`.pyd`) are bound to a specific Python version. **You must ensure that the Python version used for compilation is exactly the same as the Python version used at runtime** (including minor version numbers; for example, 3.10 and 3.11 are incompatible).

If the versions do not match, you may encounter errors like the following when importing the module:
`ImportError: ... undefined symbol: _PyThreadState_UncheckedGet`
or
`ModuleNotFoundError: No module named ...`
