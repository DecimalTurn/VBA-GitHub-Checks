import requests
import os
import subprocess
import time

all_issues = None
token = ""

def get_all_issues(token, repo_slug):
    global all_issues
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
            print(f"🔴 Failed to fetch issues. Status code: {response.status_code}")
            raise ValueError("Problem while fetching issues.")
    
    return all_issues

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


def already_issue_for_user(user):   
    # Iterate through all issues and check if the user matches
    for existing_issue in all_issues:
        # Extract the user from the existing issue title
        user_in_issue = existing_issue.split('/')[0].replace("[", "")
        if user == user_in_issue:
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

def count_vba_related_files(repo_path):
    vba_extensions = ['.bas', '.cls', '.frm', '.vba', '.vbs', '.vb', '.d.vb', '.vbproj']
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
    print(f"Token: {'*' * len(token)}")  # Avoid printing the actual token
    print(f"Headers: {headers}")
    print(f"Data: {data}")

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"🟢 Issue created successfully: {response.json()['html_url']}")
        return response.json()['number']
    else:
        print(f"🔴 Failed to create issue. Status code: {response.status_code}")
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
    global all_issues

    try:
        # Clone the repo
        try:
            repo_name = clone_repo(repo['html_url'], 'repos')
        except Exception as e:
            print(f"Error cloning the repo: {e}")
            return

        repo_path = os.path.join('repos', repo_name)

        try:
            counts = count_vba_related_files(repo_path)
        except Exception as e:
            print(f"🔴 Error counting VBA-related files: {e}")
            return

        if counts[".vb"] > 0 and counts[".vbproj"] == 0 and counts[".d.vb"] == 0 and counts[".bas"] == 0:       
            # Read and process the template file
            template_path = './templates/' + 'Issue A: Use of vb extension.md'
            replacements = {
                'user': repo['owner']['login'],
                'reponame': repo['name'],
                'url': repo['html_url']
            }

            slug = get_slug(repo)
            issue_title = f"[{slug}] detected as Visual Basic .NET"
            
            try:
                issue_body = read_template_file(template_path, replacements)
            except Exception as e:
                print(f"🔴 Error reading the template file: {e}")
                return

            try:
                issue_number = create_github_issue(token, os.getenv('GITHUB_REPOSITORY'), issue_title, issue_body, ["external", "Check A"])
            except Exception as e:
                print(f"🔴 Error creating GitHub issue: {e}")
                return

            if issue_number != 0:
                try:
                    new_issue = get_issue(token, os.getenv('GITHUB_REPOSITORY'), issue_number)
                    all_issues.append(new_issue)
                except Exception as e:
                    print(f"🔴 Error retrieving or appending the issue: {e}")
    except Exception as e:
        print(f"🔴 An unexpected error occurred: {e}")

def get_slug(repo):
    return repo['owner']['login'] + "/" + repo['name']

def main():

    global all_issues
    global token
    token = os.getenv('GITHUB_TOKEN')
    all_issues = get_all_issues(token, os.getenv('GITHUB_REPOSITORY'))

    query = 'VBA'
    query = 'VBA in:name,description'
    per_page = 50  # Number of repos to fetch per page
    total_pages = 5  # Number of pages to check (you can adjust this value)

    for page in range(1, total_pages + 1):
        print(f"Fetching page {page}...")
        repos = search_github_repos(query, per_page=per_page, page=page)
    
        if page == 1:
            print(f"Found {repos['total_count']} repositories")
        print('-' * 40)

        if repos:
            for repo in repos['items']:

                if repo['language'] == 'VBA':
                    continue

                print(f"Name: {repo['name']}")
                print(f"Description: {repo['description']}")
                print(f"Language: {repo['language']}")
                print(f"URL: {repo['html_url']}")
                print(f"Updated at: {repo['updated_at']}")
                
                if repo['language'] == "Visual Basic .NET":
                    print("")

                    user = repo['owner']['login']
                    if already_issue_for_user(user):
                        print(f"🟡 Issue already exists for user: {user}")
                        continue

                    fix_vbnet_issue(repo)
                        
                    print('-' * 40)
        else:
            print("No repositories found.")

        time.sleep(2)

if __name__ == "__main__":
    main()
