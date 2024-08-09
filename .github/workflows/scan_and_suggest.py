import requests
import os
import subprocess
import time

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
    vba_extensions = ['.bas', '.cls', '.frm', '.vb']
    counts = {ext: 0 for ext in vba_extensions}
    
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            for ext in vba_extensions:
                if file.endswith(ext):
                    counts[ext] += 1

    # Print the counts
    for ext, count in counts.items():
        print(f"Number of '{ext}' files: {count}")
    else:
        print(f"No files with the specified extensions were found.")
    
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

def fix_vbnet_issue(repo):
        # Clone the repo
        clone_repo(repo['html_url'], 'repos')
        repo_name = repo['html_url'].split('/')[-1]
        repo_path = os.path.join('repos', repo_name)
        counts = count_vba_related_files(repo_path)

        if counts[".vb"] > 0 and counts[".bas"] == 0:
            # Prepare the issue information
            issue_info = f"Issue 1: {repo['owner']['login']} - {repo['html_url']}\n"

            # Append to the text file
            with open('./repos/actions.txt', 'a') as file:
                file.write(issue_info)
            
            print(f"Appended issue information to actions.txt for {repo['html_url']}")

            # Create an issue in the active repository
            repo_full_name = os.getenv('GITHUB_REPOSITORY')  # e.g., 'owner/repo'
            token = os.getenv('GITHUB_TOKEN')  # GitHub token
            issue_title = f"[{repo['name']}] detected as Visual Basic .NET"
            issue_body = "Hello @DecimalTurn," + chr(34) + chr(34) + "There seems to be a small issue with your repo."
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