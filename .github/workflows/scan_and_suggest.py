import requests
import os
import subprocess
import time
# Custom modules
import gh

all_issues_title = None

def already_issue_for_user(user):   
    # Iterate through all issues and check if the user matches
    for existing_issue in all_issues_title:
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

def read_template_file(template_path, replacements):
    with open(template_path, 'r') as file:
        template_content = file.read()
    print("Replace merge fields")
    # Replace merge fields in the template
    for key, value in replacements.items():
        template_content = template_content.replace(f"%{{{key}}}%", value)
    
    return template_content

def report_file_extensions_issue(token, repo):
    global all_issues

    try:
        # Clone the repo
        try:
            repo_name = gh.clone_repo(repo['html_url'], 'repos')
        except Exception as e:
            print(f"Error cloning the repo: {e}")
            return

        repo_path = os.path.join('repos', repo_name)

        try:
            counts = gh.count_vba_related_files(repo_path)
        except Exception as e:
            print(f"🔴 Error counting VBA-related files: {e}")
            return

        if repo['language'] == "Visual Basic .NET" and counts[".vb"] > 0 and counts[".vbproj"] == 0 and counts[".d.vb"] == 0 and counts[".bas"] == 0:       
            # VB.NET extension used for VBA code
            create_issue_wrapper(token, repo, 'is detected as Visual Basic .NET', 'Check A: Use of vb extension.md', 'Check A')
        
        if repo['language'] == "VBScript" and counts[".vbs"] > 0 and counts[".vba"] == 0 and counts[".bas"] == 0:
            # VBScript extension used for VBA code
            create_issue_wrapper(token, repo, 'is detected as VBScript', 'Check B: Use of vbs extension.md', 'Check B')

        if repo['language'] is None and counts['No ext'] > 0:
            # No extension used for VBA code
            create_issue_wrapper(token, repo, 'is not detected as VBA', 'Check C: Use of no extension.md', 'Check C')

        if repo['language'] is None and counts[".txt"] > 0:
            # txt extension used for VBA code
            create_issue_wrapper(token, repo, 'is not detected as VBA', 'Check D: Use of txt extension.md', 'Check D')

    except Exception as e:
        print(f"🔴 An unexpected error occurred: {e}")

def create_issue_wrapper(token, repo, issue_title_suffix, template_name, label_name):
        # Read and process the template file
        template_path = './templates/' + template_name
        replacements = {
            'user': repo['owner']['login'],
            'reponame': repo['name'],
            'url': repo['html_url']
        }

        slug = get_slug(repo)
        issue_title = f"[{slug}] {issue_title_suffix}"
        
        try:
            issue_body = read_template_file(template_path, replacements)
        except Exception as e:
            print(f"🔴 Error reading the template file: {e}")
            return

        try:
            issue_number = create_github_issue(token, os.getenv('GITHUB_REPOSITORY'), issue_title, issue_body, ["external", label_name])
        except Exception as e:
            print(f"🔴 Error creating GitHub issue: {e}")
            return

        if issue_number != 0:
            try:
                new_issue = gh.get_issue(token, os.getenv('GITHUB_REPOSITORY'), issue_number)
                all_issues_title.append(new_issue['title'])
            except Exception as e:
                print(f"🔴 Error retrieving or appending the issue: {e}")

def get_slug(repo):
    return repo['owner']['login'] + "/" + repo['name']

def main():

    global all_issues_title
    token = os.getenv('GITHUB_TOKEN')
    all_issues_title = gh.get_all_issues_title(token, os.getenv('GITHUB_REPOSITORY'))

    query = 'VBA NOT VBScript'
    # query = 'VBA in:name,description'
    per_page = 100  # Number of repos to fetch per page
    total_pages = 1  # Number of pages to check

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
                
                if repo['language'] == "VBA" or repo['language'] == "Visual Basic 6.0":
                    print("")

                    user = repo['owner']['login']
                    if already_issue_for_user(user):
                        print(f"🟡 Issue already exists for user: {user}")
                        print('-' * 40)
                        continue
                        
                    print(f"Performing checks")

                    if gh.gitattributes_exists():
                        if gh.gitattributes_misconfigured():
                            print("🔴 .gitattributes is misconfigured and won't handle line endings conversion properly.")
                        else:
                            print("🟢 .gitattributes is configured correctly.")

                if repo['language'] == "Visual Basic .NET" or repo['language'] == "VBScript" or repo['language'] is None:
                    print("")

                    user = repo['owner']['login']
                    if already_issue_for_user(user):
                        print(f"🟡 Issue already exists for user: {user}")
                        print('-' * 40)
                        continue
                        
                    print(f"Performing checks")
                    report_file_extensions_issue(token, repo)
                        
                print('-' * 40)
        else:
            print("No repositories found.")

        time.sleep(2)

if __name__ == "__main__":
    main()
