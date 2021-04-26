DICTIONARY="${1:-dictionary.txt}"
POSTINGS="${2:-postings.txt}"

python3 search.py -d "$DICTIONARY" -p "$POSTINGS" -q queries/q1.txt -o queries/o1.txt
python3 search.py -d "$DICTIONARY" -p "$POSTINGS" -q queries/q2.txt -o queries/o2.txt
python3 search.py -d "$DICTIONARY" -p "$POSTINGS" -q queries/q3.txt -o queries/o3.txt