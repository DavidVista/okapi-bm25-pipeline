from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType


spark = SparkSession.builder \
    .appName("Load Indexer Data") \
    .config("spark.cassandra.connection.host", "scylla-server") \
    .getOrCreate()

# Step 1: Vocabulary Data (Document Frequency)

vocab_schema = StructType([
    StructField("term", StringType(), True),
    StructField("df", IntegerType(), True)
])

df_df = spark.read \
    .option("delimiter", "\t") \
    .option("header", "false") \
    .option("quote", "") \
    .schema(vocab_schema) \
    .csv("/indexer/vocab")

df_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="vocabulary", keyspace="indexdb") \
    .mode("append") \
    .save()

# Step 2: Document Index (Term Frequency)


tf_schema = StructType([
    StructField("term", StringType(), True),
    StructField("doc_id", StringType(), True),
    StructField("tf", IntegerType(), True)
])

tf_df = spark.read \
    .option("delimiter", "\t") \
    .option("header", "false") \
    .option("quote", "") \
    .schema(tf_schema) \
    .csv("/indexer/index")

tf_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="inverted_index", keyspace="indexdb") \
    .mode("append") \
    .save()

# Step 3: Document Lengths

dl_schema = StructType([
    StructField("doc_id", StringType(), True),
    StructField("dl", IntegerType(), True)
])

dl_df = spark.read \
    .option("delimiter", "\t") \
    .option("header", "false") \
    .option("quote", "") \
    .schema(dl_schema) \
    .csv("/indexer/document_lengths")

dl_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="doc_lengths", keyspace="indexdb") \
    .mode("append") \
    .save()

# Step 4: Total Documents Count and Total Document Length

stats_schema = StructType([
    StructField("key", StringType(), True),
    StructField("value", DoubleType(), True)
])

stats_df = spark.read \
    .option("delimiter", "\t") \
    .option("header", "false") \
    .option("quote", "") \
    .schema(stats_schema) \
    .csv("/indexer/stats")

stats_df.write \
    .format("org.apache.spark.sql.cassandra") \
    .options(table="global_stats", keyspace="indexdb") \
    .mode("append") \
    .save()
