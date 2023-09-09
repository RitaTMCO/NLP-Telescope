import json 
import optuna
import argparse
import os
import numpy as np
import pandas as pd
import scipy.stats as stats
from itertools import combinations
from typing import Dict, List
import matplotlib.pyplot as plt


mt_metrics = [
      "COMET",
      "BLEU",
      "chrF",
      "ZeroEdit",
      "BERTScore",
      "TER",
      "GLEU"
]


u_metrics = [
        "Average",
        "Median",
        "Social Choice Theory",
        "Weighted Sum 12",
        "Weighted Sum 24",
        "Weighted Sum 36",
        "Weighted Sum 12 TER",
        "Weighted Sum 24 TER",
        "Weighted Sum 36 TER",
        "Weighted Mean 12",
        "Weighted Mean 24",
        "Weighted Mean 36",
]

all_metrics = u_metrics + mt_metrics



def bars_ascending_plot(input_file:str, domain:str, ref:str, languages_pair:str):
    data_file = pd.read_csv(input_file +  "/evaluation.csv")
    data = data_file.to_dict("index", index="metrics")
    o_file_name = ref.replace(".","-").replace("-txt","")

    correlations_data = {'System Accuracy':{}, 'Pearson':{}}
    correlations = {'System Accuracy':{}, 'Pearson':{}}
    
    for data in list(data.values()):
        for cor in list(correlations_data.keys()):
            name = data["metric"]
            correlations_data[cor][name] = data[cor]
    
    for cor in list(correlations.keys()):
        for m in all_metrics:
            correlations[cor][m] = correlations_data[cor][m]

    
    metrics = list(correlations[cor].keys())
    n = len(metrics)-len(mt_metrics) + 1
    r = np.array([i for i in range(n)])

    size = 15

    for name, cor in correlations.items():
        order_metrics = sorted(cor, key=cor.get, reverse=True)
        metrics = []
        colors = []
        mt = 0
        cor_scores = []
        for m in order_metrics:
            if m in mt_metrics and mt == 1:
                continue
            elif m in mt_metrics and mt == 0:
                colors.append("orange")
                mt +=1
            else:
                colors.append("#33b2ff")
            
            metrics.append(m)
            cor_scores.append(cor[m])
        
        plt.figure(figsize=(10,5))
        plt.clf()
        axs = plt.bar(r*1.05, cor_scores, edgecolor="white", width=0.9, color=colors)
        plt.axhline(y = 0.75, color = 'r', linestyle = '-')

        for i in range(len(metrics)):
            h = axs[i].get_height()
            plt.text(axs[i].get_x() + axs[i].get_width() / 2.0, 0.05, metrics[i], ha="center",color="black",fontsize=size, rotation=90)
        plt.yticks(fontsize=size)
        
        plt.xticks(r, ["" for _ in range(len(metrics))],fontsize=30, weight='bold')
        plt.ylabel("Correlation coefficient",fontsize=size)
        plt.title(name + " in domain " + domain + " (" + ref + ")",fontsize=size, pad=25)
        plt.axhline(linewidth=1, color='black')
        plt.savefig(input_file +  "/" + name + "_" + o_file_name + "_evaluation.png")
        plt.clf()
        plt.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_path",
        help="Input path",
        required=True,
        type=str
    ),
    parser.add_argument(
        "-p",
        "--languages_pair",
        help="Language pair (e.g. en-ru).",
        required=True,
        type=str
    )

    args = parser.parse_args()

    input = args.input_path + "/" + args.languages_pair + "/"

    for domain in os.listdir(input): 

        reference_path = input + domain + "/"

        for reference in os.listdir(reference_path): 

            input_path = reference_path + reference
            bars_ascending_plot(input_path, domain,reference,args.languages_pair)





