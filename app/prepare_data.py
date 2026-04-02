from pathvalidate import sanitize_filename
from pyspark.sql import SparkSession
from unidecode import unidecode
import re


spark = SparkSession.builder \
    .appName('data preparation') \
    .master("local") \
    .config("spark.sql.parquet.enableVectorizedReader", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

df = spark.read.parquet("/a.parquet")
n = 1000
df = df.select(['id', 'title', 'text']).sample(fraction=100 * n / df.count(), seed=0).limit(n)


def safe_filename(filename):
    """
    Keep only alphanumeric, underscore, hyphen, and dot.
    Replace everything else with underscore.
    """
    # First, apply pathvalidate to remove filesystem‑invalid characters
    sanitized = sanitize_filename(filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    # Replace non-ASCII chars
    sanitized = unidecode(sanitized)
    # Replace any character that is not alnum, underscore, hyphen, or dot with underscore
    cleaned = re.sub(r'[^\w\-\.]', '_', sanitized)
    # Avoid double underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned


def create_doc(row):
    base = str(row['id']) + "_" + row['title']
    filename = "data/" + safe_filename(base) + ".txt"
    with open(filename, "w") as f:
        f.write(row['text'])


df.foreach(create_doc)

spark.stop()
