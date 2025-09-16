# This script will add a user to the exclusion list if they comment "stop" on an issue created by the GitHub Action for their account.
# The issue and comment IDs are passed as arguments to the script: python './.github/workflows/exclusion.py' --issue_id ${{ github.event.issue.number }} --comment_id ${{ github.event.comment.id }}

import utils
import os
import sys
import argparse
import gh
import hashlib

def main(issue_id, comment_id):
    # Get the GitHub token from environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    # Get the repository from environment variables
    repo_name = os.getenv('GITHUB_REPOSITORY')
    if not repo_name:
        print("GITHUB_REPOSITORY environment variable not set.")
        sys.exit(1)

    try:
        # Get the issue using gh.py
        issue = gh.get_issue(github_token, repo_name, issue_id)
        if not issue:
            print(f"Error: Could not fetch issue {issue_id}")
            sys.exit(1)
            
        # Get the comment using gh.py
        comment = gh.get_comment(github_token, repo_name, comment_id)
        if not comment:
            print(f"Error: Could not fetch comment {comment_id}")
            sys.exit(1)
    except Exception as e:
        print(f"Error fetching issue or comment: {e}")
        sys.exit(1)

    # Check if the comment body starts with "stop"
    if comment['body'].strip().lower().startswith("stop"):
        user = utils.get_user_from_title(issue['title'])
        if user:
            # Add the SHA256 hash of the username to the exclusion file (following the same pattern as scan_and_suggest.py)
            user_hash = hashlib.sha256(user.encode('utf-8')).hexdigest().lower()
            exclusion_file = 'exclusion.txt'
            with open(exclusion_file, 'a') as f:
                f.write(user_hash + '\n')
            print(f"User '{user}' (hash: {user_hash}) added to exclusion list.")
        else:
            print("Could not extract user from issue title.")
    else:
        print("Comment is not 'stop'. No action taken.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process issue and comment IDs.')
    parser.add_argument('--issue_id', type=int, required=True, help='The ID of the issue.')
    parser.add_argument('--comment_id', type=int, required=True, help='The ID of the comment.')

    args = parser.parse_args()
    main(args.issue_id, args.comment_id)