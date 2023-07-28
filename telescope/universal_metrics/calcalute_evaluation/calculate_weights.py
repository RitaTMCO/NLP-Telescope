import json 
import optuna
import argparse
import numpy as np
import pandas as pd
from pytorch_lightning import seed_everything
from itertools import combinations
from typing import Dict, List


optuna.logging.set_verbosity(optuna.logging.WARNING)

class SystemsScores:
    def __init__(self, human_scores:Dict[str,float], metrics_scores:Dict[str,Dict[str,float]], metrics: List[str]) ->None:
        self.human_scores = {}
        self.metrics_scores = {}
        self.metrics = metrics
        self.systems_names = []
        for sys_name, human_score in human_scores.items():
            if sys_name in metrics_scores.keys():
                self.human_scores[sys_name] = human_score
                self.metrics_scores[sys_name] = metrics_scores[sys_name]
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
    def read_metrics_scores(filename:str) -> Dict[str,Dict[str,float]]:
        data = pd.read_csv(filename,index_col=[0])
        metrics_scores = data.to_dict()
        sys_names = list(metrics_scores.keys())
        metrics = list(metrics_scores[sys_names[0]].keys())
        return metrics_scores, metrics
    
    def systems_one_metric_scores(self, metric:str):
        sys_metric_scores = []
        for sys_name in self.systems_names:
            sys_metric_scores.append(self.metrics_scores[sys_name][metric])
        return sys_metric_scores
    
    def systems_human_scores(self):
        sys_human_scores = []
        for sys_name in self.systems_names:
            sys_human_scores.append(self.human_scores[sys_name])
        return sys_human_scores
    
    def has_systems(self) -> bool:
        return self.systems_names != []


class StudyWeights:
    def __init__(self, systems_scores: SystemsScores, seed:int, trials:int) -> None:
        self.systems_scores = systems_scores
        self.seed = seed
        self.trials = trials

    @staticmethod
    def system_accuracy(metric_scores, gold_scores, systems_names) -> float:
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
        return tp/len(pairs) 

    def objective(self,trial) -> float:
        metrics = self.systems_scores.metrics
        weights = [trial.suggest_float(m, -1, 1) for m in metrics]
        weights = {m: w for m, w in zip(metrics, weights)}
        gold_scores = self.systems_scores.systems_human_scores()
        weighted_mean_scores_per_sys = list(np.array(
            [weights[m] * np.array(self.systems_scores.systems_one_metric_scores(m)) for m in weights.keys()]
        ).sum(axis=0))
        accuracy = self.system_accuracy(weighted_mean_scores_per_sys, gold_scores, self.systems_scores.systems_names)
        return accuracy
    
    def optimize_weights(self) -> None:
        study = optuna.create_study(sampler=optuna.samplers.TPESampler(seed=self.seed), direction="maximize")
        study.optimize(lambda x: self.objective(x), n_trials=args.trials, show_progress_bar=True)
        self.weights = study.best_trial.params
        print(self.weights)

    def write_file(self, path:str) -> None:
        data = self.weights
        data["system_names"] = self.systems_scores.systems_names
        data["number_of_trials"] = self.trials
        data["seed"] = self.seed
        f = open(path + "/metrics_weights.txt", "w")
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
        "--metrics_scores_file", 
        help="Metrics system scores file (.csv)", 
        required=True,
        type=str
    )
    parser.add_argument(
        "--seed_everything",
        type=int,
        default=12,
        help="Training Seed.",
    )
    parser.add_argument(
        "--trials", 
        help="Number of trials in Optune search.", 
        default=2000, 
        type=int
    )
    parser.add_argument(
        "-o",
        "--output_path", 
        help="Output Path.", 
        type=str
    )

    args = parser.parse_args()
    seed_everything(args.seed_everything)

    human_scores = SystemsScores.read_human_scores(args.human_scores_file)
    metrics_scores, metrics = SystemsScores.read_metrics_scores(args.metrics_scores_file)
    systems_scores = SystemsScores(human_scores,metrics_scores,metrics)

    study = StudyWeights(systems_scores,args.seed_everything,args.trials)
    study.optimize_weights()
    study.write_file(args.output_path)