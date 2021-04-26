import os
import pickle

from dictionary_entry import DictionaryEntry
from temp_dir_util import DICT_FILE, LISTS_FILE
from io_util import load_posting_list_from_pickle

def get_dictionary_and_postings_file(directory):
    """
    Gets the dictionary (object) and the postings list file
    based on the contents found in `dictionary`.

    It assumes that only one dictionary file and one postings
    list file are in the directory.
    """
    dictionary = None
    postings_file = None

    directory = os.scandir(directory)

    for file in directory:
        if DICT_FILE in file.name:
            with open(file, 'rb') as f:
                dictionary = pickle.loads(f.read())
        elif LISTS_FILE in file.name:
            postings_file = file
        else:
            assert False, 'Unknown file type'

    assert dictionary != None and postings_file != None, 'Dict or file is missing'
    return (dictionary, postings_file)

def get_postings_list(dictionary, term_index, postings_file):
    """
    Get postings list for the term that is at `term_index` of the `dictionary`,
    where the postings list should be represented in `postings_file`.
    """
    index_start = dictionary[term_index].start_pointer
    index_end = dictionary[term_index].end_pointer
    return load_posting_list_from_pickle(postings_file, index_start, index_end)

def update_dictionary_and_write_list(updated_postings_list, \
    dir_path, term, prev_end_pointer, dictionary, postings_file=LISTS_FILE):
    """
    Updates the dictionary and writes the postings list to file.
    """
    write_postings_list(updated_postings_list, dir_path, postings_file)
    entry = DictionaryEntry(term, prev_end_pointer, updated_postings_list)
    dictionary.append(entry)
    return entry

def write_postings_list(postings_list, dir_path, postings_file):
    """
    Writes postings list to file.
    """
    dir_path = os.path.join(dir_path, postings_file)
    with open(dir_path, 'ab') as f:
        pickle.dump(postings_list, f)

def write_dictionary(dictionary, dir_path, dict_file=DICT_FILE):
    """
    Writes dictionary to file.
    """
    dir_path = os.path.join(dir_path, dict_file)
    with open(dir_path, 'wb') as f:
        pickle.dump(dictionary, f)

def write_lengths_and_dictionary(lengths_and_court_importance, dictionary,\
    dir_path, dict_file=DICT_FILE):
    """
    Writes dictionary and lengths and court importance information to dictionary file.
    """
    dir_path = os.path.join(dir_path, dict_file)
    with open(dir_path, "wb") as f:
        pickle.dump(lengths_and_court_importance, f)
        pickle.dump(dictionary, f)
