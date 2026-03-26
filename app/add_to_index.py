import sys
import uuid
from cassandra.cluster import Cluster
from pyspark import SparkContext

# Stage 1: Read input file and compute statistics using Spark RDD

print("Reading the uploaded file with Spark")

if len(sys.argv) != 2:
    print("Usage: spark-submit script.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

sc = SparkContext(appName="WordCountRDD")

# Read file as RDD of lines
lines = sc.textFile(file_path)

# Split lines into words, flatten, and filter empty strings
words = lines.flatMap(lambda line: line.split()) \
             .filter(lambda w: w != "")

# Count term frequencies: (word, 1) -> reduceByKey
tf_rdd = words.map(lambda w: (w, 1)) \
              .reduceByKey(lambda a, b: a + b)

# Collect term frequencies as a list of (word, tf) – small enough for one document
tf_list = tf_rdd.collect()

# Total number of words
total_words = words.count()

sc.stop()

print("Data was prepared")

# Stage 2: Update database with the obtained statistics

print("Updating ScyllaDB contents")

# Generate new document ID
doc_id = str(uuid.uuid4())

# Connect to ScyllaDB

CONTACT_POINTS = ['scylla-server']
KEYSPACE = "indexdb"

cluster = Cluster(CONTACT_POINTS)
session = cluster.connect()
session.set_keyspace(KEYSPACE)

# Insert document length
session.execute(
    "INSERT INTO doc_lengths (doc_id, dl) VALUES (%s, %s)",
    (doc_id, total_words)
)
print(f"Inserted doc_lengths for {doc_id}, length={total_words}")


# Insert inverted index (append, no concurrency issues)
prep_inv = session.prepare("INSERT INTO inverted_index (term, doc_id, tf) VALUES (?, ?, ?)")
for term, tf in tf_list:
    session.execute(prep_inv, (term, doc_id, tf))


# Update vocabulary (atomic increment)
prep_select = session.prepare("SELECT df FROM vocabulary WHERE term = ?")
prep_update = session.prepare("UPDATE vocabulary SET df = ? WHERE term = ? IF df = ?")
prep_insert = session.prepare("INSERT INTO vocabulary (term, df) VALUES (?, ?) IF NOT EXISTS")


def increment_df(term):
    while True:
        # Read current
        row = session.execute(prep_select, (term,)).one()
        if row is None:
            # Row doesn't exist, then try to insert with df=1
            result = session.execute(prep_insert, (term, 1))
            if result[0].applied:
                return
            # else conflict: another thread inserted concurrently, retry
        else:
            # Row doesn't exist, then try to update if value has not changed
            new_df = row.df + 1
            result = session.execute(prep_update, (new_df, term, row.df))
            if result[0].applied:
                return
            # else conflict: another thread inserted concurrently, retry


distinct_terms = set(term for term, _ in tf_list)
for term in distinct_terms:
    increment_df(term)


# Update global stats (atomic increment)
prep_get_docs = session.prepare("SELECT value FROM global_stats WHERE key = 'total_docs'")
prep_upd_docs = session.prepare("UPDATE global_stats SET value = ? WHERE key = 'total_docs' IF value = ?")
prep_get_len = session.prepare("SELECT value FROM global_stats WHERE key = 'total_doc_length'")
prep_upd_len = session.prepare("UPDATE global_stats SET value = ? WHERE key = 'total_doc_length' IF value = ?")


# Update `total_docs` by 1
def increment_docs():
    while True:
        row = session.execute(prep_get_docs).one()
        old = row.value if row else 0
        new = old + 1
        result = session.execute(prep_upd_docs, (new, old))
        if result[0].applied:
            return


# Update `total_doc_length` by dl
def add_len(dl):
    while True:
        row = session.execute(prep_get_len).one()
        old = row.value if row else 0
        new = old + dl
        result = session.execute(prep_upd_len, (new, old))
        if result[0].applied:
            return


increment_docs()
add_len(total_words)

print("All updates completed.")


# Clean up
session.shutdown()
cluster.shutdown()
print("Done.")
