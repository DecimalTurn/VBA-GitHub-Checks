from dataclasses import dataclass
from typing import Dict
import re

@dataclass
class GitEolInfo:
    index: str
    working_directory: str
    attribute: str

def parse_git_ls_files_output(lines):
    result: Dict[str, GitEolInfo] = {}

    for line in lines:
        # Split on whitespace and tabs, file path is always the last field
        parts = re.split(r'[ \t]+', line.strip(), maxsplit=4)
        if len(parts) < 5:
            continue  # Skip malformed lines
        index, working_dir, attr, eol, path = parts
        # Remove prefix before '/' for each field
        def strip_prefix(val):
            return val.split('/', 1)[1] if '/' in val else val
        index = strip_prefix(index)
        working_dir = strip_prefix(working_dir)
        attribute = strip_prefix(attr)
        # Unescape quoted paths
        if path.startswith('"') and path.endswith('"'):
            # Remove quotes and decode unicode escapes
            path = bytes(path[1:-1], 'utf-8').decode('unicode_escape')
        result[path] = GitEolInfo(index=index, working_directory=working_dir, attribute=attribute)

    return result
