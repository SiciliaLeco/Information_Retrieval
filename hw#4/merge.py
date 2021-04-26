import os
import shutil

from temp_dir_util import TEMP_DIR, TO_MERGE_DIR, MERGED_DIR, move_from_merged
from index_util import get_dictionary_and_postings_file, get_postings_list, \
    update_dictionary_and_write_list, write_dictionary

def merge_blocks():
    """
    Merges (2-way merge) the postings and dictionaries obtained from the 
    blocks recursively, until no further merging has to be done.
    """
    while not is_merge_completed():
        dirs = os.scandir(os.path.join(TEMP_DIR, TO_MERGE_DIR))
        to_merge_dirs = []

        for directory in dirs:
            to_merge_dirs.append(directory)

            if len(to_merge_dirs) < 2:
                continue

            merge_dirs(to_merge_dirs)
            [shutil.rmtree(str(to_merge_dir.path)) for to_merge_dir \
                in to_merge_dirs]
            to_merge_dirs = []
        
        move_from_merged()

def is_merge_completed():
    """
    Checks whether the merge process is completed. It returns
    `True` if there is only one dictionary and postings lists;
    otherwise, it returns `False`.
    """
    num_files = 0
    files = os.scandir(os.path.join(TEMP_DIR, TO_MERGE_DIR))

    for _ in files:
        num_files += 1
        
        if num_files > 1:
            return False
    
    return True

def merge_dirs(to_merge_dirs):
    """ 
    Merges the two directories which are specified in `to_merge_dirs`.
    At any one time, at most two postings lists (of the same term) are
    merged.
    """
    assert len(to_merge_dirs) == 2, 'Merging invalid number of directories'

    (dictionary_0, postings_file_0) = get_dictionary_and_postings_file(to_merge_dirs[0])
    (dictionary_1, postings_file_1) = get_dictionary_and_postings_file(to_merge_dirs[1])

    merged_dir_name = str(min(int(to_merge_dirs[0].name), \
        int(to_merge_dirs[1].name)))
    merged_dir_path = os.path.join(TEMP_DIR, MERGED_DIR, merged_dir_name)

    if not os.path.isdir(merged_dir_path):
        os.mkdir(merged_dir_path)

    dictionary_index_0 = 0
    dictionary_index_1 = 0

    term = None
    prev_end_pointer = -1
    merged_dictionary = []

    while dictionary_index_0 < len(dictionary_0) and dictionary_index_1 < len(dictionary_1):
        term_0 = dictionary_0[dictionary_index_0].term
        term_1 = dictionary_1[dictionary_index_1].term

        updated_postings_list = []

        if term_0 == term_1:
            term = term_0

            list_0 = get_postings_list(dictionary_0, dictionary_index_0, \
                postings_file_0)
            list_1 = get_postings_list(dictionary_1, dictionary_index_1, \
                postings_file_1)
            updated_postings_list = merge_postings_lists(list_0, list_1)

            dictionary_index_0 += 1
            dictionary_index_1 += 1
        elif term_0 < term_1:
            term = term_0
            updated_postings_list = get_postings_list(dictionary_0, \
                dictionary_index_0, postings_file_0)
            dictionary_index_0 += 1
        else:
            term = term_1
            updated_postings_list = get_postings_list(dictionary_1, \
                dictionary_index_1, postings_file_1)
            dictionary_index_1 += 1
        
        entry = update_dictionary_and_write_list(updated_postings_list, \
            merged_dir_path, term, prev_end_pointer, merged_dictionary)
        prev_end_pointer = entry.end_pointer

    while dictionary_index_0 < len(dictionary_0):
        term = dictionary_0[dictionary_index_0].term
        postings_list = get_postings_list(dictionary_0, dictionary_index_0, postings_file_0)

        entry = update_dictionary_and_write_list(postings_list, merged_dir_path, \
            term, prev_end_pointer, merged_dictionary)
        prev_end_pointer = entry.end_pointer

        dictionary_index_0 += 1
    
    while dictionary_index_1 < len(dictionary_1):
        term = dictionary_1[dictionary_index_1].term
        postings_list = get_postings_list(dictionary_1, dictionary_index_1, postings_file_1)

        entry = update_dictionary_and_write_list(postings_list, merged_dir_path, \
            term, prev_end_pointer, merged_dictionary)
        prev_end_pointer = entry.end_pointer

        dictionary_index_1 += 1
    
    write_dictionary(merged_dictionary, merged_dir_path)

def merge_postings_lists(list_0, list_1):
    """
    Merges postings lists.
    """
    index_0 = 0
    index_1 = 0
    postings_list = []

    while index_0 < len(list_0) and index_1 < len(list_1):
        doc_id_0 = list_0[index_0][0]
        doc_id_1 = list_1[index_1][0]

        token_info_0 = list_0[index_0]
        token_info_1 = list_1[index_1]

        if doc_id_0 == doc_id_1:
            # Will never reach this state
            postings_list.append(token_info_0)
            index_0 += 1
            index_1 += 1
        elif doc_id_0 < doc_id_1:
            postings_list.append(token_info_0)
            index_0 += 1
        else:
            postings_list.append(token_info_1)
            index_1 += 1
    
    while index_0 < len(list_0):
        postings_list.append(list_0[index_0])
        index_0 += 1

    while index_1 < len(list_1):
        postings_list.append(list_1[index_1])
        index_1 += 1

    return postings_list