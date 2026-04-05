"""Unit tests for exact-title closed issue detection."""
import os
import sys
import types
import unittest

# Make sure we can import workflow helpers from the workflows directory.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
WORKFLOWS_DIR = os.path.join(ROOT_DIR, ".github", "workflows")
if WORKFLOWS_DIR not in sys.path:
    sys.path.insert(0, WORKFLOWS_DIR)

if "requests" not in sys.modules:
    sys.modules["requests"] = types.SimpleNamespace()

import gh  # noqa: E402
import scan_and_suggest  # noqa: E402


class ClosedIssueTitleMatchTests(unittest.TestCase):
    def test_returns_true_for_exact_title_match_in_closed_issues(self):
        original_get_all_issues = gh.get_all_issues

        try:
            gh.get_all_issues = lambda *_args, **_kwargs: [
                {
                    "number": 17,
                    "title": "[user/repo] is missing a .gitattributes file",
                    "closed_at": "2024-01-10T12:00:00Z",
                }
            ]

            self.assertTrue(
                gh.has_closed_issue_with_exact_title(
                    token="token",
                    repo_slug="owner/repo",
                    issue_title="[user/repo] is missing a .gitattributes file",
                )
            )
        finally:
            gh.get_all_issues = original_get_all_issues


class CreateIssueWrapperClosedTitleTests(unittest.TestCase):
    def test_create_issue_wrapper_skips_when_matching_closed_issue_exists(self):
        original_env = os.environ.get("GITHUB_REPOSITORY")
        original_has_closed_issue = scan_and_suggest.gh.has_closed_issue_with_exact_title
        original_read_template_file = scan_and_suggest.read_template_file
        original_create_github_issue = scan_and_suggest.gh.create_github_issue

        template_reads = []
        issue_creations = []

        try:
            os.environ["GITHUB_REPOSITORY"] = "DecimalTurn/VBA-GitHub-Checks"
            scan_and_suggest.gh.has_closed_issue_with_exact_title = lambda *_args, **_kwargs: True

            def _fake_read_template_file(*args, **kwargs):
                template_reads.append((args, kwargs))
                return "body"

            def _fake_create_github_issue(*args, **kwargs):
                issue_creations.append((args, kwargs))
                return 123

            scan_and_suggest.read_template_file = _fake_read_template_file
            scan_and_suggest.gh.create_github_issue = _fake_create_github_issue

            created = scan_and_suggest.create_issue_wrapper(
                token="token",
                repo={
                    "name": "repo",
                    "html_url": "https://example.test/user/repo",
                    "owner": {"login": "user"},
                },
                issue_title_suffix="is missing a .gitattributes file",
                template_name="Check G.md",
                label_name="Check G",
            )

            self.assertFalse(created)
            self.assertEqual(template_reads, [])
            self.assertEqual(issue_creations, [])
        finally:
            if original_env is None:
                os.environ.pop("GITHUB_REPOSITORY", None)
            else:
                os.environ["GITHUB_REPOSITORY"] = original_env

            scan_and_suggest.gh.has_closed_issue_with_exact_title = original_has_closed_issue
            scan_and_suggest.read_template_file = original_read_template_file
            scan_and_suggest.gh.create_github_issue = original_create_github_issue

    def test_returns_false_for_different_title_in_closed_issues(self):
        original_get_all_issues = gh.get_all_issues

        try:
            gh.get_all_issues = lambda *_args, **_kwargs: [
                {
                    "number": 17,
                    "title": "[user/repo] has a .gitattributes misconfiguration",
                    "closed_at": "2024-01-10T12:00:00Z",
                }
            ]

            self.assertFalse(
                gh.has_closed_issue_with_exact_title(
                    token="token",
                    repo_slug="owner/repo",
                    issue_title="[user/repo] is missing a .gitattributes file",
                )
            )
        finally:
            gh.get_all_issues = original_get_all_issues


if __name__ == "__main__":
    unittest.main()
