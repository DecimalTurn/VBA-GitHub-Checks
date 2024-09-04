# Summary:
# - Collect all open issues
# - Filter by check/issue
# - CheckA

# This script at the moment performs Subcheck A only
# SubCheck AA: Verify that now all files have the .vba extension and no longer have the .vb extension (.vbs for check B).
# SubCheck AB: Verify if the user intentionally left files with the .vb extension (.vbs for check B) in the repository.

import requests
import os
import sys

# Custom modules
import gh

all_open_issues = None

def follow_up_issues(token, repo_slug):
    global all_open_issues
    
    for issue in all_open_issues:

        # See what Check is associated with the issue
        # The Check is based on the label (Check A, Check B, etc)
        check = gh.get_check(issue)

        if check == None:
            continue

        # Extract the user and repo_name from the issue title
        user = issue['title'].split('/')[0].replace("[", "")
        repo_name = issue['title'].split('/')[1].split(']')[0]
        
        if check == "A":
            follow_up_check_A(token, user, repo_name, issue)
        elif check == "B":
             follow_up_check_B(token, user, repo_name, issue)


def follow_up_check_A(token, user, repo_name, issue):

    repo_slug = user + "/" + repo_name

    # Check if there is already a comment with the tag [SubCheck A] in the comments of the issue
    if gh.already_commented(issue, "[SubCheck A"):
        print(f"Already commented on issue {issue['title']} for SubCheck A")
        return

    # Get the information on the repo
    repo_info = get_repo_info(token, user, repo_name)
    if not repo_info:
        print(f"Failed to get repo info for issue: {issue['title']}")
        return

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check A
    if repo_info['language'] == 'VBA':
        
        if not gh.already_commented(issue, "[SubCheck AA]"):
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['.vb'] == 0:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, repo_slug, issue)
        else:
            comment += "However, there are still files with the .vb extension. Is this intentional? [SubCheck AA]" + "\n"               
        
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['.vb'] > 0 and not gh.already_commented(issue, "[SubCheck AB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔 [SubCheck AB]. " + "\n"
            comment += "There are still files with the .vb extension. Is this intentional?" + "\n"  

    if comment:
        write_comment(token, os.getenv('GITHUB_REPOSITORY'), issue, comment)

def follow_up_check_B(token, user, repo_name, issue):

    repo_slug = user + "/" + repo_name

    # Check if there is already a comment with the tag [SubCheck B] in the comments of the issue
    if gh.already_commented(issue, "[SubCheck B"):
        print(f"Already commented on issue {issue['title']} for SubCheck B")
        return

    # Get the information on the repo
    repo_info = get_repo_info(token, user, repo_name)
    if not repo_info:
        print(f"Failed to get repo info for issue: {issue['title']}")
        return

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check B
    if repo_info['language'] == 'VBA':
        
        if not gh.already_commented(issue, "[SubCheck BA]"):
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['.vbs'] == 0:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, repo_slug, issue)
        else:
            comment += "However, there are still files with the .vbs extension. Is this intentional? [SubCheck AA]" + "\n"               
        
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['.vbs'] > 0 and not gh.already_commented(issue, "[SubCheck BB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔 [SubCheck AB]. " + "\n"
            comment += "There are still files with the .vbs extension. Is this intentional?" + "\n"  

    if comment:
        write_comment(token, os.getenv('GITHUB_REPOSITORY'), issue, comment)


def get_repo_info(token, user, repo_name):
    url = f"https://api.github.com/repos/{user}/{repo_name}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repo_info = response.json()
        return repo_info
    else:
        print(f"Failed to fetch repo info for {user}/{repo_name}. Status code: {response.status_code}")
        return None

def get_counts(token, user, repo_name):
    #This function is not implemented yet, return an error when called
    #print("Function has_vb_files not implemented yet.")
    #sys.exit(1)   
   
    # Clone the repo
    html_url = f"https://github.com/{user}/{repo_name}"
    try:
        repo_name = gh.clone_repo(html_url, 'repos')
    except Exception as e:
        print(f"Error cloning the repo: {e}")
        return

    # Count the number of .vb files in the repo
    repo_path = os.path.join('repos', repo_name)
    try:
        return gh.count_vba_related_files(repo_path)
    except Exception as e:
        print(f"🔴 Error counting VBA-related files: {e}")
        return

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

    global all_open_issues
    token = os.getenv('GITHUB_TOKEN')
    all_open_issues = gh.get_all_issues(token, os.getenv('GITHUB_REPOSITORY'), 'open')

    follow_up_issues(token, os.getenv('GITHUB_REPOSITORY'))


if __name__ == "__main__":
    main()