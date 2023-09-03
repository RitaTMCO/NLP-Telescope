#!/bin/sh

echo "----------------------- seed 12 -----------------------"

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 12 

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 12 --ter TRUE

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 12 --weighted_mean TRUE


echo "----------------------- seed 24 -----------------------"

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 24 

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 24 --ter TRUE

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 24 --weighted_mean TRUE


echo "----------------------- seed 36 -----------------------"

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 36 

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 36 --ter TRUE

python calculate_weights.py -m data/wmt21.news/zh-en/nlp-telescope-scores/zh-en.txt/zh-en.refA.txt/results.csv -g data/wmt21.news/zh-en/human-scores/zh-en.mqm.sys.score --trials 1000 --yaml ../../../user/universal_metrics.yaml -o data/weights-wmt21-zh-en-refA --seed_everything 36 --weighted_mean TRUE
