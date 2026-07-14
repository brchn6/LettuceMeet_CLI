
# Decisions Log

## Initial Decisions

* Use `uv` for Python environment and dependency management.
* Use `.venv/` as the local virtual environment.
* Use `.agents/init.md` for agent operating instructions.
* Use `.memory/progress.md` to track work progress.
* Use `.memory/decisions.md` to track project decisions.
* Prefer `uv run` for running commands inside the project environment.
* Use `requests` as the only runtime dependency.
* Use `argparse` (stdlib) for CLI framework -- no extra dependency.
* Use `requests-mock` for HTTP mocking in tests.
* Token resolution chain: `--token` flag > `LETTUCEMEET_TOKEN` env var > `data/session.json`.
* Anonymous responses only for `respond` command (authenticated responses not implemented).

## Architecture Decisions

* **2026-07-14**: Package structure under `src/lettucemeet_cli/` with separate
  modules for CLI, client, API, models, overlap, and config.
* **2026-07-14**: GraphQL operations embedded as raw strings in `api.py`
  (extracted from HAR/JS bundle). Not using a GraphQL client library.
* **2026-07-14**: Session token stored in gitignored `data/session.json`.
* **2026-07-14**: `CreateEventInput.to_api_variables()` returns a flat dict
  (without `{"input": ...}` wrapper). The API layer wraps it.
* **2026-07-14**: `CreatePollResponseInput.to_api_variables()` includes the
  `{"input": ...}` wrapper.
* **2026-07-14**: Overlap computed as hour-grid per date, no sliding window
  or minute-level precision. Simpler and sufficient for typical poll resolution.
