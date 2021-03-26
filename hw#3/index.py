#!/usr/bin/python3
import re
import nltk
import math
import os
import sys
import getopt
import string
from nltk.stem.porter import PorterStemmer

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

'''
    This .py file is to generate a dictionary of term and its postings file to make rank
    retrieval more convenient.
    *format for data structure*:
    dictionary format: Dict[term] = doc_freq, postings
    postings format: postings (type=list), element type=tuple
    [(docID1, term_freq1), (docID2, term_freq2),....]
    --------------------------------------
    *format for txt file*
    dictionary.txt: term doc_freq postings_start_ptr postings_end_ptr\n
    postings.txt: docID1,term_freq1 docID2,term_freq2
'''

class Dict(object):
    def __init__(self):
        self.dictionary = dict()

    def add_terms(self, term, docID, tfd):
        if self.dictionary.__contains__(term) == False:
            postings = [(docID, tfd)]
            self.dictionary[term] = [1, postings]
        else:
            self.dictionary[term][0] += 1 # docFrequency + 1
            self.dictionary[term][1].append((docID, tfd)) # term Postings list update

    def show_items(self):
        '''
        to check if the output result is in the right format
        '''
        for k,v in self.dictionary.items():
            print(k, v)

    def get_dict(self):
        return self.dictionary

def data_preprocess(line):
    '''
    :param: line, one line in the file
    :return: a list of processed tokens
    '''

    stemmer = PorterStemmer()
    return_term = []
    # tokenize the sentences in one line
    sents = nltk.sent_tokenize(line)
    for sent in sents:
        # tokenize the words in one sentence
        words = nltk.word_tokenize(sent)
        for word in words:
            word = stemmer.stem(word.lower())
            # omit the punctuation
            if word not in string.punctuation:
                return_term.append(word)



    return return_term

def term_count(tokens):
    '''
    count frequency for terms in one document
    :param tokens: type=list()
    :return: type=dict()
    '''
    output = dict()
    for token in tokens:
        if output.__contains__(token) == False:
            output[token] = 1
        else:
            output[token] += 1
    return output

def tf(item):
    '''
    calculate term frequency weight
    '''
    if item > 0:
        return math.log10(item) + 1
    else:
        return 0

def write_disk(result, dictFile="dictionary.txt", postFile="postings.txt"):
    '''
    write current data (Dict()) to the disk
    :param temp_result: type=Dict()
    '''
    f_dict = open(dictFile, 'w')
    f_post = open(postFile, 'w')
    dictionary = result.get_dict()
    for term, info in sorted(dictionary.items()):
        doc_freq = info[0]
        post = info[1]
        temp_post = []
        for item in post: #[(docID, termFreq), (), ...]
            write_info = str(item[0]) + "," + str(item[1])
            temp_post.append(write_info)

        f_dict.write(term + " " + str(doc_freq) + " " + str(f_post.tell()))
        write_posting = " ".join(temp_post)
        f_post.write(write_posting + '\n')
        f_dict.write(" " + str(f_post.tell()) + "\n")
    f_dict.close()
    f_post.close()

def calculate_docLength(doc_dict):
    length = 0
    for val in doc_dict.values():
        length += tf(val) ** 2
    return math.sqrt(length)

def write_doc_length(lengthlist, filename):
    '''
    this function is to write length information for each doc
    :param lengthlist: type=list(), contain info about each doc's length
    :param filename: type=list(), a list of doc's filename
    :return:
    '''
    docLenfile = open("length.txt", 'w')
    tot_len = len(lengthlist)
    docLenfile.write(str(tot_len) + "\n")
    for i in range(len(lengthlist)):
        write_info = str(filename[i]) + " " + str(lengthlist[i]) + "\n"
        docLenfile.write(write_info)
    docLenfile.close()

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # This is an empty method
    # Pls implement your code in below

    path = os.listdir(in_dir)
    reuter_files = sorted([file for file in path], key=int)  # filename list, sorted

    dictionary = Dict()
    docLength = list()

    for file in reuter_files:
        f = open(in_dir + file, 'r')
        data = f.read()
        tokens = data_preprocess(data)
        tmp_dict = term_count(tokens)
        for k, v in tmp_dict.items(): # k=term, v=doc_freq
            dictionary.add_terms(k, int(file) ,v)
        length = calculate_docLength(tmp_dict)

        docLength.append(length)
        f.close()

    write_doc_length(docLength, reuter_files)
    write_disk(dictionary, out_dict, out_postings)



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
