from pathvalidate import sanitize_filename
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace, udf
from pyspark.sql.types import StringType
from preprocess import preprocess_text


# Register the UDF
preprocess_udf = udf(preprocess_text, StringType())


spark = SparkSession.builder \
    .appName('data preparation') \
    .master("local") \
    .config("spark.sql.parquet.enableVectorizedReader", "true") \
    .getOrCreate()

df = spark.read.parquet("/a.parquet")
n = 1000
df = df.select(['id', 'title', 'text']).sample(fraction=100 * n / df.count(), seed=0).limit(n)


df = df.withColumn("text", preprocess_udf("text"))


def create_doc(row):
    filename = "data/" + sanitize_filename(str(row['id']) + "_" + row['title']).replace(" ", "_") + ".txt"
    with open(filename, "w") as f:
        f.write(row['text'])


df.foreach(create_doc)


# Clean newlines/tabs and write CSV for MapReduce
df = df.withColumn("title", regexp_replace("title", "[\n\r\t]", " "))

df.write.csv("/input/data", sep="\t")

spark.stop()
