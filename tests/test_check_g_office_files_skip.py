"""Unit tests for Check G skip logic when VBA-enabled Office files are present."""
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
import utils  # noqa: E402


class OfficeFileDetectionTests(unittest.TestCase):
    def test_has_vba_enabled_office_files_true(self):
        counts = {ext: 0 for ext in utils.office_vba_extensions}
        counts[".xlsm"] = 1
        self.assertTrue(utils.has_vba_enabled_office_files(counts))

    def test_has_vba_enabled_office_files_false(self):
        counts = {ext: 0 for ext in utils.office_vba_extensions}
        self.assertFalse(utils.has_vba_enabled_office_files(counts))


class ReportMissingGitattributesIssueTests(unittest.TestCase):
    def test_skips_check_g_issue_creation_when_office_files_present(self):
        original_has_office_files = scan_and_suggest.utils.has_vba_enabled_office_files
        original_gitattributes_needed = scan_and_suggest.gh.gitattributes_needed
        original_create_issue_wrapper = scan_and_suggest.create_issue_wrapper

        issue_creation_calls = []
        gitattributes_needed_calls = []

        try:
            scan_and_suggest.utils.has_vba_enabled_office_files = lambda _counts: True

            def _fake_gitattributes_needed(_repo_path, _counts):
                gitattributes_needed_calls.append(True)
                return True

            def _fake_create_issue_wrapper(*args, **kwargs):
                issue_creation_calls.append((args, kwargs))
                return True

            scan_and_suggest.gh.gitattributes_needed = _fake_gitattributes_needed
            scan_and_suggest.create_issue_wrapper = _fake_create_issue_wrapper

            scan_and_suggest.report_missing_gitattributes_issue(
                repo_path="dummy/repo",
                counts={".xlsm": 1},
                token="token",
                repo={"name": "repo", "owner": {"login": "user"}, "html_url": "https://example.test"},
            )

            self.assertEqual(gitattributes_needed_calls, [])
            self.assertEqual(issue_creation_calls, [])
        finally:
            scan_and_suggest.utils.has_vba_enabled_office_files = original_has_office_files
            scan_and_suggest.gh.gitattributes_needed = original_gitattributes_needed
            scan_and_suggest.create_issue_wrapper = original_create_issue_wrapper


if __name__ == "__main__":
    unittest.main()
