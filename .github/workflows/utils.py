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

