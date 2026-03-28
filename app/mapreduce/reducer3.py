import sys

current_doc = None
current_title = None
total = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 3:
        sys.stderr.write(f"Skipping line with {len(parts)} fields: {line}\n")
        continue
    doc_id, doc_title, count = parts[0], parts[1], parts[2]

    try:
        count = int(count)
    except ValueError:
        sys.stderr.write(f"Skipping non‑numeric count: {count}\n")
        continue

    if current_doc == doc_id:
        total += count
    else:
        if current_doc is not None:
            print(f"{current_doc}\t{current_title}\t{total}")
        current_doc = doc_id
        current_title = doc_title
        total = count

if current_doc is not None:
    print(f"{current_doc}\t{current_title}\t{total}")
