#!/usr/bin/env python3
"""LettuceMeet CLI - terminal automation for LettuceMeet meeting polls.

Usage:
    uv run python main.py login <token>
    uv run python main.py create --title "My Poll" --dates 2026-07-14
    uv run python main.py show <id>
    uv run python main.py respond <id> --name Alice --email a@b.com --slots "DATE START END"
    uv run python main.py overlap <id>
    uv run python main.py delete <id>
"""

import sys
from lettucemeet_cli.cli import main

sys.exit(main())
