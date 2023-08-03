import json 
import optuna
import argparse
import numpy as np
import pandas as pd
import scipy.stats as stats
from itertools import combinations
from typing import Dict, List


optuna.logging.set_verbosity(optuna.logging.WARNING)

class SystemsScores:
    def __init__(self, human_scores:Dict[str,float], metric_scores:Dict[str,float], metric: str, human_scores_file:str , metric_scores_file:str) ->None:
        self.human_scores = {}
        self.metric_scores = {}
        self.metric = metric
        self.systems_names = []
        self.human_scores_file = human_scores_file
        self.metric_scores_file = metric_scores_file
        for sys_name, human_score in human_scores.items():
            if sys_name in metric_scores.keys():
                self.human_scores[sys_name] = human_score
                self.metric_scores[sys_name] = metric_scores[sys_name]
                self.systems_names.append(sys_name)

    @staticmethod
    def read_human_scores(filename:str) -> Dict[str,float]:
        f = open(filename, "r")
        lines = f.readlines()
        f.close()
        human_scores = {}
        for line in lines:
            sys_name, human_score = line.split("\t")
            if human_score != "None":
                human_scores[sys_name] = float(human_score)
        return human_scores

    @staticmethod
    def read_metric_scores(filename:str) -> Dict[str,Dict[str,float]]:
        data = pd.read_csv(filename,index_col=[0])
        rank_scores = data.to_dict('index')
        metric_scores = {}
        for rank, data in rank_scores.items():
            metric_scores[data["System"]] = data["Score"]
        return metric_scores

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


    def write_file(self, path:str) -> None:
        data = {}
        data["system_accuracy"] = self.system_accuracy_value
        data["spearman"] = self.spearman_value
        data["pearson"] = self.pearson_value
        data["kendall"] = self.kendall_value
        data["system_names"] = self.systems_scores.systems_names
        data["human_scores_file"] = self.systems_scores.human_scores_file
        data["human_scores"] = self.systems_scores.human_scores
        data["metric_scores_file"] = self.systems_scores.metric_scores_file
        data["metric_scores"] = self.systems_scores.metric_scores
        f = open(path + "/" + self.systems_scores.metric + "-evaluation.json", "w")
        json.dump(data,f,indent=4)
        f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g",
        "--human_scores_file",
        help="Human system scores file (.txt).",
        required=True,
        type=str
    )
    parser.add_argument(
        "-m",
        "--metric_scores_file", 
        help="Universal Metric scores file (.csv)", 
        required=True,
        type=str
    )
    parser.add_argument(
        "-n",
        "--universal_metric_name", 
        help="Universal Metric Name", 
        required=True,
        type=str
    )
    parser.add_argument(
        "-o",
        "--output_path", 
        help="Output Path.", 
        type=str
    )

    args = parser.parse_args()

    human_scores = SystemsScores.read_human_scores(args.human_scores_file)
    metric_scores = SystemsScores.read_metric_scores(args.metric_scores_file)
    systems_scores = SystemsScores(human_scores,metric_scores,args.universal_metric_name,args.human_scores_file,args.metric_scores_file)

    if systems_scores.has_systems():
        metrics_evaluation = MetricsEvaluation(systems_scores)
        metrics_evaluation.evaluate()
        metrics_evaluation.write_file(args.output_path)