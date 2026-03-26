#!/bin/bash

# Check if a local file path is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <local_file_path>"
    exit 1
fi

LOCAL_FILE="$1"
HDFS_TARGET_DIR="/data"

# Extract the filename
FILENAME=$(basename "$LOCAL_FILE")

# Copy the file to HDFS
hdfs dfs -put "$LOCAL_FILE" "$HDFS_TARGET_DIR/$FILENAME"

# Check if the operation succeeded
if [ $? -eq 0 ]; then
    echo "File $FILENAME successfully copied to $HDFS_TARGET_DIR"
else
    echo "Failed to copy file"
    exit 1
fi

source .venv/bin/activate


# Python of the driver (/app/.venv/bin/python)
export PYSPARK_DRIVER_PYTHON=$(which python) 


unset PYSPARK_PYTHON

spark-submit add_to_index.py "$HDFS_TARGET_DIR/$FILENAME"
