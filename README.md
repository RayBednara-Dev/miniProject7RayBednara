### INF601 - Advanced Programming in Python
### Ray Bednara
### Mini Project 7


# MP7

An MCP (Model Context Protocol) server that wraps the Practice Hub REST API from
Mini Project 1, so Claude Code can read, create, and modify your own posts on the
hub through a set of defined tools instead of calling the API by hand.

## Description

A FastMCP server, built with the official `mcp` Python SDK, that exposes the
Practice Hub API as MCP tools. An MCP client such as Claude Code can call
`list_posts`, `get_post`, `create_post`, `update_post`, and `delete_post`
directly, with the Practice Hub base URL and bearer token read from the
environment instead of hard-coded.

**Features**
* `list_posts(mine, tag)` &mdash; list posts, optionally filtered to only your own (`mine=True`) and/or by `tag`
* `get_post(post_id)` &mdash; fetch a single post by id
* `create_post(title, body, tags)` &mdash; create a new post owned by you
* `update_post(post_id, title, body, tags)` &mdash; edit one of your own posts
* `delete_post(post_id)` &mdash; delete one of your own posts
* Clear error handling &mdash; API errors (403 on someone else's post, 404 on a
  missing post, etc.) and network failures come back as a plain
  `{"error": "..."}` message instead of crashing the server

**Project structure**
* `server.py` &mdash; the FastMCP server and its five tools (the deliverable)
* `requirements.txt` &mdash; `mcp[cli]`, `httpx`, `python-dotenv`
* `.env.example` &mdash; template for local environment variables (copy to `.env`)
* `transcript.md` &mdash; acceptance test transcript

## Getting Started

### Dependencies

pip install all items found in requirements.txt

### Installing

* Clone or download this repository
* From the project root, create and activate a virtual environment (recommended)
* Install dependencies:
```
pip install -r requirements.txt
```

### Configuration

The server reads its configuration from the environment &mdash; the token is
never hard-coded:

* `PRACTICE_API_URL` &mdash; base URL of the Practice Hub API (defaults to
  `https://practice.fhsucyber.com` if not set)
* `PRACTICE_API_TOKEN` &mdash; your Practice Hub bearer token (required)

For local testing, copy `.env.example` to `.env` and fill in your token &mdash;
`server.py` calls `load_dotenv()` on startup, and `.env` is listed in
`.gitignore` so it's never committed. Otherwise set the variables directly:
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

### Registering with Claude Code

* Register the server as a stdio MCP server, passing the environment variables
  with `-e` so the token never has to be typed into a config file by hand:
```
claude mcp add practice-hub -e PRACTICE_API_URL=https://practice.fhsucyber.com -e PRACTICE_API_TOKEN=your-token-here -- python C:/Users/raybe/Documents/INF601/MP7-RayBednara/server.py
```
  (Use the full absolute path to `server.py` so the command works no matter
  what directory Claude Code is started from.)
* Verify it connected:
```
claude mcp list
```
  which should show `practice-hub: python C:/Users/raybe/Documents/INF601/MP7-RayBednara/server.py - √ Connected`.

### Executing program

* How to run the program
* Step-by-step bullets
```
python server.py
```
* This starts the server on stdio, waiting for an MCP client to connect &mdash;
  it won't print anything on its own, which is expected for stdio transport
* With the server registered, just ask Claude Code to use the tools, e.g.
  "using the practice-hub MCP tools, list my posts and create a new one"

### Acceptance test

The acceptance test is: **Claude Code, using this server, reads your posts,
creates a new post, and modifies an existing post.**

Run it headlessly with:
```
claude -p "Using ONLY the practice-hub MCP server tools: 1) list my posts (mine=true), 2) create a new post titled 'MP7 MCP Acceptance Test', 3) update that post's title/body, 4) fetch it again to confirm the update, 5) delete the test post." \
  --allowedTools "mcp__practice-hub__list_posts" "mcp__practice-hub__create_post" "mcp__practice-hub__update_post" "mcp__practice-hub__get_post" "mcp__practice-hub__delete_post"
```
The full transcript of this run &mdash; every tool call, its input, and the
API's response &mdash; is in [`transcript.md`](transcript.md).

## Authors

Contributors names and contact info

Ray Bednara  (r_bednara@mail.fhsu.edu)


## AI Usage

Claude Code (Anthropic) was used throughout this project to:
* Write `server.py` (the FastMCP server, its five tools, and the shared
  request helper that normalizes Practice Hub API errors into clear
  `{"error": ...}` messages)
* Scaffold `requirements.txt`, `.gitignore`, `.env.example`, and this README
* Run `claude mcp add` to register the server with Claude Code, and drive the
  headless acceptance test (`claude -p ...`) whose output is recorded in
  `transcript.md`

All generated code was reviewed, run, and tested locally by the author before
being committed. The Practice Hub endpoint behavior itself was taken directly
from the working `client.py` built by hand in Mini Project 1.
