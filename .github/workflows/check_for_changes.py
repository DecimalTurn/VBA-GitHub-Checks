#Q: Should the outter loop be relative to the different Checks (A, B, C , etc) or one issue at a time?
#A: from a degugging perspective, it would be nicer to have the logs grouped by types of checks to see how things behave
#   from a preformance standpoint, it might be slightly better to have the outter loop be the Issues-iterator, but that should be minimal

#todo:
# - Collect all open issues
# - Filter by check/issue
# - CheckA:
# - Extract user and repo_name (repo slug)
# - Get the infos on the repo
# - Check the infos to see if language is VBA
# - If yes, close the issue and write a comment.
# - If no, check if at least some files now have the extension .vba
    # - If yes, write a message saying that it's great that they changing the name of files from .vb to .vba, but there are still files with the .vb extension. Is that volontrary?

# This script at the moment performs Subcheck A only
# SubCheck A: Verify that now all files have the .vba extension and no longer have the .vb extension (.vbs for check B).

import requests
import os
import sys

# Custom modules
import gh

all_issues = None

def follow_up_issues(token, repo_slug):
    global all_issues
    
    for issue in all_issues:
        # Extract the user and repo_name from the issue title
        user, repo_name = issue['title'].split('/')[0].replace("[", ""), issue['title'].split('/')[1].replace("]", "")
        
        #Check if there is already a comment with the tag [SubCheck A] in the comments of the issue
        if gh.already_commented(issue, "[SubCheck A]"):
            print(f"Already commented on issue {issue['title']} for SubCheck A")
            continue

        # Get the information on the repo
        repo_info = get_repo_info(token, user, repo_name)
        
        if repo_info:
            # Check if the language is not VBA
            if repo_info['language'] == 'VBA':
                
                if not gh.already_commented(issue, "[SubCheck A]"):
                    comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

                # Check if there are still files with the .vb extension if not, close the issue
                if not has_vb_files(repo_info['repo_path']):
                    comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
                    close_issue(token, repo_slug, issue)
                else:
                    comment += "However, there are still files with the .vb extension. Is this intentional? [SubCheck A]" + "\n"               
                
            else:
                # Check if there are now files with the .vba extension
                if has_vba_files(repo_info['repo_path']) and not gh.already_commented(issue, "[SubCheck B]"):
                    comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔 [SubCheck B]. " + "\n"
            
            if comment:
                write_comment(token, repo_slug, issue, comment)

        else:
            print(f"Failed to get repo info for issue: {issue['title']}")

def get_repo_info(token, user, repo_name):
    url = f"https://api.github.com/repos/{user}/{repo_name}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repo_info = response.json()
        repo_info['repo_path'] = os.path.join('repos', f"{user} --- {repo_name}")
        return repo_info
    else:
        print(f"Failed to fetch repo info for {user}/{repo_name}. Status code: {response.status_code}")
        return None

def has_vb_files(repo_path):
    #This function is not implemented yet, return an error when called
    print("Function has_vb_files not implemented yet.")
    sys.exit(1)    
    

def close_issue(token, repo_slug, issue):
    issue_number = issue['number']
    
    if issue_number:
        url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {token}'
        }
        data = {
            'state': 'closed'
        }
        
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"🟢 Issue {issue_number} closed successfully")
        else:
            print(f"🔴 Failed to close issue {issue_number}. Status code: {response.status_code}")
            print(response.json())
    else:
        print(f"Failed to get issue number for issue: {issue['title']}")

def write_comment(token, repo_slug, issue, comment):
    issue_number = issue['number']
    
    if issue_number:
        url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}/comments"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {token}'
        }
        data = {
            'body': comment
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"🟢 Comment posted successfully on issue {issue_number}")
        else:
            print(f"🔴 Failed to post comment on issue {issue_number}. Status code: {response.status_code}")
            print(response.json())
    else:
        print(f"Failed to get issue number for issue: {issue['title']}")


def main():

    global all_issues
    token = os.getenv('GITHUB_TOKEN')
    all_issues = gh.get_all_issues(token, os.getenv('GITHUB_REPOSITORY'), 'open')

    follow_up_issues(token, os.getenv('GITHUB_REPOSITORY'))


if __name__ == "__main__":
    main()