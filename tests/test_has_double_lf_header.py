"""Unit tests for has_double_lf_header helper.
"""
import os
import sys
import tempfile
import types
import unittest

# Ensure requests import in gh.py is satisfied without installing the package.
if "requests" not in sys.modules:
    sys.modules["requests"] = types.SimpleNamespace()

# Make sure we can import gh from the workflows directory.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
WORKFLOWS_DIR = os.path.join(ROOT_DIR, ".github", "workflows")
if WORKFLOWS_DIR not in sys.path:
    sys.path.insert(0, WORKFLOWS_DIR)

import gh  # noqa: E402


def _write_temp_bytes(content: bytes, suffix: str) -> str:
    tmp = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=suffix)
    tmp.write(content)
    tmp.close()
    return tmp.name


class DoubleLfHeaderTests(unittest.TestCase):
    def test_cls_with_double_lf_header_is_true(self):
        path = _write_temp_bytes(
            (
                b"VERSION 1.0 CLASS\n"
                b"\n"
                b"BEGIN\n"
                b"    MultiUse = -1\n"
                b"END\n"
                b"Attribute VB_Name = \"CRYPTO\"\n"
            ),
            suffix=".cls",
        )
        self.addCleanup(os.remove, path)
        self.assertTrue(gh.has_double_lf_header(path))

    def test_cls_with_single_lf_header_is_false(self):
        path = _write_temp_bytes(
            (
                b"VERSION 1.0 CLASS\n"
                b"BEGIN\n"
                b"    MultiUse = -1\n"
                b"END\n"
                b"Attribute VB_Name = \"CRYPTO\"\n"
            ),
            suffix=".cls",
        )
        self.addCleanup(os.remove, path)
        self.assertFalse(gh.has_double_lf_header(path))

    def test_cls_with_crlf_header_is_false(self):
        path = _write_temp_bytes(
            (
                b"VERSION 1.0 CLASS\r\n"
                b"BEGIN\r\n"
                b"    MultiUse = -1\r\n"
                b"END\r\n"
                b"Attribute VB_Name = \"CRYPTO\"\r\n"
            ),
            suffix=".cls",
        )
        self.addCleanup(os.remove, path)
        self.assertFalse(gh.has_double_lf_header(path))

    def test_frm_with_double_lf_header_is_true(self):
        path = _write_temp_bytes(
            (
                b"VERSION 5.00\n"
                b"\n"
                b"Begin {guid} UserForm1\n"
            ),
            suffix=".frm",
        )
        self.addCleanup(os.remove, path)
        self.assertTrue(gh.has_double_lf_header(path))

    def test_file_without_version_header_is_false(self):
        path = _write_temp_bytes(
            (
                b"Attribute VB_Name = \"Module1\"\n"
                b"\n"
                b"Sub Test()\n"
                b"End Sub\n"
            ),
            suffix=".cls",
        )
        self.addCleanup(os.remove, path)
        self.assertFalse(gh.has_double_lf_header(path))

    def test_crlf_double_line_is_false(self):
        path = _write_temp_bytes(
            (
                b"VERSION 1.0 CLASS\r\n"
                b"\r\n"
                b"BEGIN\r\n"
            ),
            suffix=".cls",
        )
        self.addCleanup(os.remove, path)
        self.assertFalse(gh.has_double_lf_header(path))


if __name__ == "__main__":
    unittest.main()
