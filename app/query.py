from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import sys
import math


# Create SparkSession
spark = SparkSession.builder \
    .appName("ReadFromScylla") \
    .config("spark.cassandra.connection.host", "scylla-server") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

sc = spark.sparkContext


# Input
if len(sys.argv) < 2:
    print("Usage: python bm25.py term1 [term2 ...]")
    sys.exit(1)

query = sys.argv[1:]
print(f"Starting search for query: {query}")


# Step 1: Read global stats

global_stats = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="global_stats", keyspace="indexdb") \
    .load()

total_docs = global_stats.filter(F.col('key') == 'total_docs').first()['value']
total_doc_length = global_stats.filter(F.col('key') == 'total_doc_length').first()['value']

total_docs = sc.broadcast(total_docs)
total_doc_length = sc.broadcast(total_doc_length)

# Step 2: Load vocabulary, filter for query terms, and broadcast term->df dictionary

vocab_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="vocabulary", keyspace="indexdb") \
    .load()

term_df_pairs = vocab_df.filter(F.col('term').isin(query)).collect()    # collect since query list is small

term_df_dict = {row.term: row.df for row in term_df_pairs}

broadcast_df = spark.sparkContext.broadcast(term_df_dict)

# Step 3: Load inverted index and filter for query terms

inverted_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="inverted_index", keyspace="indexdb") \
    .load()

inverted_index_rdd = inverted_df.filter(F.col('term').isin(query)).rdd.map(lambda row: (row.doc_id, (row.term, row.tf)))

# Step 4: Load document lengths

doc_lengths_df = spark.read \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="doc_lengths", keyspace="indexdb") \
    .load()

doc_lengths_rdd = doc_lengths_df.rdd.map(lambda row: (row.doc_id, (row.doc_title, row.dl)))

# Step 5: Join inverted_index and doc_lengths on doc_id

joined_rdd = inverted_index_rdd.join(doc_lengths_rdd)


def flatten(row):
    # row is (doc_id, ((term, tf), dl))
    doc_id, ((term, tf), (doc_title, dl)) = row
    return (term, doc_id, tf, doc_title, dl)


stats_rdd = joined_rdd.map(flatten)

# Step 6: Compute BM25 scores using stats_rdd and broadcast_df


def bm25_score(row, k1=1.0, b=0.75):

    dl_avg = total_doc_length.value / total_docs.value

    term, doc_id, tf, doc_title, dl = row

    df = broadcast_df.value.get(term)
    idf = math.log((total_docs.value - df + 0.5) / (df + 0.5))

    numerator = tf * (k1 + 1)
    denominator = tf + k1 * (1 - b + b * (dl / dl_avg))
    term_score = idf * numerator / denominator

    return (doc_id, (doc_title, term_score))


term_scores_rdd = stats_rdd.map(bm25_score)


# Step 7: Aggregate term scores for documents and retrieve top 10

doc_scores_rdd = term_scores_rdd.reduceByKey(lambda x, y: (x[0], x[1] + y[1]))      # 0 -> doc_title, 1 -> term_score

# Take top 10 by score (descending)
top10 = doc_scores_rdd.takeOrdered(10, key=lambda x: -x[1][1])     # 0 -> doc_id, 1 -> [0 -> doc_title, 1 -> term_score]

for doc_id, (doc_title, score) in top10:
    print(doc_id, doc_title)

spark.stop()
