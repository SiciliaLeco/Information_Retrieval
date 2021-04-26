#!/usr/bin/python3

import csv
import sys
import getopt
import pickle
from create_blocks import create_blocks_and_find_lengths
from compression import encode_gap
from merge import merge_blocks
from temp_dir_util import setup_dirs, remove_dirs
from term_info import TermInfo
from index_util import write_lengths_and_dictionary

def get_docs_from_csv(data_path):
    """
    Get documents from the given csv file.

    For the baseline model, combine all the text, only store two features
    for each document: docIDs, text.

    return a list, each element contains doc_id and doc_text.
    """

    csv.field_size_limit(sys.maxsize)

    with open(data_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        # docIDs are already sorted in the original dataset
        docs = [row for row in csv_reader]
        return docs

def usage():
    print("usage: " + sys.argv[0] + " -i dataset-file -d dictionary-file -p postings-file")

def build_index(in_dataset, out_dict, out_postings):
    """
    Builds index from documents stored in the dataset file,
    then write results to the dictionary file and postings file
    """
    print('indexing...')

    documents = get_docs_from_csv(in_dataset)

    # create directory to store intermediate dictionaries
    setup_dirs(out_dict, out_postings)
    lengths_and_court_importance = create_blocks_and_find_lengths(documents)

    merge_blocks()
    
    encode_gap(out_dict, out_postings)
    save_dictionary_lengths_and_court(out_dict, lengths_and_court_importance)

    # remove directory that stores intermediate dictionaries
    remove_dirs()

def save_dictionary_lengths_and_court(out_dict, lengths_and_court_importance):
    """
    Loads the dictionary that has been saved at `out_dict` and save it 
    as a dict. In addition, save the `lengths_and_court_importance` at `out_dict`.

    `out_dict` will thus store two pickle objects. The first is `lenghts_and_court_importance`.
    The second is the dictionary.

    NOTE: Assumes that the original dictionary is a list.
    """
    dictionary = None
    with open(out_dict, 'rb') as f:
        dictionary = pickle.load(f)
    dictionary_as_map = {}

    for entry in dictionary:
        term_info = TermInfo(entry)
        dictionary_as_map[entry.term] = term_info

    dir_path = '.'
    write_lengths_and_dictionary(lengths_and_court_importance, dictionary_as_map,\
        dir_path, out_dict)


input_file_dataset = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # dataset file
        input_file_dataset = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_file_dataset == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_file_dataset, output_file_dictionary, output_file_postings)
