#!/usr/bin/python3
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.porter import PorterStemmer
import string
import re
import nltk
import sys
import getopt
import os
import glob
import linecache

M = 60000  #### set memory size, 60000 for 10 blocks


def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


class term_dict(object):
    def __init__(self):
        '''
        initialize the params
        '''
        self.terms = dict()  # format: "term":[doc_freq, postings_list]
        self.size = 0  # size of occupied memory
        self.tmpidx = 0  # indexing output 'blkX.txt'

    def add_terms(self, term, doc_id, end):
        '''
        add terms to the dictionary
            --> if available memory: store in mem
            --> if not available: write to disk
        :return: whether can move to the next token (current token has already been parsed)
        '''
        if not end:
            if self.size < M:  # still have space to store terms
                if self.terms.__contains__(term):
                    if self.terms[term][1][-1] != doc_id:
                        # the doc_id has not occurred in the term's postings list
                        self.terms[term][1].append(doc_id)
                        self.terms[term][0] += 1
                        self.size += 1
                else:
                    postings = [doc_id]
                    self.terms[term] = [1, postings]
                    self.size += 1
                return True    # can move to next token

            else:  # no enough space, write current 'self.terms' to blkX.txt
                tmpfile = "blk" + str(self.tmpidx) + ".txt"
                # write self.terms to blkX.txt
                f = open(tmpfile, 'w')
                for term in sorted(self.terms):
                    write_info = term + " " + str(self.terms[term][0])
                    for posting in self.terms[term][1]:
                        write_info += " " + str(posting)
                    f.write(write_info + "\n")
                # write format: term doc_freq docID1 docID2 .....\n
                f.close()
                self.size = 0
                self.terms = dict()
                self.tmpidx += 1
                # cannot move to next token
                return False    # can move to next token (no token parsed this time)
        else:
            # if finish parsing all docs and dictionary not empty, flush the dictionary to the disk
            if self.terms != {}:
                tmpfile = "blk" + str(self.tmpidx) + ".txt"
                f = open(tmpfile, 'w')
                for term in sorted(self.terms):
                    write_info = term + " " + str(self.terms[term][0])
                    for posting in self.terms[term][1]:
                        write_info += " " + str(posting)
                    f.write(write_info + "\n")
                f.close()
                self.size = 0
                self.terms = dict()
                self.tmpidx += 1



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
            # Port stemming and case folding
            word = stemmer.stem(word).lower()
            # omit the punctuation
            if word not in string.punctuation:
                return_term.append(word)

    return return_term


def merge_list(list1, list2):
    '''
    Basically, OR operation between two lists.

    Since the files to be parsed are sorted, if there exists a term appearing in both list1 and list2, the docIDs of
    posting_list1 in list1 and posting_list2 in list2 for the term must be sorted separately, and it can only be
    one of the two cases as follows.

    Case 1: all sorted docIDs in posting_list1 are smaller than all sorted docIDs in posting_list2.
    eg. posting_list1: 1, 2, 3
        posting_list2: 4, 5, 6

    Case 2: all docIDs except the last one in posting_list1 are smaller than all docIDs in posting_list2, and the last
    docID in posting_list1 is equal to the first docID in posting_list2.
    eg. posting_list1: 1, 2, 3
        posting_list2: 3, 5, 6

    :param list1, list2: two list of tuples (term, [doc_freq, posting_list])
    :return: a merged list of tuples (term, [doc_freq, posting_list])
    '''
    merged_list = []
    m = n = 0
    while m <= len(list1) - 1 and n <= len(list2) - 1:
        if list1[m][0] == list2[n][0]:
            # last docID in posting_list1 = first docID in posting_list2
            if list1[m][1][1][-1] == list2[n][1][1][0]:
                merged_list.append((list1[m][0], [int(list1[m][1][0]) + int(list2[n][1][0]) - 1] + [
                    list1[m][1][1] + list2[n][1][1][1:]]))
            else:
                merged_list.append(
                    (list1[m][0], [int(list1[m][1][0]) + int(list2[n][1][0])] + [list1[m][1][1] + list2[n][1][1]]))
            m += 1
            n += 1
        elif list1[m][0] < list2[n][0]:
            merged_list.append(list1[m])
            m += 1
        else:
            merged_list.append(list2[n])
            n += 1
    while m <= len(list1) - 1:
        merged_list.append(list1[m])
        m += 1
    while n <= len(list2) - 1:
        merged_list.append(list2[n])
        n += 1

    return merged_list


def merge_dict(dict1, dict2, start, i):
    if dict1 == {} and dict2 == {}:
        print("Invalid case since two dictionaries are {}")
        return
    if dict1 == {} and dict2 != {}:
        return dict2
    if dict1 != {} and dict2 == {}:
        return dict1
    result = dict()

    for code in range(start, i):
        if chr(code) in dict1 and chr(code) in dict2:
            # combine the chunks of all dictionaries of all blocks for every start_char
            if dict1[chr(code)] == [] and dict2[chr(code)] == []:
                result[chr(code)] = []
            elif dict1[chr(code)] == [] and dict2[chr(code)] != []:
                result[chr(code)] = dict2[chr(code)]
            elif dict1[chr(code)] != [] and dict2[chr(code)] == []:
                result[chr(code)] = dict1[chr(code)]
            else:
                result[chr(code)] = merge_list(dict1[chr(code)], dict2[chr(code)])
    return result


def n_way_merge(dict_blocks, start, i, end):
    if not end:
        # delete all items of key chr(i) in the dictionaries of all blocks
        for dictionary in dict_blocks:
            if chr(i) in dictionary:
                del dictionary[chr(i)]

    result = dict()
    for j in range(len(dict_blocks)):
        if end:
            # if end, then start == i, so merge only chr(i)
            result = merge_dict(result, dict_blocks[j], start, i + 1)
        else:
            # otherwise, merge start_char of range chr(start) to chr(i)-1
            result = merge_dict(result, dict_blocks[j], start, i)
    return result


def writeToDisk(temp_result, dictFile, postFile):
    f_dict = open(dictFile, 'a')
    f_post = open(postFile, 'a')

    for code in range(ord('!'), ord('~') + 1):
        if chr(code) in temp_result:
            if temp_result[chr(code)] != []:
                # term_tuple = [(term, [freq, posting_list])]
                for term_tuple in temp_result[chr(code)]:
                    f_dict.write(term_tuple[0] + " " + str(term_tuple[1][0]) + " " + str(f_post.tell()))
                    write_infoP = " ".join(posting for posting in term_tuple[1][1])
                    f_post.write(write_infoP + '\n')
                    f_dict.write(" " + str(f_post.tell()) + "\n")

    f_dict.close()
    f_post.close()


def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    in_dir: input dictionary index
    out_dict: dictionary.txt
    out_postings: postings.txt
    """
    print('indexing...')

    '''
    generate blkX.txt files for blocks with SPIMI implemented
    '''
    path = os.listdir(in_dir)
    reuter_files = sorted([file for file in path], key=int)  # filename list, sorted

    # write all docIDs to docID.txt
    docIDfile = open("docID.txt", 'w')
    write_info = " ".join(reuter_files)
    docIDfile.write(write_info)
    docIDfile.close()

    dictionary = term_dict()
    end = False   # indicate whether all docs have been parsed
    for file in reuter_files:
        f = open(in_dir + file, 'r')
        while True:
            line = f.readline()  # read line by line
            if not line:  # finish reading, end
                break
            else:
                tokens = data_preprocess(line)
                if tokens == []:  # if null, continue to process
                    continue
                i = 0
                while i < len(tokens):
                    increment_i = dictionary.add_terms(tokens[i], int(file), end)
                    # only increase i when token[i] has been parsed
                    if increment_i:
                        i += 1

        f.close()

    end = True
    dictionary.add_terms("", -1, end)  # flush current dictionary if not empty

    '''
    merge the blkX.txt files with n-way merge.
    
    Since we need to guarantee that the merged result of the decent-sized chunks of each block lies in the final output,
    we set the set of terms starting with a particular character in the ASCII code table from 21 to 126 (decimal) as
    the basic unit. 
    
    Then we merge terms of basic units character by character. For example, we start at char '!' and hit the memory size 
    when we're parsing '$', then we abandon the '$' to not to exceed the memory, and merge the terms starting with char from 
    '!' to '#'. However, there's a limitation for this algorithm, if the memory size is not large enough to exceed the 
    size of the basic units for a particular char of all blocks, the program may come into an endless loop. For example, we 
    start at char '!', but the size of basic units for '!' of all blocks already exceeds the memory size. Then we would 
    repetitively abandon '!' and start at '!', which is meaningless. Thus, please don't change the memory size we set for 
    your convenience unless you have to do so.
    
    We're going to merge the chunks of all blocks for terms starting with char in a particular range once we hit the memory
    or all blocks have already been parsed. For the merge of chunks of all blocks, we use the simplest approach to merge 
    them one by one. For example, if we need to merge the chunks of char range from '!' to '#', we merge the basic units 
    one by one for every char in the range. To get the merged result for a particular char in the range, we merge the 
    dictionaries of every block for this char one by one.
    '''

    block_filenames = sorted(glob.glob('blk*.txt'))

    # one dictionary for each block to store the terms to be merged:
    # format for a dict(): {start_char: a list of tuples (term, [doc_freq, posting_list])}
    # we store the tuples in a list instead of a dictionary to maintain the lexicographical order among terms
    dict_blocks = [dict() for i in range(len(block_filenames))]

    # boolean values for each block indicating whether the blkX.txt has been finished
    end_blocks = [False] * len(block_filenames)

    # remember the second latest line numbers when start_char of terms change
    before_restartline = [1] * len(block_filenames)

    # remember the lastest line numbers when start_char of terms change
    restartline = [1] * len(block_filenames)

    # boolean values indicating whether there exists a term in the block having been parsed for each start_char
    pass_blocks = [False] * len(block_filenames)

    flag = False  # indicate whether should write to the disk (memory is full or all blocks are finished)
    end = False  # whether all blocks are finished

    # start from char '!'
    i = ord('!')
    # remember first start_char of terms in the memory
    start = i
    # occupied memory size
    size = 0

    while True:

        for j in range(len(block_filenames)):
            dict_blocks[j][chr(i)] = []

            index = restartline[j]
            line = linecache.getline(block_filenames[j], index)

            if not line.startswith(chr(i)):
                continue

            while line.startswith(chr(i)) and not flag:
                pass_blocks[j] = True
                line = line.rstrip().split(' ')
                term = line[0]
                df = line[1]
                posting_list = line[2:]
                size += int(df)

                if size >= M:
                    flag = True
                    break

                dict_blocks[j][chr(i)].append((term, [df] + [posting_list]))

                index += 1
                line = linecache.getline(block_filenames[j], index)

            if flag:
                # if memory is full and some blocks have been parsed (start_char changes again), restore the passed
                # blocks' restart indexes to the original ones
                for block_i in range(j):
                    if pass_blocks[block_i]:
                        restartline[block_i] = before_restartline[block_i]
                break
            else:
                # if memory is not full, then 'line' must start with a new start_char whose indexes we need to remember
                before_restartline[j] = restartline[j]
                restartline[j] = index
                # mark ends for the blocks if finished
                if line == "":
                    end_blocks[j] = True
                    if all(indicator == True for indicator in end_blocks):
                        # if all blocks are finished, then flush the memory
                        flag = True
                        end = True

        if flag:
            if start == i and not end:
                # start_char's range is starting and ending at the same char but not finish all blocks,
                # which is the case we mentioned before where size of basic units of a particular char
                # of all blocks already exceeds the memory which would come into an infinite loop
                print("A unit is too large, set a larger M")
                sys.exit(2)
            # partial result which should be written to the disk
            temp_result = n_way_merge(dict_blocks, start, i, end)
            writeToDisk(temp_result, out_dict, out_postings)
            if end:
                break
            dict_blocks = [dict() for i in range(len(block_filenames))]  # re-initialise the dictionaries for blocks
            size = 0  # re-initialise the size
            flag = False
            start = i  # restart from chr(i)
            end_blocks = [False] * len(block_filenames)
            continue

        pass_blocks = [False] * len(block_filenames)

        i += 1

        if i == ord('~') + 1:
            break






input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i':  # input directory
        input_directory = a
    elif o == '-d':  # dictionary file
        output_file_dictionary = a
    elif o == '-p':  # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
