# GitHub API Notes

Documentation about GitHub's API behavior and quirks discovered during development.

## Code Search API

### Search Qualifiers

#### `extension:` vs `path:` Keyword

(2025-12-17) The `path:` keyword doesn't work when searching for files with specific patterns, the `extension:` keyword works since it's part of the old search keywords