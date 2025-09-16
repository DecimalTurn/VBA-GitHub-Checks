import os

SUBFOLDERNAME = 'repos'

def subfolder_name():
    return SUBFOLDERNAME

def unique_folder(user_name, repo_name):
    return user_name + " --- " + repo_name

def repo_path(user_name, repo_name):
    return os.path.join(SUBFOLDERNAME, unique_folder(user_name, repo_name))

# REF: https://stackoverflow.com/a/7392391/5958842
def is_binary_file(path, blocksize=1024):
    """
    Check if a file is binary.
    
    Args:
        path (str): Path to the file.
        blocksize (int): Number of bytes to read for detection (default 1024).
    
    Returns:
        bool: True if binary, False if text.
    """

    # Define text characters (same logic as file(1))
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})

    if not os.path.isfile(path):
        raise FileNotFoundError(f"No such file: {path}")
    
    with open(path, 'rb') as f:
        chunk = f.read(blocksize)
    return bool(chunk.translate(None, textchars))

def get_user_from_title(issue_title):
    """Extract the username from the issue title."""
    if issue_title.startswith('[') and ']' in issue_title:
        return issue_title.split('/')[0].replace("[", "")
    return None   

def load_exclusion_list(exclusion_file_path):
    """Load SHA256 hashes from the exclusion file"""
    exclusion_hashes = set()
    try:
        with open(exclusion_file_path, 'r') as file:
            for line in file:
                hash_value = line.strip()
                if hash_value:  # Skip empty lines
                    exclusion_hashes.add(hash_value.lower())
        print(f"Loaded {len(exclusion_hashes)} exclusion hashes from {exclusion_file_path}")
    except FileNotFoundError:
        print(f"Warning: Exclusion file {exclusion_file_path} not found. No users will be excluded.")
    except Exception as e:
        print(f"Error reading exclusion file {exclusion_file_path}: {e}")
    return exclusion_hashes