import heapq
from math import sqrt

from io_util import load_lengths_and_dictionary, load_posting_list, load_term_info
from query_util import calculate_weight, calculate_weighted_tf, intersect, is_phrase, calculate_idf, union
from tokenizer import tokenize_query, tokenize_boolean_query
from query_expansion import query_expansion

# Relevance feedback
K_DOCS = 10 # Number of relevant docs
K_TERMS = 5 # Number of most frequent terms
ALPHA = 1
BETA = 0.75

# Phrase queries
PHRASE_WEIGHT = 0.95

# Weight of original term vs expanded term
EXPANSION_WEIGHT = 5

# Quality score
QUALITY_WEIGHT = 0
QUALITY_SCORE = {
    0 : 0.7,
    1 : 0.9,
    2 : 1
}

class SearchEngine:
    """
    Represents a search engine which supports free text queries and boolean queries over
    the specified dict_file and postings_file
    """

    def __init__(self, dict_file, postings_file):
        # lengths is actually lengths_court_importance of format {docID: (length, court_importance)}
        # courtImportance: 0, 1, 2 indicating importance from small to large
        (self.lengths, self.dictionary) = load_lengths_and_dictionary(dict_file)
        self.postings_file = postings_file
        self.num_of_docs = len(self.lengths)
        
        self.phrase_dict = {} # Temporary dict to store document frequency for queries phrases
        self.original_query_vec = {}
        self.query_vec = {}
        self.query_weight_set = False # Initially query weight is initialised to tf of each term in the query

    def run_query(self, query):
        """
        Runs the given query and returns all the relevant docs
        """
        is_boolean_query = "AND" in query
        is_phrasal_query = '"' in query
        
        scores = {}
        if is_boolean_query: 
            query_terms = tokenize_boolean_query(query)
            expanded_query_terms = self.expand_boolean_query(query_terms)
            optimized_query_terms = self.optimize_query_order(expanded_query_terms)
            docs = self.handle_boolean_query(optimized_query_terms)

            self.query_vec = {}
            for or_terms in expanded_query_terms:
                assert len(or_terms) > 0
                original_term = or_terms[0]
                if original_term not in self.query_vec:
                    self.query_vec[original_term] = 0
                # Assign more weights to original term
                self.query_vec[original_term] += EXPANSION_WEIGHT
                for or_term in or_terms[1:]:
                    if or_term not in self.query_vec:
                        self.query_vec[or_term] = 0
                    self.query_vec[or_term] += 1

            # Exact match
            scores = self.compute_cosine_score(self.query_vec, docs, phrase_weight=1)
            result = self.get_ranked_results(scores)

            # Insufficient docs for query refinement
            if len(result) < K_DOCS:
                new_scores = self.compute_cosine_score(self.query_vec)
                new_result = self.get_ranked_results(new_scores, k=K_DOCS - len(result), excluding=scores)
                result += new_result
                # Copy scores of newly added documents
                for doc_id in new_result:
                    scores[doc_id] = new_scores[doc_id]

        else: # Free text query
            self.query_vec = tokenize_query(query)
            self.query_vec = self.expand_free_text_query(self.query_vec)
            scores = self.compute_cosine_score(self.query_vec)
            result = self.get_ranked_results(scores, k=K_DOCS)

            # Keep the scores for top K docs
            temp_scores = {}
            for doc_id in result:
                temp_scores[doc_id] = scores[doc_id]
            scores = temp_scores

        # Query refinement
        self.query_vec = self.refine_query_with_relevance_feedback(self.query_vec, result[:K_DOCS])
        if is_boolean_query or is_phrasal_query: # retain initial rankings
            new_scores = self.compute_cosine_score(self.query_vec)
            new_result = self.get_ranked_results(new_scores, excluding=scores)
            result += new_result
            scores.update(new_scores)
        else:
            scores = self.compute_cosine_score(self.query_vec)
            result = self.get_ranked_results(scores)

        return (result, scores)
    
    def optimize_query_order(self, query_terms):
        """
        Returns a sorted list of query terms by increasing document frequency.
        The query terms might contain phrases.
        """
        doc_freqs = {}
        for or_terms in query_terms:
            if len(or_terms) == 1:
                term = or_terms[0]
                if is_phrase(term):
                    if term in self.phrase_dict:
                        doc_freq = len(self.phrase_dict[term])
                    else:
                        # Estimate the df of a phase to be min of the df of the individual words within the phrases
                        doc_freq = self.num_of_docs
                        phrase_words = term.split()
                        for phrase_word in phrase_words:
                            term_info = load_term_info(phrase_word, self.dictionary)
                            if term_info is None:
                                doc_freq = 0
                                continue

                            doc_freq = min(doc_freq, term_info.doc_freq)
                else:
                    term_info = load_term_info(term, self.dictionary)
                    if term_info is None:
                        doc_freq = 0
                    else:
                        doc_freq = term_info.doc_freq
            else:
                # Estimate the df to be the sum of df of each or_term
                doc_freq = 0
                for or_term in or_terms:
                    term_info = load_term_info(or_term, self.dictionary)
                    if term_info is None:
                        continue
                    else:
                        doc_freq = max(doc_freq + term_info.doc_freq, self.num_of_docs)
            doc_freqs[" ".join(or_terms)] = doc_freq
        
        return sorted(query_terms, key=lambda term:doc_freqs[" ".join(or_terms)])

    def get_posting_list(self, query_term, is_strict=True):
        """
        Returns the posting list of the query term. 

        Structure of posting list:
        [
            [doc_id, {
                term: [tf, positions],
                ...
            }],
            ...
        ]
        
        The query_term can either be a phrase or a single term. 
        If the query term is a single term, its posting list is retrieved from 
        the postings file. 
        If the query term is a phrase, a phrase search is excuted to produce the 
        posting list for the phrase. 
        
        When is_strict is set to True, the returned posting list only contains docs 
        with the exact phrase. When is_strict is set to False, the returned posting 
        list also contains docs without the exact phrase but with words within the phrase.
        """
        phrase_words = query_term.split()
        if len(phrase_words) == 1: # Single term retrieval
            return load_posting_list(query_term, self.dictionary, self.postings_file)
        else: # Phrase query
            if query_term in self.phrase_dict:
                return self.phrase_dict[query_term]
            
            first_word = phrase_words[0]
            curr_result = self.get_posting_list(first_word)
            curr_phrase = [first_word]
            
            for phrase_word in phrase_words[1:]:
                # No need to continue if the current result is already empty
                if len(curr_result) == 0:
                    break

                posting_list = self.get_posting_list(phrase_word)
                curr_result = intersect(curr_result, posting_list, phrase_word, " ".join(curr_phrase), is_strict)
                curr_phrase.append(phrase_word)
            
            # Cache posting list for phrase
            self.phrase_dict[query_term] = curr_result

            return curr_result
    
    def get_document_frequency(self, term):
        """
        Returns the document frequency of the given term.
        The term can be either a phrase or a term.
        If it is a phrase, it only returns the document frequency
        when the phrase in present in phrase_dict. 
        (You must retrieve its posting list before calling this method)
        """
        if is_phrase(term):
            if term not in self.phrase_dict:
                return None
            
            return len(self.phrase_dict[term])
        else:
            term_info = load_term_info(term, self.dictionary)
            if term_info is None:
                return None
            
            return term_info.doc_freq
    
    def merge_posting_lists(self, terms):
        if len(terms) == 1:
            return self.get_posting_list(terms[0], is_strict=False)
        else:
            curr_result = []
            for term in terms:
                posting_list = self.get_posting_list(term, is_strict=False)
                curr_result = union(curr_result, posting_list)
            return curr_result


    def handle_boolean_query(self, query_terms):
        """
        Executes AND operations over the given query_terms and 
        returns a posting list where each doc contains each of the
        term in query_terms. Note: relaxed posting lists for phrases
        are used.
        """
        if len(query_terms) == 0:
            return []
        
        first_term = query_terms[0]
        curr_result = self.merge_posting_lists(first_term)
        curr_phrase = [first_term]
        
        for term in query_terms[1:]:
            posting_list = self.merge_posting_lists(term)
            
            # Ignore non-existing term
            if len(posting_list) == 0:
                continue
            
            curr_result = intersect(curr_result, posting_list)
        
        return curr_result
    
    def expand_free_text_query(self, query_vec):
        """
        Expand the given query vector with WordNet.
        """
        expanded_query_vec = {}
        for term, tf in query_vec.items():
            expanded_query_vec[term] = tf * EXPANSION_WEIGHT
            if is_phrase(term):
                continue
            expanded_terms = query_expansion(term, self.dictionary)
            for expanded_term in expanded_terms:
                if expanded_term not in expanded_query_vec:
                    expanded_query_vec[expanded_term] = 0
                expanded_query_vec[expanded_term] += 1
        
        return expanded_query_vec
    
    def expand_boolean_query(self, query_terms):
        """
        Expand the given query terms with WordNet.
        """
        expanded_query_terms = []
        for term in query_terms:
            if is_phrase(term):
                expanded_query_terms.append([term])
                continue
            
            or_terms = []
            or_terms.append(term)
            expanded_terms = query_expansion(term, self.dictionary)
            for expanded_term in expanded_terms:
                or_terms.append(expanded_term)
            expanded_query_terms.append(or_terms)
        
        print(expanded_query_terms)
        return expanded_query_terms
    
    def refine_query_with_relevance_feedback(self, query_vec, relevant_docs):
        """
        Refine the given query vector with relevance feedback using 
        the given relevant documents.
        """
        modified_query_vec = {}

        doc_vec_sum = {}
        for doc_id in relevant_docs:
            doc_vec = self.lengths[doc_id][0][1]

            count = 0

            # Sort by descending tf-idf
            doc_vec = sorted(doc_vec, key=lambda term_tf : term_tf[1] * calculate_idf(self.num_of_docs, self.get_document_frequency(term_tf[0])), reverse=True)

            for term, weighted_tf in doc_vec:
                if count > K_TERMS:
                    break
                if term not in doc_vec_sum:
                     doc_vec_sum[term] = 0
                     count += 1
                tf_idf = weighted_tf * calculate_idf(self.num_of_docs, self.get_document_frequency(term))
                doc_vec_sum[term] += BETA * tf_idf / len(relevant_docs)
        
        for term, weight in  doc_vec_sum.items():
             if weight > 0:
                modified_query_vec[term] = weight
        
        for term, weight in query_vec.items():
            if term not in modified_query_vec:
                modified_query_vec[term] = 0
            modified_query_vec[term] += ALPHA * weight

        return modified_query_vec

    def compute_cosine_score(self, query_vec, documents=None, phrase_weight=PHRASE_WEIGHT):
        """
        Compute cosine similarity score of query_vec with the given documents.
        If no documents are specified, the scores for all documents are computed.

        The phrase_weight value determines how much weight is given to docs with exact 
        phrase in the query vec.
        """
        scores = {}
        for term, query_weight in query_vec.items():
            if documents is None: # Free text queries
                posting_list = self.get_posting_list(term, is_strict=False)
            else: # Boolean queries 
                posting_list = documents

            doc_freq = self.get_document_frequency(term)

            if doc_freq is None:
                continue
            
            if not self.query_weight_set:
                self.original_query_vec[term] = query_weight
                query_weight = calculate_weight(query_weight, self.num_of_docs, doc_freq)
                query_vec[term] = query_weight

            for doc_id_info in posting_list:
                doc_id = doc_id_info[0]
                doc_info = doc_id_info[1]
                if term in doc_info:
                    (term_freq, _) = doc_info[term]
                else:
                    term_freq = 0
                
                phrase_words = term.split()
                doc_weight = 0

                for phrase_word in phrase_words:
                    # Term freq refers to the tf of the phrase
                    # Phrase word tf referts to the tf of one word within the phrase
                    if phrase_word not in doc_info:
                        phrase_word_tf = 0
                    else:
                        (phrase_word_tf, _) = doc_info[phrase_word]
                    adjusted_tf = term_freq + (phrase_word_tf - term_freq) * (1 - phrase_weight)
                    doc_weight += calculate_weighted_tf(adjusted_tf)

                if doc_id not in scores:
                    scores[doc_id] = 0
                scores[doc_id] += query_weight * doc_weight

            if not self.query_weight_set:
                self.query_weight_set = False

        for doc_id, similarity_score in scores.items():
            quality_score = QUALITY_SCORE[self.lengths[doc_id][1]]
            doc_len = self.lengths[doc_id][0][0]
            scores[doc_id] = QUALITY_WEIGHT * quality_score + (1 - QUALITY_WEIGHT) * similarity_score / doc_len
        
        return scores

    def get_ranked_results(self, scores, k=None, threshold=None, excluding=None):
        """
        Returns the top k docIDs with highest cosine similarity scores.
        If k is not specified, return all docIDS.
        If there are fewer than k docIDs in the given scores, return all
        relevant docIDs. The returned array is sorted by their similary scores, 
        then by docIDs. 
        """
        result = []

        heap = self.convert_to_heap(scores)
        while len(heap) > 0:
            if k is not None and len(result) >= k:
                break
            
            pair = heapq.heappop(heap)

            if threshold is not None and pair.score < threshold:
                break

            if excluding is not None and pair.doc_id in excluding:
                continue

            result.append(pair.doc_id)
        
        return result
    
    def convert_to_heap(self, scores):
        """
        Convert the scores dictionary to a heap which each (docID, score) pair is 
        sorted by score in descending order, then by quality in ascending order
        """
        pairs = []
        for doc_id, score in scores.items():
            if score > 0:
                quality = self.lengths[doc_id][1]
                pairs.append(DocScorePair(doc_id, score, quality))

        # Transform list of doc-score pairs into a heap, in-place, in linear time
        heapq.heapify(pairs)

        return pairs


class DocScorePair(object):
    """
    Represents a (docID, score) pair which can be compared with "<" operator
    """
    def __init__(self, doc_id, score, quality):
        self.doc_id = doc_id
        self.score = score
        self.quality = quality

    def __lt__(self, other):
        # If the scores are the same, sort by docID
        if self.score == other.score:
            return self.quality > other.quality
        else:
            return self.score > other.score
