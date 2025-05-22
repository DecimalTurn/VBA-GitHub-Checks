# Github API utilities
import os
import requests
import subprocess
import re
import utils
import datetime

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

def create_github_issue(token, this_repo_slug, title, body, labels=None):
    url = f"https://api.github.com/repos/{this_repo_slug}/issues"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    data = {
        'title': title,
        'body': body,
        'labels': labels if labels else []  # Use the provided labels or an empty list if none are given
    }
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"🟢 Issue created successfully: {response.json()['html_url']}")
        return response.json()['number']
    else:
        print(f"🔴 Failed to create issue. Status code: {response.status_code}")
        print(response.json())

# Once during the existence of the repo, we need to create a new issue that stores the information about the repo we've scanned in the last week
# Can call create_github_issue and pass it hardcoded values that are unique to that issue
def create_github_issue_for_scanned_repo(token, this_repo_slug):
    title = "Scanning cache"
    body = "This issue is used to store the information about the repo we've scanned in the last week"
    create_github_issue(token, this_repo_slug, title, body)

def get_issue_for_scanned_repo(token, this_repo_slug):
    # Get all issues for the repo
    all_issues = get_all_issues(token, this_repo_slug)
    
    # Iterate through all issues and check if the title matches
    for issue in all_issues:
        if issue['title'] == "Scanning cache":
            return issue
    
    # If no matching issue is found, return None
    return None

def update_issue_for_scanned_repo(token, this_repo_slug, issue_number, body):
    url = f"https://api.github.com/repos/{this_repo_slug}/issues/{issue_number}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    data = {
        'body': body
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print(f"🟢 Issue updated successfully: {response.json()['html_url']}")
    else:
        print(f"🔴 Failed to update issue. Status code: {response.status_code}")
        print(response.json())


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
        raise ValueError("URL can't be empty.")

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    repo_name =  utils.unique_folder(repo_url.split('/')[-2], repo_url.split('/')[-1])
    repo_path = os.path.join(destination_folder, repo_name)
    
    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} into {repo_path}")
        subprocess.run(["git", "clone", "--depth", "1", repo_url, repo_path])
        return True
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

def gitattributes_exists(repo_path):
    
    # Check if the .gitattributes file exists
    git_attributes_path = os.path.join(repo_path, '.gitattributes')
    
    if not os.path.exists(git_attributes_path):
        return False
    
    # If it exists, return True
    return True

# Check if there is a rule in the .gitattrubutes file that would cause .frm and .cls files to be checked-out as with LF instread of CRLF
def gitattributes_misconfigured(repo_path, counts):

    # If the repo_path is empty, assume the current directory
    if not repo_path:
        repo_path = os.getcwd()

    # Check if the .gitattributes file exists
    git_attributes_path = os.path.join(repo_path, '.gitattributes')
    
    if not os.path.exists(git_attributes_path):
        # throw an error if the file does not exist
        print("🔴 .gitattributes file does not exist")
        raise ValueError("Problem while checking .gitattributes file.")
    
    # Print the output of git ls-files --eol for .frm and .cls files
    try:
        print(f"Running 'git ls-files --eol *.frm' in {repo_path}")
        frm_ls_eol = subprocess.run(
            ["git", "ls-files", "--eol", "*.frm"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        print(f"Output of 'git ls-files --eol *.frm':\n{frm_ls_eol.stdout.strip()}")

        print(f"Running 'git ls-files --eol *.cls' in {repo_path}")
        cls_ls_eol = subprocess.run(
            ["git", "ls-files", "--eol", "*.cls"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        print(f"Output of 'git ls-files --eol *.cls':\n{cls_ls_eol.stdout.strip()}")
    except Exception as e:
        print(f"🔴 Error running 'git ls-files --eol': {e}")

    # Check the EOL attribute for .frm and .cls files
    try:
        print(f"Checking EOL attribute for .frm files in {repo_path}")
        frm_eol_result = subprocess.run(
            ["git", "check-attr", "eol", "*.frm"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        print(f".frm eol result: {frm_eol_result.stdout.strip()}")

        print(f"Checking EOL attribute for .cls files in {repo_path}")
        cls_eol_result = subprocess.run(
            ["git", "check-attr", "eol", "*.cls"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        print(f".cls eol result: {cls_eol_result.stdout.strip()}")
        
        # Parse the output to check if the EOL is set to LF
        frm_not_crlf = "eol: lf" in frm_eol_result.stdout or "eol: unspecified" in frm_eol_result.stdout
        cls_not_crlf = "eol: lf" in cls_eol_result.stdout or "eol: unspecified" in cls_eol_result.stdout
        print(f".frm not CRLF: {frm_not_crlf}, .cls not CRLF: {cls_not_crlf}")

        print(f"Checking text attribute for .frm files in {repo_path}")
        frm_text_result = subprocess.run(
            ["git", "check-attr", "text", "*.frm"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        print(f".frm text result: {frm_text_result.stdout.strip()}")

        print(f"Checking text attribute for .cls files in {repo_path}")
        cls_text_result = subprocess.run(
            ["git", "check-attr", "text", "*.cls"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        print(f".cls text result: {cls_text_result.stdout.strip()}")

        # Parse the output to check if the text attribute is set to auto
        frm_text = "text: auto" in frm_text_result.stdout or "text: set" in frm_text_result.stdout
        cls_text = "text: auto" in cls_text_result.stdout or "text: set" in cls_text_result.stdout
        print(f".frm text: {frm_text}, .cls text: {cls_text}")

        # Check if the repo contains .frm and .cls files using the counts 
        frm_count = counts[".frm"]
        cls_count = counts[".cls"]
        print(f"Number of .frm files: {frm_count}, Number of .cls files: {cls_count}")

        if (frm_text and frm_not_crlf and frm_count > 0) or (cls_text and cls_not_crlf and cls_count > 0):
            print("gitattributes check result: True")
            return True
        else:
            print("gitattributes check result: False")
            return False
    except Exception as e:
        print(f"🔴 Error while checking .gitattributes: {e}")
        return False
    
# This function will receive a list of repos and generate the body for the issue
# The body of the issue will be a TOML file formatted as a code block
# The format will be:
# ```toml
# [repo_slug]
# repo_name = "repo_name"
# repo_url = "repo_url"
# repo_owner = "repo_owner"
# commit_id = "latest_commit"
# scan_date = "analysis_date"
# outcome = "outcome"
# ```
def generate_body_for_issue_for_scanned_repo(previous, new_repos):

    # parse the previous issue body
    # and create a dictionary with the repo_slug as the key
    # and the rest of the information as the value
    previous_repos = {}
    for line in previous.splitlines():
        if line.startswith("[") and line.endswith("]"):
            repo_slug = line[1:-1]
            previous_repos[repo_slug] = {}
        elif "=" in line:
            key, value = line.split("=")
            key = key.strip()
            value = value.strip().strip('"')
            previous_repos[repo_slug][key] = value
    
    # Now we can create the body for the new issue
    # If the scan_date for a repo is older than a week, we can remove it from the body
    # If the repo is not in the previous issue, we can add it to the body
    # If the repo is in the previous issue, we can update the scan_date and outcome if the commit_id is different
    current_repos = {}
    for repo in previous_repos:
        repo_slug = f"{repo['owner']['login']}/{repo['name']}"
        # Check if the repo was scanned in the last week
        scan_date = datetime.datetime.strptime(repo['scan_date'], "%Y-%m-%d")
        if (datetime.datetime.now() - scan_date).days <= 7:
            # Add the repo to the current repos
            current_repos[repo_slug] = {
                'repo_name': repo['name'],
                'repo_url': repo['html_url'],
                'repo_owner': repo['owner']['login'],
                'commit_id': repo['commit_id'],
                'scan_date': repo['scan_date'],
                'outcome': repo['outcome']
            }
    
    # Loop over repos in repos and add them to the current_repos
    for repo in new_repos:
        repo_slug = f"{repo['owner']['login']}/{repo['name']}"
        # Check if the repo is already in the current_repos
        if repo_slug not in current_repos:
            # Add the repo to the current_repos
            current_repos[repo_slug] = {
                'repo_name': repo['name'],
                'repo_url': repo['html_url'],
                'repo_owner': repo['owner']['login'],
                'commit_id': repo['commit_id'],
                'scan_date': repo['scan_date'],
                'outcome': repo['outcome']
            }
        else:
            # Check if the commit_id is different
            if current_repos[repo_slug]['commit_id'] != repo['commit_id']:
                # Update the commit_id and scan_date
                current_repos[repo_slug]['commit_id'] = repo['commit_id']
                current_repos[repo_slug]['scan_date'] = repo['scan_date']
                current_repos[repo_slug]['outcome'] = repo['outcome']

    # Now we can create the body for the new issue
    body = "```toml\n"
    for repo in current_repos:
        body += f"[{repo['owner']['login']}/{repo['name']}]\n"
        body += f'repo_name = "{repo["name"]}"\n'
        body += f'repo_url = "{repo["html_url"]}"\n'
        body += f'repo_owner = "{repo["owner"]["login"]}"\n'
        body += f'commit_id = "{repo["commit_id"]}"\n'
        body += f'scan_date = "{repo["scan_date"]}"\n'
        body += f'outcome = "{repo["outcome"]}"\n'
        body += "\n"
    body += "```"
    return body
