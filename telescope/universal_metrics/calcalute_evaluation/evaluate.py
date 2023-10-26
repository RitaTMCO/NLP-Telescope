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

u_metrics = {
        "average" : "Average",
        "median" : "Median",
        "social-choice-theory" : "Social Choice Theory",
        "weighted-mean-1000" : "Weighted Mean 1000",
        "weighted-mean-3000" : "Weighted Mean 3000",
        "weighted-mean-5000" : "Weighted Mean 5000",
        "weighted-sum-1000" : "Weighted Sum 1000",
        "weighted-sum-3000" : "Weighted Sum 3000",
        "weighted-sum-5000" : "Weighted Sum 5000",
    }


def create_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

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
                metrics_evaluation.write_dataframe(output_path)

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

    def pearson(self,metric_scores, gold_scores): 
        self.pearson_value = stats.pearsonr(metric_scores, gold_scores)[0]
        print("Pearson : " + str(self.pearson_value))
    

    def evaluate(self):
        gold_scores = self.systems_scores.systems_human_scores()
        metric_scores =  self.systems_scores.systems_metric_scores()
        systems_names = self.systems_scores.systems_names
        self.system_accuracy(metric_scores, gold_scores, systems_names)
        self.pearson(metric_scores, gold_scores)

    def write_dataframe(self, output_path:str) -> None:
        if self.systems_scores.metric in u_metrics:
            data = {"metric":u_metrics[self.systems_scores.metric]}
        else:
            data = {"metric": self.systems_scores.metric}

        data["System Accuracy"] = round(self.system_accuracy_value,3)
        data["Pearson"] = round(self.pearson_value,3)


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

        df = pd.DataFrame([data])

        if os.path.exists(path) and os.path.isfile(path + "/evaluation.csv"):
            data_file = pd.read_csv(path + "/evaluation.csv")
            d_res = pd.concat([data_file,df])
        
        else:
            create_dir(output_path)
            create_dir(path_lang)
            create_dir(path_domain)
            create_dir(path)
            d_res = df

        d_res.to_csv(path + "/evaluation.csv", index=False)

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

                    path_lang_1 = args.output_path + "/" + args.languages_pair + "/"
                    path_domain_2 = path_lang_1 + domain + "/"
                    path_3 = path_domain_2 + "/" + reference + "/"
                    if os.path.exists(path_3) and os.path.isfile(path_3 + "/evaluation.csv"):
                        os.remove(path_3 + "/evaluation.csv")

                    metric_scores_file = reference_path + reference + "/results.csv"
                    evaluate_metrics(metric_scores_file, human_scores_file, args.languages_pair, reference, domain, args.output_path, args.metric)

                    u_metric_scores_file = reference_path + reference + "/universal_results.csv"
                    evaluate_metrics(u_metric_scores_file, human_scores_file, args.languages_pair, reference, domain, args.output_path, args.metric)


                        