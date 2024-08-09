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

def fix_vbnet_issue(repo):
        # Clone the repo
        clone_repo(repo['html_url'], 'repos')
        repo_name = repo['html_url'].split('/')[-1]
        repo_path = os.path.join('repos', repo_name)
        count_vba_related_files(repo_path)

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