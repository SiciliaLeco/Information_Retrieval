### 1. Proofreading

1. compute_cosine_score in search_engine.py:

   ```
   for posting in posting_list:
       doc_id = posting[0]
       term_doc_freq = posting[1]
       doc_weight = calculate_weighted_tf(term_doc_freq)
   
       if doc_id not in scores:
           scores[doc_id] = 0
       scores[doc_id] += query_weight * doc_weight
   ```

posting_list is a dictionary of keys 'docIDs', values '[tf, position_list]'

ps. may need to sort keys when doing concurrent merge (bi-word, tri-word)

### 2. Query parsing

#### 2.1 Phrase + boolean e.g. "a b" AND c

1. find the sets of docIDs for phrase "a b" A and for word "c" B
2. intersect A and B = C
3. calculate cosine_similarity between free text **a b c** and docID set **C**
4. return topk docs in C by cosine_score if k is <= |C|
5. if k>|C|, then use cosine_similarity to rank the rest docs to return the following
k-|C| docs

#### 2.2 Phrase + free text e.g. "a b" c d

1. parse the posting lists of a and b concurrently to get the docIDs where **"a b"** appear and the number of times **"a b"** appears for the docIDs. Let c(**"a b"**, docX) denote the number of times **"a b"** occurring in docX.

2. Two ways to reformulate the scoring function

2.1 let phrase_score of docX for a particular phrase be the number of times this phrase occurring in docX divided by the total number of times this phrase occurring in all documents. (If multiple phrases, use the average)  

   score(q, d) = alpha*cosine_score(**a b c d**, docX) +  beta*c(**"a b"**, docX) /sum(c(**"a b"**, docX)) [scale it to 0-1]
   ps. can tune alpha, beta to adjust the weights of free text and phrases

2.2 consider the phrase as a word, calculate its term frequency in every doc, then calculate the cosine_similarity scores together with other words.

3. return topk docs by score(q, d)

### 3. Zone indexing

#### 3.1 assign tf to date_posted, title, court

content = ' '.join([content, date_posted\*alpha\*len(content) , title\*gamma\*len(content) , court\*beta\*len(content)])

alpha, beta, gamma: three decimal constants

### 4. Index  compression
#### 4.1 Compress dictionary or postings, not applicable
#### 4.2 Compress pickled files: lzma, brotli ... algorithms


