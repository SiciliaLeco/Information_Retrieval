import os
import shutil

"""
File/directory paths for intermediate dictionaries
and postings lists.
"""
TEMP_DIR = "temp"
TO_MERGE_DIR = "to_merge"
MERGED_DIR = "merged"
DICT_FILE = "dict.txt"
LISTS_FILE = "lists.txt"

def setup_dirs(out_dict, out_postings):
    """
    Removes directory and files that will be overwritten during
    the indexing process, and creates the necessary temporary 
    directories.

    Note that removal of directory and files is done to ensure
    that we start from a clean slate.
    """
    if os.path.isdir(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

    os.mkdir(TEMP_DIR)

    if not os.path.isdir(os.path.join(TEMP_DIR, TO_MERGE_DIR)):
        os.mkdir(os.path.join(TEMP_DIR, TO_MERGE_DIR))

    if not os.path.isdir(os.path.join(TEMP_DIR, MERGED_DIR)):
        os.mkdir(os.path.join(TEMP_DIR, MERGED_DIR))
    
    if os.path.isfile(out_dict):
        os.remove(out_dict)
    
    if os.path.isfile(out_postings):
        os.remove(out_postings)

def remove_dirs():
    """
    Removes the temporary directory.
    """
    shutil.rmtree(TEMP_DIR)

def move_from_merged():
    """
    Moves all (sub-)directories and files from MERGED_DIR to
    TO_MERGE_DIR.
    """
    main_src_path = os.path.join(TEMP_DIR, MERGED_DIR)
    main_dest_path = os.path.join(TEMP_DIR, TO_MERGE_DIR)
    merged_dirs = os.scandir(main_src_path)

    for merged_dir in merged_dirs:
        shutil.move(str(merged_dir.path), os.path.join(main_dest_path))
