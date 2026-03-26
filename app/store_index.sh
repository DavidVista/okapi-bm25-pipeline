#!/bin/bash


echo "Create keyspace"
python3 create_keyspace.py

echo "Store the index and others to Cassandra/ScyllaDB tables"

spark-submit \
--driver-memory 4g \
--packages com.scylladb:spark-scylladb-connector_2.12:4.0.0 \
--conf spark.cassandra.connection.host=scylla-server \
store_index.py
