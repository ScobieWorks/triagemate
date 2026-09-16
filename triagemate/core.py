"""Core logic for TriageMate.

All functions interact with the GitHub REST API using only the standard
library.  The helper ``_request`` abstracts the HTTP details and handles
authentication via the ``GITHUB_TOKEN``.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

API_URL = "https://api.github.com"


def _request(method: str, url: str, token: str, data=None):
    """Send an HTTP request to the GitHub API.

    Parameters
    ----------
    method: str
        HTTP method (GET, POST, PATCH, etc.).
    url: str
        Full API endpoint.
    token: str
        Personal access token for authentication.
    data: dict | None
        JSON‑serialisable payload for POST/PATCH.
    """
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API error {e.code}: {e.read().decode()}") from e


def get_issues(owner: str, repo: str, token: str, state: str = "open"):
    """Return a list of issues for the given repository."""
    url = f"{API_URL}/repos/{owner}/{repo}/issues?state={state}&per_page=100"
    return _request("GET", url, token)


def label_issue(owner: str, repo: str, issue_number: int, labels, token: str):
    """Add labels to an issue."""
    url = f"{API_URL}/repos/{owner}/{repo}/issues/{issue_number}/labels"
    data = {"labels": labels}
    return _request("POST", url, token, data)


def close_issue(owner: str, repo: str, issue_number: int, token: str):
    """Close an issue."""
    url = f"{API_URL}/repos/{owner}/{repo}/issues/{issue_number}"
    data = {"state": "closed"}
    return _request("PATCH", url, token, data)


def is_stale(issue, stale_days: int) -> bool:
    """Return True if the issue has not been updated for ``stale_days``."""
    updated_at = datetime.fromisoformat(issue["updated_at"].rstrip("Z")).replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - updated_at) > timedelta(days=stale_days)


def suggest_priority(issue) -> str:
    """Return a simple priority string based on labels and comment count."""
    labels = [lbl["name"] for lbl in issue.get("labels", [])]
    comments = issue.get("comments", 0)
    if "bug" in labels and comments > 5:
        return "high"
    if "enhancement" in labels and comments > 3:
        return "medium"
    return "low"


def generate_summary(issues):
    """Return a JSON string summarising the issue list."""
    total = len(issues)
    open_issues = sum(1 for i in issues if i["state"] == "open")
    closed_issues = total - open_issues
    label_counts = {}
    for i in issues:
        for lbl in i.get("labels", []):
            label_counts[lbl["name"]] = label_counts.get(lbl["name"], 0) + 1
    summary = {
        "total_issues": total,
        "open_issues": open_issues,
        "closed_issues": closed_issues,
        "label_counts": label_counts,
    }
    return json.dumps(summary, indent=2)
