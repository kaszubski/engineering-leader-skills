#!/usr/bin/env python3
"""repo-xray — compute team-health signals from a repo's git + GitHub history.

Deterministic engine for the repo-xray skill. Prints a JSON blob of signals;
the skill narrates it. All counting happens HERE — never ask the model to count.

Usage:
    python3 signals.py [--repo PATH] [--days N]

Requires: git (always). gh (optional — GitHub PR signals degrade gracefully).

Status: v0.1 — scaffolding complete; signal computations are TODO.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone


def run(cmd: list[str], cwd: str) -> str | None:
    """Run a command; return stdout, or None on any failure."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=60
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return result.stdout if result.returncode == 0 else None


def gh_available(cwd: str) -> bool:
    return run(["gh", "auth", "status"], cwd) is not None


# --- raw data ---------------------------------------------------------------

def git_log(repo: str, since: str) -> list[dict]:
    """Parse `git log --numstat` since a date into commit records.

    TODO: parse into [{sha, author, date, files: [...]}].
    """
    raw = run(
        ["git", "log", f"--since={since}", "--numstat",
         "--pretty=format:%H%x09%an%x09%aI"],
        repo,
    )
    if raw is None:
        return []
    commits: list[dict] = []
    # TODO: parse `raw`
    return commits


def gh_prs(repo: str) -> list[dict]:
    """Fetch merged PRs with review data via the gh CLI.

    TODO: shape the records the signal functions need.
    """
    raw = run(
        ["gh", "pr", "list", "--state", "merged", "--limit", "200",
         "--json", "number,author,createdAt,mergedAt,reviews"],
        repo,
    )
    if raw is None:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


# --- signals ----------------------------------------------------------------
# Each returns {value, detail, severity}. severity in {ok, watch, concern}.
# TODO: implement. Keep ALL counting here — the skill must not recompute.

def signal_knowledge_silos(commits: list[dict]) -> dict:
    """Files only ever touched by a single author."""
    return {"value": None, "detail": "TODO", "severity": "ok"}


def signal_review_concentration(prs: list[dict]) -> dict:
    """Is one person reviewing most PRs?"""
    return {"value": None, "detail": "TODO", "severity": "ok"}


def signal_time_to_first_review(prs: list[dict]) -> dict:
    """Time from PR open to first review — and its drift over the window."""
    return {"value": None, "detail": "TODO", "severity": "ok"}


def signal_stale_prs(prs: list[dict]) -> dict:
    """PRs that sat open well beyond the norm before merge."""
    return {"value": None, "detail": "TODO", "severity": "ok"}


def signal_silent_merges(prs: list[dict]) -> dict:
    """PRs merged with zero review or approval."""
    return {"value": None, "detail": "TODO", "severity": "ok"}


# --- main -------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="repo-xray team-health signals")
    parser.add_argument("--repo", default=".", help="path to the git repo")
    parser.add_argument("--days", type=int, default=90, help="analysis window")
    args = parser.parse_args()

    since = (
        datetime.now(timezone.utc) - timedelta(days=args.days)
    ).date().isoformat()

    commits = git_log(args.repo, since)
    has_gh = gh_available(args.repo)
    prs = gh_prs(args.repo) if has_gh else []

    report = {
        "window_days": args.days,
        "github_data": has_gh,
        "commits_analyzed": len(commits),
        "prs_analyzed": len(prs),
        "signals": {
            "knowledge_silos": signal_knowledge_silos(commits),
            "review_concentration": signal_review_concentration(prs),
            "time_to_first_review": signal_time_to_first_review(prs),
            "stale_prs": signal_stale_prs(prs),
            "silent_merges": signal_silent_merges(prs),
        },
    }
    if not has_gh:
        report["note"] = "gh unavailable — GitHub PR signals skipped; git-only mode."

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
