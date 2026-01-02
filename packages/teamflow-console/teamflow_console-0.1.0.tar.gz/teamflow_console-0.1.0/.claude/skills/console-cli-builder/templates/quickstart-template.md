# Quick Start: {{APP_NAME}}

**Prerequisites**: Python 3.13+, UV package manager

## 🚀 Quick Start (Fastest Path)

```bash
# 1. Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
irm https://astral.sh/uv/install.ps1 | iex        # Windows PowerShell

# 2. Navigate to project and install dependencies
cd /path/to/{{APP_SLUG}}
uv sync --all-extras

# 3. Run the app
uv run python -m src.main
```

**That's it!** You're now running {{APP_NAME}}.

---

## Running the Application

### Launch the App

**IMPORTANT**: Always set `PYTHONPATH=src` before running.

```bash
# Linux/macOS/WSL
PYTHONPATH=src uv run python -m src.main

# Windows PowerShell
$env:PYTHONPATH="src"; uv run python -m src.main

# Windows CMD
set PYTHONPATH=src && uv run python -m src.main
```

**Alternative: Activate venv first**

```bash
# Activate venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Then run
PYTHONPATH=src python -m src.main
```

---

## Running Tests

```bash
# Run all tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/test_models.py -v

# Run with verbose output
uv run pytest -xvs
```

---

## Development Setup

```bash
# Format code
uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Lint (requires PYTHONPATH)
PYTHONPATH=src uv run pylint src/

# Type check
uv run mypy src/
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'cli'"

**Solution**: Set `PYTHONPATH=src` before running:
```bash
PYTHONPATH=src uv run python -m src.main
```

### Issue: Virtual environment corrupted

**Solution**: Delete and recreate:
```bash
rm -rf .venv  # Linux/macOS
Remove-Item -Recurse -Force .venv  # Windows PowerShell
uv sync --all-extras
```

---

## Project Structure

```
src/
├── main.py              # Entry point
├── models/              # Pydantic data models
├── services/            # Business logic
├── cli/                 # CLI interface (menus, prompts)
└── lib/                 # Utilities (formatting, validation, storage)

tests/
├── unit/                # Model and service tests
├── integration/         # End-to-end workflow tests
└── contract/            # API contract tests
```

---

**Enjoy using {{APP_NAME}}!** 🚀
