#!/bin/bash

source .venv/bin/activate

# Run MapReduce Pipeline
bash create_index.sh

# Store Index Data in the ScyllaDB Server
bash store_index.sh

