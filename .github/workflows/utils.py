import os

SUBFOLDERNAME = 'repos'

def subfolder_name():
    return SUBFOLDERNAME

def unique_folder(user_name, repo_name):
    return user_name + " --- " + repo_name

def repo_path(user_name, repo_name):
    return os.path.join(SUBFOLDERNAME, unique_folder(user_name, repo_name))

