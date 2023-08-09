import json 
import optuna
import argparse
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
from itertools import combinations
from typing import Dict, List

from colorama import Fore


optuna.logging.set_verbosity(optuna.logging.WARNING)


def create_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

def evaluate_universal_metrics(metric_scores_path:str, metric_scores_file:str, human_scores_file:str, language_pair:str, reference:str, domain:str, output_path:str,
                     universal_metric:str):
    metric_name = metric_scores_file.replace("_ranks_systems.csv", "")

    if (universal_metric and universal_metric == metric_name) or not universal_metric:

        print(Fore.RED + "\n---------Universal Metric: " + metric_name)
        print(Fore.WHITE)

        human_scores = SystemsScores.read_human_scores(human_scores_file, domain)
        metric_scores = SystemsScores.read_universal_metric_scores(metric_scores_path + metric_scores_file, metric_name)
        systems_scores = SystemsScores(human_scores,metric_scores,metric_name,human_scores_file,metric_scores_path + metric_scores_file,
                                   language_pair,reference,domain)

        if systems_scores.has_systems():
            metrics_evaluation = MetricsEvaluation(systems_scores)
            metrics_evaluation.evaluate()
            metrics_evaluation.write_file(output_path)

def evaluate_metrics(metric_scores_file:str, human_scores_file:str, language_pair:str, reference:str, domain:str, output_path:str, arg_metric:str):
    
    human_scores = SystemsScores.read_human_scores(human_scores_file, domain)
    metrics_scores,metrics = SystemsScores.read_metrics_scores(metric_scores_file)

    for metric in metrics:
        if (arg_metric and arg_metric == metric) or not arg_metric:
            metric_scores = metrics_scores[metric]

            print(Fore.CYAN + "\n---------Metric: " + metric)
            print(Fore.WHITE)

            systems_scores = SystemsScores(human_scores,metric_scores,metric,human_scores_file,metric_scores_file,language_pair,reference,domain)

            if systems_scores.has_systems():
                metrics_evaluation = MetricsEvaluation(systems_scores)
                metrics_evaluation.evaluate()
                metrics_evaluation.write_file(output_path)

class SystemsScores:
    def __init__(self, human_scores:Dict[str,float], metric_scores:Dict[str,float], metric: str, human_scores_file:str , metric_scores_file:str,
                 language_pair:str,reference:str,domain:str) ->None:
        self.human_scores = {}
        self.metric_scores = {}
        self.metric = metric
        self.systems_names = []
        self.human_scores_file = human_scores_file
        self.metric_scores_file = metric_scores_file

        self.language_pair = language_pair
        self.domain = domain
        self.reference = reference

        for sys_name, human_score in human_scores.items():
            if sys_name in metric_scores.keys():
                self.human_scores[sys_name] = human_score
                self.metric_scores[sys_name] = metric_scores[sys_name]
                self.systems_names.append(sys_name)

    @staticmethod
    def read_human_scores(filename:str, domain:str) -> Dict[str,float]:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        human_scores = {}
        for line in lines:
            domain_file, sys_name, human_score = line.split("\t")
            if human_score != "None\n" and domain_file == domain:
                human_scores[sys_name] = float(human_score)
        return human_scores

    @staticmethod
    def read_universal_metric_scores(filename:str, metric_name:str) -> Dict[str,Dict[str,float]]:
        data = pd.read_csv(filename,index_col=[0])
        data = data.rename_axis('rank').reset_index()
        scores = data.set_index('System').to_dict("index")
        
        metric_scores = {}
        for system, data in scores.items():
            if metric_name == "social-choice-theory":
                metric_scores[system] = data["Score"] * -1
            else:
                metric_scores[system] = data["Score"]
                
        return metric_scores

    @staticmethod
    def read_metrics_scores(filename:str) -> Dict[str,Dict[str,float]]:
        data = pd.read_csv(filename,index_col=[0])
        metrics_scores = data.to_dict("index")
        metrics = list(metrics_scores.keys())

        for metric, data in metrics_scores.items():
            if metric == "TER":
                for system_name, score in data.items():
                    metrics_scores[metric][system_name] = score * -1
        return metrics_scores, metrics

    def systems_metric_scores(self):
        sys_metric_scores = []
        for sys_name in self.systems_names:
            sys_metric_scores.append(self.metric_scores[sys_name])
        return sys_metric_scores
    
    def systems_human_scores(self):
        sys_human_scores = []
        for sys_name in self.systems_names:
            sys_human_scores.append(self.human_scores[sys_name])
        return sys_human_scores
    
    def has_systems(self) -> bool:
        return self.systems_names != []


class MetricsEvaluation:
    def __init__(self, systems_scores: SystemsScores) -> None:
        self.systems_scores = systems_scores

    def system_accuracy(self, metric_scores, gold_scores, systems_names) -> float:
        """ To Ship not to Ship (Kocmi et al. 2021) system accuracy. """
        data = pd.DataFrame({
            "y_hat": metric_scores, 
            "y": gold_scores, 
            "sys": systems_names
        })
        data = data.groupby('sys').mean()
        pairs = list(combinations(data.index.tolist(), 2))
        tp = 0
        for system_a, system_b in pairs:
            human_delta  = data.loc[system_a]["y"] - data.loc[system_b]["y"]
            metric_delta = data.loc[system_a]["y_hat"] - data.loc[system_b]["y_hat"]
            if (human_delta >= 0) ^ (metric_delta < 0):
                tp += 1
        self.system_accuracy_value = tp/len(pairs) 
        print("System_accuracy: " + str(self.system_accuracy_value))
    
    def spearman(self,metric_scores, gold_scores): 
        self.spearman_value = stats.spearmanr(metric_scores, gold_scores)[0]
        print("Spearman : " + str(self.spearman_value))

    def pearson(self,metric_scores, gold_scores): 
        self.pearson_value = stats.pearsonr(metric_scores, gold_scores)[0]
        print("Pearson : " + str(self.pearson_value))
    
    def kendall(self,metric_scores, gold_scores): 
        self.kendall_value = stats.kendalltau(metric_scores, gold_scores)[0]
        print("Kendall : " + str(self.kendall_value))
    
    def evaluate(self):
        gold_scores = self.systems_scores.systems_human_scores()
        metric_scores =  self.systems_scores.systems_metric_scores()
        systems_names = self.systems_scores.systems_names
        self.system_accuracy(metric_scores, gold_scores, systems_names)
        self.spearman(metric_scores, gold_scores)
        self.pearson(metric_scores, gold_scores)
        self.kendall(metric_scores, gold_scores)


    def write_file(self, output_path:str) -> None:
        data = {}
        data["system_accuracy"] = self.system_accuracy_value
        data["spearman"] = self.spearman_value
        data["pearson"] = self.pearson_value
        data["kendall"] = self.kendall_value

        data["languages_pair"] = self.systems_scores.language_pair
        data["domain"] = self.systems_scores.domain
        data["reference"] = self.systems_scores.reference

        data["system_names"] = self.systems_scores.systems_names
        data["human_scores_file"] = self.systems_scores.human_scores_file
        data["human_scores"] = self.systems_scores.human_scores
        data["metric_scores_file"] = self.systems_scores.metric_scores_file
        data["metric_scores"] = self.systems_scores.metric_scores

        path_lang = output_path + "/" + self.systems_scores.language_pair + "/"
        path_domain = path_lang + self.systems_scores.domain + "/"
        path = path_domain + "/" + self.systems_scores.reference + "/"

        create_dir(output_path)
        create_dir(path_lang)
        create_dir(path_domain)
        create_dir(path)

        f = open(path + "/" + self.systems_scores.metric + "-evaluation.json", "w")
        json.dump(data,f,indent=4)
        f.close()

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
    parser.add_argument(
        "-m",
        "--metric",
        help="Metric.",
        type=str
    )
    parser.add_argument(
        "-d",
        "--domain",
        help="Domain.",
        type=str
    )
    parser.add_argument(
        "-r",
        "--reference",
        help="Reference.",
        type=str
    )
    parser.add_argument(
        "-o",
        "--output_path", 
        help="Output Path.", 
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

        if (domain and domain == args.domain) or not args.domain:
            print(Fore.GREEN + "\n---Domain: " + domain)

            reference_path = domains_path + domain + "/nlp-telescope-scores/" + args.languages_pair + "-" + domain + "/"

            for reference in os.listdir(reference_path): 

                if (reference and reference == args.reference) or not args.reference:

                    print(Fore.LIGHTYELLOW_EX + "\n------Reference: " + reference)

                    metric_scores_file = reference_path + reference + "/results.csv"
                    evaluate_metrics(metric_scores_file, human_scores_file, args.languages_pair, reference, domain, args.output_path, args.metric)


                    universal_metric_scores_path = reference_path + reference + "/universal_metrics/"
                    for universal_metric_scores_file in os.listdir(universal_metric_scores_path):
                        if universal_metric_scores_file == "weighted_mean" or universal_metric_scores_file == "weighted-mean":
                            weighted_mean_path = universal_metric_scores_path + universal_metric_scores_file + "/"

                            for weighted_mean_file in os.listdir(weighted_mean_path):
                                evaluate_universal_metrics(weighted_mean_path, weighted_mean_file, human_scores_file, args.languages_pair, reference, domain, 
                                                           args.output_path, args.metric)
                        elif universal_metric_scores_file == "pairwise-comparison_ranks_systems.csv":
                            continue
                        else:
                            evaluate_universal_metrics(universal_metric_scores_path, universal_metric_scores_file, human_scores_file, args.languages_pair, reference, 
                                                       domain, args.output_path, args.metric)

                        