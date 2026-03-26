import sys


def unquote(field):
    """Remove surrounding double quotes if present."""
    if field.startswith('"') and field.endswith('"'):
        return field[1:-1]   # strip one leading and one trailing quote
    return field


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    parts = line.split('\t')
    if len(parts) < 3:
        sys.stderr.write(f"Skipping line with {len(parts)} fields: {line}\n")
        continue
    doc_id = parts[0]               # first field is doc_id, title is parts[1] (not needed)
    text = '\t'.join(parts[2:])     # reconstruct text in case it contains tabs

    doc_id = unquote(doc_id)
    text = unquote(text)

    for word in text.split():
        # Output (doc_id, 1) for each word occurrence
        print(f"{doc_id}\t1")
