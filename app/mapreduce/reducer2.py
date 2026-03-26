import sys

current_word = None
total = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        sys.stderr.write(f"Skipping line with {len(parts)} fields: {line}\n")
        continue
    word, count = parts[0], parts[1]

    try:
        count = int(count)
    except ValueError:
        sys.stderr.write(f"Skipping non‑numeric count: {count}\n")
        continue

    if current_word == word:
        total += count
    else:
        if current_word is not None:
            print(f"{current_word}\t{total}")
        current_word = word
        total = count

if current_word is not None:
    print(f"{current_word}\t{total}")
