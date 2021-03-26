#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import *
import string
import math
from time import time
import heapq

class dictionary(object):
    def __init__(self):
        self.term_dict = {}

    def add_term(self, term, freq, start, end):
        self.term_dict[term] = [freq, start, end]

    def show_items(self):
        '''
        to check if the output result is in the right format
        '''
        for k,v in self.term_dict.items():
            print(k, v)


def generate_dict(dict_file):
    Dict = dictionary()
    f = open(dict_file, 'r')
    term_infos = f.read().splitlines()
    for info in term_infos:
        info = info.split(" ")
        Dict.add_term(info[0], info[1], info[2], info[3])
    f.close()
    return Dict


def preprocess_sentence(sent):
    '''
    pre-process the input query sentence
    using stemmer
    :param sent:
    :return:
    '''
    if sent == '':
        return []
    tokens = word_tokenize(sent)
    # print(tokens)
    # tokens = sent.split(' ')
    stemmer = PorterStemmer()
    return_token_list = []
    for token in tokens:
        # token = stemmer.stem(token).lower()
        token = stemmer.stem(token.lower())
        if token not in string.punctuation:
            return_token_list.append(token)
    return return_token_list

def term_count(tokens):
    '''
    count frequency for terms in one query
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

def get_postings(postings_file, start, end):
    f = open(postings_file, 'r')
    f.seek(start, 0)
    postings = f.read(end - start)
    f.close()
    postings = postings.strip().split(' ')
    result_pairs = []
    for pair in postings:
        pair = pair.split(',')
        result_pairs.append((int(pair[0]), int(pair[1])))
    return result_pairs

def calculate_scores(tokens, queryTf, D, N, lengths, postings_file):
    scores = dict()

    if len(tokens) == 1:
        # if only one token in the query, no need to calculate idf
        if tokens[0] not in D.term_dict:
            return []
        else:
            info = D.term_dict[tokens[0]]   # [freq, start_pos, end_pos]
            df, start, end = int(info[0]), int(info[1]), int(info[2])
            pairs = get_postings(postings_file, start, end)
            for pair in pairs:
                if pair[0] not in scores:
                    scores[pair[0]] = math.log10(pair[1]) + 1
                else:
                    scores[pair[0]] += math.log10(pair[1]) + 1
    else:
        # if more than one tokens in the query, need to calculate idf
        count_notin = 0
        for token in tokens:
            if token not in D.term_dict:
                count_notin += 1
                continue

            info = D.term_dict[token]   # [freq, start_pos, end_pos]
            df, start, end = int(info[0]), int(info[1]), int(info[2])
            pairs = get_postings(postings_file, start, end)
            w_tq = (math.log10(queryTf[token]) + 1) * math.log10(N/df)

            for pair in pairs:
                if pair[0] not in scores:
                    scores[pair[0]] = w_tq * (math.log10(pair[1]) + 1)
                else:
                    scores[pair[0]] += w_tq * (math.log10(pair[1]) + 1)

        if count_notin == len(tokens):
            return []

    for docID in scores:
        scores[docID] /= lengths[docID]

    heap_docs = []
    for docID, score in scores.items():
        tmp_node = (-score, docID)
        heapq.heappush(heap_docs, tmp_node)

    # first sort by score descending, if there's a tier, then sort by docID ascending
    top10 = heapq.nsmallest(10, heap_docs)
    top10_docs = []
    for i in top10:
        top10_docs.append(i[1])

    # sorted_scores = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    #
    # for (docID, score) in sorted_scores[:10]:
    #     top10_docs.append(docID)
    return top10_docs

def write_to_output_file(results_file, answer_list):
    r_file = open(results_file, 'w')

    for answer in answer_list:
        str_list = []
        for number in answer:
            str_list.append(str(number))
        write_info = " ".join(str_list) + "\n"
        r_file.write(write_info)

    r_file.close()

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below


    # start_time = time()

    # generate a dictionary from dictionary.txt
    q_file = open(queries_file, 'r')
    query_sent = q_file.read().splitlines()
    D = generate_dict(dict_file)


    lengths = dict()
    length_file = open('length.txt', 'r')
    length_sent = length_file.read().splitlines()
    # N: the total number of docs
    N = int(length_sent[0])
    # lengths: store length of docs in formate {docID: length_docID}
    for line in length_sent[1:]:
        len_info = line.split(' ')
        lengths[int(len_info[0])] = float(len_info[1])

    query_result = []
    for q in query_sent:
        tokens = preprocess_sentence(q)
        if tokens == []:
            query_result.append([])
            continue
        queryTf = term_count(tokens)
        # print(queryTf)
        top10_docs = calculate_scores(tokens, queryTf, D, N, lengths, postings_file)
        query_result.append(top10_docs)

    # print(str(time()-start_time) + ' sec')
    # for result in  query_result:
        # print(result)

    write_to_output_file(results_file, query_result)



dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
