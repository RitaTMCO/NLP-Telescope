#!/bin/sh

python telescope/universal_metrics/calcalute_evaluation/calculate_universal_scores.py -i telescope/universal_metrics/calcalute_evaluation/data/wmt22/ -p en-de
python telescope/universal_metrics/calcalute_evaluation/calculate_universal_scores.py -i telescope/universal_metrics/calcalute_evaluation/data/wmt22/ -p en-ru
python telescope/universal_metrics/calcalute_evaluation/calculate_universal_scores.py -i telescope/universal_metrics/calcalute_evaluation/data/wmt22/ -p zh-en

python telescope/universal_metrics/calcalute_evaluation/evaluate.py -i telescope/universal_metrics/calcalute_evaluation/data/wmt22/ -p en-de -o telescope/universal_metrics/calcalute_evaluation/data_evaluation/
python telescope/universal_metrics/calcalute_evaluation/evaluate.py -i telescope/universal_metrics/calcalute_evaluation/data/wmt22/ -p en-ru -o telescope/universal_metrics/calcalute_evaluation/data_evaluation/
python telescope/universal_metrics/calcalute_evaluation/evaluate.py -i telescope/universal_metrics/calcalute_evaluation/data/wmt22/ -p zh-en -o telescope/universal_metrics/calcalute_evaluation/data_evaluation/

python telescope/universal_metrics/calcalute_evaluation/evaluate_plot.py -i telescope/universal_metrics/calcalute_evaluation/data_evaluation -p en-de
python telescope/universal_metrics/calcalute_evaluation/evaluate_plot.py -i telescope/universal_metrics/calcalute_evaluation/data_evaluation -p en-ru
python telescope/universal_metrics/calcalute_evaluation/evaluate_plot.py -i telescope/universal_metrics/calcalute_evaluation/data_evaluation -p zh-en