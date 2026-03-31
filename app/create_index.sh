#!/bin/bash

echo "Create index using MapReduce pipelines"

echo "Pipeline 1: Inverted Index (/indexer/index)"

mapred streaming \
  -D stream.num.map.output.key.fields=2 \
  -D mapreduce.job.output.key.comparator.class=org.apache.hadoop.mapreduce.lib.partition.KeyFieldBasedComparator \
  -D mapreduce.partition.keycomparator.options="-k1,1 -k2,2" \
  --files mapreduce/mapper1.py,mapreduce/reducer1.py \
  -mapper 'python3 mapper1.py' \
  -reducer 'python3 reducer1.py' \
  -input /input/data \
  -output /indexer/index \
  2> logs.txt

echo "Pipeline 2: Vocabulary (/indexer/vocab)"

mapred streaming --files mapreduce/mapper2.py,mapreduce/reducer2.py -mapper 'python3 mapper2.py' \
-reducer 'python3 reducer2.py' -input /indexer/index -output /indexer/vocab 2> logs.txt

echo "Pipeline 3: Document Lengths (/indexer/document_lengths)"

mapred streaming --files mapreduce/mapper3.py,mapreduce/reducer3.py -mapper 'python3 mapper3.py' \
-reducer 'python3 reducer3.py' -input /input/data -output /indexer/document_lengths 2> logs.txt

echo "Pipeline 4: Statistics - total documents count, total document length (/indexer/stats)"

mapred streaming -D mapreduce.job.reduces=1 \
--files mapreduce/mapper4.py,mapreduce/reducer4.py -mapper 'python3 mapper4.py' \
-reducer 'python3 reducer4.py' -input /indexer/document_lengths -output /indexer/stats \
2> logs.txt

echo "MapReduce Pipelines are finished"
