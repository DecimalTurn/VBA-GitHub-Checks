from dataclasses import dataclass
from typing import Dict
import re

@dataclass
class GitEolInfo:
    index: str
    working_directory: str
    attribute_text: str
    attribute_eol: str

def parse_git_ls_files_output(lines):
    result: Dict[str, GitEolInfo] = {}

    for line in lines:
        # Split on whitespace and tabs, file path is always the last field
        parts = re.split(r'[ \t]+', line.strip(), maxsplit=4)
        if len(parts) < 5:
            # Try to handle missing eol section (e.g., no space after text property)
            # Try splitting with maxsplit=3
            parts = re.split(r'[ \t]+', line.strip(), maxsplit=3)
            if len(parts) < 4:
                continue  # Still malformed, skip
            index, working_dir, attr, path = parts
            eol = 'eol=unspecified'
        else:
            index, working_dir, attr, eol, path = parts
        # Remove prefix before '/' for each field
        def strip_prefix(val):
            return val.split('/', 1)[1] if '/' in val else val
        index = strip_prefix(index)
        working_dir = strip_prefix(working_dir)
        attribute_text = strip_prefix(attr)
        attribute_eol = eol
        # Unescape quoted paths
        if path.startswith('"') and path.endswith('"'):
            # Remove quotes and decode unicode escapes
            path = bytes(path[1:-1], 'utf-8').decode('unicode_escape')
        result[path] = GitEolInfo(index=index, working_directory=working_dir, attribute_text=attribute_text, attribute_eol=attribute_eol)

    return result
