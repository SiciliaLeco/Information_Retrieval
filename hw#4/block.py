import pickle
import os

from temp_dir_util import TEMP_DIR, TO_MERGE_DIR, DICT_FILE, LISTS_FILE
from dictionary_entry import DictionaryEntry

class Block:
    """
    Represents a block. It has a capacity of `MAX_TOKENS`.
    """
    MAX_TOKENS = 10000000

    def __init__(self):
        self.dictionary = {}
        self.tokens_count = 0
        self.curr_dictionary_id = 0

    def is_full(self):
        """
        Checks whether the block is full.
        """
        return self.tokens_count >= self.MAX_TOKENS

    def is_empty(self):
        """
        Checks whether the dictionary is empty.
        """
        return not self.dictionary

    def add(self, token):
        """
        Adds `token` to the block.
        """
        (term, doc_id, tf, position_list) = token
        if term not in self.dictionary:
            self.dictionary[term] = []
        self.dictionary[term].append((doc_id, tf, position_list))
        self.tokens_count += 1

    def clear(self):
        """
        Clears the block.
        """
        self.dictionary = {}
        self.tokens_count = 0

    def save_dictionary(self):
        """
        Saves the dictionary created with the tokens that
        were added after (if it ever was) `clear` was called.
        To do so, the terms and the postings lists are written
        to two separate files.
        """
        sorted_terms = sorted(list(self.dictionary.keys()))

        postings_lists = []
        dictionary = []
        prev_end_pointer = -1

        for term in sorted_terms:
            postings_list = self.dictionary[term]
            prev_end_pointer = self.add_entry(term, prev_end_pointer, \
                postings_list, postings_lists, dictionary)

        self.write_to_disk(dictionary, postings_lists)

    def add_entry(self, current_term, prev_end_pointer, \
        postings_list, postings_lists, dictionary):
        """
        Adds an entry (which corresponds to a term) to the dictionary,
        and adds the postings list to postings lists. It also returns
        the updated prev_end_pointer.
        """
        entry = DictionaryEntry(current_term, \
                prev_end_pointer, postings_list)
        dictionary.append(entry)
        postings_lists.append(postings_list)

        return entry.end_pointer

    def write_to_disk(self, dictionary, postings_lists):
        """
        Writes the dictionary and postings lists to disk.
        """
        dict_lists_dir_path = os.path.join(TEMP_DIR, TO_MERGE_DIR, \
            str(self.curr_dictionary_id))

        if not os.path.isdir(dict_lists_dir_path):
            os.mkdir(dict_lists_dir_path)

        self.write_dictionary_to_disk(dictionary, dict_lists_dir_path)
        self.write_lists_to_disk(postings_lists, dict_lists_dir_path)

        self.curr_dictionary_id += 1

    def write_dictionary_to_disk(self, dictionary, dir_path):
        """
        Writes dictionary to disk.
        """
        dictionary_path = os.path.join(dir_path, DICT_FILE)

        with open(dictionary_path, 'wb') as f:
            pickle.dump(dictionary, f)

    def write_lists_to_disk(self, postings_lists, lists_path):
        """
        Writes postings lists to disk.
        """
        postings_lists_path = os.path.join(lists_path, LISTS_FILE)

        with open(postings_lists_path, 'wb') as f:
            for postings_list in postings_lists:
                pickle.dump(postings_list, f)
