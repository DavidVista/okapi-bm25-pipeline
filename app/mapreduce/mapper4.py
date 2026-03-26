import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        sys.stderr.write(f"Skipping line with {len(parts)} fields: {line}\n")
        continue
    doc_id, count = parts
    print(f"key\t{count}")
