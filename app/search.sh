#!/bin/bash

source .venv/bin/activate

# Python of the driver (/app/.venv/bin/python)
export PYSPARK_DRIVER_PYTHON=$(which python) 

# Python of the excutor (./.venv/bin/python)
export PYSPARK_PYTHON=./.venv/bin/python

spark-submit \
--master yarn \
--archives /app/.venv.tar.gz#.venv \
--packages com.scylladb:spark-scylladb-connector_2.12:4.0.0 \
--conf spark.cassandra.connection.host=scylla-server \
query.py $1