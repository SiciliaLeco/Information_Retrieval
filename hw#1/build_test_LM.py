#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import sys
import getopt
import math

class lang_Model:
    '''
    language model class
    '''
    def __init__(self):
        ## dictionary to store 4-gram data
        ## for malay, idone and temil.
        self.mlydict = {}
        self.idndict = {}
        self.tmidict = {}

    def count_mlysize(self):
        '''
        the following three count functions are used to count
        vocabulary size in each lang model.
        '''
        size = 0
        for key in self.mlydict.keys():
            size += self.mlydict[key]
        return size

    def count_idnsize(self):
        size = 0
        for key in self.idndict.keys():
            size += self.idndict[key]
        return size

    def count_tmisize(self):
        size = 0
        for key in self.tmidict.keys():
            size += self.tmidict[key]
        return size


def count_Freq(tag, str, LM):
    '''
    count the frequency of every 4-gram, store into its dict
    dict is deciede by tag, str is text.
    this is used by build_LM function
    :param tag:
    :param str:
    :return:
    '''
    #assert str > 4
    str = str.strip()
    tempDict = {}
    if(tag == "malaysian"):
        tempDict = LM.mlydict
    elif(tag == "indonesian"):
        tempDict = LM.idndict
    elif(tag == "tamil"):
        tempDict = LM.tmidict

    begin, end = 0, 3 # two pointers

    while(end < len(str)):
        prev_word = "".join(str[begin:end])
        gram = prev_word + str[end]
        # print(gram)
        # print(str[end] + " | " + str[begin:end]) #debug
        ## prepare for the add-1 smoothing process
        if (LM.mlydict.__contains__(gram) == False):
            LM.mlydict[gram] = 0
        if (LM.idndict.__contains__(gram) == False):
            LM.idndict[gram] = 0
        if (LM.tmidict.__contains__(gram) == False):
            LM.tmidict[gram] = 0
        tempDict[gram] += 1

        begin += 1
        end += 1

    return tempDict

def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print("building language models...")
    # This is an empty method
    # Pls implement your code below
    LM = lang_Model() # train and get this model
    with open(in_file) as f:
        for line in f.readlines():
            tag = line.split(" ")[0] # split the corpus by " " and get tag info
            str = " ".join(line.split(" ")[1:]) # get sentence by deleting tag(label)
            if(tag == "malaysian"):
                LM.mlydict = count_Freq(tag, str, LM)
            elif(tag == "tamil"):
                LM.tmidict = count_Freq(tag, str, LM)
            elif(tag == "indonesian"):
                LM.idndict = count_Freq(tag, str, LM)
    # count 4gram finish
    print("language models finished!")
    return LM


def calc_miss(LM, str):
    '''
    this method is to calculate how many 4gram in the given string
    are not in the LM, and return the value
    :param LM: my language model
    :param str: the given test string
    :return: the miss frequency that the given string happens
    '''
    begin, end = 0, 3
    ma_miss, in_miss, tm_miss = 0, 0, 0 # initialize counting result
    while end < len(str):
        tmpword = str[begin:end+1]
        if (LM.mlydict.__contains__(tmpword) == False):
            ma_miss += 1
        if (LM.idndict.__contains__(tmpword) == False):
            in_miss += 1
        if (LM.tmidict.__contains__(tmpword) == False):
            tm_miss += 1
        begin += 1
        end += 1
    return ma_miss, in_miss, tm_miss


def calc_Prob(LM, word, inst):
    '''
    a function to calculate a single probability from given LM
    :param LM: my lang model
    :param word: the 4gram word to be calculated
    :param inst: instruction on which language to test
        0 ~ malay, 1 ~ indo, 2 ~ demil
    :param ml_miss: miss frequency of the string
    :param in_miss:
    :param dm_miss:
    :return:
    '''
    # initialize for prob and cW
    prob, V, cW = 1, 0, 0
    if(inst == 0):
        tmpDict = LM.mlydict
        cW = LM.count_mlysize()
        V = len(LM.mlydict)
    elif inst == 1:
        tmpDict = LM.idndict
        cW = LM.count_idnsize()
        V =len(LM.idndict)
    else:
        tmpDict = LM.tmidict
        cW = LM.count_tmisize()
        V = len(LM.tmidict)

    ## add-1 smoothing process
    if(tmpDict.__contains__(word) == False):
        prob = 1 # don't handle grams that don't exist in my LM
    else:
        prob = (tmpDict[word] + 1) / (V + cW)

    return math.log10(prob)  # augment the probability to make convenient to compare

def judge_Language_Type(a,b,c,miscount, tot):
    '''
    this is to judge the language type by the calculated probability,
    as for "other" label, it is detemined by the miss rate of the 4-gram in test string,
    that is:
    if the 4gram don't belong to my LM, then it is treated as alien gram.
    if there are too many alien 4grams, it shows that doesn't belong to the 3 language
    the threshold value is determined by param@bound
    :param a, b, c: three probability results
    :param miscount: the number that the 4-gram in the test string that dont belong to my LM
    :param tot: length of the test string
    :return:
    '''
    bound = 2.3
    # value of bound is determined by my observation of the test set
    misrate = miscount / tot
    if misrate > bound:
        return "other"
    elif((a > b) and (a > c)):
        return "malaysian"
    elif((b > a) and (b > c)):
        return "indonesian"
    elif((c > a) and (c > b)):
        return "tamil"
    else:
        return "other"

def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    # This is an empty method
    # Pls implement your code below
    pred_lst = [] # store result
    with open(in_file) as fin:
        for line in fin.readlines():
            line = line.strip()  # delete "\n"
            begin, end = 0, 3 # gram size = 4
            p_malay, p_indo, p_temil = 0, 0, 0
            ml_miss, in_miss, dm_miss = calc_miss(LM, line)
            mis_count = ml_miss + in_miss + dm_miss

            while(end < len(line)):
                ## calculate the probability
                gramword = "".join(line[begin:end+1]) # 4gram word
                p_malay += calc_Prob(LM, gramword, 0)
                # because use logs so here use "+" to accumulate probability
                p_indo += calc_Prob(LM, gramword, 1)
                p_temil += calc_Prob(LM, gramword, 2)

                begin += 1
                end += 1
            # print(judge_Language_Type(p_malay, p_indo, p_temil, mis_count, len(line))) #debug
            pred_lst.append(judge_Language_Type(p_malay, p_indo, p_temil, mis_count, len(line)) + " " + line)

    with open(out_file, "w") as fout: # write result to the file
        for pred in pred_lst:
            fout.write(pred+"\n")

def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"
    )


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "b:t:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-b":
        input_file_b = a
    elif o == "-t":
        input_file_t = a
    elif o == "-o":
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
