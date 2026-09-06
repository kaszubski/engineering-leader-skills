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
    if not 1 <= contributors <= 2 or sig["severity"] not in ("watch", "concern"):
        return sig
    softened = {"concern": "watch", "watch": "ok"}[sig["severity"]]
    out = dict(sig)
    out["severity"] = softened
    out["detail"] += (f" — softened from '{sig['severity']}' "
                      f"(small team: {contributors} contributor(s))")
    return out


# --- raw data ---------------------------------------------------------------

def git_log(repo: str, since: str) -> list[dict] | None:
    """Parse `git log --numstat` since a date into commit records.

    Each record: {sha, author, date, files: [path, ...]}.
    A 'COMMIT' sentinel in the pretty-format makes header lines unambiguous.
    """
    raw = run(
        ["git", "log", "--no-merges", f"--since={since}", "--numstat",
         "--pretty=format:COMMIT%x09%H%x09%aN%x09%aI"],  # %aN honours .mailmap
        repo,
    )
    if raw is None:
        return None
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


def fetch_prs(repo: str, state: str) -> list[dict] | None:
    """Return validated records, [] for a successful empty read, None on failure."""
    fields = ("number,author,createdAt,mergedAt,reviews" if state == "merged"
              else "number,createdAt,isDraft")
    raw = run(["gh", "pr", "list", "--state", state, "--limit", str(PR_FETCH_LIMIT),
               "--json", fields], repo)
    if raw is None:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None
    for pr in data:
        if not isinstance(pr, dict) or not parse_iso(pr.get("createdAt")):
            return None
        if state == "merged":
            if not parse_iso(pr.get("mergedAt")) or not isinstance(pr.get("reviews"), list):
                return None
            if any(not isinstance(r, dict) for r in pr["reviews"]):
                return None
        elif not isinstance(pr.get("isDraft"), bool):
            return None
    return data


def gh_prs(repo: str) -> list[dict] | None:
    return fetch_prs(repo, "merged")


def gh_open_prs(repo: str) -> list[dict] | None:
    return fetch_prs(repo, "open")


def as_utc(dt: datetime) -> datetime:
    """Treat a naive datetime as UTC so it can be compared to aware ones."""
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def filter_prs_to_window(prs: list[dict], since: datetime) -> list[dict]:
    """Keep only PRs merged inside the analysis window.

    `gh pr list` has no --since; it returns the most recent merged PRs
    regardless of age. Without this filter, a --days 30 run would compute
    every PR-based signal over arbitrarily old history.
    """
    kept = []
    for pr in prs:
        merged = parse_iso(pr.get("mergedAt"))
        if merged and as_utc(merged) >= since:
            kept.append(pr)
    return kept


def pr_window_covered(fetched: list[dict], since: datetime) -> bool:
    """Whether the fetched merged-PR slice reaches back past the window start.

    If the fetch hit its cap *and* the oldest PR we got is still newer than
    the window start, older in-window PRs exist that we never saw — the
    PR-based signals then cover only part of the window.
    """
    if not hit_pr_cap(fetched):
        return True
    dates = [d for d in (parse_iso(p.get("mergedAt")) for p in fetched) if d]
    if not dates:
        return False
    return as_utc(min(dates)) <= since


def is_bot_review(review: dict) -> bool:
    """Whether a review was left by a bot (dependabot, CI apps, Copilot...)."""
    author = review.get("author") or {}
    if author.get("is_bot"):
        return True
    login = author.get("login") or ""
    return login.endswith("[bot]") or login.startswith("app/")


def human_reviews(pr: dict) -> list[dict]:
    """A PR's reviews with bot reviews stripped out.

    Every review-based signal means *human* review: a bot approval should
    neither count as review coverage nor mask a slow human response.
    """
    return [r for r in (pr.get("reviews") or []) if not is_bot_review(r)]


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
                "severity": "unknown"}

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
        for review in human_reviews(pr):
            login = (review.get("author") or {}).get("login")
            if login:
                counts[login] += 1

    total = sum(counts.values())
    if total == 0:
        return {"value": 0, "detail": "no reviews recorded in the window",
                "severity": "unknown"}

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
                        for r in human_reviews(pr)]
        review_times = [t for t in review_times if t]
        if not review_times:
            continue
        hours = (min(review_times) - created).total_seconds() / 3600
        if hours >= 0:
            samples.append((created, hours))

    if not samples:
        return {"value": None, "detail": "no reviewed PRs in the window",
                "severity": "unknown"}

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


def signal_stale_prs(prs: list[dict], open_prs: list[dict] | None = None,
                     now: datetime | None = None) -> dict:
    """PRs that sat — or are still sitting — open well beyond the norm.

    Two populations: merged PRs that took >STALE_DAYS to land, and currently
    open non-draft PRs already older than that. The second is the more literal
    "stale PR"; counting only merged ones would miss the PR nobody is merging.
    Drafts are excluded — parked on purpose is not stale.
    """
    now = as_utc(now) if now else datetime.now(timezone.utc)

    merged_ages: list[tuple[object, float]] = []  # (number, days)
    for pr in prs:
        created = parse_iso(pr.get("createdAt"))
        merged = parse_iso(pr.get("mergedAt"))
        if not created or not merged:
            continue
        days = (merged - created).total_seconds() / 86400
        if days >= 0:
            merged_ages.append((pr.get("number"), days))

    open_ages: list[tuple[object, float]] = []
    for pr in open_prs or []:
        if pr.get("isDraft"):
            continue
        created = parse_iso(pr.get("createdAt"))
        if not created:
            continue
        days = (now - as_utc(created)).total_seconds() / 86400
        if days >= 0:
            open_ages.append((pr.get("number"), days))

    total = len(merged_ages) + len(open_ages)
    if total == 0:
        return {"value": 0,
                "detail": "no merged or open PRs with dates in the window",
                "severity": "unknown"}

    stale_merged = [(n, d) for n, d in merged_ages if d > STALE_DAYS]
    stale_open = [(n, d) for n, d in open_ages if d > STALE_DAYS]
    stale = stale_merged + stale_open
    ratio = len(stale) / total
    detail = (f"{len(stale)} of {total} PRs sat open >{STALE_DAYS}d "
              f"({ratio:.0%}): {len(stale_merged)} eventually merged, "
              f"{len(stale_open)} still open")
    if stale:
        oldest = sorted(stale, key=lambda x: -x[1])[:3]
        detail += " — e.g. " + ", ".join(f"#{n} ({d:.0f}d)" for n, d in oldest)
    return {"value": len(stale), "detail": detail,
            "severity": severity(ratio, 0.1, 0.3)}


def signal_silent_merges(prs: list[dict]) -> dict:
    """Merged PRs that had no review at all."""
    if not prs:
        return {"value": 0, "detail": "no merged PRs in the window",
                "severity": "unknown"}

    silent = [pr for pr in prs if not human_reviews(pr)]
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
    if args.days <= 0:
        parser.error("--days must be positive")

    since_dt = datetime.now(timezone.utc) - timedelta(days=args.days)
    since = since_dt.date().isoformat()

    commits = git_log(args.repo, since)
    has_gh = gh_available(args.repo)
    fetched_prs = gh_prs(args.repo) if has_gh else None
    open_prs = gh_open_prs(args.repo) if has_gh else None

    def source_status(records, available=True):
        if not available:
            return "unavailable"
        if records is None:
            return "error"
        return "ok" if records else "empty"

    sources = {
        "git": source_status(commits),
        "merged_prs": source_status(fetched_prs, has_gh),
        "open_prs": source_status(open_prs, has_gh),
    }
    contributors = len({c["author"] for c in commits}) if commits is not None else None
    prs = filter_prs_to_window(fetched_prs or [], since_dt)
    window_covered = pr_window_covered(fetched_prs, since_dt) if fetched_prs is not None else None
    open_covered = not hit_pr_cap(open_prs) if open_prs is not None else None
    if window_covered is False:
        sources["merged_prs"] = "partial"
    if open_covered is False:
        sources["open_prs"] = "partial"

    measurements = {
        "knowledge_silos": damp_for_small_team(
            signal_knowledge_silos(commits or []), contributors or 0),
        "review_concentration": damp_for_small_team(
            signal_review_concentration(prs), contributors or 0),
        "time_to_first_review": signal_time_to_first_review(prs),
        "stale_prs": signal_stale_prs(prs, open_prs),
        "silent_merges": damp_for_small_team(
            signal_silent_merges(prs), contributors or 0),
    }
    dependencies = {
        "knowledge_silos": ("git",),
        "review_concentration": ("merged_prs",),
        "time_to_first_review": ("merged_prs",),
        "stale_prs": ("merged_prs", "open_prs"),
        "silent_merges": ("merged_prs",),
    }
    for name, required in dependencies.items():
        incomplete = [f"{source}: {sources[source]}" for source in required
                      if sources[source] not in ("ok", "empty")]
        if incomplete:
            measurements[name] = {
                "value": None, "severity": "unknown",
                "detail": "Measurement unavailable or incomplete — " + ", ".join(incomplete),
            }

    report = {
        "window_days": args.days,
        "github_data": fetched_prs is not None and open_prs is not None,
        "sources": sources,
        "commits_analyzed": len(commits) if commits is not None else None,
        "prs_fetched": len(fetched_prs) if fetched_prs is not None else None,
        "prs_analyzed": len(prs) if fetched_prs is not None else None,
        "open_prs_analyzed": len(open_prs) if open_prs is not None else None,
        "pr_window_covered": window_covered,
        "open_prs_covered": open_covered,
        "contributors": contributors,
        "signals": measurements,
    }
    notes = [f"{source}: {status}" for source, status in sources.items() if status != "ok"]
    if notes:
        report["note"] = ("Data limits — " + "; ".join(notes)
                          + ". Unknown is not healthy. Check access/read errors; a partial "
                          "source hit the fetch cap. Empty means a successful read with no records.")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
