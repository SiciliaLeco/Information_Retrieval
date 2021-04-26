from math import log10, sqrt

def calculate_weighted_tf(tf):
    """
    Returns the weighted tf
    """
    if tf == 0:
        return 0
    
    return 1 + log10(tf)

def calculate_idf(N, df):
    """
    Returns the idf given the collection size (N) and 
    document frequency(df)
    """
    if df == 0:
        return 0
    
    return log10(N / df)

def calculate_weight(tf, N, df):
    """
    Returns the tf-idf weight
    """
    weighted_tf = calculate_weighted_tf(tf)
    idf = calculate_idf(N, df)
    return weighted_tf * idf

def intersect(list1, list2, curr_term=None, prev_term=None, is_strict=True):
    """
    Returns the intersection of two posting lists.

    If `curr_term` and `prev_term` are specified, the position list will be matched as well.
    """
    result = []
    i = 0
    j = 0

    len1 = len(list1)
    len2 = len(list2)

    skip_len1 = int(sqrt(len1))
    skip_len2 = int(sqrt(len2))

    while i < len1 and j < len2:
        doc1 = get_doc_id(list1[i])
        doc2 = get_doc_id(list2[j])

        if doc1 == doc2:
            # For phrase queries
            if prev_term is not None:
                prev_positions = list1[i][1][prev_term][1]
                curr_positions = list2[j][1][curr_term][1]
                new_phrase = " ".join([prev_term, curr_term])
                prev_len = len(prev_term.split())
                (phrase_tf, phrase_pos) = get_token_info_for_phrase(prev_len, prev_positions, curr_positions)
                phrase_info = [doc1, {
                    new_phrase: (phrase_tf, phrase_pos)
                }]
                if phrase_tf != 0:
                    result.append(merge_doc_info(list1[i], phrase_info))

                    if is_strict:
                        result.append(merge_doc_info(list1[i], list2[j]))
                
                if not is_strict:
                    result.append(merge_doc_info(list1[i], list2[j]))
            else:
                result.append(merge_doc_info(list1[i], list2[j]))
            
            i += 1
            j += 1
        elif doc1 < doc2:
            skip_ptr = get_skip_pointer(len1, skip_len1, i)
            if skip_ptr is not None and get_doc_id(list1[skip_ptr]) <= doc2:
                i = skip_ptr
            else:
                i += 1
        else:
            skip_ptr = get_skip_pointer(len2, skip_len2, j)
            if skip_ptr is not None and get_doc_id(list2[skip_ptr]) <= doc1:
                j = skip_ptr
            else:
                j += 1
    
    return result

def union(list1, list2):
    """
    Returns the union of two posting lists.
    """
    result = []
    i = 0
    j = 0

    len1 = len(list1)
    len2 = len(list2)

    while i < len1 and j < len2:
        doc1 = get_doc_id(list1[i])
        doc2 = get_doc_id(list2[j])

        if doc1 == doc2:
            result.append(merge_doc_info(list1[i], list2[j]))
            i += 1
            j += 1
        elif doc1 < doc2:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1

    while i < len(list1):
        result.append(list1[i])
        i += 1

    while j < len(list2):
        result.append(list2[j])
        j += 1

    return result

def get_token_info_for_phrase(prev_len, prev_positions, curr_positions):
    """
    This method is used for phrase search.

    Returns the intersection of two position list. A match is found when a 
    position from prev_position + prev_len is the same as another position 
    from curr_positions.

    Returns the number of matches and the starting position of the matches.
    """
    count = 0
    pos = []

    i = 0
    j = 0

    len1 = len(prev_positions)
    len2 = len(curr_positions)

    skip_len1 = int(sqrt(len1))
    skip_len2 = int(sqrt(len2))

    while i < len1 and j < len2:
        pos1 = prev_positions[i]
        pos2 = curr_positions[j]

        if pos1 + prev_len == pos2:
            pos.append(pos1)
            count += 1
            i += 1
            j += 1
        elif pos1 + prev_len < pos2:
            skip_ptr = get_skip_pointer(len1, skip_len1, i)
            if skip_ptr is not None and prev_positions[skip_ptr] + prev_len <= pos2:
                i = skip_ptr
            else:
                i += 1
        else:
            skip_ptr = get_skip_pointer(len2, skip_len2, j)
            if skip_ptr is not None and curr_positions[skip_ptr] <= pos1 + prev_len:
                j = skip_ptr
            else:
                j += 1

    return (count, pos)

# Precondition: both target and source should have same docID
def merge_doc_info(target, source):
    """
    Merge two doc_info.

    Structure of doc_info: 
    [
        doc_id,
        {
            term: (tf, [position]),
            ...
        }
    ]
    """
    doc_id = target[0]
    target_doc_info = target[1]
    source_doc_info = source[1]
    target_doc_info.update(source_doc_info)
    return [doc_id, target_doc_info]

def get_doc_info(term, posting, prev_doc_id):
    """
    Construct doc info for a posting.
    """
    (gap, tf, positions) = posting
    return [prev_doc_id + gap, {
        term: (tf, positions)
    }]

def get_skip_pointer(max_len, skip_len, i):
    """
    Calculates skip pointer index on the fly.
    """
    if i % skip_len == 0 and (i + skip_len) < max_len and skip_len > 1:
        return i + skip_len
    else:
        return None

def get_doc_id(doc_info):
    """
    Returns the docID from doc_info.
    """
    return doc_info[0]

def is_phrase(term):
    """
    Returns True if the given term is a phrase, otherwise False.
    """
    return len(term.split()) > 1
