from nltk.corpus import wordnet as wn
from tokenizer import tokenize_word_enhanced

def query_expansion(term, dictionary):
    """
    input type = str
    retrieve the term with highest weight, insert into
    this function and find its expanded query terms
    """
    word_net = wn.synsets(term)
    expanded_terms = []
    for net in word_net:
        lemma_terms = net.lemma_names()
        for lemma_term in lemma_terms:
            lemma_term = tokenize_word_enhanced(lemma_term)
            if lemma_term not in expanded_terms:
                expanded_terms.append(lemma_term)

    # examine whether the new term is in the dictionary
    return_terms = []
    for expanded_term in expanded_terms:
        if expanded_term in dictionary.keys() and expanded_term != term:
            return_terms.append(expanded_term)

    if len(return_terms) >= 2:
        return return_terms[:2]
    else:
        return return_terms