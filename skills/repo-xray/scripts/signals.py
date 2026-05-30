#!/usr/bin/env python3
"""repo-xray — compute team-health signals from a repo's git + GitHub history.

Deterministic engine for the repo-xray skill. Prints a JSON blob of signals;
the skill narrates it. All counting happens HERE — never ask the model to count.

Usage:
    python3 signals.py [--repo PATH] [--days N]

Requires: git (always). gh (optional — GitHub PR signals degrade gracefully).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from statistics import median

STALE_DAYS = 14  # a PR open longer than this before merge counts as stale
PR_FETCH_LIMIT = 200  # gh pr list cap; hitting it means we saw only a recent slice


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


def parse_iso(value: object) -> datetime | None:
    """Parse an ISO-8601 timestamp (handles a trailing 'Z')."""
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def severity(ratio: float, watch: float, concern: float) -> str:
    """Map a ratio to a severity band."""
    if ratio >= concern:
        return "concern"
    if ratio >= watch:
        return "watch"
    return "ok"


def damp_for_small_team(sig: dict, contributors: int) -> dict:
    """Soften a team-size-sensitive severity by one band on a tiny team.

    A 66% silent-merge rate means something different on a two-person repo than
    on a thirty-person team: with one or two contributors, single-author files,
    a dominant reviewer, and unreviewed merges are largely *structural* — there
    is no one else. So for 1–2 contributors we drop one band (concern→watch,
    watch→ok) and say we did. With 0 contributors we don't know the team size
    (no git history read), so we leave the signal untouched.
    """
    if not 1 <= contributors <= 2 or sig["severity"] == "ok":
        return sig
    softened = {"concern": "watch", "watch": "ok"}[sig["severity"]]
    out = dict(sig)
    out["severity"] = softened
    out["detail"] += (f" — softened from '{sig['severity']}' "
                      f"(small team: {contributors} contributor(s))")
    return out


# --- raw data ---------------------------------------------------------------

def git_log(repo: str, since: str) -> list[dict]:
    """Parse `git log --numstat` since a date into commit records.

    Each record: {sha, author, date, files: [path, ...]}.
    A 'COMMIT' sentinel in the pretty-format makes header lines unambiguous.
    """
    raw = run(
        ["git", "log", "--no-merges", f"--since={since}", "--numstat",
         "--pretty=format:COMMIT%x09%H%x09%an%x09%aI"],
        repo,
    )
    if raw is None:
        return []
    commits: list[dict] = []
    current: dict | None = None
    for line in raw.splitlines():
        if line.startswith("COMMIT\t"):
            parts = line.split("\t")
            if len(parts) >= 4:
                current = {"sha": parts[1], "author": parts[2],
                           "date": parts[3], "files": []}
                commits.append(current)
            else:
                current = None
        elif current is not None and line.strip():
            parts = line.split("\t", 2)  # added, deleted, path
            if len(parts) == 3:
                current["files"].append(parts[2])
    return commits


def gh_prs(repo: str) -> list[dict]:
    """Fetch merged PRs (with review data) via the gh CLI."""
    raw = run(
        ["gh", "pr", "list", "--state", "merged", "--limit", str(PR_FETCH_LIMIT),
         "--json", "number,author,createdAt,mergedAt,reviews"],
        repo,
    )
    if raw is None:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def hit_pr_cap(prs: list) -> bool:
    """Whether the PR fetch likely truncated — we got a full page of results.

    A busy repo can have far more than PR_FETCH_LIMIT merged PRs; when it does,
    every PR-based ratio is computed on the most recent slice only. The skill
    must say so rather than present a partial sample as the whole history.
    """
    return len(prs) >= PR_FETCH_LIMIT


# --- signals ----------------------------------------------------------------
# Each returns {value, detail, severity}. severity in {ok, watch, concern}.
# All counting lives here — the skill narrates, it never recomputes.

def signal_knowledge_silos(commits: list[dict]) -> dict:
    """Actively-changed files touched by only a single author."""
    authors: dict[str, set[str]] = defaultdict(set)
    touches: Counter = Counter()
    for c in commits:
        for path in c.get("files", []):
            authors[path].add(c["author"])
            touches[path] += 1

    active = [p for p in touches if touches[p] >= 2]
    if not active:
        return {"value": 0,
                "detail": "no file changed twice or more in the window",
                "severity": "ok"}

    silos = [p for p in active if len(authors[p]) == 1]
    ratio = len(silos) / len(active)
    detail = (f"{len(silos)} of {len(active)} actively-changed files are "
              f"single-author ({ratio:.0%})")
    if silos:
        top = sorted(silos, key=lambda p: -touches[p])[:3]
        detail += " — e.g. " + ", ".join(
            f"{p} ({next(iter(authors[p]))})" for p in top)
    return {"value": len(silos), "detail": detail,
            "severity": severity(ratio, 0.25, 0.5)}


def signal_review_concentration(prs: list[dict]) -> dict:
    """Whether a single person performs most reviews."""
    counts: Counter = Counter()
    for pr in prs:
        for review in pr.get("reviews") or []:
            login = (review.get("author") or {}).get("login")
            if login:
                counts[login] += 1

    total = sum(counts.values())
    if total == 0:
        return {"value": 0, "detail": "no reviews recorded in the window",
                "severity": "ok"}

    top_login, top_count = counts.most_common(1)[0]
    share = top_count / total
    detail = (f"{top_login} did {top_count} of {total} reviews "
              f"({share:.0%}); {len(counts)} reviewer(s) total")
    return {"value": round(share, 2), "detail": detail,
            "severity": severity(share, 0.4, 0.6)}


def signal_time_to_first_review(prs: list[dict]) -> dict:
    """Median time from PR open to first review — plus its drift."""
    samples: list[tuple[datetime, float]] = []  # (created, hours)
    for pr in prs:
        created = parse_iso(pr.get("createdAt"))
        if not created:
            continue
        review_times = [parse_iso(r.get("submittedAt"))
                        for r in (pr.get("reviews") or [])]
        review_times = [t for t in review_times if t]
        if not review_times:
            continue
        hours = (min(review_times) - created).total_seconds() / 3600
        if hours >= 0:
            samples.append((created, hours))

    if not samples:
        return {"value": None, "detail": "no reviewed PRs in the window",
                "severity": "ok"}

    hours_list = [h for _, h in samples]
    med = median(hours_list)
    detail = (f"median time to first review: {med:.1f}h "
              f"across {len(samples)} reviewed PRs")

    if len(samples) >= 6:  # report drift only with enough data
        ordered = sorted(samples, key=lambda s: s[0])
        mid = len(ordered) // 2
        early = median([h for _, h in ordered[:mid]])
        late = median([h for _, h in ordered[mid:]])
        if late > early * 1.5:
            detail += f"; trending slower ({early:.1f}h → {late:.1f}h)"
        elif early > late * 1.5:
            detail += f"; trending faster ({early:.1f}h → {late:.1f}h)"

    band = "concern" if med > 72 else "watch" if med > 24 else "ok"
    return {"value": round(med, 1), "detail": detail, "severity": band}


def signal_stale_prs(prs: list[dict]) -> dict:
    """Merged PRs that sat open well beyond the norm."""
    ages: list[tuple[object, float]] = []  # (number, days)
    for pr in prs:
        created = parse_iso(pr.get("createdAt"))
        merged = parse_iso(pr.get("mergedAt"))
        if not created or not merged:
            continue
        days = (merged - created).total_seconds() / 86400
        if days >= 0:
            ages.append((pr.get("number"), days))

    if not ages:
        return {"value": 0, "detail": "no merged PRs with dates in the window",
                "severity": "ok"}

    stale = [(n, d) for n, d in ages if d > STALE_DAYS]
    ratio = len(stale) / len(ages)
    detail = (f"{len(stale)} of {len(ages)} merged PRs stayed open "
              f">{STALE_DAYS}d before merge ({ratio:.0%})")
    if stale:
        oldest = sorted(stale, key=lambda x: -x[1])[:3]
        detail += " — e.g. " + ", ".join(f"#{n} ({d:.0f}d)" for n, d in oldest)
    return {"value": len(stale), "detail": detail,
            "severity": severity(ratio, 0.1, 0.3)}


def signal_silent_merges(prs: list[dict]) -> dict:
    """Merged PRs that had no review at all."""
    if not prs:
        return {"value": 0, "detail": "no merged PRs in the window",
                "severity": "ok"}

    silent = [pr for pr in prs if not (pr.get("reviews") or [])]
    ratio = len(silent) / len(prs)
    detail = (f"{len(silent)} of {len(prs)} merged PRs had no review "
              f"({ratio:.0%})")
    if silent:
        nums = [str(pr.get("number")) for pr in silent[:5]]
        detail += " — e.g. #" + ", #".join(nums)
    return {"value": len(silent), "detail": detail,
            "severity": severity(ratio, 0.1, 0.3)}


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

    # Distinct commit authors in the window — a deterministic proxy for team
    # size, used to calibrate the team-size-sensitive signals below.
    contributors = len({c["author"] for c in commits})

    prs_truncated = hit_pr_cap(prs)

    report = {
        "window_days": args.days,
        "github_data": has_gh,
        "commits_analyzed": len(commits),
        "prs_analyzed": len(prs),
        "prs_truncated": prs_truncated,
        "contributors": contributors,
        "signals": {
            "knowledge_silos": damp_for_small_team(
                signal_knowledge_silos(commits), contributors),
            "review_concentration": damp_for_small_team(
                signal_review_concentration(prs), contributors),
            "time_to_first_review": signal_time_to_first_review(prs),
            "stale_prs": signal_stale_prs(prs),
            "silent_merges": damp_for_small_team(
                signal_silent_merges(prs), contributors),
        },
    }
    if not has_gh:
        report["note"] = "gh unavailable — GitHub PR signals skipped; git-only mode."
    elif prs_truncated:
        report["note"] = (
            f"PR fetch hit the {PR_FETCH_LIMIT}-PR cap; all PR-based signals "
            "(review concentration, time-to-first-review, stale PRs, silent "
            "merges) reflect only the most recent merged PRs, not the full "
            "history. Narrow --days, or read these ratios as a recent slice."
        )

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
