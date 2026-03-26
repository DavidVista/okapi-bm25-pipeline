import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) < 3:
        sys.stderr.write(f"Skipping line with {len(parts)} fields: {line}\n")
        continue
    word, doc_id = parts[0], parts[1]
    # Output (word, 1) - each (word, doc_id) contributes exactly once
    print(f"{word}\t1")
