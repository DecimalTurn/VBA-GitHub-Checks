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
