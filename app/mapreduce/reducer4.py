import sys

total = 0
count = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        sys.stderr.write(f"Skipping line with {len(parts)} fields: {line}\n")
        continue

    # part[0]: 'key', part[1]: count
    val = parts[1]

    try:
        val = int(val)
    except ValueError:
        sys.stderr.write(f"Skipping non‑numeric count: {val}\n")
        continue

    total += val
    count += 1


print(f"total_docs\t{count}")
print(f"total_doc_length\t{total}")
