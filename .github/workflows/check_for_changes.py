# Summary:
# - Collect all open issues
# - Filter by check/issue


import requests
import os
import sys
import re

# Custom modules
import gh
import utils

all_open_issues = None

def follow_up_issues(token, repo_slug):
    global all_open_issues
    
    for issue in all_open_issues:

        # See what Check is associated with the issue
        # The Check is based on the label (Check A, Check B, etc)
        check = gh.get_check(issue)

        if check == None:
            continue

        # Extract the user and repo_name from the issue title
        user = utils.get_user_from_title(issue['title'])
        repo_name = issue['title'].split('/')[1].split(']')[0]
        repo_url = "https://github.com/" + repo_slug

        repo_info = get_repo_info(token, user, repo_name)
        if not repo_info:
            print(f"Failed to get repo info for issue: {issue['title']}")
            continue

        # Check if the repo was deleted or privated
        if repo_info['status_code'] == 404:
            print(f"Repo {user}/{repo_name} has been deleted, closing issue {issue['title']}")
            gh.close_issue(token, repo_slug, issue, "not_planned")
            gh.write_comment(token, repo_slug, issue, "Looks like the repository has been deleted or privated. Closing the issue.")
            gh.add_label_to_issue(token, os.getenv('GITHUB_REPOSITORY'), issue['number'], "repo deleted")
            continue
        
        if check == "A":
            follow_up_check_A(token, repo_info, user, repo_name, issue)
        elif check == "B":
             follow_up_check_B(token, repo_info, user, repo_name, issue)
        elif check == "C":
             follow_up_check_C(token, repo_info, user, repo_name, issue)
        elif check == "D":
             follow_up_check_D(token, repo_info, user, repo_name, issue)
        elif check == "E":
             follow_up_check_E(token, repo_info, user, repo_name, issue)
        elif check == "F":
             follow_up_check_F(token, repo_info, user, repo_name, issue)
        elif check == "G":
             follow_up_check_G(token, repo_info, user, repo_name, issue)


def follow_up_check_A(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check A
    if repo_info['language'] == 'VBA':
        
        subCheck = False
        gitattribute_override = check_gitattributes(token, user, repo_name, 'vb')
        if not gitattribute_override:
            subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck AA]")

        if not subCheck:
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['.vb'] == 0 or gitattribute_override:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += "However, there are still files with the .vb extension. Is this intentional? [SubCheck AA]" + "\n"               
                gh.add_label_to_issue(token, main_repo_slug, issue_number, "partially completed")
        
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['.vb'] > 0 and not gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck AB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔. " + "\n"
            comment += "There are still files with the .vb extension. Is this intentional? [SubCheck AB]" + "\n"  

    if comment:
        gh.write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_B(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check B
    if repo_info['language'] == 'VBA':
        
        subCheck = False
        gitattribute_override = check_gitattributes(token, user, repo_name, 'vbs')
        if not gitattribute_override:
            subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck BA]")
        
        if not subCheck:
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['.vbs'] == 0 or gitattribute_override:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += "However, there are still files with the .vbs extension. Is this intentional? [SubCheck BA]" + "\n"               
                gh.add_label_to_issue(token, main_repo_slug, issue_number, "partially completed")
        
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['.vbs'] > 0 and not gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck BB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔." + "\n"
            comment += "There are still files with the .vbs extension. Is this intentional? [SubCheck BB]" + "\n"  

    if comment:
        gh.write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_C(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check C
    if repo_info['language'] == 'VBA':

        subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck CA]")
        if not subCheck:
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['No ext'] == 0:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += "However, there are still files with no extension that contain VBA code. Is this intentional? [SubCheck CA]" + "\n"   
                gh.add_label_to_issue(token, main_repo_slug, issue_number, "partially completed")
           
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['No ext'] > 0 and not gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck CB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔." + "\n"
            comment += "There are still files with no extension that contain VBA code. Is this intentional? [SubCheck CB]" + "\n"  

    if comment:
        gh.write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_D(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""

    # Part specific to Check D
    if repo_info['language'] == 'VBA':

        subCheck = False
        gitattribute_override = check_gitattributes(token, user, repo_name, 'txt')
        if not gitattribute_override:
            subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck DA]")

        if not subCheck:
            comment = "Looks like you made some changes and the repository is now reported as VBA, great!" + "\n"

        if counts['.txt'] == 0 or gitattribute_override:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask." + "\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += "However, there are still files with the .txt extension that contain VBA code. Is this intentional? [SubCheck DA]" + "\n"   
                gh.add_label_to_issue(token, main_repo_slug, issue_number, "partially completed")
           
    else:

        # Check if there are now files with the .vba extension
        if counts['.vba'] > 0 and counts['.txt'] > 0 and not gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck DB]"):
            comment = "I see that you've made some changes to the files, but the repo is still reported as not VBA 🤔." + "\n"
            comment += "There are still files with the .txt extension that contain VBA code. Is this intentional? [SubCheck DB]" + "\n"  

    if comment:
        gh.write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_E(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')
    repo_path = utils.repo_path(repo_info['owner']['login'], repo_info['name'])

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    handle_misconfigured_gitattributes(token, main_repo_slug, issue, issue_number, repo_path, counts)

def handle_misconfigured_gitattributes(token, main_repo_slug, issue, issue_number, repo_path, counts):
    comment = ""
    subCheck = False
    wrong_eol_files = False
    number_of_wrong_eol_files = 0
    frm_files_with_lf_in_working_directory = []
    cls_files_with_lf_in_working_directory = []

    # Part specific to Check E
    try:
        misconfigured = gh.gitattributes_misconfigured(repo_path, counts)
    except Exception as e:
        error_message = (
            f"Error while checking .gitattributes configuration: {e}"
        )
        print(error_message)
        raise

    try:
        import git_ls_parser
        git_ls_output = gh.get_git_ls_files_output(repo_path)
        #debugging: 
        # print("git ls-files output: \n" + ("\n".join(git_ls_output) if isinstance(git_ls_output, list) else str(git_ls_output)))
        parsed_data = git_ls_parser.parse_git_ls_files_output(git_ls_output)

        #debugging:
        # print("Parsed git ls-files output:")
        # if not parsed_data:
        #     print("No parsed data found.")
        # for path, info in parsed_data.items():
        #     print(f"Path: {path}, Index: {info.index}, Working Directory: {info.working_directory}, Attribute: {info.attribute_text} {info.attribute_eol}")
        
        frm_files_with_lf_in_working_directory = [fname for fname, info in parsed_data.items() if fname.endswith(".frm") and info.working_directory == "lf"]
        if frm_files_with_lf_in_working_directory:
            print("\033[91m.frm files with LF in working directory:\033[0m")
            for file in frm_files_with_lf_in_working_directory:
                print(f" - {file}")
        else:
            print("No .frm files with LF in working directory found.")

        cls_files_with_lf_in_working_directory = [fname for fname, info in parsed_data.items() if fname.endswith(".cls") and info.working_directory == "lf"]
        if cls_files_with_lf_in_working_directory:
            print("\033[91m.cls files with LF in working directory:\033[0m")
            for file in cls_files_with_lf_in_working_directory:
                print(f" - {file}")
        else:
            print("No .cls files with LF in working directory found.")

        if frm_files_with_lf_in_working_directory or cls_files_with_lf_in_working_directory:
            wrong_eol_files = True
            number_of_wrong_eol_files = len(frm_files_with_lf_in_working_directory) + len(cls_files_with_lf_in_working_directory)
        else:
            print("No frm/cls files with LF line endings found in the working directory.")
    except Exception as e:
        error_message = (
            f"Error while parsing git ls-files output: {e}"
        )
        print(error_message)

    # SubCheck EA logic, inspired by other checks
    if not misconfigured:
        subCheck = gh.already_commented(token, main_repo_slug, issue_number, "[SubCheck EA]")
        if not subCheck:
            comment = "Looks like you made some changes and the .gitattributes file is now correctly configured.\n"
        if not wrong_eol_files:
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask.\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)
        else:
            if not subCheck:
                comment += (
                    f"However, there are still {number_of_wrong_eol_files} .frm/.cls files with LF line endings. "
                    "You need to renormalize these files. [SubCheck EA]\n"
                    "\n"
                    "If you still have the original files exported from the VBE in your working directory and you are able to use Git from the command line, you can simply run the following 2 commands:\n"
                    "```bash\n"
                    "git add . --renormalize\n"
                    "git commit -m \"Restore line endings\"\n"
                    "```\n"
                    "\n"
                    "<h3>Option B:</h3>\n"
                    "\n"
                    "You could also simply use [Enforce-CRLF](https://github.com/DecimalTurn/Enforce-CRLF) which will make sure to enforce CRLF in your repo for all the current files and will also prevent LF from being introduced by mistake in the future.\n"
                    "\n"
                    "For more information on how to configure your .gitattributes file and why you don't want to set the `text` property for VBA files, you can have a look at https://github.com/DecimalTurn/VBA-on-GitHub.\n"
                    "\n"
                    "And if you have any questions, feel free to ask it here and a real human will answer you.\n"
                )
                gh.add_label_to_issue(token, main_repo_slug, issue_number, "partially completed")

    if comment:
        gh.write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_F(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')
    repo_path = utils.repo_path(repo_info['owner']['login'], repo_info['name'])

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""
    problematic_files_check_f = [] 

    import git_ls_parser
    git_ls_output = gh.get_git_ls_files_output(repo_path)
    parsed_data = git_ls_parser.parse_git_ls_files_output(git_ls_output)
        
    # Part specific to Check F
    try:
        problematic_files_check_f = gh.get_problematic_files_check_f(parsed_data)
        if problematic_files_check_f:
            print("\033[91mProblematic files for Check F:\033[0m")
            for file in problematic_files_check_f:
                print(f" - {file}")
        else:
            print("No problematic files for Check F found.")
            comment = "Looks like you made some changes and files now have the correct line endings in the Git Index.\n"
            comment += "This issue is now resolved, so I'm closing it. If you have any questions, feel free to ask.\n"
            gh.close_issue(token, main_repo_slug, issue, "completed")
            handle_labels_after_completion(token, main_repo_slug, issue_number)

    except Exception as e:
        error_message = (
            f"Error while checking problematic files for Check F: {e}"
        )
        print(error_message)
    
    if comment:
        gh.write_comment(token, main_repo_slug, issue, comment)

def follow_up_check_G(token, repo_info, user, repo_name, issue):

    issue_number = issue['number']
    main_repo_slug = os.getenv('GITHUB_REPOSITORY')
    repo_path = utils.repo_path(repo_info['owner']['login'], repo_info['name'])

    counts = get_counts(token, user, repo_name)
    if not counts:
        print(f"Failed to get counts for issue: {issue['title']}")
        return

    comment = ""
        
    # Part specific to Check G
    try:
        if gh.gitattributes_exists(repo_path):
            # We can use Check E's logic since it's the logic for when the .gitattributes is present, but misconfigured.
            handle_misconfigured_gitattributes(token, main_repo_slug, issue, issue_number, repo_path, counts)
        else:
            print("No .gitattributes file found, nothing to do for Check G.")

    except Exception as e:
        error_message = (
            f"Error while checking problematic files for Check G: {e}"
        )
        print(error_message)
    
    if comment:
        gh.write_comment(token, main_repo_slug, issue, comment)


# This function looks inside the gitattributes file of the repository to check if the they added a rule to 
# consider the extension as VBA via the linguist-language override
def check_gitattributes(token, user, repo_name, ext):
    # The repo should already be cloned at this stage, so we look directly in the gitattributes file
    repo_path = utils.repo_path(user, repo_name)
    gitattributes_path = os.path.join(repo_path, '.gitattributes')
    if not os.path.exists(gitattributes_path):
        return False
    
    # Check if there is a line with the pattern *.ext linguist-language=VBA
    pattern = re.compile(rf"\*\.{ext}\s+.*\blinguist-language=VBA")
    with open(gitattributes_path, 'r') as file:
        for line in file:
            if pattern.search(line):
                return True

def handle_labels_after_completion(token, main_repo_slug, issue_number):
    gh.add_label_to_issue(token, main_repo_slug, issue_number, "completed")
    gh.remove_label_from_issue(token, main_repo_slug, issue_number, "stale", ignore_not_found=True) 
    gh.remove_label_from_issue(token, main_repo_slug, issue_number, "partially completed", ignore_not_found=True) 

def get_repo_info(token, user, repo_name):
    url = f"https://api.github.com/repos/{user}/{repo_name}"
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repo_info = response.json()
        # Add a status code to the repo_info
        repo_info['status_code'] = response.status_code
        return repo_info
    elif response.status_code == 404:
        # Return a minimal repo_info indicating not found
        return {'status_code': 404, 'full_name': f"{user}/{repo_name}"}
    else:
        print(f"Failed to fetch repo info for {user}/{repo_name}. Status code: {response.status_code}")
        return None

def get_counts(token, user, repo_name):
    #This function is not implemented yet, return an error when called
    #print("Function has_vb_files not implemented yet.")
    #sys.exit(1)   
   
    # Clone the repo
    html_url = f"https://github.com/{user}/{repo_name}"
    try:
        gh.clone_repo(html_url)
    except Exception as e:
        print(f"Error cloning the repo: {e}")
        return

    # Count the number of files in the repo

    repo_path = utils.repo_path(user, repo_name)
    if not os.path.exists(repo_path):
        print(f"🔴 Error: Repository path {repo_path} does not exist.")
        return
    
    try:
        return gh.count_vba_related_files(repo_path)
    except Exception as e:
        print(f"🔴 Error counting VBA-related files: {e}")
        return


def main():

    global all_open_issues
    token = os.getenv('GITHUB_TOKEN')
    all_open_issues = gh.get_all_issues(token, os.getenv('GITHUB_REPOSITORY'), 'open')

    follow_up_issues(token, os.getenv('GITHUB_REPOSITORY'))


if __name__ == "__main__":
    main()


