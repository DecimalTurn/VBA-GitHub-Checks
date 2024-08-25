#Q: Should the outter loop be relative to the different Checks (A, B, C , etc) or one issue at a time?
#A: from a degugging perspective, it would be nicer to have the logs grouped by types of checks to see how things behave
#   from a preformance standpoint, it might be slightly better to have the outter loop be the Issues-iterator, but that should be minimal

#todo:
# - Collect all open issues
# - Filter by check/issue
# - CheckA:
# - Extract user and repo_name (repo slug)
# - Get the infos on the repo
# - Check the infos to see if language is not VBA
# - If yes, close the issue and write a comment.
# - If no, check if at least some files now have the extension .vba
    # - If yes, write a message saying that it's great that they changing the name of files from .vb to .vba, but there are still files with the .vb extension. Is that volontrary.

