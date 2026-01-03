from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Literal

import requests
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from dev_tools.cli_utils import _die, _die_from, read_json_dict, show_help_callback
from dev_tools.paths import get_default_config_path

# Comment type constants
COMMENT_TYPE_ISSUE = "issue_comment"
COMMENT_TYPE_REVIEW = "review_comment"
COMMENT_TYPE_PR_REVIEW = "review"

# Emoji mappings for rich formatting
_REACTION_EMOJI = {
    "+1": "👍",
    "-1": "👎",
    "laugh": "😄",
    "confused": "😕",
    "heart": "❤️",
    "hooray": "🎉",
    "eyes": "👀",
    "rocket": "🚀",
}

_COMMENT_TYPE_EMOJI = {
    COMMENT_TYPE_ISSUE: "📝",
    COMMENT_TYPE_REVIEW: "💬",
    COMMENT_TYPE_PR_REVIEW: "✅",
}

app = typer.Typer(help="GitHub commands")


@app.callback(invoke_without_command=True)
def _github_root(ctx: typer.Context) -> None:
    """
    Print the command help and exit if no subcommand was invoked.
    """
    show_help_callback(ctx)


def _get_github_token() -> str:
    """
    Retrieve the GitHub token, preferring environment variables and falling back to the default config file.

    Looks for GITHUB_TOKEN then GH_TOKEN in the environment; if neither is set, reads
    ./.sdt/configs/config.json and uses the value at key `github.token`. Exits the process with an error message if no
    valid token is found.

    Returns:
        str: The GitHub token with surrounding whitespace removed.
    """
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()

    config_path = get_default_config_path()
    if not config_path.exists():
        _die(
            "Error: Missing GitHub token. Set GITHUB_TOKEN (recommended) or GH_TOKEN, "
            "or store it in ./.sdt/configs/config.json at key github.token.",
        )

    data = read_json_dict(config_path, file_type="config file")
    github = data.get("github")
    if not isinstance(github, dict):
        _die(
            "Error: Missing GitHub token. Set GITHUB_TOKEN (recommended) or GH_TOKEN, "
            "or store it in ./.sdt/configs/config.json at key github.token.",
        )

    token_value = github.get("token")
    if not isinstance(token_value, str) or not token_value.strip():
        _die(
            "Error: Missing GitHub token. Set GITHUB_TOKEN (recommended) or GH_TOKEN, "
            "or store it in ./.sdt/configs/config.json at key github.token.",
        )

    return token_value.strip()


def _get_default_github_user() -> str:
    """
    Return the default GitHub username from the local config file.

    Reads ./.sdt/configs/config.json and returns the value of `github.user` if present,
    falling back to `github.login` when `github.user` is missing or empty. If the
    config file, the `github` object, or both username fields are missing or empty,
    the process exits with an error message.

    Returns:
        str: The GitHub username with surrounding whitespace removed.
    """
    config_path = get_default_config_path()
    if not config_path.exists():
        _die(
            "Error: Missing GitHub user. Pass --user, or store it in ./.sdt/configs/config.json at key github.user.",
        )

    data = read_json_dict(config_path, file_type="config file")
    github = data.get("github")
    if not isinstance(github, dict):
        _die(
            "Error: Missing GitHub user. Pass --user, or store it in ./.sdt/configs/config.json at key github.user.",
        )

    user_value = github.get("user")
    if not isinstance(user_value, str) or not user_value.strip():
        user_value = github.get("login")

    if not isinstance(user_value, str) or not user_value.strip():
        _die(
            "Error: Missing GitHub user. Pass --user, or store it in ./.sdt/configs/config.json at key github.user.",
        )

    return user_value.strip()


_GITHUB_SSH_RE = re.compile(r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$")
_GITHUB_HTTPS_RE = re.compile(r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$")


def _run_git_config_origin_url() -> str:
    """
    Retrieve the Git remote 'origin' URL from the local repository.

    Returns:
        str: The origin remote URL as a non-empty string.
    """
    try:
        proc = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        _die_from(exc, f"Error running git: {exc}")

    if proc.returncode != 0:
        _die("Error: Could not determine GitHub repo (missing git remote 'origin'?)")

    url = proc.stdout.strip()
    if not url:
        _die("Error: Could not determine GitHub repo (empty git remote 'origin' URL)")
    return url


def _detect_repo_slug() -> str:
    """
    Determine the repository slug in the form "owner/repo" from the git remote origin URL.

    If the origin URL is not a supported GitHub SSH or HTTPS format, the process exits with an error message.

    Returns:
        repo_slug (str): Repository slug as "owner/repo".
    """
    url = _run_git_config_origin_url()

    m = _GITHUB_SSH_RE.fullmatch(url)
    if m:
        return f"{m.group('owner')}/{m.group('repo')}"

    m = _GITHUB_HTTPS_RE.fullmatch(url)
    if m:
        return f"{m.group('owner')}/{m.group('repo')}"

    _die(f"Error: Unsupported git remote URL for GitHub: {url}")


@dataclass(frozen=True)
class _GitHubResponse:
    status_code: int
    json_data: Any
    links: dict[str, dict[str, str]]


@dataclass(frozen=True)
class PRComment:
    """
    Represents a pull request comment with normalized fields.
    """

    type: str
    id: int
    created_at: str
    updated_at: str
    user: str
    body: str
    html_url: str
    author_association: str
    reactions: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        """Convert the comment to a dictionary for JSON serialization."""
        return {
            "type": self.type,
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "user": self.user,
            "body": self.body,
            "html_url": self.html_url,
            "author_association": self.author_association,
            "reactions": self.reactions,
        }


def _format_comments_json(comments: list[PRComment]) -> str:
    """
    Format comments as pretty-printed JSON.

    Parameters:
        comments (list[PRComment]): List of comments to format.

    Returns:
        str: JSON string with 2-space indentation.
    """
    comments_dicts = [comment.to_dict() for comment in comments]
    return json.dumps(comments_dicts, indent=2)


def _format_comments_plain(comments: list[PRComment]) -> str:
    """
    Format comments as plain text with simple headers and separators.

    Parameters:
        comments (list[PRComment]): List of comments to format.

    Returns:
        str: Plain text representation with one comment per section.
    """
    sections = []
    for comment in comments:
        header = f"{comment.type} {comment.created_at} {comment.user}"
        sections.append(f"{header}\n{comment.body}")
    return "\n---\n".join(sections)


def _format_comments_rich(comments: list[PRComment]) -> None:
    """
    Display comments using rich terminal formatting with colors, emoji, and panels.

    Parameters:
        comments (list[PRComment]): List of comments to display.
    """
    console = Console()

    for comment in comments:
        # Build header with metadata
        header = Text()
        header.append(f"{_COMMENT_TYPE_EMOJI.get(comment.type, '💬')} ", style="bold")
        header.append(f"{comment.type}", style="bold cyan")
        header.append(f" #{comment.id}", style="dim")
        header.append(f" • {comment.created_at}", style="dim")

        # Build user line
        user_line = Text()
        user_line.append("👤 ", style="bold")
        user_line.append(f"{comment.user}", style="bold green")
        user_line.append(f" ({comment.author_association})", style="dim")
        if comment.html_url:
            user_line.append(" • 🔗 ", style="dim")
            user_line.append(comment.html_url.replace("https://", ""), style="blue underline")

        # Build reactions line
        reactions_line = Text()
        has_reactions = False
        for key, emoji in _REACTION_EMOJI.items():
            count = comment.reactions.get(key, 0)
            if count > 0:
                if has_reactions:
                    reactions_line.append("  ")
                reactions_line.append(f"{emoji} {count}", style="yellow")
                has_reactions = True

        # Build content as a single Text object
        content = Text()
        content.append_text(header)
        content.append("\n")
        content.append_text(user_line)
        content.append("\n")
        if has_reactions:
            content.append_text(reactions_line)
            content.append("\n")
        content.append("\n")
        content.append(comment.body)

        # Render as panel
        panel = Panel(
            content,
            border_style="blue",
            padding=(0, 1),
        )
        console.print(panel)
        console.print()  # Empty line between comments


def _github_get(url: str, *, token: str, params: dict[str, Any] | None = None) -> _GitHubResponse:
    """
    Perform an authenticated GET request to the GitHub API and return structured response data.

    Performs a GET to `url` using `token` for Bearer authentication, attempts to parse the response body as JSON
    (returns `None` for `json_data` if parsing fails), and extracts response links for pagination. On common HTTP error
    statuses (401, 403, 404) or other 4xx/5xx responses the function exits with a descriptive error message.

    Parameters:
        url (str): Full GitHub API URL to request.
        token (str): GitHub API token used for Bearer authentication.
        params (dict[str, Any] | None): Optional query parameters to include in the request.

    Returns:
        _GitHubResponse: Dataclass with fields:
            - status_code: HTTP status code from the response.
            - json_data: Parsed JSON payload, or `None` if the body could not be parsed as JSON.
            - links: Dictionary of parsed `Link` headers useful for pagination (empty dict if none).
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "sdt",
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
    except Exception as exc:
        _die_from(exc, f"Error: Request failed: {exc}")

    try:
        payload = resp.json()
    except Exception:
        payload = None

    if resp.status_code == 401:
        _die("Error: GitHub authentication failed (401). Check your token.")
    if resp.status_code == 403:
        _die("Error: GitHub request forbidden (403). Check token scopes and rate limits.")
    if resp.status_code == 404:
        _die("Error: GitHub resource not found (404). Check repo/PR id permissions.")
    if resp.status_code >= 400:
        msg = None
        if isinstance(payload, dict):
            msg = payload.get("message")
        _die(f"Error: GitHub API error ({resp.status_code}){': ' + msg if msg else ''}")

    return _GitHubResponse(status_code=resp.status_code, json_data=payload, links=getattr(resp, "links", {}) or {})


def _paginate_json(
    url: str,
    *,
    token: str,
    params: dict[str, Any] | None = None,
    limit: int | None = None,
) -> list[Any]:
    """
    Fetches and aggregates paginated JSON array responses from a GitHub API endpoint.

    Parameters:
        url (str): The API endpoint URL to request.
        token (str): GitHub authentication token to include in requests.
        params (dict[str, Any] | None): Additional query parameters merged into each request.
            `per_page` is set to 100 by default and `page` is managed internally.
        limit (int | None): Maximum number of items to return; if provided, the result is truncated to this many items.

    Returns:
        list[Any]: Combined list of items from the paginated responses, truncated to `limit` when specified.

    Notes:
        The function expects each page's JSON payload to be an array; it exits the program with an error if a non-list
        JSON response is received.
    """
    items: list[Any] = []
    page = 1

    while True:
        page_params: dict[str, Any] = {}
        if params:
            page_params.update(params)
        page_params.setdefault("per_page", 100)
        page_params["page"] = page

        data = _github_get(url, token=token, params=page_params)
        if not isinstance(data.json_data, list):
            _die(f"Error: Unexpected API response shape for {url} (expected list).")

        items.extend(data.json_data)
        if limit is not None and len(items) >= limit:
            return items[:limit]

        has_next = "next" in data.links
        if not data.json_data or not has_next:
            return items

        page += 1


def _paginate_search_issues(
    *,
    token: str,
    query: str,
    limit: int,
) -> list[dict[str, Any]]:
    """
    Fetch up to `limit` search results from the GitHub Search Issues API for the given query, following pagination as
    needed.

    Parameters:
        token (str): GitHub API token used for authenticated requests.
        query (str): GitHub search query string (as accepted by the search/issues endpoint).
        limit (int): Maximum number of result items to return; function returns at most this many items.

    Returns:
        list[dict[str, Any]]: A list of raw issue/search result objects as returned by the API, in the order received.
        (up to `limit` items).
    """
    url = "https://api.github.com/search/issues"
    items: list[dict[str, Any]] = []
    page = 1

    while True:
        params: dict[str, Any] = {
            "q": query,
            "per_page": min(100, max(1, limit - len(items))),
            "page": page,
        }
        data = _github_get(url, token=token, params=params)
        if not isinstance(data.json_data, dict):
            _die("Error: Unexpected API response shape for search/issues (expected object).")
        raw_items = data.json_data.get("items")
        if not isinstance(raw_items, list):
            _die("Error: Unexpected API response shape for search/issues (missing items).")

        for raw in raw_items:
            if isinstance(raw, dict):
                items.append(raw)
            if len(items) >= limit:
                return items[:limit]

        has_next = "next" in data.links
        if not raw_items or not has_next:
            return items

        page += 1


def _execute_list_mode(*, user: str | None, state: Literal["open", "closed", "all"], limit: int) -> None:
    """
    List pull requests in the current repository authored by a given user.

    Parameters:
        user (str | None): GitHub username to filter by; if None, the default configured GitHub user is used.
        state (Literal["open", "closed", "all"]): Which PR states to include; use "all" to include both open and closed.
        limit (int): Maximum number of PRs to retrieve; stops listing after this many results.
    """
    token = _get_github_token()
    repo = _detect_repo_slug()
    if user is None:
        user = _get_default_github_user()
    q = f"type:pr repo:{repo} author:{user}"
    if state != "all":
        q = f"{q} state:{state}"

    results = _paginate_search_issues(token=token, query=q, limit=limit)
    for item in results:
        number = item.get("number")
        title = item.get("title") or ""
        pr_state = item.get("state") or ""
        html_url = item.get("html_url") or ""
        typer.echo(f"#{number} {title} ({pr_state}) {html_url}".rstrip())


def _execute_details_mode(*, pr_id: int, output_format: Literal["json", "rich", "plain"]) -> None:
    """
    Display all comments for a specific pull request from the repository's GitHub API in the chosen format.

    Fetches issue comments, inline review comments, and pull request reviews for the given PR,
    normalizes and sorts them by creation time, and renders the combined comment list as JSON
    (`"json"`), a rich-formatted view (`"rich"`), or plain text (`"plain"`).

    Parameters:
        pr_id (int): The pull request number/ID to show comments for.
        output_format (Literal["json", "rich", "plain"]): Output format: `"json"` for
            pretty-printed JSON, `"rich"` for a Rich panel view, or `"plain"` for simple
            plain-text output.
    """
    token = _get_github_token()
    repo = _detect_repo_slug()
    owner, name = repo.split("/", 1)

    # Build API URLs
    base_url = f"https://api.github.com/repos/{owner}/{name}"
    issue_comments_url = f"{base_url}/issues/{pr_id}/comments"
    review_comments_url = f"{base_url}/pulls/{pr_id}/comments"
    reviews_url = f"{base_url}/pulls/{pr_id}/reviews"

    # Fetch all comment types
    issue_comments = _paginate_json(issue_comments_url, token=token)
    review_comments = _paginate_json(review_comments_url, token=token)
    reviews = _paginate_json(reviews_url, token=token)

    # Process and combine all comments
    combined: list[PRComment] = []
    combined.extend(_process_comments(issue_comments, COMMENT_TYPE_ISSUE))
    combined.extend(_process_comments(review_comments, COMMENT_TYPE_REVIEW))
    combined.extend(_process_comments(reviews, COMMENT_TYPE_PR_REVIEW, filter_empty=True))

    # Sort by creation time
    combined.sort(key=lambda c: c.created_at)

    # Format and display based on selected format
    if output_format == "json":
        typer.echo(_format_comments_json(combined))
    elif output_format == "rich":
        _format_comments_rich(combined)
    elif output_format == "plain":
        typer.echo(_format_comments_plain(combined))


@app.command("prs")
def prs(
    pr_id: int | None = typer.Option(None, "--id", "-i", help="Pull request number/ID to show details for"),  # noqa: B008
    user: str | None = typer.Option(None, "--user", "-u", help="GitHub login to filter PRs by author (list mode)"),  # noqa: B008
    state: Literal["open", "closed", "all"] = typer.Option("open", "--state", help="Filter by PR state (list mode)"),  # noqa: B008
    limit: int = typer.Option(50, "--limit", min=1, max=500, help="Max number of PRs to print (list mode)"),  # noqa: B008
    output_format: Literal["json", "rich", "plain"] = typer.Option(  # noqa: B008
        "json",
        "--format",
        "-f",
        help="Output format for PR details (details mode): json, rich, or plain",
    ),
) -> None:
    """
    List pull requests or show detailed comments for a specific PR.

    Without --id: Lists pull requests authored by a user in the current repository.
    With --id: Shows all comments for the specified pull request.

    Examples:
        sdt github prs                           # List open PRs for default user
        sdt github prs --user alice --state all  # List all PRs for alice
        sdt github prs --id 123                  # Show comments for PR #123
        sdt github prs -i 123 --format rich      # Show PR #123 with colors (short form)
    """
    if pr_id is None:
        _execute_list_mode(user=user, state=state, limit=limit)
    else:
        _execute_details_mode(pr_id=pr_id, output_format=output_format)


def _normalize_comment(comment: dict[str, Any], *, comment_type: str) -> PRComment:
    """
    Convert a raw GitHub API comment object into a normalized PRComment instance.

    Parameters:
        comment: Raw comment object returned by the GitHub API; fields may be missing or
            malformed.
        comment_type: Label assigned to the resulting comment's `type` field (for example,
            "issue_comment" or "review_comment").

    Returns:
        PRComment: A PRComment populated from `comment`, using empty strings or zero values
            when expected fields are missing or invalid.
    """
    # Extract user login
    user_obj = comment.get("user")
    user_login = ""
    if isinstance(user_obj, dict):
        login = user_obj.get("login")
        if isinstance(login, str):
            user_login = login

    # Extract basic fields
    comment_id = comment.get("id", 0)
    if not isinstance(comment_id, int):
        comment_id = 0

    created_at = comment.get("created_at", "")
    if not isinstance(created_at, str):
        created_at = ""

    updated_at = comment.get("updated_at", "")
    if not isinstance(updated_at, str):
        updated_at = ""

    body = comment.get("body") or ""
    if not isinstance(body, str):
        body = str(body)

    html_url = comment.get("html_url", "")
    if not isinstance(html_url, str):
        html_url = ""

    author_association = comment.get("author_association", "")
    if not isinstance(author_association, str):
        author_association = ""

    # Extract reactions
    reactions_obj = comment.get("reactions", {})
    reactions: dict[str, int] = {}
    if isinstance(reactions_obj, dict):
        for key in _REACTION_EMOJI:
            value = reactions_obj.get(key, 0)
            if isinstance(value, int):
                reactions[key] = value

    return PRComment(
        type=comment_type,
        id=comment_id,
        created_at=created_at,
        updated_at=updated_at,
        user=user_login,
        body=body,
        html_url=html_url,
        author_association=author_association,
        reactions=reactions,
    )


def _normalize_review_timestamps(review: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize review's submitted_at timestamp to created_at/updated_at fields.

    Parameters:
        review (dict[str, Any]): Review object from GitHub API.

    Returns:
        dict[str, Any]: Review with normalized timestamp fields.
    """
    normalized = dict(review)
    submitted_at = review.get("submitted_at", "")
    normalized["created_at"] = submitted_at
    normalized["updated_at"] = submitted_at
    return normalized


def _process_comments(items: list[Any], comment_type: str, filter_empty: bool = False) -> list[PRComment]:
    """
    Process API response items into PRComment instances.

    Parameters:
        items (list[Any]): List of comment/review objects from GitHub API.
        comment_type (str): Type of comment (issue_comment, review_comment, review).
        filter_empty (bool): If True, filter out items without body text.

    Returns:
        list[PRComment]: List of normalized comment instances.
    """
    comments: list[PRComment] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if filter_empty and not item.get("body"):
            continue

        # Normalize reviews to have created_at/updated_at
        if comment_type == COMMENT_TYPE_PR_REVIEW:
            item = _normalize_review_timestamps(item)

        comments.append(_normalize_comment(item, comment_type=comment_type))
    return comments
