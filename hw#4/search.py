#!/usr/bin/python3

import sys
import getopt

from search_engine import SearchEngine

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q query-file -o output-file-of-results")

def run_search(dict_file, postings_file, query_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given query file and output the results to a file
    """

    query_file = open(query_file, "r")
    results_file = open(results_file, "w")

    engine = SearchEngine(dict_file, postings_file)

    query = query_file.readline()

    (result, scores) = engine.run_query(query)

    # TODO: remove (evaluation code)
    print("----------START-----------------")
    print("Query: ", query)
    print("Output size", len(result))

    relevant_docs = []
    for line in query_file:
        relevant_docs.append(int(line))
    
    print("Positions of relevant docs")
    indices = []
    for doc in relevant_docs:
        idx = result.index(doc) if doc in result else -1
        if idx != -1:
            indices.append(idx)
        print(doc, idx)
    
    # print_doc(relevant_docs[0])

    # print()
    # print("Returned top K docs (not in relevant docs)")
    # for i in range(1):
    #     if i >= len(result):
    #         break
    #     if i in indices:
    #         continue
    #     doc = result[i]
    #     print(doc, i, scores[doc])
    #     # print_doc(doc)
    
    # Calculation
    if len(indices) == 0:
        precision = 0
    else:
        precision = len(indices) / (max(indices) + 1)
    
    if len(relevant_docs) == 0:
        recall = 0
    else:
        recall = len(indices) / len(relevant_docs)
    
    if precision == 0 and recall == 0:
        f2 = 0
    else:
        f2 = (5 * precision * recall) / (4 * precision + recall)

    print()
    print("Precision", precision)
    print("Recall", recall)
    print("F2 measure", f2)
    print("-----------END-----------------")

    # Write to results file
    if len(result) == 0:
        results_file.write("\n")
    else:
        results_file.write(" ".join(map(str, result)))
        
    query_file.close()
    results_file.close()

dictionary_file = postings_file = file_of_query = output_file_of_results = None

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
        file_of_query = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_query == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_query, file_of_output)
