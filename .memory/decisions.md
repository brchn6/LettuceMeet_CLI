# Decisions Log

## Architecture

- **Python 3.11+**, `uv` for environment management.
- `requests` as the only runtime dependency. `argparse` (stdlib) for CLI -- no extra deps.
- Package under `src/lettucemeet_cli/` with separate modules: CLI, client, API, models, overlap, config.
- GraphQL operations embedded as raw strings in `api.py` (extracted from browser HAR capture, not using a GraphQL client library).
- Token chain: `--token` flag > `LETTUCEMEET_TOKEN` env var > `data/session.json`.
- Anonymous responses only for `respond` (authenticated response flow not implemented).
- Overlap computed as hour-grid per date. Sufficient for typical poll resolution.
