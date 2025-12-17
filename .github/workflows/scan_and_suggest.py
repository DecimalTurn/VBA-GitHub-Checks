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

# Number of stars threshold to start analyzing VBA repos for issues with .gitattributes and EOL
start_threshold_vba_repo = 1

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
    with open(template_path, 'r', encoding='utf-8') as file:
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
            if create_issue_wrapper(token, repo, 'is detected as Visual Basic .NET', 'Check A: Use of vb extension.md', 'Check A'):
                print("✅ Issue created for Check A - exiting early")
                return
        
        if repo['language'] == "VBScript" and counts[".vbs"] > 0 and counts[".vba"] == 0 and counts[".bas"] == 0:
            # VBScript extension used for VBA code
            if create_issue_wrapper(token, repo, 'is detected as VBScript', 'Check B: Use of vbs extension.md', 'Check B'):
                print("✅ Issue created for Check B - exiting early")
                return

        if repo['language'] is None and counts['No ext'] > 0:
            # No extension used for VBA code
            if create_issue_wrapper(token, repo, 'is not detected as VBA', 'Check C: Use of no extension.md', 'Check C'):
                print("✅ Issue created for Check C - exiting early")
                return

        if repo['language'] is None and counts[".txt"] > 0:
            # txt extension used for VBA code
            if create_issue_wrapper(token, repo, 'is not detected as VBA', 'Check D: Use of txt extension.md', 'Check D'):
                print("✅ Issue created for Check D - exiting early")
                return

        if repo['language'] is None and any(counts[ext] > 0 for ext in gh.office_vba_extensions) and all(counts[ext] == 0 for ext in gh.code_extensions):
            # create_issue_wrapper(token, repo, 'does not have any source code', 'Check _: Missing source code.md', 'Check _')

            # Since the issue template is not ready, we only want to preserve the list of repos that are in this situation by appending to a list of repo contained in the body of an issue.
            # This means that we have to call the github API and edit the following issue https://github.com/DecimalTurn/VBA-GitHub-Checks/issues/871
            # We simply want to add a the URL of the repo as a new bullet point to the list 
            new_repo = f" 1. {repo['html_url']}\n"
            gh.append_to_issue_body_if_missing(token, main_repo_slug, 871, new_repo)
            print(f"🔴 Repo {repo['html_url']} contain VBA-Enabled Office documents, but not any source code. Logged in issue #871.")
            return
        
        print("🟢 No issues detected based on file extensions.")

    except Exception as e:
        print(f"🔴 An unexpected error occurred: {e}")

def create_issue_wrapper(token, repo, issue_title_suffix, template_name, label_name, additional_replacements=None):
        # Read and process the template file
        template_path = './templates/' + template_name
        replacements = {
            'user': repo['owner']['login'],
            'reponame': repo['name'],
            'url': repo['html_url']
        }
        
        # Add any additional replacements if provided
        if additional_replacements:
            replacements.update(additional_replacements)

        slug = get_slug(repo)
        issue_title = f"[{slug}] {issue_title_suffix}"
        
        # Check if there's a recently closed issue with the same title
        try:
            if gh.check_recently_closed_issue(token, os.getenv('GITHUB_REPOSITORY'), issue_title, months=3):
                print(f"🔴 An identical issue was closed recently. Skipping issue creation for: {issue_title}")
                return False
        except Exception as e:
            print(f"🔴 Error checking for recently closed issues: {e}")
            print(f"🔴 Skipping issue creation as a safety measure for: {issue_title}")
            return False
        
        try:
            issue_body = read_template_file(template_path, replacements)
        except Exception as e:
            print(f"🔴 Error reading the template file: {e}")
            return False

        try:
            issue_number = gh.create_github_issue(token, os.getenv('GITHUB_REPOSITORY'), issue_title, issue_body, ["external", label_name])
        except Exception as e:
            print(f"🔴 Error creating GitHub issue: {e}")
            return False

        if issue_number != 0:
            try:
                new_issue = gh.get_issue(token, os.getenv('GITHUB_REPOSITORY'), issue_number)
                all_issues_title.append(new_issue['title'])
                return True
            except Exception as e:
                print(f"🔴 Error retrieving or appending the issue: {e}")
                return False
        
        return False

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

def has_xvba_modules_folder(repo_path):
    """
    Check if the repository has an xvba_modules folder in the root directory.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        True if xvba_modules folder exists in root directory, False otherwise
    """
    xvba_modules_path = os.path.join(repo_path, 'xvba_modules')
    return os.path.isdir(xvba_modules_path)

def format_filename_for_markdown(filename):
    """
    Format a filename for use in Markdown by escaping special characters.
    
    Args:
        filename: The filename to format
        
    Returns:
        The filename with special characters escaped for Markdown
    """
    # Escape backticks and other special Markdown characters
    return filename.replace('`', '\\`').replace('_', '\\_')

def main():

    global all_issues_title, all_open_issues_title
    token = os.getenv('GITHUB_TOKEN')
    all_issues_title = gh.get_all_issues_title(token, os.getenv('GITHUB_REPOSITORY'))
    all_open_issues_title = get_open_issues_title(token, os.getenv('GITHUB_REPOSITORY'))

    # Load exclusion list
    exclusion_file_path = './.github/workflows/exclusion.txt'
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

        if repos:
            for repo in repos['items']:
                print('=' * 60)
                analyze_repo(token, repo, exclusion_hashes)
                
        else:
            print("No repositories found.")

        time.sleep(2)

def analyze_repo(token, repo, exclusion_hashes):
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    print(f"Name: {repo['name']}")
    print(f"Author: {repo['owner']['login']}")
    print(f"Description: {repo['description']}")
    print(f"Language: {repo['language']}")
    print(f"URL:↓")
    print(f"{repo['html_url']}")
    print(f"Updated at: {repo['updated_at']}")
    print(f"Stars: {repo['stargazers_count']}")
    
    # Check if user is excluded
    user = repo['owner']['login']
    if is_user_excluded(user, exclusion_hashes):
        print(f"🚫 User {user} is excluded (SHA256 hash matches exclusion list)")
        return
    
    # Spam prevention - check for open issues only
    if already_open_issue_for_user(user):
        print(f"🟡 Open issue already exists for user: {user}")
        print('-' * 40)
        return

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

    # Check if the repo is empty
    if gh.is_repo_empty(repo_path):
        print(f"🚫 Repository {repo['html_url']} is empty. Skipping further analysis.")
        return

    try:
        file_counts = gh.count_vba_related_files(repo_path)
    except Exception as e:
        print(f"::warning file={__file__}::Error counting VBA-related files in {repo_path}: {e}")
        return

    # Check for xvba_modules folder and log to issue #1108 if found
    if has_xvba_modules_folder(repo_path):
        # Log to issue #1108 for repos with xvba_modules folder
        new_repo = f" 1. {repo['html_url']}\n"
        gh.append_to_issue_body_if_missing(token, main_repo_slug, 1108, new_repo)
        print(f"☑️ Repo {repo['html_url']} contains an xvba_modules folder. Logged in issue #1108.")
        return

    if repo['language'] == "VBA" and repo['stargazers_count'] >= start_threshold_vba_repo:
        print('-' * 20)
        print(f"Performing checks on VBA repo: {repo_path}")
        
        print('-' * 20)
        print(f"Checking .gitattributes checks")
        report_gitattributes_issues(repo_path, file_counts, token, repo)
        
        print('-' * 20)
        print(f"Checking EOL in VBA files")
        report_eol_issues(repo_path, file_counts, token, repo)

    if repo['language'] == "Visual Basic .NET" or repo['language'] == "VBScript" or repo['language'] is None:
        print('-' * 20)
        print(f"Performing file extension checks")
        report_file_extensions_issue(token, repo, file_counts)

def report_missing_gitattributes_issue(repo_path, counts, token, repo):
    """
    Check if a .gitattributes file is needed and create Check G issue if appropriate.
    
    Args:
        repo_path: Path to the repository
        counts: File counts from gh.count_vba_related_files
        token: GitHub token
        repo: Repository object
    """
    if gh.gitattributes_needed(repo_path, counts):
        print("Creating issue...")
        print("🔴 This repo has a problem corresponding to check G")
        
        # Get the problematic files for Check G
        try:
            import git_ls_parser
            git_ls_output = gh.get_git_ls_files_output(repo_path)
            parsed_data = git_ls_parser.parse_git_ls_files_output(git_ls_output)
            problematic_files_check_g = gh.get_problematic_files_check_g(parsed_data)
            
            if problematic_files_check_g:
                print(f"🔴 Found .frm/.cls files with LF line endings and no .gitattributes file:")
                for file in problematic_files_check_g:
                    print(f" - {file}")
                
                # Format the list of problematic files for the template
                ls_files_report = "\n".join([f"- `{format_filename_for_markdown(file)}`" for file in problematic_files_check_g])
                additional_replacements = {
                    'ls_files_report': ls_files_report
                }

                if create_issue_wrapper(token, repo, 'is missing a .gitattributes file', 'Check G.md', 'Check G', additional_replacements):
                    print("✅ Issue created for Check G")

            else:
                print("🔴 No problematic files found for Check G")
        except Exception as e:
            print(f"🔴 Error while checking problematic files for Check G: {e}")
    else:
        print("🟢 .gitattributes file is not needed.")

def report_gitattributes_issues(repo_path, counts, token, repo):

    if not gh.gitattributes_exists(repo_path):
        print("🟡 .gitattributes file is missing.")
        report_missing_gitattributes_issue(repo_path, counts, token, repo)
        return

    if gh.gitattributes_misconfigured(repo_path, counts):
        print("🔴 .gitattributes is misconfigured and won't handle line endings conversion properly.")
        print("Creating issue...")
        if create_issue_wrapper(token, repo, 'has a .gitattributes misconfiguration', 'Check E.md', 'Check E'):
            print("✅ Issue created for Check E")
    else:
        print("🟢 .gitattributes is configured correctly.")

def report_eol_issues(repo_path, counts, token, repo):
    # Going beyond the .gitattributes checks, we can parse the output of `git ls-files` 
    # to check for line endings in actual files as they are in the working directory.
    # Note that the EOL in the working directory will depend on the core.autocrlf setting 
    # of the git client used to clone the repository. In the case of a Unix system, like the 
    # GitHub Actions runner on ubuntu, the files will be checked out with core.autocrlf=false and this will immitate the 
    # content of the .zip file downloaded from GitHub
    try:
        import git_ls_parser
        git_ls_output = gh.get_git_ls_files_output(repo_path)
        parsed_data = git_ls_parser.parse_git_ls_files_output(git_ls_output)
        print("Parsed git ls-files output:")
        for path, info in parsed_data.items():
            attr_text = ", ".join(info.attribute_text) if isinstance(info.attribute_text, list) else str(info.attribute_text)
            attr_eol = ", ".join(info.attribute_eol) if isinstance(info.attribute_eol, list) else str(info.attribute_eol)
            print(f"Path: {path}, Index: {info.index}, Working Directory: {info.working_directory}, Attribute: {attr_text} {attr_eol}")
        

        # Problematic files for Check F (only)
        # Check for .frm and .cls files with LF and -text
        problematic_files_check_f = gh.get_problematic_files_check_f(parsed_data)
        
        if problematic_files_check_f:
            print(f"🔴 Found .frm/.cls files with LF in index without proper text/eol attributes:")
            for file in problematic_files_check_f:
                print(f" - {file}")
            
            # Format the list of problematic files for the template
            ls_files_report = "\n".join([f"- `{format_filename_for_markdown(file)}`" for file in problematic_files_check_f])
            additional_replacements = {
                'ls_files_report': ls_files_report
            }
            
            if create_issue_wrapper(token, repo, 'has .frm/.cls files with wrong line endings', 'Check F.md', 'Check F', additional_replacements):
                print("✅ Issue created for Check F")

            # TODO: Create another similar check that will trigger if there are frm/cls files with LF and text unspecified (rare case)
            # If text unspecified + eol=/=clrf means that no conversion will happen when downloading the .zip file from Github and on cloning the repos if core.autocrlf is false/unspecified
            # That case is very similar to Check E since it can be solved by adding a proper lines to the .gitattributes file (+renormalizing the files for option 1)
            # (Note that if text set + eol=/=crlf means that no conversion will happen when downloading the .zip file from Github [Already taken care of in Check E])
            
    except Exception as e:
        print(f"🔴 Error while parsing git ls-files output: {e}")
    
    return  # No return value needed

if __name__ == "__main__":
    main()


