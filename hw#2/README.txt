This is the README file for A0229596L-A0228878H's submission
email: e0680464@u.nus.edu  e0675841@u.nus.edu

== Python Version ==

We're using Python Version <3.7.6> for this assignment.

== General Notes about this assignment ==

1. We implement SPIMI algorithm and n-way merge to generate docID.txt, dictionary.txt, and postings.txt during the indexing stage.
 
1) Generate docID.txt for all sorted docIDs and blkX.txt files for all blocks
   We store all sorted docIDs to docID.txt. We parse through the documents with file names sorted and hash the tokens parsed to a dictionary of format {token: [doc_freq, posting_list]}. In addition to the tokenization, stemming, and case-folding required, we also choose to omit the punctuations and keep the numbers since many numbers are still meaningful such as the episode numbers and it's difficult to distinguish the meaningful numbers from the meaningless ones.
   We consider the memory size occupied as the number of docIDs we have added to the dictionary’s posting lists. Once the memory is full or we have finished parsing all documents, we write the dictionary with terms (keys) sorted to a block represented by a file blkX.txt and flush the dictionary.

2) Merge blkX.txt files to build dictionary.txt and posting.txt
   We implement n-way merge for blkX.txt files considering two-way merge may still need the memory to accommodate posting lists of all terms in the documents.
   Since we need to guarantee that the merged result of the decent-sized chunks of each block lies in the final output, we set the set of terms starting with a particular character in the ASCII code table from 21 to 126 (decimal) as the basic unit, and merge the terms by the largest multiple of the basic units within the memory. For one merge, since the dictionaries to be merged are within the memory size, we will do a simple merge to consecutively merge from block1 to blockN. 
   Then we write the corresponding information in the merged dictionary to dictionary.txt and posting.txt every time after merge.


2. We read the dictionary from dictionary.txt, process the queries, perform required operations of ANDs, ORs, NOTs with the dictionary to find the corresponding posting lists in postings.txt

   Before searching query results, we first need to load dictionary.txt into memory. We create a class called “dictionary” to store the term information (document frequency and pointers related to its postings list’s position). As for the postings list, we load them from postings.txt when needed.

1) Preprocess query sentences and build Reverse Polish Notations (RPNs)
   We first preprocess the query sentences, using NLTK tools to make the tokens regularized. The related function is “preprocess_sentence”. Notice that in some query sentences, multiple NOTs are contained and would cause trouble when searching, so we create a “delete_redundant_NOT” function to resolve this. 
   After getting the sequence of query sentences, we insert the output sequence into the  “shunting_yard” function to find the RPN of the query. The RPN can be used to calculate the results of a query sentence efficiently. We pop the top two elements to be operated once we encounter a binary operator(“AND”, “OR”) or the top one once we encounter a unary operator(“NOT”).

2) Process the query by stack
   Before getting the final results, we need to consider different operations on AND, NOT and OR. That is: for “NOT A”, we need to find out all postings that don’t belong to A’s postings list, so we build a “reverse_postings” to get the new postings. If we meet “NOT” when processing queries, we pop the last term from the stack and reverse its postings.
   For “A AND B”, as told in the lecture, we can apply to skip pointers (evenly distributed) to improve the efficiency of our algorithm. Since we use the random access structure lists, we don't need to store the skip pointers separately with extra space, instead we check whether there exist skip pointers based on the index. Nevertheless, we can’t use skip pointers on “NOT” or “OR” operations because these two require going through every element in postings list, thus applying skip pointers would neglect some docIDs, leading to incorrect results. After exhausting all elements in the stack, we output the query result, and write it to the output file.
   Noted that for punctuations that appear in the query sentences, since we have deleted punctuations when building the dictionary, so when processing query sentences, we set the postings list for punctuations as empty list. (postings = list())

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

index.py: implement SPIMI algorithm and n-way merge to generate docID.txt, dictionary.txt, postings.txt
search.py: implement searching process for the query sentences
dictionary.txt: store terms, document frequencies, posting_list pointers (start_byte and end_byte)
postings.txt: posting lists corresponding to the terms in dictionary.txt of the same lines
docID.txt: all docIDs in sorted order
test1.txt: sample queries
output1.txt: correct anwers to the sample queries
blkX.txt (X from 0 to 9): each line of term, freq, posting lists for blockX
README.txt: a general overview of our work
ESSAY.txt: our answers to the essay questions

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] We, A0229596L-A0228878H, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions. 

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

[1] shunting yard algorithm implementation: https://old-panda.com/2020/11/29/shunting-yard-algorithm/

[2] test dataset for search part: https://github.com/fzdy1914/HW2-Queries
