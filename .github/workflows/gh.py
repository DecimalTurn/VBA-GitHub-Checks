# Github API utilities
import requests

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
def already_commented(issue, sub_string):
    comments = issue['comments']
    if comments > 0:
        for comment in issue['comments']:
            if sub_string in comment['body']:
                return True
    return False

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
        subprocess.run(["git", "clone", repo_url, repo_path])
        return repo_name
    else:
        print(f"Repository {repo_name} already exists in {destination_folder}.")
        raise ValueError("Problem with cloning.")