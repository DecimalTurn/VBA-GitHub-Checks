import requests
import os
import subprocess
import time
import hashlib
# Custom modules
import gh
import utils

all_issues_title = None
all_open_issues_title = None

def already_issue_for_user(user):   
    # Iterate through all issues and check if the user matches
    for existing_issue in all_issues_title:
        # Extract the user from the existing issue title
        user_in_issue = utils.get_user_from_title(existing_issue)
        if user == user_in_issue:
            return True
    return False

def already_open_issue_for_user(user):   
    # Iterate through all open issues and check if the user matches
    for existing_issue in all_open_issues_title:
        # Extract the user from the existing issue title
        user_in_issue = utils.get_user_from_title(existing_issue)
        if user == user_in_issue:
            return True
    return False

 

def search_github_repos(query, sort='updated', order='desc', per_page=60, page=1):
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

def read_template_file(template_path, replacements):
    with open(template_path, 'r') as file:
        template_content = file.read()
    print("Replace merge fields")
    # Replace merge fields in the template
    for key, value in replacements.items():
        template_content = template_content.replace(f"%{{{key}}}%", value)
    
    return template_content

def report_file_extensions_issue(token, repo, counts):
    global all_issues

    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    try:
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

        if repo['language'] is None and any(counts[ext] > 0 for ext in gh.office_vba_extensions) and all(counts[ext] == 0 for ext in gh.code_extensions):
            # create_issue_wrapper(token, repo, 'does not have any source code', 'Check F: Missing source code.md', 'Check F')

            # Since the issue template is not ready, we only want to preserve the list of repos that are in this situation by appending to a list of repo contained in the body of an issue.
            # This means that we have to call the github API and edit the following issue https://github.com/DecimalTurn/VBA-GitHub-Checks/issues/871
            # We simply want to add a the URL of the repo as a new bullet point to the list 
            new_repo = f" 1. {repo['html_url']}\n"
            gh.append_to_issue_body_if_missing(token, main_repo_slug, 871, new_repo)

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
            issue_number = gh.create_github_issue(token, os.getenv('GITHUB_REPOSITORY'), issue_title, issue_body, ["external", label_name])
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

def get_open_issues_title(token, repo_slug):
    """Get titles of only open issues"""
    url = f"https://api.github.com/repos/{repo_slug}/issues"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    params = {
        'per_page': 100,  # Maximum number of issues per page
        'state': 'open',  # Fetch only open issues
        'page': 1         # Start with the first page
    }
    
    all_open_issues_title = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            issues = response.json()
            all_open_issues_title.extend([issue['title'] for issue in issues])
            
            if len(issues) < 100:
                # If fewer than 100 issues were returned, this is the last page
                break
            else:
                # Move to the next page
                params['page'] += 1
        else:
            print(f"🔴 Failed to fetch open issues. Status code: {response.status_code}")
            raise ValueError("Problem while fetching open issues.")
    
    return all_open_issues_title

def get_username_sha256(username):
    """Compute SHA256 hash of a username"""
    return hashlib.sha256(username.encode('utf-8')).hexdigest().lower()

def is_user_excluded(username, exclusion_hashes):
    """Check if a username's SHA256 hash is in the exclusion list"""
    user_hash = get_username_sha256(username)
    return user_hash in exclusion_hashes

def main():

    global all_issues_title, all_open_issues_title
    token = os.getenv('GITHUB_TOKEN')
    all_issues_title = gh.get_all_issues_title(token, os.getenv('GITHUB_REPOSITORY'))
    all_open_issues_title = get_open_issues_title(token, os.getenv('GITHUB_REPOSITORY'))

    # Load exclusion list
    exclusion_file_path = './exclusion.txt'
    exclusion_hashes = utils.load_exclusion_list(exclusion_file_path)

    query = 'VBA NOT VBScript'
    # query = 'VBA in:name,description'
    per_page = 50  # Number of repos to fetch per page (max: 100)
    total_pages = 1  # Number of pages to check

    for page in range(1, total_pages + 1):
        print(f"Fetching page {page}...")
        repos = search_github_repos(query, per_page=per_page, page=page)
    
        if page == 1:
            print(f"Found {repos['total_count']} repositories")
        print('-' * 40)

        if repos:
            for repo in repos['items']:

                print(f"Name: {repo['name']}")
                print(f"Description: {repo['description']}")
                print(f"Language: {repo['language']}")
                print(f"URL: {repo['html_url']}")
                print(f"Updated at: {repo['updated_at']}")
                
                # Check if user is excluded
                user = repo['owner']['login']
                if is_user_excluded(user, exclusion_hashes):
                    print(f"🚫 User {user} is excluded (SHA256 hash matches exclusion list)")
                    print('-' * 40)
                    continue
                
                # Spam prevention - check for open issues only
                if already_open_issue_for_user(user):
                    print(f"🟡 Open issue already exists for user: {user}")
                    print('-' * 40)
                    continue

                # Clone the repo
                try:
                    gh.clone_repo(repo['html_url'])
                except Exception as e:
                    print(f"Error cloning the repo: {e}")
                    return
                
                #TODO : 
                # Store the commit hash of the last commit, the scan_date and the outcome of the scan to be saved in an issue
                # Save the information at the end in the issue_for_scanned_repo (see gh.py)

                repo_path = utils.repo_path(repo['owner']['login'], repo['name'])
                try:
                    counts = gh.count_vba_related_files(repo_path)
                except Exception as e:
                    print(f"::warning file={__file__}::Error counting VBA-related files in {repo_path}: {e}")
                    continue

                if repo['language'] == "VBA" or repo['language'] == "Visual Basic 6.0":
                    print("")

                    print(f"Performing .gitattributes checks")
                    
                    print(f"Checking .gitattributes in {repo_path}")

                    if gh.gitattributes_exists(repo_path):
                        if gh.gitattributes_misconfigured(repo_path, counts):
                            print("🔴 .gitattributes is misconfigured and won't handle line endings conversion properly.")
                            print("Creating issue...")
                            create_issue_wrapper(token, repo, 'has a .gitattributes misconfiguration', 'Check E: .gitattributes is misconfigured.md', 'Check E')



                        else:
                            print("🟢 .gitattributes is configured correctly.")

                        # Going beyond the .gitattributes checks, we can parse the output of `git ls-files` 
                        # to check for line endings in actual files as they are in the working directory.
                        # Note that the EOL in the working directory will depend on the core.autocrlf setting 
                        # of the git client used to clone the repository. In the case of a unix system, like the 
                        # GitHub Actions runner, the files will be checked out with core.autocrlf=false and this will immitate the 
                        # content of the .zip file downloaded from GitHub.
                        try:
                            import git_ls_parser
                            git_ls_output = gh.get_git_ls_files_output(repo_path)
                            parsed_data = git_ls_parser.parse_git_ls_files_output(git_ls_output)
                            print("Parsed git ls-files output:")
                            for path, info in parsed_data.items():
                                attr_text = ", ".join(info.attribute_text) if isinstance(info.attribute_text, list) else str(info.attribute_text)
                                attr_eol = ", ".join(info.attribute_eol) if isinstance(info.attribute_eol, list) else str(info.attribute_eol)
                                print(f"Path: {path}, Index: {info.index}, Working Directory: {info.working_directory}, Attribute: {attr_text} {attr_eol}")
                            
                            frm_files_with_lf_in_working_directory = [fname for fname, info in parsed_data.items() if fname.endswith(".frm") and info.working_directory == "lf"]
                            if frm_files_with_lf_in_working_directory:
                                print(".frm files with LF in working directory:")
                                for file in frm_files_with_lf_in_working_directory:
                                    print(f" - {file}")
                            else:
                                print("No .frm files with LF in working directory found.")

                            cls_files_with_lf_in_working_directory = [fname for fname, info in parsed_data.items() if fname.endswith(".cls") and info.working_directory == "lf"]
                            if cls_files_with_lf_in_working_directory:
                                print(".cls files with LF in working directory:")
                                for file in cls_files_with_lf_in_working_directory:
                                    print(f" - {file}")
                            else:
                                print("No .cls files with LF in working directory found.")
                                
                        except Exception as e:
                            print(f"🔴 Error while parsing git ls-files output: {e}")

                    else:
                        print("🟡 .gitattributes file is missing.")

                if repo['language'] == "Visual Basic .NET" or repo['language'] == "VBScript" or repo['language'] is None:
                    print("")
                        
                    print(f"Performing file extension checks")
                    report_file_extensions_issue(token, repo, counts)
                        
                print('-' * 40)
        else:
            print("No repositories found.")

        time.sleep(2)

if __name__ == "__main__":
    main()

