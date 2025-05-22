# Summary:
# - Collect all open issues
# - Filter by check/issue


import requests
import os
import sys
import re

# Custom modules
import gh
import utils

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
        repo_url = "https://github.com/" + repo_slug

        repo_info = get_repo_info(token, user, repo_name)
        if not repo_info:
            print(f"Failed to get repo info for issue: {issue['title']}")
            continue

        # Check if the repo was deleted or privated
        if repo_info['status_code'] == 404:
            print(f"Repo {user}/{repo_name} has been deleted, closing issue {issue['title']}")
            gh.close_issue(token, repo_slug, issue, "not_planned")
            write_comment(token, repo_slug, issue, "Looks like the repository has been deleted or privated. Closing the issue.")
            gh.add_label_to_issue(token, os.getenv('GITHUB_REPOSITORY'), issue['number'], "repo deleted")
            continue
        
        if check == "A":
            follow_up_check_A(token, repo_info, user, repo_name, issue)
        elif check == "B":
             follow_up_check_B(token, repo_info, user, repo_name, issue)
        elif check == "C":
             follow_up_check_C(token, repo_info, user, repo_name, issue)
        elif check == "D":
             follow_up_check_D(token, repo_info, user, repo_name, issue)


def follow_up_check_A(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check A
    if repo_info['language'] == 'VBA':
        
        subCheck = False
        gitattribute_override = check_gitattributes(token, user, repo_name, 'vb')
        if not gitattribute_override:
            subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck AA]")

        if not subCheck:
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['.vb'] == 0 or gitattribute_override:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += "However, there are still files with the .vb extension. Is this intentional? [SubCheck AA]" + "\n"               
        
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['.vb'] > 0 and not gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck AB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔. " + "\n"
            comment += "There are still files with the .vb extension. Is this intentional? [SubCheck AB]" + "\n"  

    if comment:
        write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_B(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check B
    if repo_info['language'] == 'VBA':
        
        subCheck = False
        gitattribute_override = check_gitattributes(token, user, repo_name, 'vbs')
        if not gitattribute_override:
            subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck BA]")
        
        if not subCheck:
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['.vbs'] == 0 or gitattribute_override:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += "However, there are still files with the .vbs extension. Is this intentional? [SubCheck BA]" + "\n"               
        
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['.vbs'] > 0 and not gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck BB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔." + "\n"
            comment += "There are still files with the .vbs extension. Is this intentional? [SubCheck BB]" + "\n"  

    if comment:
        write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_C(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check C
    if repo_info['language'] == 'VBA':

        subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck CA]")
        if not subCheck:
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['No ext'] == 0:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += "However, there are still files with no extension that contain VBA code. Is this intentional? [SubCheck CA]" + "\n"   
           
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['No ext'] > 0 and not gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck CB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔." + "\n"
            comment += "There are still files with no extension that contain VBA code. Is this intentional? [SubCheck CB]" + "\n"  

    if comment:
        write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_D(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check D
    if repo_info['language'] == 'VBA':

        subCheck = False
        gitattribute_override = check_gitattributes(token, user, repo_name, 'txt')
        if not gitattribute_override:
            subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck DA]")

        if not subCheck:
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['.txt'] == 0 or gitattribute_override:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += "However, there are still files with the .txt extension that contain VBA code. Is this intentional? [SubCheck DA]" + "\n"   
           
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['.txt'] > 0 and not gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck DB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔." + "\n"
            comment += "There are still files with the .txt extension that contain VBA code. Is this intentional? [SubCheck DB]" + "\n"  

    if comment:
        write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_E(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check E
    if not gh.gitattributes_misconfigured(token, user, repo_name):
        comment = "Looks like you made some changes and the .gitattributes file is now correctly configured." + "\n"
        comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
        gh.close_issue(token, main_repo_slug, issue, "completed")
        handle_labels_after_completion(token, main_repo_slug, issue_number)
        return

    if comment:
        write_comment(token, main_repo_slug, issue, comment)

# This function looks inside the gitattributes file of the repository to check if the they added a rule to 
# consider the extension as VBA via the linguist-language override
def check_gitattributes(token, user, repo_name, ext):
    # The repo should already be cloned at this stage, so we look directly in the gitattributes file
    repo_path = utils.repo_path(user, repo_name)
    gitattributes_path = os.path.join(repo_path, '.gitattributes')
    if not os.path.exists(gitattributes_path):
        return False
    
    # Check if there is a line with the pattern *.ext linguist-language=VBA
    pattern = re.compile(rf"\*\.{ext}\s+.*\blinguist-language=VBA")
    with open(gitattributes_path, 'r') as file:
        for line in file:
            if pattern.search(line):
                return True

def handle_labels_after_completion(token, main_repo_slug, issue_number):
    gh.add_label_to_issue(token, main_repo_slug, issue_number, "completed")
    gh.remove_label_from_issue(token, main_repo_slug, issue_number, "stale")  

def get_repo_info(token, user, repo_name):
    url = f"https://api.github.com/repos/{user}/{repo_name}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repo_info = response.json()
        # Add a status code to the repo_info
        repo_info['status_code'] = response.status_code
        return repo_info
    elif response.status_code == 404:
        # Return a minimal repo_info indicating not found
        return {'status_code': 404, 'full_name': f"{user}/{repo_name}"}
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
        gh.clone_repo(html_url)
    except Exception as e:
        print(f"Error cloning the repo: {e}")
        return

    # Count the number of files in the repo

    repo_path = utils.repo_path(user, repo_name)
    if not os.path.exists(repo_path):
        print(f"🔴 Error: Repository path {repo_path} does not exist.")
        return
    
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