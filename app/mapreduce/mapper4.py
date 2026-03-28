import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) != 3:
        sys.stderr.write(f"Skipping line with {len(parts)} fields: {line}\n")
        continue
    count = parts[2]          # parts[0] is doc_id, parts[1] is doc_title (ignored)
    print(f"key\t{count}")
