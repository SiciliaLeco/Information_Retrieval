#!/usr/bin/python3
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import PorterStemmer
import re
import nltk
import sys
import getopt
import os

punctuation = ['"', ',', '&', '(', ')', '-', '.', "'"]
M = 20 #### set memory size, you can personalize ####

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

class term_dict(object):
    def __init__(self):
        '''
        initialize the params
        '''
        self.terms = dict() # format: "term":[doc_freq, postings_list]
        self.size = 0 # size of occupied memory
        self.tmpidx = 0 # indexing output 'blk_X.txt'

    def add_terms(self, term, doc_id):
        '''
        add terms to the dictionary
            --> if available memory: store in mem
            ---> if not available: write to disk
        :param term:
        :param doc_id:
        :return:
        '''
        if self.size < M - 1: # still have space to store terms
            if self.terms.__contains__(term):
                if self.terms[term][1][-1] != doc_id: # current term has occured in the postings
                    self.terms[term][1].append(doc_id)
                    self.terms[term][0] += 1
            else:
                postings = [doc_id]
                self.terms[term] = [1, postings]
                self.size += 1

        else: # no enough space, write current 'self.terms' to blkX.txt
            tmpfile = "blk" + str(self.tmpidx) + ".txt" # generated file name #### you can chagne the index ####
            #TODO: write self.terms to blkx.txt
            f = open(tmpfile, 'w')
            for term in sorted(self.terms):
                write_info =  term + " " + str(self.terms[term][0])
                for posting in self.terms[term][1]:
                    write_info += " " + str(posting)
                f.write(write_info+"\n")
            # write format: term doc_freq docID1 docID2 .....\n
            self.size = 0
            self.terms = dict()
            self.tmpidx += 1


def data_preprocess(line):
    '''
    tokenize, porter stemmer,
    :param file: file name
    :return: list of processed terms
    '''
    stemmer = PorterStemmer()
    return_term = []
    words = nltk.sent_tokenize(line)
    for word in words:
        tokens = nltk.word_tokenize(word)
            # print(tokens)
        for token in tokens:
            token = stemmer.stem(token).lower()
            if token not in punctuation:
                return_term.append(token)

    return sorted(return_term)


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
    reuter_files = sorted([file for file in path], key=int)  # filename list, sorted
    reuter_files = reuter_files[:2]  # remember to delete this
    dictionary = term_dict()
    for file in reuter_files:
        f = open(in_dir + file)
        while True:
            line = f.readline() # read line by line
            if not line: # finish reading, end
                break
            else:
                tokens = data_preprocess(line)
                if tokens == []: # if null, continue to process
                    continue
                for token in tokens:
                    dictionary.add_terms(token, int(file))

        f.close()



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
