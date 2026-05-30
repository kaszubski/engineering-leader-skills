#!/usr/bin/env python3
"""Tests for repo-xray's signal engine.

The skill's whole premise is "LLMs miscount, so the counting lives in code you
can trust." These tests are what make that trust earned rather than asserted.

Zero dependencies — run with the stdlib:
    python3 -m unittest discover -s skills/repo-xray/tests
or directly:
    python3 skills/repo-xray/tests/test_signals.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import signals  # noqa: E402


# --- helpers ----------------------------------------------------------------

def commit(author: str, *files: str, sha: str = "deadbeef") -> dict:
    return {"sha": sha, "author": author, "date": "2026-01-01T00:00:00Z",
            "files": list(files)}


def review(login: str, submitted: str | None = None) -> dict:
    r: dict = {"author": {"login": login}}
    if submitted is not None:
        r["submittedAt"] = submitted
    return r


def pr(number: int, *, created: str | None = None, merged: str | None = None,
       reviews: list | None = None) -> dict:
    return {"number": number, "createdAt": created, "mergedAt": merged,
            "reviews": reviews or []}


# --- pure helpers -----------------------------------------------------------

class TestSeverity(unittest.TestCase):
    def test_bands(self):
        # severity(ratio, watch, concern)
        self.assertEqual(signals.severity(0.0, 0.25, 0.5), "ok")
        self.assertEqual(signals.severity(0.24, 0.25, 0.5), "ok")
        self.assertEqual(signals.severity(0.25, 0.25, 0.5), "watch")  # at watch
        self.assertEqual(signals.severity(0.49, 0.25, 0.5), "watch")
        self.assertEqual(signals.severity(0.5, 0.25, 0.5), "concern")  # at concern
        self.assertEqual(signals.severity(1.0, 0.25, 0.5), "concern")


class TestParseIso(unittest.TestCase):
    def test_valid(self):
        self.assertIsNotNone(signals.parse_iso("2026-01-01T00:00:00Z"))
        self.assertIsNotNone(signals.parse_iso("2026-01-01T00:00:00+00:00"))

    def test_invalid(self):
        self.assertIsNone(signals.parse_iso(None))
        self.assertIsNone(signals.parse_iso(""))
        self.assertIsNone(signals.parse_iso(12345))  # non-string
        self.assertIsNone(signals.parse_iso("not-a-date"))

    def test_z_suffix_equals_offset(self):
        self.assertEqual(
            signals.parse_iso("2026-01-01T00:00:00Z"),
            signals.parse_iso("2026-01-01T00:00:00+00:00"),
        )


# --- knowledge silos --------------------------------------------------------

class TestKnowledgeSilos(unittest.TestCase):
    def test_empty(self):
        out = signals.signal_knowledge_silos([])
        self.assertEqual(out["value"], 0)
        self.assertEqual(out["severity"], "ok")

    def test_single_touch_files_are_not_active(self):
        # A file touched only once is excluded — needs >= 2 touches to count.
        out = signals.signal_knowledge_silos([commit("alice", "a.py")])
        self.assertEqual(out["value"], 0)
        self.assertIn("no file changed twice", out["detail"])

    def test_single_author_active_file_is_a_silo(self):
        commits = [
            commit("alice", "solo.py", "shared.py"),   # touch 1
            commit("alice", "solo.py"),                 # touch 2 -> solo active
            commit("bob", "shared.py"),                 # touch 2 -> shared active
        ]
        # active = {solo.py (2, alice-only), shared.py (2, alice+bob)}
        # silos  = {solo.py}; ratio = 1/2 = 0.5 -> concern
        out = signals.signal_knowledge_silos(commits)
        self.assertEqual(out["value"], 1)
        self.assertEqual(out["severity"], "concern")
        self.assertIn("solo.py", out["detail"])
        self.assertIn("alice", out["detail"])

    def test_well_shared_repo_is_ok(self):
        commits = [
            commit("alice", "x.py"),
            commit("bob", "x.py"),
            commit("alice", "y.py"),
            commit("bob", "y.py"),
        ]
        # both active files have 2 authors -> 0 silos -> ok
        out = signals.signal_knowledge_silos(commits)
        self.assertEqual(out["value"], 0)
        self.assertEqual(out["severity"], "ok")


# --- review concentration ---------------------------------------------------

class TestReviewConcentration(unittest.TestCase):
    def test_no_reviews(self):
        out = signals.signal_review_concentration([pr(1)])
        self.assertEqual(out["value"], 0)
        self.assertEqual(out["severity"], "ok")

    def test_one_reviewer_dominates(self):
        prs = [
            pr(1, reviews=[review("alice")] * 6),
            pr(2, reviews=[review("bob")] * 4),
        ]
        # alice 6 / 10 total = 0.6 -> concern (watch .4, concern .6)
        out = signals.signal_review_concentration(prs)
        self.assertEqual(out["value"], 0.6)
        self.assertEqual(out["severity"], "concern")
        self.assertIn("alice", out["detail"])

    def test_balanced_reviews_ok(self):
        prs = [pr(1, reviews=[review("alice"), review("bob"), review("carol")])]
        out = signals.signal_review_concentration(prs)
        self.assertEqual(out["severity"], "ok")


# --- time to first review ---------------------------------------------------

class TestTimeToFirstReview(unittest.TestCase):
    def test_no_reviewed_prs(self):
        out = signals.signal_time_to_first_review([pr(1, created="2026-01-01T00:00:00Z")])
        self.assertIsNone(out["value"])
        self.assertEqual(out["severity"], "ok")

    def test_uses_earliest_review(self):
        prs = [pr(1, created="2026-01-01T00:00:00Z", reviews=[
            review("alice", "2026-01-01T05:00:00Z"),
            review("bob", "2026-01-01T02:00:00Z"),  # earliest -> 2h
        ])]
        out = signals.signal_time_to_first_review(prs)
        self.assertEqual(out["value"], 2.0)
        self.assertEqual(out["severity"], "ok")

    def test_severity_bands(self):
        slow = [pr(1, created="2026-01-01T00:00:00Z",
                   reviews=[review("a", "2026-01-04T01:00:00Z")])]  # 73h
        out = signals.signal_time_to_first_review(slow)
        self.assertEqual(out["severity"], "concern")

    def test_drift_detected_with_enough_samples(self):
        prs = []
        for i, day in enumerate(range(1, 7)):
            created = f"2026-01-0{day}T00:00:00Z"
            delta_h = 2 if i < 3 else 10  # later PRs slower
            sub = f"2026-01-0{day}T{delta_h:02d}:00:00Z"
            prs.append(pr(i, created=created, reviews=[review("a", sub)]))
        out = signals.signal_time_to_first_review(prs)
        self.assertIn("trending slower", out["detail"])


# --- stale PRs --------------------------------------------------------------

class TestStalePrs(unittest.TestCase):
    def test_no_dated_prs(self):
        out = signals.signal_stale_prs([pr(1)])
        self.assertEqual(out["value"], 0)
        self.assertEqual(out["severity"], "ok")

    def test_stale_threshold(self):
        prs = [
            pr(1, created="2026-01-01T00:00:00Z", merged="2026-01-02T00:00:00Z"),   # 1d  fresh
            pr(2, created="2026-01-01T00:00:00Z", merged="2026-01-20T00:00:00Z"),   # 19d stale
        ]
        # 1 of 2 stale = 0.5 -> concern (watch .1, concern .3)
        out = signals.signal_stale_prs(prs)
        self.assertEqual(out["value"], 1)
        self.assertEqual(out["severity"], "concern")
        self.assertIn("#2", out["detail"])

    def test_exactly_14_days_is_not_stale(self):
        # STALE_DAYS boundary: > 14, not >= 14
        prs = [pr(1, created="2026-01-01T00:00:00Z", merged="2026-01-15T00:00:00Z")]  # 14d
        out = signals.signal_stale_prs(prs)
        self.assertEqual(out["value"], 0)


# --- silent merges ----------------------------------------------------------

class TestSilentMerges(unittest.TestCase):
    def test_no_prs(self):
        out = signals.signal_silent_merges([])
        self.assertEqual(out["value"], 0)
        self.assertEqual(out["severity"], "ok")

    def test_silent_ratio(self):
        prs = [
            pr(1, reviews=[review("alice")]),
            pr(2),  # silent
            pr(3),  # silent
        ]
        # 2 of 3 silent = 0.67 -> concern (watch .1, concern .3)
        out = signals.signal_silent_merges(prs)
        self.assertEqual(out["value"], 2)
        self.assertEqual(out["severity"], "concern")

    def test_all_reviewed_ok(self):
        prs = [pr(1, reviews=[review("alice")]), pr(2, reviews=[review("bob")])]
        out = signals.signal_silent_merges(prs)
        self.assertEqual(out["value"], 0)
        self.assertEqual(out["severity"], "ok")


# --- small-team calibration -------------------------------------------------

class TestDampForSmallTeam(unittest.TestCase):
    def _sig(self, sev: str) -> dict:
        return {"value": 1, "detail": "x", "severity": sev}

    def test_softens_one_band_for_tiny_team(self):
        self.assertEqual(
            signals.damp_for_small_team(self._sig("concern"), 2)["severity"],
            "watch")
        self.assertEqual(
            signals.damp_for_small_team(self._sig("watch"), 1)["severity"],
            "ok")

    def test_records_why_in_detail(self):
        out = signals.damp_for_small_team(self._sig("concern"), 1)
        self.assertIn("softened", out["detail"])
        self.assertIn("concern", out["detail"])

    def test_ok_is_untouched(self):
        out = signals.damp_for_small_team(self._sig("ok"), 1)
        self.assertEqual(out["severity"], "ok")
        self.assertNotIn("softened", out["detail"])

    def test_larger_teams_untouched(self):
        for n in (3, 10, 30):
            out = signals.damp_for_small_team(self._sig("concern"), n)
            self.assertEqual(out["severity"], "concern")

    def test_zero_contributors_untouched(self):
        # 0 means we couldn't read git history — don't guess the team is small.
        out = signals.damp_for_small_team(self._sig("concern"), 0)
        self.assertEqual(out["severity"], "concern")

    def test_does_not_mutate_input(self):
        original = self._sig("concern")
        signals.damp_for_small_team(original, 1)
        self.assertEqual(original["severity"], "concern")


# --- git_log parser (integration: real temp repo) ---------------------------

class TestGitLogParser(unittest.TestCase):
    """Exercises the --numstat parser end-to-end against a real git repo."""

    def _git(self, repo: str, *args: str, author: str | None = None) -> None:
        env = dict(os.environ)
        env.update({
            "GIT_AUTHOR_NAME": author or "Test", "GIT_AUTHOR_EMAIL": "t@e.x",
            "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@e.x",
        })
        subprocess.run(["git", *args], cwd=repo, env=env, check=True,
                       capture_output=True, text=True)

    def test_parses_authors_and_files(self):
        with tempfile.TemporaryDirectory() as repo:
            self._git(repo, "init", "-q")
            (Path(repo) / "a.py").write_text("one\n")
            self._git(repo, "add", "a.py")
            self._git(repo, "commit", "-q", "-m", "first", author="Alice")

            (Path(repo) / "b.py").write_text("two\n")
            self._git(repo, "add", "b.py")
            self._git(repo, "commit", "-q", "-m", "second", author="Bob")

            commits = signals.git_log(repo, since="2000-01-01")

            self.assertEqual(len(commits), 2)
            authors = {c["author"] for c in commits}
            self.assertEqual(authors, {"Alice", "Bob"})
            touched = {f for c in commits for f in c["files"]}
            self.assertEqual(touched, {"a.py", "b.py"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
