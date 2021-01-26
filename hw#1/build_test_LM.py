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
        self.mlydict = {}
        self.idndict = {}
        self.tmidict = {}

    def count_mlysize(self, key):
        size = 0
        if(self.mlydict.__contains__(key) == False):
            return 0
        for key2 in self.mlydict[key]:
                size += 1
        return size

    def count_idnsize(self, key):
        size = 0
        if(self.idndict.__contains__(key) == False):
            return 0
        for key2 in self.idndict[key]:
                size += 1
        return size

    def count_tmisize(self,key):
        size = 0
        if(self.tmidict.__contains__(key) == False):
            return 0
        for key2 in self.tmidict[key]:
                size += 1
        return size



def count_Freq(tag, str, LM):
    '''
    count the frequency of every 4-gram, store into its dict
    dict is deciede by tag, str is text
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
    else:
        tempDict = LM.tmidict

    begin, end = 0, 3

    while(end < len(str)):
        prev_word = "".join(str[begin:end])
        # print(str[end] + " | " + str[begin:end]) #debug
        if (tempDict.__contains__(str[end]) == False):
            tempDict[str[end]] = {}  # initialize dict for it
        elif (tempDict[str[end]].__contains__(prev_word) == False):
            tempDict[str[end]][prev_word] = 1
        else:
            tempDict[str[end]][prev_word] += 1
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
            str = " ".join(line.split(" ")[1:]) # get sentence by deleting tag
            if(tag == "malaysian"):
                LM.mlydict = count_Freq(tag, str, LM)
            elif(tag == "tamil"):
                LM.midict = count_Freq(tag, str, LM)
            elif(tag == "indonesian"):
                LM.idndict = count_Freq(tag, str, LM)
    # count 4gram finish
    return LM

def calc_Prob(LM, prev_word, word, inst, V, mis_count):
    '''
    a function used to calculate a single probability from given LM
    :param LM:
    :param prev_word:
    :param word:
    :param inst: 0~malay 1~indon 2 ~ tamil
    :return:
    '''
    prob = 1
    cW = 0
    if(inst == 0):
        tmpDict = LM.mlydict
        cW = LM.count_mlysize(word)
    elif inst == 1:
        tmpDict = LM.idndict
        cW = LM.count_idnsize(word)
    else:
        tmpDict = LM.tmidict
        cW = LM.count_tmisize(word)

    if(tmpDict.__contains__(word) == False):
        prob = (0 + 1) / V
        mis_count += 1
    elif(tmpDict[word].__contains__(prev_word) == False):
        prob = (0 + 1) / (V + cW)
        mis_count += 1
    else:
        prob = (tmpDict[word][prev_word] + 1) / (V + cW)

    return prob * 100, mis_count # augment the probability to make convenient to compare

def judge_Language_Type(a,b,c,miscount, tot):
    '''
    this is to judge the language type by the calculated probability,
    as for "other" label, it is detemined by the miss rate of the 4-gram in test string,
    that is:
    if the 4gram that don't belong to my LM,then it is treated as alien gram.
    if there are too many 4grams don't belong to my LM, it shows that doesn't belong to the 3 language
    :param a, b, c: three probability results
    :param miscount: the number that the 4-gram in the test string that dont belong to my LM
    :param tot: length of the test string
    :return:
    '''
    bound = 2.5
    misrate = miscount / tot
    if misrate > bound:
        return "other"
    elif((a > b) and (a > c)):
        return "malaysian"
    elif((b > a) and (b > c)):
        return "indonesian"
    elif((c > a) and (c > b)):
        return "tamil"

def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    # This is an empty method
    # Pls implement your code below
    pred_lst = []
    with open(in_file) as fin:
        for line in fin.readlines():
            line = line.strip()
            set_lst = set(line)
            V_lst = len(set_lst)  # V size
            begin, end = 0, 3 # gram size = 4
            p_malay, p_indo, p_temil = 1, 1, 1
            mis_count = 0
            while(end < len(line)):
                prev_word = "".join(line[begin:end])
                p1, mis_count = calc_Prob(LM, prev_word, line[end], 0, V_lst, mis_count)
                p_malay *= p1
                p2, mis_count = calc_Prob(LM, prev_word, line[end], 1, V_lst, mis_count)
                p_indo *= p2
                p3, mis_count = calc_Prob(LM, prev_word, line[end], 2, V_lst, mis_count)
                p_temil *= p3
                begin += 1
                end += 1
            pred_lst.append(judge_Language_Type(math.log10(p_malay), math.log10(p_indo), math.log10(p_temil), mis_count, len(line)) + " " + line)
            # print(math.log10(p_malay), math.log10(p_indo), math.log10(p_temil))
            # print(judge_Language_Type(p_malay, p_indo, p_temil, mis_count, len(line))) #debug
            # print(mis_count/ len(line))

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
