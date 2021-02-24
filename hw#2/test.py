import os
import nltk
from nltk.stem.porter import PorterStemmer
index = "training/"
fr = sorted([f for f in os.listdir(index)], key=int)
# print(fr)

punctuation = ['"', ',', '&', '(', ')', '-', '.', "'"]
M = 100 # set memory size
class term_dict(object):
    def __init__(self):
        self.terms = dict() # format: "term":[doc_freq, postings_list]
        self.size = 0
        self.tmpidx = 0 # indexing output 'blk_X.txt'
    def add_terms(self, term):
        if self.size < M - 1: # still have space to store terms
            #TODO: memory有多余的，更新term到dict里面

        else: # no enough space, write current 'self.terms' to temp.txt
            tmpfile = "blk" + str(self.tmpidx) + ".txt" # generated file name
            #TODO: write self.terms to blkx.txt
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

    return return_term


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
                # print(tokens)


        f.close()

build_index("training/", "a.v", "b.v")