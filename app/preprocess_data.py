from pyspark import SparkContext
from preprocess import preprocess_text


def process_file(file):
    filepath, text = file

    filename = filepath.split("/")[-1]
    filename = filename.split(".txt")[0]

    document_id, document_title = filename.split("_", 1)
    processed_text = preprocess_text(text)

    return document_id, document_title, processed_text


# Read data files

print("Reading the data with Spark RDD")

sc = SparkContext(appName="PrepareDataForMapReduce")

# Read as RDD of (filename, file text)
files_rdd = sc.wholeTextFiles("/data/*")

# Apply preprocessing to each file -> (document_id, document_title, preprocessed text)
processed_rdd = files_rdd.map(process_file)

# Convert each row to a tab‑separated string
csv_rdd = processed_rdd.map(lambda row: f"{row[0]}\t{row[1]}\t{row[2]}")

# Save as text files (creates /input/data directory with part files)
csv_rdd.saveAsTextFile("/input/data")

sc.stop()
