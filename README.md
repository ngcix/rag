# rag

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Build

### Development (in-place compile)

Compile Cython extensions directly in `src/` directory:

```bash
make compile
```

### Production (wheel + pip install)

Build wheel and install via pip (clean, tracked installation):

```bash
# Full build: compile Cython + build wheel + pip install
make build

# Or step by step:
make build-only   # Compile Cython and build wheel
make install      # Install wheel via pip
```

### PyInstaller (standalone executable)

```bash
# Build with PyInstaller after Cython compile
python buildscript/main.py -c -i
```

### Clean

```bash
# Clean all build artifacts
make clean

# Clean only compiled extensions (.c, .so, .pyd)
make clean-src
```

## Run

```bash
make run
```

## Commands Summary

| Command | Description |
|---------|-------------|
| `make compile` | Compile Cython extensions in-place (dev) |
| `make build` | Full build: wheel + pip install |
| `make build-only` | Build wheel only (no install) |
| `make install` | Install built wheel via pip |
| `make run` | Run the application |
| `make clean` | Clean all build artifacts |
| `make clean-src` | Clean only compiled extensions |

## Project Structure

```
rag/
├── Makefile              # Build commands
├── requirements.txt      # Python dependencies
├── setup.py              # Cython build setup
├── buildscript/          # Build scripts
│   ├── config.py         # Build configuration
│   ├── cython.py         # Cython compile + wheel build
│   ├── main.py           # Build entry point
│   └── pyinstaller.py    # PyInstaller packaging
└── src/
    └── rag/              # Source package
        ├── __init__.py
        ├── main.py       # Entry point
        └── utils/
            └── logcat.py
```

## Build Output

- **In-place compile** (`make compile`): `.pyd`/`.so` files in `src/`
- **Wheel build** (`make build`): `dist/rag-0.1-*.whl`
- **PyInstaller** (`-i` flag): `dist/<project_name>/`


