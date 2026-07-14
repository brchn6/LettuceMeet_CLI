# Project Overview: LettuceMeet Terminal Automation (init.md)

## The Goal
The primary objective of this project is to automate the native, live **LettuceMeet website** directly from a terminal window using an AI agent. The agent must be able to generate polls and read responses from the real website dynamically.

## Architecture & Strategy
Because the official platform does not issue public API tokens, this automation uses the website's internal GraphQL backend (`https://lettucemeet.com`). 
* **Action Mode:** Your script makes direct Python `requests` or executes terminal commands to interface with LettuceMeet's servers.
* **Scope:** Provide a CLI (Command Line Interface) interaction model for creating events, extracting participant availability grids, and calculating ideal meeting overlaps.

## File Hierarchy and Execution Instructions
A hard file containing the core terminal execution commands or automation wrapper has been placed directly in this root directory. 

### Instructions for the Agent:
1. **Analyze the Script:** Inspect the files in this folder to locate the core execution script (e.g., `lettucemeet_cli.py` or similar). 
2. **Terminal Integration:** Read the implementation of the script to understand how it handles internal authentication tokens or anonymous event queries.
3. **Command Orchestration:** Prepare to call this script from the terminal to create live events or parse current availability layouts when asked by the operator.

Good luck! Let's get this automated.
