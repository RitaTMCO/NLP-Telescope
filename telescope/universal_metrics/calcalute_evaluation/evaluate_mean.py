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
        "Weighted Mean 1000",
        "Weighted Mean 3000",
        "Weighted Mean 5000",
        "Weighted Sum 1000",
        "Weighted Sum 3000",
        "Weighted Sum 5000",
]

all_metrics = u_metrics + mt_metrics





def calcualte_mean_per_domain(input_path:str, domain:str):

    a_correlations_data = {}


    for l in ["en-de", "en-ru", "zh-en"]: 
        input = input_path + "/" + l + "/" + domain + "/" 
        reference_path = input + "/"
        for reference in os.listdir(reference_path): 
            input_r = reference_path + reference
            data_file = pd.read_csv(input_r +  "/evaluation.csv")
            data = data_file.to_dict("index", index="metrics")
            o_file_name = reference.replace(".","-").replace("-txt","")

    
            for data in list(data.values()):
                name = data["metric"]
                if name not in a_correlations_data:
                    a_correlations_data[name] = []
                a_correlations_data[name].append(data["System Accuracy"])

    print(a_correlations_data)
    pd_dict = pd.DataFrame({metric:[sum(corr)/len(corr)] for metric, corr in a_correlations_data.items()},index=["Average of System Accuracy"])
    pd_dict.to_csv(input_path + "/average/domain/" + domain  + "_evaluation.csv")    
    return {metric:sum(corr)/len(corr) for metric, corr in a_correlations_data.items()}


def calcualte_mean_per_language_pair(input_path:str, languages_pair:str):

    a_correlations_data = {}
    input = input_path + "/" + languages_pair + "/"


    for domain in ["conversation", "ecommerce","news", "social"]: 
        reference_path = input + domain + "/"
        for reference in os.listdir(reference_path): 
            input_r = reference_path + reference

            data_file = pd.read_csv(input_r +  "/evaluation.csv")
            data = data_file.to_dict("index", index="metrics")
            o_file_name = reference.replace(".","-").replace("-txt","")

    
            for data in list(data.values()):
                name = data["metric"]
                if name not in a_correlations_data:
                    a_correlations_data[name] = []
                a_correlations_data[name].append(data["System Accuracy"])

    print(a_correlations_data)
    pd_dict = pd.DataFrame({metric:[sum(corr)/len(corr)] for metric, corr in a_correlations_data.items()},index=["Average of System Accuracy"])
    pd_dict.to_csv(input_path + "/average/language-pair/" + languages_pair  + "_evaluation.csv")
    return {metric:sum(corr)/len(corr) for metric, corr in a_correlations_data.items()}




def bars_ascending_plot(correlations_data:dict, t_name:str, output:str):

    met = list(correlations_data.keys())
    n = len(met)-len(mt_metrics) + 1
    r = np.array([i for i in range(n)])
    cor = {}

    size = 15

    for m in all_metrics:
        cor[m] = correlations_data[m]

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

    for i in range(len(metrics)):
        plt.text(axs[i].get_x() + axs[i].get_width() / 2.0, 0.05, metrics[i], ha="center",color="black",fontsize=size, rotation=90)
    plt.yticks(fontsize=size)
    
    plt.xticks(r, ["" for _ in range(len(metrics))],fontsize=30, weight='bold')
    plt.ylabel("Average of System Accuracy",fontsize=size)
    plt.title("Average of System Accuracy in " + t_name,fontsize=size, pad=25)
    plt.axhline(linewidth=1, color='black')
    plt.savefig(output + t_name  + "_evaluation.png")
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

    args = parser.parse_args()

    languages = ["en-de", "en-ru", "zh-en"]


    for l in languages:
        print(calcualte_mean_per_language_pair(args.input_path, l, ))
        bars_ascending_plot(calcualte_mean_per_language_pair(args.input_path, l), l, args.input_path + "/average/language-pair/")
    
    
    for domain in ["conversation", "ecommerce","news", "social"]:
        print(calcualte_mean_per_domain(args.input_path, domain))
        bars_ascending_plot(calcualte_mean_per_domain(args.input_path, domain), domain, args.input_path + "/average/domain/")

