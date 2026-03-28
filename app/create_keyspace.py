from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import sys

# Configuration
CONTACT_POINTS = ['scylla-server']
KEYSPACE = 'indexdb'
REPLICATION_FACTOR = 1

# Connect to ScyllaDB
cluster = Cluster(contact_points=CONTACT_POINTS)
session = cluster.connect()

# Create keyspace if it doesn't exist
keyspace_stmt = f"""
    CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
    WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': {REPLICATION_FACTOR}}}
"""
session.execute(keyspace_stmt)
print(f"Keyspace '{KEYSPACE}' ready.")

# Use the keyspace
session.set_keyspace(KEYSPACE)

# Define table creation statements
tables = {
    'vocabulary': """
        CREATE TABLE IF NOT EXISTS vocabulary (
            term text PRIMARY KEY,
            df int
        )
    """,
    'inverted_index': """
        CREATE TABLE IF NOT EXISTS inverted_index (
            term text,
            doc_id text,
            tf int,
            PRIMARY KEY ((term), doc_id)
        )
    """,
    'doc_lengths': """
        CREATE TABLE IF NOT EXISTS doc_lengths (
            doc_id text PRIMARY KEY,
            doc_title text,
            dl int
        )
    """,
    'global_stats': """
        CREATE TABLE IF NOT EXISTS global_stats (
            key text PRIMARY KEY,
            value double
        )
    """
}

# Execute each table creation
for table_name, stmt in tables.items():
    try:
        session.execute(stmt)
        print(f"Table '{table_name}' created (or already exists).")
    except Exception as e:
        print(f"Error creating table '{table_name}': {e}", file=sys.stderr)

# Close connection
session.shutdown()
cluster.shutdown()
print("Schema setup complete.")
