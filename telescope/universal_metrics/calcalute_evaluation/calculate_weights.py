import json 
import yaml
import optuna
import argparse
import numpy as np
import pandas as pd
from pytorch_lightning import seed_everything
from itertools import combinations
from typing import Dict, List
from telescope.utils import read_yaml_file


optuna.logging.set_verbosity(optuna.logging.WARNING)

class SystemsScores:
    def __init__(self, human_scores:Dict[str,float], metrics_scores:Dict[str,Dict[str,float]], metrics: List[str], human_scores_file:str , metrics_scores_file:str) ->None:
        self.human_scores = {}
        self.metrics_scores = {}
        self.metrics = metrics
        self.systems_names = []
        self.human_scores_file = human_scores_file
        self.metrics_scores_file = metrics_scores_file
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

    def objective(self,trial,ter,weighted_mean) -> float:
        metrics = self.systems_scores.metrics
        if not ter and not weighted_mean:
            weights = [trial.suggest_float(m, -1, 1) for m in metrics]
        elif ter:
            weights = []
            for m in metrics:
                if m == "TER":
                    weights.append(trial.suggest_float(m, -1, 0))
                else:
                    weights.append(trial.suggest_float(m, 0, 1))
        elif weighted_mean:
            weights = [trial.suggest_float(m, 0, 1) for m in metrics]

        weights = {m: w for m, w in zip(metrics, weights)}

        gold_scores = self.systems_scores.systems_human_scores()

        weighted_sum_scores_per_sys = np.array(
            [weights[m] * np.array(self.systems_scores.systems_one_metric_scores(m)) for m in weights.keys()]
        ).sum(axis=0)

        if weighted_mean:
            weighted_mean_scores_per_sys = weighted_sum_scores_per_sys / sum(weights.values())
            accuracy = self.system_accuracy(list(weighted_mean_scores_per_sys), gold_scores, self.systems_scores.systems_names)
        else:
            accuracy = self.system_accuracy(list(weighted_sum_scores_per_sys), gold_scores, self.systems_scores.systems_names)
        return accuracy
    
    def optimize_weights(self,ter:bool,weighted_mean:bool) -> None:
        study = optuna.create_study(sampler=optuna.samplers.TPESampler(seed=self.seed), direction="maximize")
        study.optimize(lambda x: self.objective(x,ter,weighted_mean), n_trials=args.trials, show_progress_bar=True)
        self.weights = study.best_trial.params
        self.best_value = study.best_value
        self.best_trial = study.best_trial.number
        print(self.weights)
    

    def write_yaml(self,weighted_mean:bool,ter:bool) -> None:
        filename = "universal_metrics.yaml"
        data_yaml = read_yaml_file(filename)

        if weighted_mean:
            u_name = "weighted-mean-" + "seed-" + str(self.seed) + "-trials-" + str(self.trials) + "_0_1" 
            data_yaml["Weighted Mean Weights"][u_name] = self.weights
        else:
            u_name = "weighted-sum-" + "seed-" + str(self.seed) + "-trials-" + str(self.trials) + "_"
            if ter:
                u_name += "TER_0_1"
            else:
                u_name += "-1_1"
            data_yaml["Weighted Sum Weights"][u_name] = self.weights
        if u_name not in data_yaml["All universal metrics"]:
            data_yaml["All universal metrics"].append(u_name)
        if u_name not in data_yaml["Machine Translation universal metrics"]:
            data_yaml["Machine Translation universal metrics"].append(u_name)

        data_final = yaml.dump(data_yaml, default_flow_style=False,sort_keys=False)
        for k in list(data_yaml.keys())[1:]:
            data_final = data_final.replace(k, '\n' + k)
            for name in data_yaml[k]:
                data_final = data_final.replace("- " + name, '  - ' + name)
        for name in list(data_yaml["Weighted Mean Weights"].keys()) + list(data_yaml["Weighted Sum Weights"].keys()):
            data_final = data_final.replace("  " + name, '\n  ' + name)
        data_final = data_final.replace("    -", '  -') 
        data_final = data_final.replace("Weighted Sum Weights", "#-------------------------- | Weights |--------------------------\n\nWeighted Sum Weights")
        data_final = data_final.replace("Weighted Mean Weights", "\nWeighted Mean Weights")

        y =  open("user/" + filename, 'w')
        y.write(data_final)
        y.close()


    def write_files(self, path:str,yaml_p:str,ter:bool,weighted_mean:bool) -> None:
        data = {}
        data["weights_metrics"] = self.weights
        data["best_value"] = self.best_value
        data["best_trial"] = self.best_trial

        data["system_names"] = self.systems_scores.systems_names
        data["number_of_trials"] = self.trials
        data["seed"] = self.seed
        data["human_scores_file"] = self.systems_scores.human_scores_file
        data["human_scores"] = self.systems_scores.human_scores
        data["metrics_scores_file"] = self.systems_scores.metrics_scores_file
        data["metrics_scores"] = self.systems_scores.metrics_scores
        
        extra = str(self.seed) + "_" + str(self.trials) + "_"
        if weighted_mean:
            extra += "weighted_mean_"
        if not weighted_mean:
            extra += "weighted_sum_"
        if ter:
            extra += "ter_"
        f = open(path + "/" + extra + "metrics_weights.json", "w")
        json.dump(data,f,indent=4)
        f.close()

        if yaml_p:
            self.write_yaml(weighted_mean,ter)


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
        "-t",
        "--ter", 
        help="The Weight for TER is between [-1,0].", 
        type=bool,
        default=False
    )
    parser.add_argument(
        "-n",
        "--weighted_mean", 
        help="Weights is between [0,1].", 
        type=bool,
        default=False
    )
    parser.add_argument(
        "-o",
        "--output_path", 
        help="Output Path.", 
        type=str
    )
    parser.add_argument(
        "-y",
        "--yaml", 
        help="Write in YAML.", 
        type=bool,
        default=False
    )

    args = parser.parse_args()
    seed_everything(args.seed_everything)

    if args.weighted_mean and args.ter:
        args.ter = False
    
    human_scores = SystemsScores.read_human_scores(args.human_scores_file)
    metrics_scores, metrics = SystemsScores.read_metrics_scores(args.metrics_scores_file)
    systems_scores = SystemsScores(human_scores,metrics_scores,metrics,args.human_scores_file,args.metrics_scores_file)

    if systems_scores.has_systems():
        study = StudyWeights(systems_scores,args.seed_everything,args.trials)
        study.optimize_weights(args.ter, args.weighted_mean)
        if args.output_path:
            study.write_files(args.output_path,args.yaml,args.ter,args.weighted_mean)