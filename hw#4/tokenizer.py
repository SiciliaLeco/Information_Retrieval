from nltk import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import re
import string

# title, content, date_posted, court
zone_weights = [3, 1, 1, 2]

stops = stopwords.words("english")+[chr(i) for i in range(ord('a'), ord('z')+1)]\
        + [chr(i) for i in range(ord('A'), ord('Z')+1)]

stemmer = PorterStemmer()

def tokenize_document(content, doc_id):
    """
    Tokenizes the given `content`, an array with the format [title, content, 
    date_posted, court]. 
    
    Returns a list of (token, doc_id, weight, positions) tuples.
    """
    tokens_by_zone = tokenize_content(content)
    token_infos = get_token_infos(tokens_by_zone)
    document_token_info = to_token_info_list(token_infos, doc_id)

    return document_token_info

def get_token_infos(tokens_by_zone):
    """
    Gets the token infos for the tokens in each zone. 
    
    Every token is mapped to an array of length 2 such that the first 
    element contains the weight associated with the token in this 
    document, and the second element is a list of the token's positions 
    in the document.

    The weight is computed based on the frequency of the token and
    which zone the token is located. It can be viewed as a substitute for
    term frequency.

    Returns a dictionary that maps each token to its information.
    """
    token_infos = {}

    idx = -1
    for zone_index, tokens in enumerate(tokens_by_zone):
        idx += 1 # introduce an artificial gap
        for token in tokens:
            if token_infos.get(token) == None:
                token_infos[token] = [zone_weights[zone_index], [idx]]
            else:
                token_infos[token][0] += zone_weights[zone_index]
                token_infos[token][1].append(idx)
            idx += 1

    return token_infos

def to_token_info_list(token_infos, doc_id):
    """
    Converts a dictionary of token information `token_infos` to a list 
    for the document with `doc_id`.

    Every token information is a tuple such that 
    `(token, doc_id, weight, positions)`, where `positions` is a list of
    integers indicating the position where the term appeared.
    """
    token_info_list = []

    for token, token_info in token_infos.items():
        token = (token, doc_id, token_info[0], token_info[1])
        token_info_list.append(token)

    return token_info_list

def tokenize_query(query):
    """
    Tokenizes the given query by splitting it by whitespace
    and tokenizing each word and phrase.

    Returns a dictionary of tokens that are mapped to their
    frequency count.

    NOTE: Any appearances of "AND"s are ignored.
    """
    words = query.split()
    words = [word for word in words if word != "AND"]

    ongoing_phrase = False
    curr_phrase = []
    token_info = {}

    for word in words:
        token = tokenize_word_enhanced(word)
        if token is None:
            continue

        if word[0] == '"':
            ongoing_phrase = True

        if ongoing_phrase:
            curr_phrase.append(token)

        if word[-1] == '"':
            ongoing_phrase = False
            token = " ".join(curr_phrase)
            curr_phrase = []
        
        if not ongoing_phrase:
            if token not in token_info:
                token_info[token] = 1
            else:
                token_info[token] += 1
    
    return token_info

def tokenize_boolean_query(query):
    """
    Tokenizes the given query by first splitting by whitespace, 
    then tokenize each word.

    Returns a list of tokens.
    """
    tokens = tokenize_query(query)
    tokens_set = set()

    for token in tokens:
        tokens_set.add(token)
    
    return list(tokens)

def tokenize_content(content):
    """
    Tokenizes the given content by applying sentence tokenization 
    followed by word tokenization prodvided by nltk library and our 
    own preprocessing heuristics (see `tokenize_word_enhanced`). 

    Returns an array of all tokens by zone such that `tokens_by_zone[i]` is 
    a list of tokens in the i-th zone.  Moreover, the token in each `tokens_by_zone[i]` is
    in sequential order. To be specific, `i` = 0, 1, 2 and 3 represent 'title', 'content',
    'date posted' and 'court' respectively.
    """
    tokens_by_zone = []   

    for text in content:
        text = remove_non_ascii_characters(text)
        text = remove_html_tags(text)
        sentences = sent_tokenize(text)
        zone_tokens = []
        for sentence in sentences:
            words = word_tokenize(sentence)
            for word in words:
                token = tokenize_word_enhanced(word)
                if token is None:
                    continue
                zone_tokens.append(token)
        tokens_by_zone.append(zone_tokens)

    return tokens_by_zone

def tokenize_word_enhanced(word):
    """
    Tokenize the given word by applying case folding and stemming.
    Returns `None` if the given word is a punctuation
    """
    word = word.strip(string.punctuation)

    # not consider a single letter and stopwords
    if len(word) == 0 or word in stops:
        return None
    return stemmer.stem(word.lower())


def remove_non_ascii_characters(text):
    """
    Removes non-ascii characters from `text` and returns the result.
    """
    cleanr = re.compile("([^\x00-\x7F])+")
    clean_text = re.sub(cleanr, ' ', text)
    return clean_text

def remove_html_tags(raw_html):
    """
    Removes html tags from `text` and returns the result.
    """
    cleanr = re.compile('<.*?>')
    clean_text = re.sub(cleanr, '', raw_html)
    return clean_text
