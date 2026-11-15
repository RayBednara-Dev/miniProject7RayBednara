### INF601 - Advanced Programming in Python
### Ray Bednara
### Mini Project 7

# MP7 - Practice Hub MCP Server

A Model Context Protocol (MCP) server, built with **FastMCP** from the
official `mcp` Python SDK, that wraps the Practice Hub REST API from
Mini Project 1. It lets an MCP client — in this case Claude Code — read,
create, update, and delete your own posts on the Practice Hub through a
small set of documented tools, instead of calling the API by hand.

## Description

`server.py` exposes five tools over MCP:

| Tool | Practice Hub endpoint | What it does |
|---|---|---|
| `list_posts(mine, tag)` | `GET /api/v1/posts` | List posts, optionally filtered to only your own (`mine=True`) and/or by `tag` |
| `get_post(post_id)` | `GET /api/v1/posts/{id}` | Fetch a single post by id |
| `create_post(title, body, tags)` | `POST /api/v1/posts` | Create a new post owned by you |
| `update_post(post_id, title, body, tags)` | `PATCH /api/v1/posts/{id}` | Edit one of your own posts |
| `delete_post(post_id)` | `DELETE /api/v1/posts/{id}` | Delete one of your own posts |

Every tool calls the Practice Hub API over HTTP with `httpx`, using a
Bearer token read from the environment. API errors (400/401/403/404/422,
etc.) and network failures are caught and returned as a plain
`{"error": "..."}` message instead of raising an exception and crashing
the server — for example, trying to edit or delete someone else's post
returns a clear "Forbidden" message (403), and fetching a missing post
returns a clear "Not found" message (404).

## Getting Started

### Dependencies

```
pip install -r requirements.txt
```

This installs `mcp[cli]` (pinned to the 1.x line, which still has
`FastMCP` at `mcp.server.fastmcp`), `httpx`, and `python-dotenv`.

### Environment variables

The server reads its configuration from the environment — **the token
is never hard-coded**:

| Variable | Required | Meaning |
|---|---|---|
| `PRACTICE_API_URL` | No (defaults to `https://practice.fhsucyber.com`) | Base URL of the Practice Hub API |
| `PRACTICE_API_TOKEN` | Yes | Your Practice Hub bearer token |

For local testing you can copy `.env.example` to `.env` and fill in your
own token — `server.py` calls `load_dotenv()` on startup, and `.env` is
listed in `.gitignore` so it's never committed. Otherwise, set the
variables directly in your shell:

```powershell
# Windows PowerShell
$env:PRACTICE_API_URL = "https://practice.fhsucyber.com"
$env:PRACTICE_API_TOKEN = "your-token-here"
```

```bash
# macOS/Linux
export PRACTICE_API_URL="https://practice.fhsucyber.com"
export PRACTICE_API_TOKEN="your-token-here"
```

### Registering the server with Claude Code

Register it as a stdio MCP server, passing the environment variables
with `-e` so the token never has to be typed into a config file by hand:

```
claude mcp add practice-hub -e PRACTICE_API_URL=https://practice.fhsucyber.com -e PRACTICE_API_TOKEN=your-token-here -- python C:/Users/raybe/Documents/INF601/MP7-RayBednara/server.py
```

(Use the full absolute path to `server.py` so the command works no
matter what directory Claude Code is started from.)

Verify it connected:

```
claude mcp list
```

which should show:

```
practice-hub: python C:/Users/raybe/Documents/INF601/MP7-RayBednara/server.py - √ Connected
```

### Running it directly (without Claude Code)

```
python server.py
```

This starts the server on stdio, waiting for an MCP client to connect
(it won't print anything on its own — that's expected for stdio
transport).

## Acceptance test

The acceptance test is: **Claude Code, using this server, reads your
posts, creates a new post, and modifies an existing post.**

With the server registered as shown above, this can be run from an
interactive Claude Code session simply by asking it to use the
`practice-hub` tools, e.g.:

> "Using the practice-hub MCP tools: list my posts, create a new post
> called 'Hello from MCP', then update that post's title."

For a reproducible, headless run (what was actually used to produce the
transcript in this repo), it was driven non-interactively:

```
claude -p "Using ONLY the practice-hub MCP server tools: 1) list my posts (mine=true), 2) create a new post titled 'MP7 MCP Acceptance Test', 3) update that post's title/body, 4) fetch it again to confirm the update, 5) delete the test post." \
  --allowedTools "mcp__practice-hub__list_posts" "mcp__practice-hub__create_post" "mcp__practice-hub__update_post" "mcp__practice-hub__get_post" "mcp__practice-hub__delete_post"
```

The full transcript of this run — every tool call, its input, and the
API's response, plus Claude Code's narration and final summary — is in
[`transcript.md`](transcript.md) in this repo. It shows the complete
round trip: list → create (post id 66) → update → get (confirms the
update stuck) → delete (cleanup).

## Project structure

```
MP7-RayBednara/
├── server.py          # the FastMCP server (the deliverable)
├── requirements.txt
├── .env.example        # template for local env vars (copy to .env)
├── .gitignore          # ignores .env, __pycache__, etc.
├── transcript.md        # acceptance test transcript
└── README.md
```

## AI Usage

Claude Code was used throughout this project:
- To write `server.py` (the FastMCP server, its five tools, and the
  shared `_request` helper that normalizes Practice Hub API errors into
  clear `{"error": ...}` messages).
- To scaffold `requirements.txt`, `.gitignore`, `.env.example`, and this
  README.
- To run `claude mcp add` to register the server with Claude Code, and
  to drive the headless acceptance test (`claude -p ...`) whose output
  is recorded verbatim in `transcript.md`.

All API design choices (which endpoints map to which tools, the error
handling strategy, reading config from `PRACTICE_API_URL` /
`PRACTICE_API_TOKEN`) were reviewed and adjusted by the author; the
Practice Hub endpoint behavior itself was taken directly from the
working `client.py` built by hand in Mini Project 1.

## Authors

Ray Bednara (ray.bednara@gmail.com)

## License

This project is licensed under the [NAME HERE] License - see the
LICENSE.md file for details.
