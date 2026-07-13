# rag

## Setup

The easiest way to get started is to use the provided `Makefile` to set up your environment:

```bash
# Create virtual environment and install all dependencies
make setup-env
```

This command will:
1. Create a `.venv` directory.
2. Install the project and its dependencies using `pip install .` (reading from `pyproject.toml`).
3. Install `pytest` for testing.

To activate the environment:
- **Linux/macOS**: `source venv/bin/activate`
- **Windows**: `venv\Scripts\activate`

## Development & Testing

### Run Tests
Run the project's test suite:
```bash
make test
```

### Development Run
Run the application in development mode:
```bash
make run
```

### In-place Compile
Compile Cython extensions directly in `src/` directory for faster execution during development:
```bash
make compile
```

## Build & Distribution

### Production (Wheel + Pip Install)
Build a distribution wheel and install it as a proper Python package:
```bash
# Full build: compile Cython + build wheel + pip install
make build

# Or step by step:
make build-only   # Compile Cython and build wheel
make install      # Install wheel via pip
```

### PyInstaller (Standalone Executable)
Build and run the application as a single standalone binary:
```bash
# Build and run executable
make build-exec

# Run the already built executable
make run-exec
```

### Clean
```bash
# Clean all build artifacts (build/, dist/, cython_build/)
make clean

# Clean only compiled extensions (.c, .so, .pyd)
make clean-src
```

## Commands Summary

| Command | Description |
|---------|-------------|
| `make setup-env` | Setup venv and install dependencies |
| `make test` | Run project tests |
| `make compile` | Compile Cython extensions in-place (dev) |
| `make run` | Run the application (dev mode) |
| `make run-exec` | Run the bundled standalone executable |
| `make build` | Full build: wheel + pip install |
| `make build-only` | Build wheel only (no install) |
| `make build-exec` | Build standalone executable |
| `make install` | Install built wheel via pip |
| `make clean` | Clean all build artifacts |
| `make clean-src` | Clean only compiled extensions |

## Project Structure

```
rag/
├── Makefile              # Build and automation commands
├── pyproject.toml        # Project configuration and dependencies
├── setup.py              # Minimal Cython build setup
├── buildscript/          # Build automation scripts
│   ├── config.py         # Build configuration
│   ├── cython_build.py   # Cython compile + wheel build
│   ├── main.py           # Build entry point
│   └── pyinstaller.py    # PyInstaller packaging
├── src/
│   └── rag/              # Source package
│       ├── __init__.py
│       ├── main.py       # Entry point
│       └── utils/
│           ├── config.py
│           └── logcat.py
└── tests/                # Project tests
    └── test_main.py
```

## Build Output

- **In-place compile** (`make compile`): `.pyd`/`.so` files in `src/`
- **Wheel build** (`make build`): `dist/rag-0.1-*.whl`
- **PyInstaller** (`make build-exec`): `dist/rag/rag` (binary executable)
