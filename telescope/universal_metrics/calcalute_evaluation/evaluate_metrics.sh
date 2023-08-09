#!/bin/sh

python evaluate.py -i data/wmt22/ -p en-de -o data_evaluation/
python evaluate.py -i data/wmt22/ -p en-ru -o data_evaluation/
python evaluate.py -i data/wmt22/ -p zh-en -o data_evaluation/