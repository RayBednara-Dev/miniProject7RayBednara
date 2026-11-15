# MP7 Acceptance Test Transcript

This is the transcript of Claude Code (headless, `claude -p`) using the
registered `practice-hub` MCP server (this repo's `server.py`) to read,
create, and modify a post on the Practice Hub — exactly the acceptance
test described in the assignment.

## Setup

The server was registered once with:

```
claude mcp add practice-hub -e PRACTICE_API_URL=https://practice.fhsucyber.com -e PRACTICE_API_TOKEN=<token> -- python C:/Users/raybe/Documents/INF601/MP7-RayBednara/server.py
```

`claude mcp list` confirmed it as connected:

```
practice-hub: python C:/Users/raybe/Documents/INF601/MP7-RayBednara/server.py - √ Connected
```

## Prompt given to Claude Code

> Using ONLY the practice-hub MCP server tools, do the following in order
> and narrate each step: 1) List my posts (mine=true) and show what's
> there before you start. 2) Create a new post titled 'MP7 MCP Acceptance
> Test' with body '...' and tag 'mp7'. 3) Update that same post: change
> its title to 'MP7 MCP Acceptance Test (updated)' and body to '...'.
> 4) Fetch the post by id again to confirm the update stuck. 5) Finally,
> delete that test post with delete_post so it doesn't clutter the hub,
> and confirm the deletion succeeded.

Run with:

```
claude -p "<prompt above>" \
  --allowedTools "mcp__practice-hub__list_posts" "mcp__practice-hub__create_post" \
                 "mcp__practice-hub__update_post" "mcp__practice-hub__get_post" \
                 "mcp__practice-hub__delete_post" \
  --output-format stream-json --verbose
```

## Tool calls made by Claude Code, in order

**Step 1 — read (`list_posts`)**

```
Tool call: mcp__practice-hub__list_posts
Input:  {"mine": true}
Result: [
  {"id": 12, "title": "Week 3 lab", "body": "My first created post.", ...}
]
```

**Step 2 — create (`create_post`)**

```
Tool call: mcp__practice-hub__create_post
Input:  {"title": "MP7 MCP Acceptance Test",
         "body": "This post was created by Claude Code through the practice-hub MCP server as part of the MP7 acceptance test.",
         "tags": ["mp7"]}
Result: {"id": 66, "title": "MP7 MCP Acceptance Test", ...}
```

Claude Code's narration: *"Created as post id 66. Step 3: updating its
title and body."*

**Step 3 — modify (`update_post`)**

```
Tool call: mcp__practice-hub__update_post
Input:  {"post_id": 66,
         "title": "MP7 MCP Acceptance Test (updated)",
         "body": "This post was updated by Claude Code through the practice-hub MCP server to demonstrate the update_post tool."}
Result: {"id": 66, "title": "MP7 MCP Acceptance Test (updated)", ...,
         "updated_at": "2026-11-15T20:18:34.171947"}
```

**Step 4 — confirm (`get_post`)**

```
Tool call: mcp__practice-hub__get_post
Input:  {"post_id": 66}
Result: {"id": 66, "title": "MP7 MCP Acceptance Test (updated)",
         "body": "This post was updated by Claude Code through the practice-hub MCP server to demonstrate the update_post tool.", ...}
```

Claude Code's narration: *"Confirmed: title and body match the update."*

**Step 5 — cleanup (`delete_post`)**

```
Tool call: mcp__practice-hub__delete_post
Input:  {"post_id": 66}
Result: {"success": true}
```

## Final summary printed by Claude Code

> All five steps completed successfully:
>
> 1. **Listed posts (mine=true)** — found existing post(s), including id 12 "Week 3 lab".
> 2. **Created** post id 66, "MP7 MCP Acceptance Test", tagged `mp7`.
> 3. **Updated** id 66 → title "MP7 MCP Acceptance Test (updated)", new body.
> 4. **Re-fetched** id 66 — confirmed title/body match the update.
> 5. **Deleted** id 66 — `{"success": true}`.

This confirms the full round trip — **read → create → modify → verify →
delete** — all performed by Claude Code exclusively through the tools
exposed by this repo's `server.py` MCP server, with no direct calls to
`requests`/`httpx` from the chat session itself.

Note: an earlier dry run of this same test left a duplicate post (id 65)
on the hub that an earlier version of the prompt didn't clean up; it was
removed by hand afterward so the hub is back to its original state.
