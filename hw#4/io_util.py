import pickle
from math import sqrt

from query_util import get_doc_info

def load_lengths_and_dictionary(dict_file):
    """
    Load lengths and dictionary from dict_file.

    Returns a tuple `(lengths, dictionary)`.

    NOTE: length includes the court importance information. In particular,
    length is in fact (doc length, court importance).
    """
    with open(dict_file, "rb") as f:
        lengths = pickle.load(f)
        dictionary = pickle.load(f)
        return (lengths, dictionary)
    
    assert False

def load_term_info(term, dictionary):
    """
    Load term info of a specified term from dictionary and postings file.
    The term info consists of the term, document frequency as well as 
    start and end pointer of its posting list.
    If the term does not exist, return None instead.
    """
    if term not in dictionary:
        return None

    return dictionary[term]

def load_posting_list(term, dictionary, postings_file):
    """
    Load posting list of a specified term from dictionary and postings file.
    If the term does not exist, return empty list instead.
    """
    info = load_term_info(term, dictionary)
    
    if info is None:
        return []
    
    index_start = info.start_pointer
    index_end = info.end_pointer

    posting_list = load_posting_list_from_pickle(postings_file, index_start, index_end)
    result = []
    prev_doc_id = 0
    for posting in posting_list:
        doc_info = get_doc_info(term, posting, prev_doc_id)
        result.append(doc_info)
        prev_doc_id = doc_info[0]
    return result

def load_posting_list_from_pickle(postings_file, index_start, index_end):
    """
    Load posting list that starts at `index_start` and ends at `index_end`
    in the given postings file.
    """
    with open(postings_file, "rb") as f:
        f.seek(index_start)
        posting_list_as_bytes = f.read(index_end - index_start + 1)
        posting_list = pickle.loads(posting_list_as_bytes)
        if not posting_list:
            assert False

        return posting_list
