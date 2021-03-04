#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import math
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import *

operator = ["AND", "OR", "NOT"]
bracket = ["(", ")"]
priority = {'NOT': 3, 'AND': 2, 'OR': 1, '(': 0, ')':0}


class dictionary(object):
    def __init__(self):
        self.term_dict = {}

    def add_term(self, term, freq, start, end):
        self.term_dict[term] = [freq, start, end]


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
    :param sent: input sentence
    :return: terms after tokenization and doing stemmer
    '''
    tokens = word_tokenize(sent)
    stemmer = PorterStemmer()
    return_token_list = []
    for token in tokens:
        t = token
        if (token not in operator) and (token not in bracket):
            t = stemmer.stem(token).lower()  # make sure that all lowered
            return_token_list.append(t)
        else:
            return_token_list.append(t)
    return return_token_list


def delete_redundant_NOT(query):
    '''
    delete multiple "NOT"s in the query sentence
    to avoid situation like: "a AND NOT NOT NOT b" that actually equals "a AND NOT b",
    we should delete meaningless NOTs to one NOT or zero NOT
    otherwise the structure of rpn would be compromised
    :param query:
    :return: simplified version of query
    '''
    not_count = 0
    cleaned_result = []
    for token in query:
        if token == "NOT":
            if not_count == 0:
                cleaned_result.append(token)
            not_count += 1
        else:
            if not_count % 2 == 0 and not_count != 0:
                cleaned_result.pop()
            cleaned_result.append(token)
            not_count = 0
    return cleaned_result


def shunting_yard(query):
    '''
    precedence: (), NOT, AND, OR
    :param query:query sentence split in to list
    :return: RPN of the query sentence, type=list
    '''
    out_rpn = list() # term stack
    op_stack = list() # operator stack
    # query = delete_redundant_NOT(query)
    for token in query:
        if token not in operator and token not in bracket:      # term
            out_rpn.append(token)

        elif token in operator:
            while op_stack and priority[op_stack[-1]] >= priority[token]:
                out_rpn.append(op_stack.pop())
            op_stack.append(token)

        elif token == bracket[0]: #(
            op_stack.append(token)
        elif token == bracket[1]: #)
            while op_stack and op_stack[-1] != bracket[0]:
                out_rpn.append(op_stack.pop())
            if op_stack and op_stack[-1] == bracket[0]:
                op_stack.pop()

    # print(op_stack)
    while len(op_stack) > 0:
        out_rpn.append(op_stack.pop())

    return out_rpn

def merge(a, b, op):
    """
    merge two postings list, union or intersect
    :param a: postings list 1
    :param b: postings list 2
    :param op: operator, type=str
    :return: merged result
    """
    # we apply evenly distributed skip pointers to all posting lists
    # (including the intermediate generated ones)
    jump_a = math.floor(math.sqrt(len(a)))
    jump_b = math.floor(math.sqrt(len(b)))

    result = []
    if op == "AND":
        i, j = 0, 0
        while i < len(a) and j < len(b):
            if a[i] < b[j]:
                if i % jump_a == 0 and i + jump_a < len(a) and jump_a != 1:
                    if a[i + jump_a] < b[j]:
                        i += jump_a
                    elif a[i + jump_a] == b[j]:
                        result.append(b[j])
                        i += jump_a + 1
                        j += 1
                    else:
                        i += 1
                else:
                    i += 1
            elif a[i] > b[j]:
                if j % jump_b == 0 and j + jump_b < len(b) and jump_b != 1:
                    if b[j + jump_b] < a[i]:
                        j += jump_b
                    elif b[j + jump_b] == a[i]:
                        result.append(a[i])
                        i += 1
                        j += jump_b + 1
                    else:
                        j += 1
                else:
                    j += 1
            else:
                result.append(a[i])
                i += 1
                j += 1
        return result

    elif op == "OR":
        i, j = 0, 0
        while i < len(a) and j < len(b):
            if a[i] < b[j]:
                result.append(a[i])
                i += 1
            elif a[i] > b[j]:
                result.append(b[j])
                j += 1
            else:
                result.append(a[i])
                i += 1
                j += 1

        while i < len(a):
            result.append(a[i])
            i += 1

        while j < len(b):
            result.append(b[j])
            j += 1
        return result

    else:
        return []


def reverse_postings(postings):
    '''
    operator is "NOT", so the new postings list should be {ALL - postings}
    :param postings:
    :return:new postings
    '''
    f = open("docID.txt", 'r')
    tot_list = f.read().split(" ")
    for i in range(len(tot_list)):
        tot_list[i] = int(tot_list[i])
    result = []
    for i in tot_list:
        if i in postings:
            continue
        else:
            result.append(int(i))
    f.close()
    return result


def find_postings(postings_file, info):
    '''
    find postings list in postings_file
    :param postings_file:
    :param info: D.term_dict[term]
    :return: postings list, type=list()
    '''
    start = int(info[1])
    end = int(info[2])
    f = open(postings_file, 'r')
    f.seek(start, 0)
    postings = f.read(end - start)
    f.close()
    postings = postings.strip().split(" ")
    result = []
    for i in postings:
        result.append(int(i))
    return result


def process_query(query, D, postings_file):
    '''
    analyze the given PRN, then calculate them one by one
    use of stack
    :param query: RPN of query
    :param D: generated by dictionary.txt
    :param postings_file: postings.txt
    :return: query result, type(list)
    '''
    stack = []
    for token in query:
        if token not in operator:
            if D.term_dict.__contains__(token) == False:
                # querying tokens don't belong to dictionary, return empty list
                stack.append([])
            else:  # contain
                info = D.term_dict[token]
                posting = find_postings(postings_file, info)
                stack.append(posting)
        elif token != "NOT":
            postings1 = stack.pop()
            postings2 = stack.pop()
            result = merge(postings1, postings2, token)
            stack.append(result)
        else:  # token = NOT, reverse the postings list
            op1 = stack.pop()
            result = reverse_postings(op1)
            stack.append(result)

    return stack[0]  # result


def result_compare(query_result, s):
    f = open(s)
    standard = f.read().splitlines()
    f.close()

    standard_result = []
    for i in range(len(standard)):
        s = standard[i].split(" ")
        tmp = []
        for j in range(len(s)):
            tmp.append(int(s[j]))
        standard_result.append(tmp)


    for i in range(len(query_result)):
        if query_result[i] == standard_result[i]:
            print("TRUE")
        else:
            print("False")
            print(query_result[i])
            print(standard_result[i])


def write_to_output_file(results_file, answer_list):
    r_file = open(results_file, 'w')

    for answer in answer_list:
        str_list = []
        for number in answer:
            str_list.append(str(number))
        write_info = " ".join(str_list) + "\n"
        r_file.write(write_info)

    r_file.close()


def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below
    q_file = open(queries_file, 'r')
    query_sent = q_file.read().splitlines()
    D = generate_dict(dict_file)
    query_result = []
    for q in query_sent:
        tokens = preprocess_sentence(q)
        tokens = delete_redundant_NOT(tokens)
        rpn = shunting_yard(tokens)
        result = process_query(rpn, D, postings_file)
        query_result.append(result)

    # result_compare(query_result, "output1.txt")
    q_file.close()

    write_to_output_file(results_file, query_result)



def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None:
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
