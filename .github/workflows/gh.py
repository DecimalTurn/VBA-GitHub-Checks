# Github API utilities
import os
import requests
import subprocess
import re
import utils
import datetime

office_vba_extensions = ['.docm', '.dotm', '.xlsm', '.xltm', '.xlsb', '.xlam', '.pptm', '.ppam', 'potm']
code_extensions = ['.bas', '.cls', '.frm', '.vba', '.vbs', '.vb', '.d.vb', '.txt', 'No ext']
config_extensions = ['.vbproj']

# how to call office_vba_extensions from another file?

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

def check_recently_closed_issue(token, repo_slug, issue_title, months=3):
    """Check if there's a closed issue with the same title that was closed less than the specified months ago"""
    import datetime
    from datetime import timezone
    
    try:
        # Get all closed issues
        closed_issues = get_all_issues(token, repo_slug, state='closed')
        
        # Calculate the cutoff date (3 months ago by default)
        cutoff_date = datetime.datetime.now(timezone.utc) - datetime.timedelta(days=30 * months)
        
        for issue in closed_issues:
            # Check if the title matches exactly
            if issue.get('title') == issue_title:
                # Parse the closed_at date
                closed_at_str = issue.get('closed_at')
                if closed_at_str:
                    try:
                        # Parse the ISO 8601 date string
                        closed_at = datetime.datetime.fromisoformat(closed_at_str.replace('Z', '+00:00'))
                        
                        # Check if it was closed recently
                        if closed_at > cutoff_date:
                            days_ago = (datetime.datetime.now(timezone.utc) - closed_at).days
                            print(f"🔴 Found recently closed issue '{issue_title}' (closed {days_ago} days ago)")
                            return True
                    except ValueError as e:
                        print(f"Warning: Could not parse closed_at date for issue {issue.get('number')}: {e}")
                        continue
        
        return False
        
    except Exception as e:
        print(f"🔴 Error checking for recently closed issues: {e}")
        raise Exception(f"Failed to check for recently closed issues: {e}")  # Throw to stop issue creation and move to next repo

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

def update_issue(token, this_repo_slug, issue_number, body):
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

def append_to_issue_body_if_missing(token, repo_slug, issue_number, content):
    if get_issue_body(token, repo_slug, issue_number).find(content) == -1:
        append_to_issue_body(token, repo_slug, issue_number, content)

def append_to_issue_body(token, repo_slug, issue_number, content):
    new_body = get_issue_body(token, repo_slug, issue_number) + content
    update_issue(token, repo_slug, issue_number, new_body)

def get_issue_body(token, repo_slug, issue_number):
    return get_issue(token, repo_slug, issue_number)['body']

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

def get_comment(token, repo_slug, comment_id):
    """Get a specific comment by its ID"""
    url = f"https://api.github.com/repos/{repo_slug}/issues/comments/{comment_id}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch comment {comment_id}. Status code: {response.status_code}")
        return None

def create_comment(token, repo_slug, issue_number, body):
    """Create a comment on an issue"""
    if not issue_number:
        print(f"🔴 Failed to create comment: issue_number is required")
        return None
        
    url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}/comments"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    data = {
        'body': body
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"🟢 Comment created successfully on issue {issue_number}")
        return response.json()
    else:
        print(f"🔴 Failed to create comment on issue {issue_number}. Status code: {response.status_code}")
        print(response.json())
        return None

def write_comment(token, repo_slug, issue, comment):
    """Create a comment on an issue (convenience function that takes issue object)"""
    issue_number = issue.get('number') if isinstance(issue, dict) else getattr(issue, 'number', None)
    
    if not issue_number:
        issue_title = issue.get('title') if isinstance(issue, dict) else getattr(issue, 'title', 'Unknown')
        print(f"🔴 Failed to get issue number for issue: {issue_title}")
        return None
    
    return create_comment(token, repo_slug, issue_number, comment)

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

def remove_label_from_issue(token, repo_slug, issue_number, label, ignore_not_found=False):
    url = f"https://api.github.com/repos/{repo_slug}/issues/{issue_number}/labels/{label}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        print(f"🟢 Label '{label}' removed from issue {issue_number} successfully")
    else:
        if response.status_code == 404 and ignore_not_found:
            print(f"⚪ Label '{label}' not found on issue {issue_number}, ignoring as per settings.")
            return
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

def clone_repo(repo_url):

    if repo_url == "":
        print("🔴 Repo URL was empty")
        raise ValueError("URL can't be empty.")

    if not os.path.exists(utils.subfolder_name()):
        os.makedirs(utils.subfolder_name())
    
    repo_slug =  utils.unique_folder(repo_url.split('/')[-2], repo_url.split('/')[-1])
    repo_path = os.path.join(utils.subfolder_name(), repo_slug)
    
    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} into {repo_path}")
        result = subprocess.run(["git", "clone", "--depth", "1", "--quiet", repo_url, repo_path])
        if result.returncode != 0:
            print(f"🔴 Failed to clone repository {repo_url}. Exit code: {result.returncode}")
            raise ValueError(f"Git clone failed with exit code {result.returncode}")
        return True
    else:
        print(f"Repository {repo_slug} already exists in {utils.subfolder_name()}.")
        raise ValueError("Problem with cloning.")
    
def count_vba_related_files(repo_path):

    vba_extensions = []
    vba_extensions.extend(code_extensions)
    vba_extensions.extend(config_extensions)
    vba_extensions.extend(office_vba_extensions)
    
    counts = {ext: 0 for ext in vba_extensions}
    
    for root, dirs, files in os.walk(repo_path):
        # Remove the '.git' directory from the list of directories to avoid descending into it
        dirs[:] = [d for d in dirs if d != '.git']
        for file in files:

            file_path = os.path.join(root, file)

            # Skip symbolic links
            if os.path.islink(file_path):
                continue
            
            for ext in vba_extensions:
                if ext == ".txt" or ext == ".vbs":
                    if file.endswith(ext) and is_vba_file(file_path):
                        counts[ext] += 1
                    continue
                if ext in office_vba_extensions:
                    if file.endswith(ext) and utils.is_binary_file(file_path):
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
        if count > 0:
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

def gitattributes_exists(repo_path):
    
    # Check if the .gitattributes file exists
    git_attributes_path = os.path.join(repo_path, '.gitattributes')
    
    if not os.path.exists(git_attributes_path):
        return False
    
    # If it exists, return True
    return True

# Check if there is a rule in the .gitattrubutes file that would cause .frm and .cls files to be checked-out with LF instread of CRLF
# ie. The text attribute is set to auto or set, and the eol attribute is set to lf or unspecified (not CRLF)
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
        print(f"\033[92m.frm eol result:\033[0m {frm_eol_result.stdout.strip()}")

        print(f"Checking EOL attribute for .cls files in {repo_path}")
        cls_eol_result = subprocess.run(
            ["git", "check-attr", "eol", "*.cls"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        print(f"\033[92m.cls eol result:\033[0m {cls_eol_result.stdout.strip()}")
        
        # Parse the output to check if the EOL is not set to CRLF
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
        print(f"\033[92m.frm text result:\033[0m {frm_text_result.stdout.strip()}")

        print(f"Checking text attribute for .cls files in {repo_path}")
        cls_text_result = subprocess.run(
            ["git", "check-attr", "text", "*.cls"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        print(f"\033[92m.cls text result:\033[0m {cls_text_result.stdout.strip()}")

        # Parse the output to check if the text attribute is set to auto
        frm_text_attribute = "text: auto" in frm_text_result.stdout or "text: set" in frm_text_result.stdout
        cls_text_attribute = "text: auto" in cls_text_result.stdout or "text: set" in cls_text_result.stdout
        print(f".frm text: {frm_text_attribute}, .cls text: {cls_text_attribute}")

        # Check if the repo contains .frm and .cls files using the counts 
        frm_count = counts[".frm"]
        cls_count = counts[".cls"]
        print(f"Number of .frm files: {frm_count}, Number of .cls files: {cls_count}")

        if (frm_text_attribute and frm_not_crlf and frm_count > 0) or (cls_text_attribute and cls_not_crlf and cls_count > 0):
            print("gitattributes misconfigured: True")
            return True
        else:
            print("gitattributes misconfigured: False")
            return False
    except Exception as e:
        print(f"🔴 Error while checking .gitattributes: {e}")
        return False

# This functions should be called only if there is no .gitattributes file in the repo 
# It will look at the output of git ls-files --eol and check if there are any .frm or .cls files LF line endings
# That would indicate the the author is working on a Windows machine and core.autocrlf is set to true
# In that case, we suggest to create a .gitattributes file with the correct settings (Check G)
def gitattributes_needed(repo_path, counts):
    
    if gitattributes_exists(repo_path):
        print("🔴 .gitattributes file found, gitattributes_needed should not be called in that context.")
        return False
    
    import git_ls_parser
    
    # If the repo_path is empty, assume the current directory
    if not repo_path:
        repo_path = os.getcwd()

    # Get the output of git ls-files --eol
    ls_files_output = get_git_ls_files_output(repo_path)
    
    if not ls_files_output:
        print("🔴 No output from 'git ls-files --eol'")
        return False

    # Parse the output to find .frm and .cls files with LF line endings
    parsed_data = git_ls_parser.parse_git_ls_files_output(ls_files_output)
    problematic_files = get_problematic_files_check_g(parsed_data)

    if problematic_files:
        print(f"🔴Problematic files found: {problematic_files}")
        return True
    else:
        print("🟢 No problematic .frm or .cls files found.")
        return False

def cls_file_excluded(file_path):
    """
    Check if a .cls file should be excluded from checks.
    
    Args:
        file_path: The full file path to check
        
    Returns:
        True if the file should be excluded (ThisWorkbook.cls or Sheet\d.cls pattern), False otherwise
    """
    # Extract just the filename from the path
    filename = os.path.basename(file_path)
    
    # Skip ThisWorkbook.cls
    if filename == "ThisWorkbook.cls":
        return True
        
    # Skip files matching Sheet\d.cls pattern (e.g., Sheet1.cls, Sheet2.cls)
    if re.match(r'^Sheet\d+\.cls$', filename):
        return True
        
    return False

def get_problematic_files_check_g(parsed_data):
    """
    Analyze parsed git ls-files output to find problematic .frm and .cls files for Check G.
    This check applies when there's no .gitattributes file and .frm/.cls files have LF line endings
    in the index, suggesting the author is on Windows with core.autocrlf=true but needs a .gitattributes file.
    
    Args:
        parsed_data: Dictionary with file paths as keys and git ls-files info as values
        
    Returns:
        List of file paths that are problematic for Check G (empty list if none found)
    """
    problematic_files_check_g = []

    for fname, info in parsed_data.items():
        if (fname.endswith(".frm") or fname.endswith(".cls")) and info.index == "lf":

            # Skip excluded .cls files (ThisWorkbook.cls and Sheet\d.cls)
            if fname.endswith(".cls") and cls_file_excluded(fname):
                continue

            problematic_files_check_g.append(fname)
    
    return problematic_files_check_g



def generate_body_for_issue_for_scanned_repo(previous, new_repos):
    """
    This function will receive a list of repos and generate the body for the issue
    The body of the issue will be a TOML file formatted as a code block
    The format will be:
    ```toml
    [repo_slug]
    repo_name = "repo_name"
    repo_url = "repo_url"
    repo_owner = "repo_owner"
    commit_id = "latest_commit"
    scan_date = "analysis_date"
    outcome = "outcome"
    """

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

def get_git_ls_files_output(repo_path):
    """
    Get the output of 'git ls-files --eol' for the given repo path.
    Returns a list of lines from the command output.
    """
    try:
        print(f"Running 'git ls-files --eol' in {repo_path}")
        result = subprocess.run(
            ["git", "ls-files", "--eol"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"🔴 Error running 'git ls-files --eol': {result.stderr.strip()}")
            return []
        return result.stdout.splitlines()
    except Exception as e:
        print(f"🔴 Error while getting git ls-files output: {e}")
        return []

def get_problematic_files_check_f(parsed_data):
    """
    Analyze parsed git ls-files output to find problematic .frm and .cls files for Check F.
    ie. files that have the text attribute unset (-text) and LF line endings.
    
    Args:
        parsed_data: Dictionary with file paths as keys and git ls-files info as values
        
    Returns:
        List of file paths that are problematic for Check F (empty list if none found)
    """
    problematic_files_check_f = []

    for fname, info in parsed_data.items():
        if (fname.endswith(".frm") or fname.endswith(".cls")) and info.index == "lf":
            
            # Skip excluded .cls files (ThisWorkbook.cls and Sheet\d.cls)
            if fname.endswith(".cls") and cls_file_excluded(fname):
                continue
            
            # Check if file has proper text attribute and eol=crlf
            attribute_list = info.attribute_text if isinstance(info.attribute_text, list) else [str(info.attribute_text)]
            has_text_attr_unset = "-text" in attribute_list
            
            eol_attribute_list = info.attribute_eol if isinstance(info.attribute_eol, list) else [str(info.attribute_eol)]
            has_crlf_eol = "eol=crlf" in eol_attribute_list
            
            # Check F only applies if text attribute is unset (-text)
            # If a file has -text set, no conversion will happen during the .zip download and when cloning the repos
            if has_text_attr_unset:
                problematic_files_check_f.append(fname)
    
    return problematic_files_check_f

def is_repo_empty(repo_path):
    # Check if the repo_path is empty
    if not repo_path:
        print("🔴 Repo path is empty")
        raise ValueError("Repo path can't be empty.")
    
    # Check if the .git directory exists
    git_dir = os.path.join(repo_path, '.git')
    if not os.path.exists(git_dir):
        print(f"🔴 .git directory does not exist in {repo_path}")
        raise ValueError(".git directory does not exist.")
    
    # Check if there are any files in the repo (excluding .git)
    for root, dirs, files in os.walk(repo_path):
        # Remove the '.git' directory from the list of directories to avoid descending into it
        dirs[:] = [d for d in dirs if d != '.git']
        if files:
            return False  # Found files, repo is not empty
    
    return True  # No files found, repo is empty