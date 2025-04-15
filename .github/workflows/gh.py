# Github API utilities
import os
import requests
import subprocess
import re

def get_all_issues_title(token, repo_slug):
    url = f"https://api.github.com/repos/{repo_slug}/issues"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    params = {
        'per_page': 100,  # Maximum number of issues per page
        'state': 'all',   # Fetch all issues, open and closed
        'page': 1         # Start with the first page
    }
    
    all_issues_title = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            issues = response.json()
            all_issues_title.extend([issue['title'] for issue in issues])
            
            if len(issues) < 100:
                # If fewer than 100 issues were returned, this is the last page
                break
            else:
                # Move to the next page
                params['page'] += 1
        else:
            print(f"🔴 Failed to fetch issues. Status code: {response.status_code}")
            raise ValueError("Problem while fetching issues.")
    
    return all_issues_title

#Change this function to get only the issues that match the state (all, open, closed)
def get_all_issues(token, repo_slug, state='all'):
    url = f"https://api.github.com/repos/{repo_slug}/issues"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }

    params = {
        'per_page': 100,  # Maximum number of issues per page
        'state': state,   # Fetch issues that match the provided state
        'page': 1         # Start with the first page
        
    }
    
    all_issues_title = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            issues = response.json()
            all_issues_title.extend([issue for issue in issues])
            
            if len(issues) < 100:
                # If fewer than 100 issues were returned, this is the last page
                break
            else:
                # Move to the next page
                params['page'] += 1
        else:
            print(f"🔴 Failed to fetch issues. Status code: {response.status_code}")
            raise ValueError("Problem while fetching issues.")
    
    return all_issues_title

def get_issue(token, repo_slug , issue_number):
    url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch issue {issue_number}. Status code: {response.status_code}")

# Check if the issue already has a comment containing the provided substring
def already_commented(token, repo_slug, issue_number, sub_string):
    url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}/comments"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        comments = response.json()
        for comment in comments:
            if sub_string in comment['body']:
                return True
    else:
        print(f"Failed to fetch comments for issue {issue_number}. Status code: {response.status_code}")
        raise ValueError("Problem while fetching comments.")
    
    return False

def add_label_to_issue(token, repo_slug, issue_number, label):
    url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}/labels"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    data = [label]
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"🟢 Label '{label}' added to issue {issue_number} successfully")
    else:
        print(f"🔴 Failed to add label to issue {issue_number}. Status code: {response.status_code}")
        print(response.json())

def remove_label_from_issue(token, repo_slug, issue_number, label):
    url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}/labels/{label}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        print(f"🟢 Label '{label}' removed from issue {issue_number} successfully")
    else:
        print(f"🔴 Failed to remove label from issue {issue_number}. Status code: {response.status_code}")
        print(response.json())

def close_issue(token, repo_slug, issue, reason):
    issue_number = issue['number']
    
    if issue_number:
        url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {token}'
        }
        data = {
            'state': 'closed',
            'state_reason': reason
        }
        
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"🟢 Issue {issue_number} closed successfully")
        else:
            print(f"🔴 Failed to close issue {issue_number}. Status code: {response.status_code}")
            print(response.json())
    else:
        print(f"Failed to get issue number for issue: {issue['title']}")

def clone_repo(repo_url, destination_folder):

    if repo_url == "":
        print("🔴 Repo URL was empty")
        return

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    repo_name =  repo_url.split('/')[-2] + " --- " + repo_url.split('/')[-1]
    repo_path = os.path.join(destination_folder, repo_name)
    
    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} into {repo_path}")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, repo_path])
        return repo_name
    else:
        print(f"Repository {repo_name} already exists in {destination_folder}.")
        raise ValueError("Problem with cloning.")
    
def count_vba_related_files(repo_path):
    vba_extensions = ['.bas', '.cls', '.frm', '.vba', '.vbs', '.vb', '.d.vb', '.vbproj', '.txt', 'No ext']
    counts = {ext: 0 for ext in vba_extensions}
    
    for root, dirs, files in os.walk(repo_path):
        # Remove the '.git' directory from the list of directories to avoid descending into it
        dirs[:] = [d for d in dirs if d != '.git']
        for file in files:
            file_path = os.path.join(root, file)
            for ext in vba_extensions:
                if ext == ".txt" or ext == ".vbs":
                    if file.endswith(ext) and is_vba_file(file_path):
                        counts[ext] += 1
                    continue
                if file.endswith(ext):
                    counts[ext] += 1
                    continue
                if ext == 'No ext' and '.' not in file:
                    if is_vba_file(file_path):
                        counts[ext] += 1
                        continue

    # Print the counts
    for ext, count in counts.items():
        print(f"Number of '{ext}' files: {count}")
    
    return counts

def is_vba_file(file_path):
    with open(file_path, 'r', encoding='cp1252', errors='ignore') as f:
        file_content = f.read()
    return has_vba_code(file_content)

def has_vba_code(file_content):
    vba_pattern = re.compile(r'^\s*(Public|Private)?\s*(Sub|Function)\s+', re.MULTILINE)
    return bool(vba_pattern.search(file_content))

# Get the labels for the issue and extract the name of the check (Check A, Check B, etc.)
def get_check(issue):
    labels = issue['labels']
    for label in labels:
        if label['name'].startswith('Check'):
            check_prefix = 'Check '
            for label in labels:
                if label['name'].startswith(check_prefix):
                    return label['name'][len(check_prefix):]
    return None

# Check if the repo is deleted by checking if the repo_url returns a 404
# NB.: Because this is a simple https request, we don't need to pass the token
def check_repo_deleted(repo_url):
    response = requests.get(repo_url)
    if response.status_code == 404:
        return True
    else:
        return False