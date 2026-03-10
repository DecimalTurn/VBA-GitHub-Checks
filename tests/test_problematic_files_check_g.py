"""Unit tests for Check G problematic file selection."""
import os
import sys
import tempfile
import unittest

# Make sure we can import workflow helpers from the workflows directory.
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
WORKFLOWS_DIR = os.path.join(ROOT_DIR, ".github", "workflows")
if WORKFLOWS_DIR not in sys.path:
    sys.path.insert(0, WORKFLOWS_DIR)

import gh  # noqa: E402
import git_ls_parser  # noqa: E402


def _write_temp_bytes(content: bytes, suffix: str) -> str:
    tmp = tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=suffix)
    tmp.write(content)
    tmp.close()
    return tmp.name


class VbaClassHeaderTests(unittest.TestCase):
    def test_cls_with_vba_class_header_is_true(self):
        path = _write_temp_bytes(
            (
                b"VERSION 1.0 CLASS\n"
                b"BEGIN\n"
                b"END\n"
            ),
            suffix=".cls",
        )
        self.addCleanup(os.remove, path)
        self.assertTrue(gh.has_vba_class_header(path))

    def test_cls_without_vba_class_header_is_false(self):
        path = _write_temp_bytes(
            (
                b"Attribute VB_Name = \"Module1\"\n"
                b"Option Explicit\n"
            ),
            suffix=".cls",
        )
        self.addCleanup(os.remove, path)
        self.assertFalse(gh.has_vba_class_header(path))


class ProblematicFilesCheckGTests(unittest.TestCase):
    def test_excludes_cls_without_vba_class_header(self):
        with tempfile.TemporaryDirectory() as repo_dir:
            class_path = os.path.join(repo_dir, "ModuleLike.cls")
            with open(class_path, "wb") as handle:
                handle.write(
                    b"Attribute VB_Name = \"ModuleLike\"\n"
                    b"Option Explicit\n"
                )

            parsed_data = {
                "ModuleLike.cls": git_ls_parser.GitEolInfo(
                    index="lf",
                    working_directory="lf",
                    attribute_text="text",
                    attribute_eol="eol=unspecified",
                )
            }

            self.assertEqual(gh.get_problematic_files_check_g(parsed_data, repo_dir), [])

    def test_includes_cls_with_vba_class_header(self):
        with tempfile.TemporaryDirectory() as repo_dir:
            class_path = os.path.join(repo_dir, "Class1.cls")
            with open(class_path, "wb") as handle:
                handle.write(
                    b"VERSION 1.0 CLASS\n"
                    b"BEGIN\n"
                    b"    MultiUse = -1\n"
                    b"END\n"
                )

            parsed_data = {
                "Class1.cls": git_ls_parser.GitEolInfo(
                    index="lf",
                    working_directory="lf",
                    attribute_text="text",
                    attribute_eol="eol=unspecified",
                )
            }

            self.assertEqual(gh.get_problematic_files_check_g(parsed_data, repo_dir), ["Class1.cls"])


if __name__ == "__main__":
    unittest.main()
