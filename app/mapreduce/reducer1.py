import sys

current_word = None
current_doc = None
total = 0

for line in sys.stdin:
    parts = line.strip().split('\t')
    if len(parts) < 3:
        sys.stderr.write(f"Skipping line with {len(parts)} fields: {line}\n")
        continue
    word, doc_id, count = parts[0], parts[1], int(parts[2])

    # If we have a current key and it differs from the new one, output
    if (current_word == word and current_doc == doc_id):
        total += count
    else:
        # Output the previous key's total
        if current_word is not None:
            print(f"{current_word}\t{current_doc}\t{total}")
        # Start a new key
        current_word = word
        current_doc = doc_id
        total = count

# Output the last key
if current_word is not None:
    print(f"{current_word}\t{current_doc}\t{total}")
