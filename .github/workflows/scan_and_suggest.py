import requests
import os
import subprocess
import time

def get_all_issues(repo_full_name, token):
    url = f"https://api.github.com/repos/{repo_full_name}/issues"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    params = {
        'per_page': 100,  # Maximum number of issues per page
        'state': 'all',   # Fetch all issues, open and closed
        'page': 1         # Start with the first page
    }
    
    all_issues = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            issues = response.json()
            all_issues.extend([issue['title'] for issue in issues])
            
            if len(issues) < 100:
                # If fewer than 100 issues were returned, this is the last page
                break
            else:
                # Move to the next page
                params['page'] += 1
        else:
            print(f"Failed to fetch issues. Status code: {response.status_code}")
            break
    
    return all_issues

def already_issue_for_user(issue_title, all_issues):
    # Extract the user from the issue_title (everything before the first '/')
    user_from_title = issue_title.split('/')[0]
    
    # Iterate through all issues and check if the user matches
    for existing_issue in all_issues:
        # Extract the user from the existing issue title
        user_from_existing = existing_issue.split('/')[0]
        # If they match, return True
        if user_from_title == user_from_existing:
            return True
    return False



def search_github_repos(query, sort='updated', order='desc', per_page=10, page=1):
    url = f"https://api.github.com/search/repositories"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    params = {
        'q': query,
        'sort': sort,
        'order': order,
        'per_page': per_page,
        'page': page
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from GitHub API. Status code: {response.status_code}")
        return None

def clone_repo(repo_url, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    repo_name = repo_url.split('/')[-1]
    repo_path = os.path.join(destination_folder, repo_name)
    
    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} into {repo_path}")
        subprocess.run(["git", "clone", repo_url, repo_path])
    else:
        print(f"Repository {repo_name} already exists in {destination_folder}.")

def count_vba_related_files(repo_path):
    vba_extensions = ['.bas', '.cls', '.frm', '.vb', '.d.vb']
    counts = {ext: 0 for ext in vba_extensions}
    
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            for ext in vba_extensions:
                if file.endswith(ext):
                    counts[ext] += 1

    # Print the counts
    for ext, count in counts.items():
        print(f"Number of '{ext}' files: {count}")
    
    return counts

def create_github_issue(repo_full_name, title, body, token):
    url = f"https://api.github.com/repos/{repo_full_name}/issues"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    data = {
        'title': title,
        'body': body
    }
    
    print(f"URL: {url}")
    print(f"Token: {'*' * len(token)}")  # Avoid printing the actual token
    print(f"Headers: {headers}")
    print(f"Data: {data}")

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"Issue created successfully: {response.json()['html_url']}")
    else:
        print(f"Failed to create issue. Status code: {response.status_code}")
        print(response.json())

def read_template_file(template_path, replacements):
    with open(template_path, 'r') as file:
        template_content = file.read()
    print("Replace merge fields")
    # Replace merge fields in the template
    for key, value in replacements.items():
        template_content = template_content.replace(f"%{{{key}}}%", value)
    
    return template_content

def fix_vbnet_issue(repo):
    # Clone the repo
    clone_repo(repo['html_url'], 'repos')
    repo_name = repo['html_url'].split('/')[-1]
    repo_path = os.path.join('repos', repo_name)
    counts = count_vba_related_files(repo_path)

    if counts[".vb"] > 0 and counts[".d.vb"] == 0 and counts[".bas"] == 0:
        # Prepare issue details
        repo_full_name = os.getenv('GITHUB_REPOSITORY')  # e.g., 'owner/repo'
        user = repo['owner']['login']
        reponame = repo['name']
        url = repo['html_url']
        
        # Get open issues
        token = os.getenv('GITHUB_TOKEN')  # GitHub token
        all_issues = get_all_issues(repo_full_name, token)

        issue_title = f"[{user}/{reponame}] detected as Visual Basic .NET"
        
        # Check if an issue already exists
        if already_issue_for_user(issue_title, all_issues):
            print(f"Issue already exists for user: {user}")
        else:
            # Read and process the template file
            template_path = './templates/' + 'Issue 1: Use of vb extension.md'
            replacements = {
                'user': user,
                'reponame': reponame,
                'url': url
            }

            issue_body = read_template_file(template_path, replacements)
            create_github_issue(repo_full_name, issue_title, issue_body, token)

def main():
    query = 'VBA'
    query = 'VBA in:name,description'
    per_page = 20  # Number of repos to fetch per page
    total_pages = 5  # Number of pages to check (you can adjust this value)

    for page in range(1, total_pages + 1):
        print(f"Fetching page {page}...")
        repos = search_github_repos(query, per_page=per_page, page=page)
    
        if repos:
            print(f"Found {repos['total_count']} repositories:")
            for repo in repos['items']:
                if repo['language'] != 'VBA':
                    print(f"Name: {repo['name']}")
                    print(f"Description: {repo['description']}")
                    print(f"Language: {repo['language']}")
                    print(f"URL: {repo['html_url']}")
                    print(f"Updated at: {repo['updated_at']}")
                    print('-' * 40)
                    
                    if repo['language'] == "Visual Basic .NET":
                        fix_vbnet_issue(repo)
        else:
            print("No repositories found.")

        time.sleep(2)

if __name__ == "__main__":
    main()