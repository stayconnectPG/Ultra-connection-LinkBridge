# Contributing

Thank you for your interest in contributing to the Debian ↔ Android Assistant Bridge!

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd debian-android-bridge
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run tests:**
   ```bash
   pytest -v
   ```

5. **Run linters:**
   ```bash
   ruff check .
   mypy debian relay
   ```

## Workflow

1. Create a feature branch from `main`
2. Implement your changes following the coding conventions in `AGENTS.md`
3. Add tests for new functionality
4. Ensure all tests and linters pass
5. Open a pull request

## Coding Standards

- **Python**: PEP 8, type hints required, `ruff` + `mypy` enforced
- **Kotlin**: Follow Kotlin coding conventions, use coroutines for async
- **Async-first**: All Python I/O should be async

## Project Structure

See `README.md` for the full architecture. Key directories:

- `debian/` — Python assistant core (FastAPI, connection manager)
- `relay/` — Python gateway (authentication, routing, sessions)
- `android/` — Kotlin Android app
- `tests/` — pytest test suite
- `docs/` — Documentation
- `scripts/` — DevOps scripts
