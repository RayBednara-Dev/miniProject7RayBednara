#INF601 - Advanced Programming in Python
#Ray Bednara
#Mini Project 7 - MCP Server for the Practice Hub API
#
# This server wraps the Practice Hub REST API (the same API used by hand
# in Mini Project 1) as a Model Context Protocol (MCP) server, so that an
# MCP client such as Claude Code can list, read, create, update, and
# delete posts on the Practice Hub through a set of well-documented tools.

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load a local .env file if one is present (handy for local testing).
# This never overrides variables already set in the real environment.
load_dotenv()

# --- Configuration: read from the environment, never hard-code secrets ---
PRACTICE_API_URL = os.environ.get(
    "PRACTICE_API_URL", "https://practice.fhsucyber.com"
).rstrip("/")
PRACTICE_API_TOKEN = os.environ.get("PRACTICE_API_TOKEN")

mcp = FastMCP("practice-hub")

# Human-readable labels for the error codes the Practice Hub API returns.
_ERROR_LABELS = {
    400: "Bad request",
    401: "Unauthorized - check that PRACTICE_API_TOKEN is set correctly",
    402: "Payment required",
    403: "Forbidden - you can only edit or delete your own posts",
    404: "Not found - no post exists with that id",
    422: "Unprocessable entity - check the fields you sent",
}


def _headers() -> dict:
    if not PRACTICE_API_TOKEN:
        raise RuntimeError(
            "PRACTICE_API_TOKEN is not set. Set it in the environment "
            "(see README.md) before using this server."
        )
    return {"Authorization": f"Bearer {PRACTICE_API_TOKEN}"}


def _request(method: str, path: str, **kwargs) -> dict:
    """Call the Practice Hub API and turn any error into a plain dict

    instead of letting an exception crash the MCP server. Both network
    failures and API error responses (400/401/403/404/422/etc.) are
    normalized into {"error": "<clear message>"} so the model always
    gets something sensible back.
    """
    url = f"{PRACTICE_API_URL}{path}"

    try:
        headers = _headers()
    except RuntimeError as exc:
        return {"error": str(exc)}

    try:
        resp = httpx.request(method, url, headers=headers, timeout=15, **kwargs)
    except httpx.RequestError as exc:
        return {"error": f"Network error calling {method} {url}: {exc}"}

    label = _ERROR_LABELS.get(resp.status_code)
    if label:
        try:
            detail = resp.json().get("message", resp.text)
        except ValueError:
            detail = resp.text
        return {
            "error": f"{label} ({resp.status_code} on {method} {path}): {detail}"
        }

    if resp.status_code >= 400:
        return {
            "error": f"API error {resp.status_code} on {method} {path}: {resp.text}"
        }

    if resp.status_code == 204 or not resp.content:
        return {"success": True}

    try:
        return resp.json()
    except ValueError:
        return {"raw": resp.text}


@mcp.tool()
def list_posts(mine: bool = False, tag: Optional[str] = None) -> dict:
    """List posts on the Practice Hub.

    Use this to browse what's on the hub. Set mine=True to list only the
    posts authored by the current user (identified by PRACTICE_API_TOKEN).
    Optionally filter the results by a tag.

    Args:
        mine: If True, only return posts owned by the authenticated user.
        tag: If given, only return posts that have this tag.
    """
    params = {"mine": mine}
    if tag:
        params["tag"] = tag
    return _request("GET", "/api/v1/posts", params=params)


@mcp.tool()
def get_post(post_id: int) -> dict:
    """Fetch a single post from the Practice Hub by its id.

    Returns a clear error (instead of crashing) if the post does not
    exist (404) or the request is otherwise rejected by the API.

    Args:
        post_id: The numeric id of the post to retrieve.
    """
    return _request("GET", f"/api/v1/posts/{post_id}")


@mcp.tool()
def create_post(title: str, body: str = "", tags: Optional[list[str]] = None) -> dict:
    """Create a new post on the Practice Hub, owned by the current user.

    Args:
        title: The title of the new post.
        body: The text content of the post. Defaults to an empty string.
        tags: Optional list of tag strings to attach to the post.
    """
    payload = {"title": title, "body": body, "tags": tags or []}
    return _request("POST", "/api/v1/posts", json=payload)


@mcp.tool()
def update_post(
    post_id: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> dict:
    """Edit one of your own posts on the Practice Hub.

    Only the fields you provide are changed; omit a field to leave it
    as-is. The Practice Hub only lets you edit posts you own - trying to
    edit someone else's post returns a 403 Forbidden, and editing a post
    that doesn't exist returns a 404 Not found. Both are reported back
    as a clear {"error": ...} message rather than raising an exception.

    Args:
        post_id: The id of the post to update.
        title: New title, if changing.
        body: New body text, if changing.
        tags: New list of tags, if changing (replaces the existing tags).
    """
    payload = {}
    if title is not None:
        payload["title"] = title
    if body is not None:
        payload["body"] = body
    if tags is not None:
        payload["tags"] = tags
    if not payload:
        return {"error": "Nothing to update - provide at least one of title, body, or tags."}
    return _request("PATCH", f"/api/v1/posts/{post_id}", json=payload)


@mcp.tool()
def delete_post(post_id: int) -> dict:
    """Delete one of your own posts on the Practice Hub.

    Deleting a post you don't own returns a 403 Forbidden, and deleting
    a post that doesn't exist returns a 404 Not found; both come back as
    a clear error message instead of an unhandled exception.

    Args:
        post_id: The id of the post to delete.
    """
    return _request("DELETE", f"/api/v1/posts/{post_id}")


if __name__ == "__main__":
    mcp.run()
