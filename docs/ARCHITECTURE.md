# Architecture: How the Agent Runs LettuceMeet CLI

## Overview

This project is a **CLI tool + AI agent harness** that automates
[LettuceMeet](https://lettucemeet.com) -- a web-based meeting poll platform --
directly from the terminal. There is no public API. The agent works by
reconstructing the internal GraphQL API from a browser HAR capture and
replaying authenticated requests via a Python CLI.

```
User request -> AI Agent (Pi) -> Python CLI -> GraphQL HTTP -> api.lettucemeet.com
```

---

## How the API Was Reverse-Engineered

### Step 1: HAR capture (removed from repo)

A 2.6 MB HTTP Archive was recorded from a real browser session using Chrome
DevTools. It contained the GraphQL queries, responses, session data, and JS
source needed to reconstruct the API. The file contained private user data and
was removed from the repository. All extracted operations are embedded in
`src/lettucemeet_cli/api.py`.

### Step 2: Operation extraction

All GraphQL operations were extracted from the HAR:

| Operation | Type | Purpose |
|---|---|---|
| `EventQuery` | Query | Fetch event + poll responses + availabilities |
| `CurrentUserQuery` | Query | Fetch user profile, events, notifications |
| `CreateEventMutation` | Mutation | Create a new poll |
| `UpdateEventMutation` | Mutation | Update event details |
| `DeleteEventMutation` | Mutation | Delete an event |
| `ScheduleEventMutation` | Mutation | Finalize a meeting time |
| `CreatePollResponseMutation` | Mutation | Submit availability |
| `UpdatePollResponseMutation` | Mutation | Update availability |
| `DeletePollResponseMutation` | Mutation | Remove availability |

The full GraphQL query texts were extracted from the minified JS bundle
(`main.0670f3f4.chunk.js`) where Relay stores them as compiled `text:"..."` strings.
These are embedded directly in `src/lettucemeet_cli/api.py`.

---

## Data Flow

```
User terminal                  src/lettucemeet_cli/
-------------                  --------------------

uv run python main.py show KZaEn
        |
        v
    cli.py: main(argv)
        |  parses args via argparse
        |  creates GraphQLClient(token)
        v
    api.py: get_event(client, "KZaEn")
        |  calls client.execute(EVENT_QUERY, variables={"id": "KZaEn"})
        v
    client.py: GraphQLClient.execute(query, variables, operation_name)
        |  builds {"query": ..., "variables": ..., "operationName": ...}
        |  adds Authorization: Bearer <token> header
        |  POSTs to https://api.lettucemeet.com/graphql
        v
    api.lettucemeet.com
        |  returns JSON {data: {event: {id, title, ..., pollResponses: [...]}}}
        v
    client.py: parses response, checks for errors
        v
    api.py: wraps in Event.from_api_data(data["event"])
        v
    models.py: Event dataclass with PollResponse, Availability children
        v
    cli.py: pretty-prints event details
        v
    Terminal output
```

---

## Token / Authentication Flow

The LettuceMeet API authenticates via a **JWT bearer token** stored in the browser's
Local Storage under the key `akoko:session_token`.

```
Token resolution chain (first wins):
  1. --token CLI flag             (session-scoped override)
  2. LETTUCEMEET_TOKEN env var    (session-scoped, no file needed)
  3. data/session.json            (persistent, written by `login` command)
  4. None                         (unauthenticated requests)
```

The token is sent as:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Token lifecycle

1. **User** logs into lettucemeet.com in a browser
2. **User** copies the `akoko:session_token` value from Local Storage
3. **User** runs `uv run python main.py login "<token>"`
4. **Token** is saved to `data/session.json`
5. **Agent** picks it up automatically via `load_token()` in `config.py`
6. Token expires after some period -- user must repeat steps 2-3

---

## What the User Must Do (for the Agent to Work)

For the AI agent (Pi) to be able to run commands like `show`, `create`, `overlap`:

1. **Browser** -- Log into [lettucemeet.com](https://lettucemeet.com)
2. **Extract token** -- Open DevTools > Application > Cookies >
   `lettucemeet.com` > `akoko:session_token` > Copy value
3. **Save token** -- Run:
   ```bash
   uv run python main.py login "<paste-token-here>"
   ```
4. **Done** -- The agent can now use all commands. Token persists in
   `data/session.json`.

If the token expires, repeat step 2-3. No other setup is needed.

---

## CLI Command Map

```
lettucemeet
  |-- login <token>        # Save a session token (one-time setup)
  |-- create               # Create a new poll event
  |   --title
  |   --description
  |   --dates
  |   --start-time
  |   --end-time
  |   --timezone
  |-- show <event-id>      # View event + all responses
  |-- respond <event-id>   # Submit availability
  |   --name
  |   --email
  |   --slots
  |-- overlap <event-id>   # Compute best meeting times
```

---

## Key Files

| File | Role |
|---|---|
| `src/lettucemeet_cli/cli.py` | CLI entry point, arg parsing, dispatch |
| `src/lettucemeet_cli/client.py` | GraphQL HTTP client, auth headers, error handling |
| `src/lettucemeet_cli/api.py` | Typed API functions with embedded GraphQL strings |
| `src/lettucemeet_cli/models.py` | Dataclasses: Event, PollResponse, Availability, inputs |
| `src/lettucemeet_cli/overlap.py` | Overlap grid computation and formatting |
| `src/lettucemeet_cli/config.py` | Session file paths, token loading, endpoint URL |
| `data/session.json` | Saved JWT token (gitignored, created by `login`) |

---

## Limitations

- **No official API** -- This uses LettuceMeet's internal GraphQL endpoint.
  If they change their schema, the operations in `api.py` must be updated.
- **Token expiration** -- JWTs expire. The user must provide a fresh token.
- **No calendar sync** -- Google Calendar / Outlook integration is present in the
  web app but not exposed in this CLI.
- **Anonymous responses only** -- The `respond` command submits as an anonymous
  user. Authenticated responses require a different flow (not implemented).
