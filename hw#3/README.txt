This is the README file for A0229596L-A0228878H's submission
email: e0680464@u.nus.edu  e0675841@u.nus.edu

== Python Version ==

We're using Python Version <3.7.6> for this assignment.

== General Notes about this assignment ==

Our work is generally divided into two parts: indexing and searching.
1. Index
1) For the indexing part, we first read all the files in the training dataset. When we read each file, we preprocess the
strings by word_tokenize(),  lower(), Porter stemming, and finally punctuations (string.punctuation) removal. Then we go
to count the term frequency for each document in a dictionary by which we get the LENGTH for each document. We
temporarily store the terms and their information (document frequency, posting lists with term frequencies) in the
dictionary, then finally write the dictionary into dictionary.txt and postings.txt.
2) The definition for LENGTH is, for each term in a particular document, we sum up each term frequency to the power of 2
and then calculate the square root of this sum to get the length needed.
3) Finally, we write our results to 3 files: dictionary.txt, postings.txt, length.txt.
The format for a posting in the postings.txt is [docID1,Term_freq1 docID2, Term_freq2...].
The format for a term in the dictionary.txt is [term doc_freq,postings_start_ptr,postings_end_ptr].
postings_start(end)_ptr are the positions in the postings.txt which indicate the start and end positions of each posting.
The format for length.txt is [N\n docID1 length1\n docID2 length2...]. The parameter N is the total number of the documents.

2. Search
1) Generate a dictionary from dictionary.txt to store document frequency, start location, and end location for every
term's posting list. Get the number of documents and the document lengths from length.txt.
2) Preprocess each query similar to the index preprocessing. We apply case folding before stemming since we found that
stemming directly on words containing upper case letters may cause some inaccuracy. For example, 'News' is stemmed to 'new',
but 'news' is stemmed to 'news'. If the query is '' or no token left after preprocessing, return an empty query result.
Afterwards, we generate a dictionary storing the frequencies of the preprocessed tokens.
3) If the preprocessed query is composed of only one token, we only consider term frequency of the documents since the
weight of the only one query term x, tf(x)*idf(x), is always the same across all documents. Thus, we parse the posting
list of x, calculate the score for every document, and normalize by the document length. (We don't divide the scores by
the query length since it's the same across all documents, which won't affect the document ranking)
If the preprocessed query is composed of more than one tokens, we calculate the weight for each query token.
Then we parse the posting list for every query token, calculate the scores for all documents, and normalize them by
the document lengths.
4) We build a heap for (-score,docID), apply heap sort to get the top 10 documents first by scores descending, and
further break the tie by docID ascending.




== Files included with this submission ==

index.py: parse the documents and generate dictionary.txt, postings.txt, length.txt
search.py: use dictionary.txt, postings.txt, length.txt, and the provided queries to generate the output file to store
the top 10 relevant documents for all queries
dictionary.txt: store terms, document frequencies, and corresponding postings' start and end locations in postings.txt
postings.txt: store docIDs and term frequencies for all terms' postings
length.txt: store the number of documents, docIDs, and corresponding document lengths
query1.txt, query2.txt: tested queries
out1.txt, out2.txt: tested results
README.txt: general information of the program


== Statement of individual work ==

[ x ] We, A0229596L-A0228878H, certify that we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, we
expressly vow that we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

The class piazza forum to obtain test cases for queries:
https://piazza.com/class/kjmny91pkrx6ag?

