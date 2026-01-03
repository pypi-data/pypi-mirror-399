# Repository Guidelines

This repository builds a notebook-first MCP Inspector alternative for debugging and testing MCP servers.

## Project Structure & Module Organization

- `src/mcp_tuning/`: Python library.
  - `inspector.py`: `InspectorClient` (connect/explore/call, history, exports).
  - `transports/`: transport implementations (`stdio`, `http`, `sse`).
  - `notebook_inspector.py`: `ipywidgets` UI.
- `examples/`: runnable demo servers + demo notebook.
  - `examples/notebooks/01_mcp_inspector_demo.ipynb`
  - `examples/servers/simple_stdio_server.py`
- `docs/`: detailed documentation.
- `cases/`: saved call cases (`*.json`).
- `exports/`: exported logs/history/results (`*.json`).
- `tests/`: pytest tests (`tests/test_*.py`).

## Build, Test, and Development Commands (uv)

This project uses `uv` for environment and dependency management.

- `uv sync`: install runtime dependencies.
- `uv sync --extra notebook --extra test`: install Jupyter + pytest extras.
- `uv run jupyter lab`: start JupyterLab.
- `python -m pytest`: run unit/integration tests.

## Coding Style & Naming Conventions

- Python: 4-space indentation, type hints where practical.
- Naming: `snake_case` for functions/modules, `PascalCase` for classes.
- Keep PRs focused; avoid unrelated refactors.

## Testing Guidelines

- Framework: `pytest`.
- Keep tests deterministic. In this environment, pytest temp/cache plugins are disabled (see `pyproject.toml`), and tests write artifacts under `test-outputs/`.

## Commit & Pull Request Guidelines

Git history may not be available here. For PRs:

- Use clear, imperative commit messages (or Conventional Commits: `feat:`, `fix:`).
- Include: what changed, how to verify (commands), and screenshots/GIFs for notebook UI changes.

## Security & Configuration Tips

- Treat MCP server commands/URLs as untrusted input; prefer explicit argv lists over shell strings where possible.
- For debugging, export logs/history/results from the notebook UI to `exports/`.
