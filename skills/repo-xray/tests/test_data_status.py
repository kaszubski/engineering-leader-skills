"""Regression coverage at the CLI orchestration boundary; no network required."""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import signals


class TestDataStatus(unittest.TestCase):
    def report(self, git="", merged="[]", opened="[]", authenticated=True):
        def run(cmd, cwd):
            if cmd[0] == "git":
                return git
            if cmd[1:3] == ["auth", "status"]:
                return "" if authenticated else None
            return merged if "merged" in cmd else opened

        output = io.StringIO()
        with patch.object(signals, "run", run), patch.object(sys, "argv", ["signals.py"]):
            with contextlib.redirect_stdout(output):
                self.assertEqual(signals.main(), 0)
        return json.loads(output.getvalue())

    def test_authenticated_read_failures_are_not_healthy(self):
        report = self.report(git=None, merged=None, opened=None)
        self.assertFalse(report["github_data"])
        self.assertIsNone(report["pr_window_covered"])
        self.assertIsNone(report["commits_analyzed"])
        self.assertEqual(report["sources"]["merged_prs"], "error")
        self.assertTrue(all(s["severity"] == "unknown" for s in report["signals"].values()))
        self.assertIn("error", report["note"])

    def test_successful_empty_reads_are_distinct_from_failure(self):
        report = self.report()
        self.assertTrue(report["github_data"])
        self.assertEqual(report["sources"], {"git": "empty", "merged_prs": "empty", "open_prs": "empty"})
        self.assertEqual(report["prs_analyzed"], 0)
        self.assertTrue(all(s["severity"] == "unknown" for s in report["signals"].values()))

    def test_missing_auth_marks_pr_sources_unavailable(self):
        report = self.report(authenticated=False)
        self.assertEqual(report["sources"]["merged_prs"], "unavailable")
        self.assertEqual(report["signals"]["silent_merges"]["severity"], "unknown")

    def test_open_failure_does_not_discard_valid_merged_measurements(self):
        stamp = signals.datetime.now(signals.timezone.utc).isoformat()
        merged = json.dumps([{"number": 1, "createdAt": stamp, "mergedAt": stamp, "reviews": []}])
        report = self.report(merged=merged, opened=None)
        self.assertEqual(report["sources"]["merged_prs"], "ok")
        self.assertEqual(report["signals"]["silent_merges"]["severity"], "concern")
        self.assertEqual(report["signals"]["stale_prs"]["severity"], "unknown")

    def test_malformed_pr_payloads_are_errors(self):
        for payload in ("invalid JSON", "{}", "[null]", '[{"number": 1}]'):
            with self.subTest(payload=payload):
                report = self.report(merged=payload)
                self.assertEqual(report["sources"]["merged_prs"], "error")
                self.assertEqual(report["signals"]["silent_merges"]["severity"], "unknown")

    def test_open_cap_marks_stale_measurement_incomplete(self):
        stamp = signals.datetime.now(signals.timezone.utc).isoformat()
        opened = json.dumps([{"number": n, "createdAt": stamp, "isDraft": False}
                             for n in range(signals.PR_FETCH_LIMIT)])
        report = self.report(opened=opened)
        self.assertEqual(report["sources"]["open_prs"], "partial")
        self.assertEqual(report["signals"]["stale_prs"]["severity"], "unknown")

    def test_merged_cap_never_grades_a_partial_sample_as_healthy(self):
        stamp = signals.datetime.now(signals.timezone.utc).isoformat()
        merged = json.dumps([{"number": n, "createdAt": stamp, "mergedAt": stamp, "reviews": []}
                             for n in range(signals.PR_FETCH_LIMIT)])
        report = self.report(merged=merged)
        self.assertFalse(report["pr_window_covered"])
        self.assertEqual(report["sources"]["merged_prs"], "partial")
        for name in ("review_concentration", "time_to_first_review", "stale_prs", "silent_merges"):
            self.assertEqual(report["signals"][name]["severity"], "unknown")

    def test_git_only_keeps_available_git_measurement(self):
        git = ("COMMIT\taaa\tAda\t2026-09-01T00:00:00Z\n1\t0\ta.py\n"
               "COMMIT\tbbb\tAda\t2026-09-02T00:00:00Z\n1\t0\ta.py\n")
        report = self.report(git=git, authenticated=False)
        self.assertEqual(report["signals"]["knowledge_silos"]["severity"], "watch")
        self.assertEqual(report["signals"]["knowledge_silos"]["value"], 1)
        self.assertEqual(report["sources"]["git"], "ok")

    def test_unreadable_repository_is_not_empty(self):
        with patch.object(signals, "gh_available", return_value=False):
            output = io.StringIO()
            with patch.object(sys, "argv", ["signals.py", "--repo", "/nonexistent/repo-xray-test"]):
                with contextlib.redirect_stdout(output):
                    signals.main()
        report = json.loads(output.getvalue())
        self.assertEqual(report["sources"]["git"], "error")
        self.assertIsNone(report["contributors"])
        self.assertEqual(report["signals"]["knowledge_silos"]["severity"], "unknown")


if __name__ == "__main__":
    unittest.main()
