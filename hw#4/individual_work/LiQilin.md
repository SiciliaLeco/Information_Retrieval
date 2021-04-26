### Li Qilin's work

#### Apr 18th

1. write new function in `index.py`, to call the functions.

2. modify `create_blocks_and_find_lengths()` in `create_blocks.py`, to suit the input format for hw4's dataset.

3. modify `count_tokenized_words()` in `tokenizer.py`, ad the positional information to each term. The format for the output dictionary `tokenized_word_freqs` becomes:

   ```
   dict[term]=[term_frequency, [position1, position2,...]]
   ```

4. modify `create_tokens_w_tf()`  in `tokenizer.py`, new variable freq_position contains both frequency and positon list for a term.

5. Modify `add()` in `block.py`, a term's info contains the position list for one document.

6. Use of pandas library.



#### Apr 19th

1. `search_engine.py`, modify `compute_cosine_score()`:

   ```python
   tf = tf_position[0]
   position_list = tf_position[1]
   ```

2. `search_engine.py`, implement a new function `phrasal_query()`, to do with phrasal query problems.

3. change stored format of Postings.txt:

for each term:
```
postings[doc_id] = (doc_frequency, position_index)
```

#### Apr 20th