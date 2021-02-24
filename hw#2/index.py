#!/usr/bin/python3
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import PorterStemmer
import re
import nltk
import sys
import getopt
import os

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def data_preprocess(file):
    '''
    tokenize, porter stemmer,
    :param file:
    :return:
    '''
    stemmer = PorterStemmer()
    with open(file, 'rb') as f:
        sentence = file.read()

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    in_dir: input dictionary index
    out_dict: dictionary.txt
    out_postings: postings.txt
    """
    print('indexing...')
    path = os.listdir(in_dir)
    reuter_files = sorted([file for file in path], key=int) #filename list
    reuter_files = reuter_files[:100] # remember to delete this

    for file in reuter_files:
        with open(file) as f:




input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
