import os
from math import sqrt

from block import Block
from tokenizer import tokenize_document
from query_util import calculate_weighted_tf

def create_blocks_and_find_lengths(doc_list):
    """
    Creates the initial blocks, finds the length and court importance
    of each document.

    Specifically, each of the files are then read and processed. 
    Moreover, doc ids, length information and court importance are 
    computed here.
    
    Returns a dictionary that maps each document ID to its length and
    court importance information. In particular, these values are stored
    as a tuple `(length, court_importance)`.

    NOTE: We assumed that `doc_list` is sorted by non-decreasing document
    IDs.
    """

    block = Block()
    lengths_and_court_importance = {}

    for doc in doc_list:
        doc_id = int(doc[0])
        content = doc[1:]
        (length, court_importance) = process_document(content, doc_id, block)
        lengths_and_court_importance[doc_id] = (length, court_importance)

    if not block.is_empty():
        block.save_dictionary()

    return lengths_and_court_importance

def process_document(content, doc_id, block):
    """
    Processes the content by tokenizing it and computes its length. 
    Then, update the given block and return the length and the court's
    importance of this document.
    """
    COURT_INDEX = 3
    tokens = tokenize_document(content, doc_id)
    court_importance = compute_court_importance(content[COURT_INDEX])
    length = compute_doc_vector(tokens)
    update_block(block, tokens)

    return (length, court_importance)
    
def compute_doc_vector(tokens):
    """
    Computes the length information using the given tokens.

    Returns `(scalar length, [(term, weighted tf)])`.
    """
    length = 0

    doc_vec = []
    for (term, _, freq, _) in tokens:
        weighted_tf = calculate_weighted_tf(freq)
        length += weighted_tf ** 2
        doc_vec.append((term, weighted_tf))

    # Sort by descending weighted tf
    doc_vec = sorted(doc_vec, key=lambda term_tf : term_tf[1], reverse=True)

    return (sqrt(length), doc_vec)

def update_block(block, tokens):
    """
    Adds the tokens to the given block as long as the 
    block is not full. Once the block is full, we will save the 
    dictionary that the block has built so far, and clear the block.
    """
    for token in tokens:
        if block.is_full():
            block.save_dictionary()
            block.clear()
        block.add(token)

"""
Courts that are given to be important and somehow important, respectively.
"""
MOST_IMPORTANT_COURTS=['SG Court of Appeal', 'SG Privy Council', 'UK House of Lords',
                       'UK Supreme Court', 'High Court of Australia', 'CA Supreme Court']

SOMEHOW_IMPORTANT_COURTS=['SG High Court', 'Singapore International Commercial Court',
                          'HK High Court', 'HK Court of First Instance', 'UK Crown Court',
                          'UK Court of Appeal', 'UK High Court', 'Federal Court of Australia',
                          'NSW Court of Appeal', 'NSW Court of Criminal Appeal',
                          'NSW Supreme Court']

def compute_court_importance(court_text):
    """
    Computes the court importance based on the `court_text`, the text that is 
    found in the 'court' zone.
    """
    if court_text in MOST_IMPORTANT_COURTS:
        return 2
    elif court_text in SOMEHOW_IMPORTANT_COURTS:
        return 1
    else:
        return 0
    