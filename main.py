#!/usr/bin/env python3
"""LettuceMeet CLI - terminal automation for LettuceMeet meeting polls.

Usage:
    uv run python main.py --help
    uv run python main.py login <token>
    uv run python main.py create --title "My Poll" --dates 2026-07-14
    uv run python main.py show J5R5a
    uv run python main.py respond J5R5a --name Alice --email a@b.com --slots "2026-07-14 09:00 12:00"
    uv run python main.py overlap J5R5a
"""

import sys
from lettucemeet_cli.cli import main

sys.exit(main())
