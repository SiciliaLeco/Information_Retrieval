import os
from temp_dir_util import TEMP_DIR, TO_MERGE_DIR
from index_util import get_dictionary_and_postings_file, get_postings_list, \
    update_dictionary_and_write_list, write_dictionary

def encode_gap(out_dict, out_postings):
    """
    Encodes gap in postings lists. For each postings list, only the first
    The updated dictionary and postings lists
    are then written to the user-specified `out_dict` and `out_postings`.
    """
    dir_path = os.path.join(TEMP_DIR, TO_MERGE_DIR)

    assert len(os.listdir(dir_path)) == 1, 'Still too many directories'

    directory = None 
    for file in os.scandir(dir_path):
        directory = file

    (dictionary, postings_file) = get_dictionary_and_postings_file(directory)
    
    updated_dictionary = []
    prev_end_pointer = -1

    new_dir_path = '.'

    for (index, entry) in enumerate(dictionary):
        postings_list = get_postings_list(dictionary, index, postings_file)
        postings_list_w_encoded_gap = get_list_w_encoded_gap(postings_list)

        term = entry.term
        entry = update_dictionary_and_write_list(postings_list_w_encoded_gap, \
            new_dir_path, term, prev_end_pointer, updated_dictionary, out_postings)
        prev_end_pointer = entry.end_pointer

    write_dictionary(updated_dictionary, new_dir_path, out_dict)

def get_list_w_encoded_gap(postings_list):
    """
    Converts a regular `postings_list` to one with encoded gap.
    The first element in the list is the docID of the first posting.
    Subsequent elements are store the gap between two adjacent postings' 
    docID. 
    """
    postings_list_w_encoded_gap = []
    prev_doc_id = 0

    for token_info in postings_list:
        doc_id = token_info[0]
        gap = doc_id - prev_doc_id
        prev_doc_id = doc_id
        updated_token_info = (gap,) + token_info[1:]
        postings_list_w_encoded_gap.append(updated_token_info)
    
    return postings_list_w_encoded_gap
