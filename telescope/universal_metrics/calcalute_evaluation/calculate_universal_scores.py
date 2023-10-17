from telescope.universal_metrics import *
import pandas as pd
from typing import Dict, List
import argparse
from colorama import Fore
import os

@staticmethod
def read_metrics_scores(filename:str) -> Dict[str,Dict[str,float]]:
    data = pd.read_csv(filename,index_col=[0])
    metrics_scores = data.to_dict("index")
    metrics = list(metrics_scores.keys())
    system_keys = list(metrics_scores[metrics[0]].keys())
    return metrics_scores, system_keys

def cal_universal_score(universal_scores_per_sys, scores):
    for sys_key, score in scores.items():
        universal_scores_per_sys[sys_key].append(score)
    return universal_scores_per_sys

def universal_average(metrics_scores, systems_keys, universal_scores_per_sys):
    average_scores = Average.universal_score(systems_keys, metrics_scores, "average")
    return cal_universal_score(universal_scores_per_sys, average_scores)

def universal_median(metrics_scores, systems_keys, universal_scores_per_sys):
    median_scores = Median.universal_score(systems_keys, metrics_scores, "median")
    return cal_universal_score(universal_scores_per_sys, median_scores)

def universal_social(metrics_scores, systems_keys, universal_scores_per_sys):
    social_scores = SocialChoiceTheory.universal_score(systems_keys, metrics_scores, "social-choice-theory")
    return cal_universal_score(universal_scores_per_sys, social_scores)

def universal_weighted_mean(metrics_scores, systems_keys, universal_scores_per_sys):
    means = ["weighted-mean-1000", "weighted-mean-3000", "weighted-mean-5000"]
    for m in means:
        weighted_mean_scores = WeightedMean.universal_score(systems_keys, metrics_scores,m)
        universal_scores_per_sys = cal_universal_score(universal_scores_per_sys, weighted_mean_scores)
    return universal_scores_per_sys

def universal_weighted_sum(metrics_scores, systems_keys, universal_scores_per_sys):
    sums = ["weighted-sum-1000", "weighted-sum-3000", "weighted-sum-5000"]
    for s in sums:
        weighted_sum_scores = WeightedSum.universal_score(systems_keys, metrics_scores,s)
        universal_scores_per_sys = cal_universal_score(universal_scores_per_sys, weighted_sum_scores)
    return universal_scores_per_sys

def cal_universal_metrics(metrics_scores, systems_keys, universal_scores_per_sys):
    universal_scores_per_sys = universal_average(metrics_scores, systems_keys, universal_scores_per_sys)
    universal_scores_per_sys = universal_median(metrics_scores, systems_keys, universal_scores_per_sys)
    universal_scores_per_sys = universal_social(metrics_scores, systems_keys, universal_scores_per_sys)
    universal_scores_per_sys = universal_weighted_mean(metrics_scores, systems_keys, universal_scores_per_sys)
    universal_scores_per_sys = universal_weighted_sum(metrics_scores, systems_keys, universal_scores_per_sys)
    return universal_scores_per_sys


def output_file(path,filename):
    list_universal_metrics = ["average", "median", "social-choice-theory", 
                     "weighted-mean-1000", "weighted-mean-3000", "weighted-mean-5000",
                     "weighted-sum-1000", "weighted-sum-3000", "weighted-sum-5000"]
    metrics_scores, systems_keys = read_metrics_scores(filename)
    universal_scores_per_sys = {sys_keys:[] for sys_keys in systems_keys}
    universal_scores_per_sys = cal_universal_metrics(metrics_scores, systems_keys, universal_scores_per_sys)
    dataframe_universal = pd.DataFrame(universal_scores_per_sys)
    dataframe_universal.index = list_universal_metrics
    dataframe_universal.to_csv(path + "/universal_results.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_path",
        help="Input path",
        required=True,
        type=str
    )
    parser.add_argument(
        "-p",
        "--languages_pair",
        help="Language pair (e.g. en-ru).",
        required=True,
        type=str
    )

    args = parser.parse_args()

    print("-----------------------------------------------------------------------------------------------")
    print(Fore.MAGENTA + "Languages Pair: " +  args.languages_pair)
    
    input = args.input_path + "/" + args.languages_pair + "/"
    human_scores_file = input + "human-scores/" + args.languages_pair + ".mqm.domain.score"
    domains_path = input + "domains/"

    for domain in os.listdir(domains_path): 

        if domain:
            print(Fore.GREEN + "\n---Domain: " + domain)

            reference_path = domains_path + domain + "/nlp-telescope-scores/" + args.languages_pair + "-" + domain + "/"

            for reference in os.listdir(reference_path): 

                if reference:

                    print(Fore.LIGHTYELLOW_EX + "\n------Reference: " + reference)

                    metric_scores_file = reference_path + reference + "/results.csv"
                    output_file(reference_path + reference,metric_scores_file)