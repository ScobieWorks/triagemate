#!/usr/bin/env python3
"""Command‑line interface for TriageMate.

The CLI accepts a set of flags that trigger the different triage actions:

* ``--label-new`` – Detects simple keywords in the issue body and applies
  corresponding labels.
* ``--close-stale`` – Closes issues that have not been updated for a
  configurable number of days.
* ``--summary`` – Prints a JSON summary of the current issue state.
* ``--suggest`` – Prints a suggested priority for each open issue.

All actions require a ``GITHUB_TOKEN`` environment variable.
"""

import argparse
import os
import sys

from .core import (
    get_issues,
    label_issue,
    close_issue,
    is_stale,
    suggest_priority,
    generate_summary,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="TriageMate: lightweight issue triage tool.")
    parser.add_argument("--owner", required=True, help="GitHub repository owner")
    parser.add_argument("--repo", required=True, help="GitHub repository name")
    parser.add_argument("--stale-days", type=int, default=30, help="Days after which an issue is considered stale")
    parser.add_argument("--label-new", action="store_true", help="Label new issues based on content")
    parser.add_argument("--close-stale", action="store_true", help="Close stale issues")
    parser.add_argument("--summary", action="store_true", help="Print triage summary")
    parser.add_argument("--suggest", action="store_true", help="Suggest priority tags for open issues")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        sys.exit(1)

    issues = get_issues(args.owner, args.repo, token)

    if args.label_new:
        for issue in issues:
            if "labels" in issue and len(issue["labels"]) == 0:
                body = issue.get("body", "").lower()
                labels = []
                if "bug" in body:
                    labels.append("bug")
                if "feature" in body or "enhancement" in body:
                    labels.append("enhancement")
                if "question" in body:
                    labels.append("question")
                if labels:
                    label_issue(args.owner, args.repo, issue["number"], labels, token)
                    print(f"Labeled issue #{issue['number']} with {labels}")

    if args.close_stale:
        for issue in issues:
            if is_stale(issue, args.stale_days):
                close_issue(args.owner, args.repo, issue["number"], token)
                print(f"Closed stale issue #{issue['number']}")

    if args.summary:
        summary = generate_summary(issues)
        print(summary)

    if args.suggest:
        for issue in issues:
            priority = suggest_priority(issue)
            print(f"Issue #{issue['number']} priority: {priority}")


if __name__ == "__main__":
    main()
