#!/bin/sh

echo "----------------------- seed 1000 -----------------------"

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 1000 

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 1000 --weighted_mean TRUE


echo "----------------------- seed 3000 -----------------------"

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 3000

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 3000 --weighted_mean TRUE


echo "----------------------- seed 5000 -----------------------"

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 5000 

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 5000 --weighted_mean TRUE