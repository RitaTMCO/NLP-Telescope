# -*- coding: utf-8 -*-
# Copyright (C) 2020 Unbabel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from typing import List, Dict

import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly
import streamlit as st
import random
import spacy
import io
import zipfile
from PIL import Image

from streamlit import runtime
from sklearn.metrics import confusion_matrix, multilabel_confusion_matrix, ConfusionMatrixDisplay
from telescope.testset import MultipleTestset
from telescope.metrics import (
    Precision, 
    Recall, 
    FDRate,
    FPRate,
    FORate,
    FNRate,
    NPValue,
    TNRate
)
from telescope.metrics.result import MultipleMetricResults
from telescope.utils import (
    FILENAME_SYSTEM_LEVEL_SCORES,
    FILENAME_ANALYSIS_METRICS_STACKED,
    FILENAME_ERROR_TYPE_ANALYSIS,
    FILENAME_SIMILAR_SOURCE_SENTENCES,
    FILENAME_DISTRIBUTION_SEGMENT,
    FILENAME_SEGMENT_COMPARISON,
    FILENAME_BOOTSTRAP,
    FILENAME_RATES,
    FILENAME_ANALYSIS_LABELS
)

T1_COLOR = "#9ACD32"
T2_COLOR = "#56C3FF"
T3_COLOR = "#FFD966"
T4_COLOR = "#DB6646"

ROTATION = 90

def buckets_ratio(number_of_systems:int):
    ratio_font = int((number_of_systems)/4)
    ratio_r = int((number_of_systems)%4)
    ratio_bar = int((number_of_systems)/2)
    ratio_fig = int((number_of_systems)/2) + ratio_r + ratio_font + ratio_bar
    return ratio_font, ratio_r, ratio_bar, ratio_fig

def calculate_color(number_of_labels:int, rgb=False):
    interval = np.linspace(0.0, 1.0, number_of_labels)
    if number_of_labels <= 10:
        colors = plt.cm.tab10(interval)
    elif number_of_labels <= 20:
        colors = plt.cm.tab20b(interval)
    elif number_of_labels <= 40:
        inter1 = np.linspace(0.0, 1.0, int(number_of_labels/2))
        inter2 = np.linspace(0.0, 1.0, number_of_labels-int(number_of_labels/2))
        colors = np.vstack((plt.cm.tab20b(inter1), plt.cm.tab20c(inter2)))
    else:
        colors = plt.cm.gist_rainbow(interval)

    if rgb:
        colors_rgb = []
        for i in range(number_of_labels):
            r,g,b = colors[i][0],colors[i][1],colors[i][2]
            colors_rgb.append("rgb(" + str(int(255 * r)) + "," + str(int(255 * g)) + "," + str(int(255 * b)) +")")
        return colors_rgb

    return colors

def create_and_save_plot_zip(path:str, saving_zip:zipfile.ZipFile, plot:plt):   
    image_bytes = io.BytesIO()
    plot.savefig(image_bytes, bbox_inches='tight', format="png")
    image = image_bytes.getvalue()
    saving_zip.writestr(path , image)
    image_bytes.close()

def save_plot(saving_dir:str, filename:str, plot:plt):  
    if not os.path.exists(saving_dir):
        os.makedirs(saving_dir)
    plot.savefig(saving_dir + "/" + filename, bbox_inches='tight')


def create_and_save_table_zip(path:str, saving_zip:zipfile.ZipFile, table:pd.DataFrame):   
    saving_zip.writestr(path, table.to_csv())

def save_table(saving_dir:str, filename:str, table:pd.DataFrame):    
    if not os.path.exists(saving_dir):
        os.makedirs(saving_dir)
    table.to_csv(saving_dir + "/" + filename)
    


###################################################
############| Plots for N systems |################
###################################################

def download_data_zip(label:str, data:bytes, filename:str, key:str, column=None):
    if column != None:
        column.download_button( 
            label=label,
            data=data,
            file_name=filename,
            mime="application/zip",
            key = key
        )
    else:
        st.download_button( 
            label=label,
            data=data,
            file_name=filename,
            mime="application/zip",
            key = key
        )

def download_data_csv(label:str, data:pd.DataFrame, filename:str, key:str, column=None):
    if column != None:
        column.download_button( 
            label=label,
            data=data.to_csv(),
            file_name=filename,
            mime="text/csv",
            key = key
        )
    else:
        st.download_button( 
            label=label,
            data=data.to_csv(),
            file_name=filename,
            mime="text/csv",
            key = key
        )

def analysis_bucket(scores_dict: Dict[str,List[float]], systems_names: List[str], labels:List[str], title:str, y_label:str):
    number_of_systems = len(systems_names)
    number_of_labels = len(labels)
    scores_label = list(scores_dict.values())
    names = tuple(systems_names)

    ratio_font, ratio_r, ratio_bar, ratio_fig = buckets_ratio(number_of_systems)
    r = [(i+ ratio_r) * number_of_systems for i in range(number_of_systems)]

    barWidth = 0.85 + ratio_bar
    font= 20 + ratio_font
    color = "black"

    plt.figure(figsize=(12+ratio_fig,10+ratio_fig))
    plt.clf()

    colors = calculate_color(number_of_labels)

    axs = [plt.bar(r, scores_label[0], edgecolor="white", width=barWidth, color=colors[0])]

    for i in range(1, number_of_labels):
        bottom = np.array([0.0 for _ in range(number_of_systems)])
        for scores_per_system in scores_label[:i]:
            scores = []
            for j in range(number_of_systems):
                if (scores_per_system[j] >= 0 and scores_label[i][j] < 0) or (scores_per_system[j] < 0 and scores_label[i][j] >= 0):
                    scores.append(0.0)
                else:
                    scores.append(scores_per_system[j])
 
            bottom += np.array(scores)
        axs.append(plt.bar(r, scores_label[i], bottom=bottom, edgecolor="white", width=barWidth,color=colors[i]))
    
    for i in range(number_of_systems):
        for ax in axs:
            h = ax[i].get_height()
            plt.text(
            ax[i].get_x() + ax[i].get_width() / 2.0,
            h / 2.0 + ax[i].get_y(),
            "{:.2f}".format(h),
            ha="center",
            va="center",
            color=color,
            fontsize=font,
            weight='bold'
            )

    plt.xticks(r, names,fontsize=18 + ratio_font,rotation = ROTATION)
    plt.yticks(fontsize=22 + ratio_font)
    plt.xlabel("Model",fontsize=22 + ratio_font)
    plt.ylabel(y_label,fontsize=22 + ratio_font)
    plt.legend(labels,fontsize = 15 + ratio_font,bbox_to_anchor=(1.02, 1))
    plt.title(title,fontsize=22+ ratio_font,pad=25)
    plt.axhline(linewidth=1, color='black')

    return plt



def system_level_scores_table(scores:pd.DataFrame,saving_dir: str = None, saving_zip:zipfile.ZipFile = None, column = None):
    if runtime.exists():
        if column != None:
            column.dataframe(scores)
        else:
            st.dataframe(scores)
        if saving_zip is not None and saving_dir is not None:
            create_and_save_table_zip(saving_dir + FILENAME_SYSTEM_LEVEL_SCORES, saving_zip, scores)

    elif saving_dir is not None:
        save_table(saving_dir,FILENAME_SYSTEM_LEVEL_SCORES,scores)


def analysis_metrics_stacked_bar_plot(multiple_metrics_results: List[MultipleMetricResults], systems_names:Dict[str, str], saving_dir: str = None, 
                                      saving_zip:zipfile.ZipFile = None, column = None):
    metrics = [m_res.metric for m_res in multiple_metrics_results]

    scores_per_metric = {m_res.metric: np.array([m_res.systems_metric_results[sys_id].sys_score for sys_id in list(systems_names.keys())]) 
            for m_res in multiple_metrics_results}

    plot = analysis_bucket(scores_per_metric, list(systems_names.values()), metrics, "Analysis of each metric", "Score") 

    if runtime.exists():
        if column == None:
            st.pyplot(plt)
        else:
            column.pyplot(plt)

        if saving_zip is not None and saving_dir is not None:
            create_and_save_plot_zip(saving_dir + FILENAME_ANALYSIS_METRICS_STACKED,saving_zip,plot)
    
    elif saving_dir is not None:
        save_plot(saving_dir, FILENAME_ANALYSIS_METRICS_STACKED,plot)

    plt.clf()
    plt.close()


#####################################################################################################################
#######################################################| NLG |#######################################################
#####################################################################################################################

def save_bootstrap_table(result:pd.DataFrame,sys_x_name:str, sys_y_name:str, saving_dir: str = None, saving_zip:zipfile.ZipFile = None):
    filename = sys_x_name + "-" + sys_y_name + FILENAME_BOOTSTRAP

    if runtime.exists():
        if saving_zip is not None and saving_dir is not None:
            saving_zip.writestr(saving_dir + filename, result.to_csv())

    elif saving_dir is not None:
        save_table(saving_dir, filename,result)

def sentences_similarity(src:List[str], output:str, language:str, saving_dir:str=None, saving_zip:zipfile.ZipFile=None, 
                         min_value:float=0.0,max_value:float=1.0):
    
    def remove_stop_words_and_punct(text:str,nlp):
        final_text = ""
        doc = nlp(text.lower())
        for token in doc:
            if not token.is_stop and not token.is_punct:
                final_text += " " + token.text
        return nlp(final_text)

    if language == "en":
        nlp = spacy.load("en_core_web_lg")
    elif language == "pt":
        nlp = spacy.load("pt_core_news_lg")
    else:
        return None

    docs_src = [remove_stop_words_and_punct(seg,nlp) for seg in src]
    docs_output = [remove_stop_words_and_punct(seg,nlp) for seg in output]
    num_seg_src = len(docs_src)

    table = []

    if runtime.exists():
        min_value,max_value = st.slider(
                    "Minimum and maximum similarity value", 0.0, 1.0, value=(0.0, 1.0), step=0.05, key="similarity")

    for seg_i in range(num_seg_src):
        if len(table) == 10:
            break
        doc_src = docs_src[seg_i]
        if not doc_src:
            continue 
        score = 0
        for doc_out in docs_output:
            score = doc_src.similarity(doc_out)
            if score >= min_value and score <= max_value:
                table.append([seg_i+1,src[seg_i]])
                break
    
    if len(table) != 0:
        filename = str(min_value) + "-" + str(max_value) + FILENAME_SIMILAR_SOURCE_SENTENCES

        df = pd.DataFrame(np.array(table), columns=["line", "source segment"])

        if runtime.exists():
            if df is not None:
                st.dataframe(df)
                if saving_dir and saving_zip:
                    create_and_save_table_zip(saving_dir + filename,saving_zip,df)

        elif saving_dir is not None:
            if df is not None:
                save_table(saving_dir, filename,df)
    else:
        if runtime.exists():
            st.warning("Segments not found")
                


def update_multiple_buckets(
    systems_results_seg_scores: Dict[str, List[float]],
    systems_names: List[str],
    crit_err_thr: float = 0.0,
    major_err_thr: float = 0.3,
    minor_err_thr: float = 0.6,
):

    number_of_systems = len(systems_names)
    total = len(list(systems_results_seg_scores.values())[0])

    no_err, minor_err, major_err, crit_err = {}, {}, {}, {}

    for system, seg_scores in systems_results_seg_scores.items():
        n_no_err = 0
        n_minor_err = 0
        n_major_err = 0
        n_crit_err = 0

        for score in seg_scores:
            if score >= minor_err_thr:
                n_no_err += 1
            elif score >= major_err_thr:
                n_minor_err += 1
            elif score >= crit_err_thr:
                n_major_err += 1
            else:
                n_crit_err += 1

        assert (
        total
        == (n_no_err + n_minor_err + n_major_err + n_crit_err)
        )

        n_no_err = (n_no_err / total) * 100
        n_minor_err = (n_minor_err / total) * 100
        n_major_err = (n_major_err / total) * 100
        n_crit_err = (n_crit_err / total) * 100

        no_err.update({system:n_no_err})
        minor_err.update({system:n_minor_err})
        major_err.update({system:n_major_err})
        crit_err.update({system:n_crit_err})

    ratio_font, ratio_r, ratio_bar, ratio_fig = buckets_ratio(number_of_systems)
    r = [(i+ ratio_r)* number_of_systems for i in range(number_of_systems)]

    plt.figure(figsize=(12+ratio_fig,10+ratio_fig))
    
    raw_data = {
        "T4Bars": list(crit_err.values()),
        "T3Bars": list(major_err.values()),
        "T2Bars": list(minor_err.values()),
        "T1Bars": list(no_err.values()),
    }
    df = pd.DataFrame(raw_data)

    T4Bars = raw_data["T4Bars"]
    T3Bars = raw_data["T3Bars"]
    T2Bars = raw_data["T2Bars"]
    T1Bars = raw_data["T1Bars"]

    # plot
    barWidth = 0.85 + ratio_bar
    font = 20 + ratio_font
    color = "black"
    names = tuple(systems_names)
    plt.clf()
    
    ax1 = plt.bar(r, T4Bars, color=T4_COLOR, edgecolor="white", width=barWidth)
    ax2 = plt.bar(
        r, T3Bars, bottom=T4Bars, color=T3_COLOR, edgecolor="white", width=barWidth
    )
    ax3 = plt.bar(
        r,
        T2Bars,
        bottom=[i + j for i, j in zip(T4Bars, T3Bars)],
        color=T2_COLOR,
        edgecolor="white",
        width=barWidth,
    )
    ax4 = plt.bar(
        r,
        T1Bars,
        bottom=[i + j + k for i, j, k in zip(T4Bars, T3Bars, T2Bars)],
        color=T1_COLOR,
        edgecolor="white",
        width=barWidth,
    )

    for r1, r2, r3, r4 in zip(ax1, ax2, ax3, ax4):
        h1 = r1.get_height()
        h2 = r2.get_height()
        h3 = r3.get_height()
        h4 = r4.get_height()

        plt.text(
            r1.get_x() + r1.get_width() / 2.0,
            h1 / 2.0,
            "{:.2f}".format(h1),
            ha="center",
            va="center",
            color=color,
            fontsize=font,
            weight='bold'
        )
        plt.text(
            r2.get_x() + r2.get_width() / 2.0,
            h1 + h2 / 2.0,
            "{:.2f}".format(h2),
            ha="center",
            va="center",
            color=color,
            fontsize=font,
            weight='bold'
        )
        plt.text(
            r3.get_x() + r3.get_width() / 2.0,
            h1 + h2 + h3 / 2.0,
            "{:.2f}".format(h3),
            ha="center",
            va="center",
            color=color,
            fontsize=font,
            weight='bold'
        )
        plt.text(
            r4.get_x() + r4.get_width() / 2.0,
            h1 + h2 + h3 + h4 / 2.0,
            "{:.2f}".format(h4),
            ha="center",
            va="center",
            color=color,
            fontsize=font,
            weight='bold'
        )

    # Custom x axis
    plt.xticks(r, names,fontsize=18 + ratio_font,rotation = ROTATION)
    plt.yticks(fontsize=22 + ratio_font)
    plt.xlabel("Model",fontsize=22 + ratio_font)

    return plt



def plot_bucket_multiple_comparison(multiple_result: MultipleMetricResults, systems_names: List[str], saving_dir: str = None, saving_zip: str = None) -> None:

    filename = multiple_result.metric + FILENAME_ERROR_TYPE_ANALYSIS

    systems_results_seg_scores = {
        system: metric_system.seg_scores
        for system, metric_system in multiple_result.systems_metric_results.items()
    }

    min_score = min(
        [ min(seg_scores) 
        for seg_scores in list(systems_results_seg_scores.values())
        ]
    )

    if multiple_result.metric == "COMET":
        values = [0.1,0.3,0.7]
        limits = [0.3,0.5,0.8]
        step = 0.1
        
    elif multiple_result.metric == "BERTScore":
        values = [0.50,0.70,0.90]
        limits = [0.50,0.70,0.90]
        step = 0.05 
    
    if min_score >= limits[0]:
        min_score = 0.0

    plot = update_multiple_buckets(
            systems_results_seg_scores,
            systems_names,
            values[0],
            values[1],
            values[2],
        )   


    if runtime.exists():

        def define_value(bucket_1,bucket_2,value):
            #if (bucket_2!=None and bucket_1 < bucket_2) or st.session_state["reset_settings"]:
            if (bucket_2!=None and bucket_1 < bucket_2):
                return value        
            elif st.session_state["first_time_error"] < 4:
                st.session_state["first_time_error"] += 1
                return value
            else:
                bucket_1


        if ("red_bucket_" + multiple_result.metric not in st.session_state or 
            "yellow_bucket_" + multiple_result.metric not in st.session_state or 
            "blue_bucket_" + multiple_result.metric not in st.session_state):
            st.session_state["red_bucket_"+ multiple_result.metric] = values[0]
            st.session_state["yellow_bucket_"+ multiple_result.metric] = values[1]
            st.session_state["blue_bucket_"+ multiple_result.metric] = values[2]
    
        if "first_time_error" not in st.session_state:
            st.session_state["first_time_error"] = 1

        st.markdown("""
                    
                    This stacked bar plot separates segments into buckets based on the percentage of segments whose segment-level score 
                    is between the minimum and maximum threshold. 

                    Each bucket has the the minimum and maximum threshold and the :red[red bucket] minimum threshold is the lowest segment-level score 
                    of all systems. You can change the maximum threshold of :red[red bucket], :orange[yellow bucket] and :blue[blue bucket] in sliders.

                    The maximum threshold of :red[red bucket] is the minimum threshold of :orange[yellow bucket], the 
                    maximum threshold of :orange[yellow bucket] is the minimum threshold of :blue[blue bucket] and the 
                    maximum threshold of :blue[blue bucket] is the minimum threshold of :green[green bucket].

                    """)
        
        #_, reset,_ = st.columns(3)
        #if reset.button("Reset settings", key="reset_settings"):
            #st.session_state["red_bucket_"+ multiple_result.metric] = values[0]
            #st.session_state["yellow_bucket_"+ multiple_result.metric] = values[1]
            #st.session_state["blue_bucket_"+ multiple_result.metric] = values[2]
        
        col1, col2, col3 = st.columns(3)

        with col1:
                v1 = define_value(st.session_state["red_bucket_"+ multiple_result.metric],None,values[0])
                st.session_state["red_bucket_"+ multiple_result.metric] = st.slider(
                    "Red bucket max threshold", min_score, limits[0], value=v1, step=step, key="bucket1")

        with col2:
                v2 = define_value(st.session_state["yellow_bucket_"+ multiple_result.metric],st.session_state["red_bucket_"+ multiple_result.metric],values[1])
                st.session_state["yellow_bucket_"+ multiple_result.metric] = st.slider(
                    "Yellow bucket max threshold", st.session_state["red_bucket_"+ multiple_result.metric], limits[1], value=v2, step=step, key="bucket2")   

        with col3:
                v3 = define_value(st.session_state["blue_bucket_"+ multiple_result.metric],st.session_state["yellow_bucket_"+ multiple_result.metric],values[2])
                st.session_state["blue_bucket_"+ multiple_result.metric] = st.slider(
                    "Blue bucket max threshold", st.session_state["yellow_bucket_"+ multiple_result.metric], limits[2], value=v3, step=step, key="bucket3")


        left, right = st.columns([0.3,0.7])
        right.pyplot(update_multiple_buckets(systems_results_seg_scores,systems_names, 
                                             st.session_state["red_bucket_"+ multiple_result.metric], 
                                             st.session_state["yellow_bucket_"+ multiple_result.metric], 
                                             st.session_state["blue_bucket_"+ multiple_result.metric]))
        plt.clf()
        plt.close()
        left.markdown(
                    """
                    The bucket analysis separates segments according to 4 different categories:
            
                    - **:green[Green bucket:]** Segments without errors.
                    - **:blue[Blue bucket:]** Segments with minor errors.
                    - **:orange[Yellow bucket:]** Segments with major errors.
                    - **:red[Red bucket:]** Segments with critical errors.
                    """
        )

        if saving_dir and saving_zip:
            create_and_save_plot_zip(saving_dir + filename, saving_zip,
                                     update_multiple_buckets(systems_results_seg_scores,systems_names, 
                                             st.session_state["red_bucket_"+ multiple_result.metric], 
                                             st.session_state["yellow_bucket_"+ multiple_result.metric], 
                                             st.session_state["blue_bucket_"+ multiple_result.metric]))


    elif saving_dir is not None:
        save_plot(saving_dir, filename, plot)


def plot_multiple_distributions( multiple_result: MultipleMetricResults, sys_names: List[str], saving_dir: str = None, 
                                saving_zip: zipfile.ZipFile = None, test:str=False) -> bool:
    scores_list = [
        metric_system.seg_scores 
        for metric_system in list(multiple_result.systems_metric_results.values())]
    scores = np.array(scores_list).T
    hist_data = [scores[:, i] for i in range(scores.shape[1])]
    number_of_systems = len(multiple_result.systems_metric_results)
    try:
        colors = calculate_color(number_of_systems,True)
        fig = ff.create_distplot(
            hist_data,
            sys_names,
            bin_size=[0.1 for _ in range(scores.shape[1])],
            colors = colors
        ) 

        fig.update_layout(xaxis_title="Score", yaxis_title="Probability Density")
        fig.update_xaxes(title_standoff = 40)


        if runtime.exists() and not test:
            st.markdown("This displot shows the distribution of segment-level scores. It is composed of histogram, kernel density estimation curve and rug plot.")
            st.plotly_chart(fig)

            if saving_dir and saving_zip:
                saving_zip.writestr(saving_dir + FILENAME_DISTRIBUTION_SEGMENT , plotly.io.to_html(fig))
        
        elif saving_dir is not None and not test:
            if not os.path.exists(saving_dir):
                os.makedirs(saving_dir)
            fig.write_html(saving_dir + "/" + FILENAME_DISTRIBUTION_SEGMENT)
        return True
    
    except np.linalg.LinAlgError:
        if runtime.exists():
            st.warning("One of outputs is same as the selected refrence. Please, remove the output or the reference.")
        return False
    


def plot_multiple_segment_comparison(multiple_result: MultipleMetricResults, system_x: List[str], system_y:List[str], source: bool = False, 
                                     saving_dir: str = None, saving_zip: zipfile.ZipFile = None) -> None:


    sys_x_id, sys_x_name = system_x
    sys_y_id, sys_y_name = system_y

    filename = sys_x_name + "-" + sys_y_name + FILENAME_SEGMENT_COMPARISON

    scores = np.array(
        [multiple_result.systems_metric_results[sys_x_id].seg_scores, 
        multiple_result.systems_metric_results[sys_y_id].seg_scores]).T

    chart_data = pd.DataFrame(scores, columns=["x_score", "y_score"])
    chart_data["difference"] = np.absolute(scores[:, 0] - scores[:, 1])
    if source:
        chart_data["source"] = multiple_result.src
    chart_data["reference"] = multiple_result.ref
    chart_data["x"] = multiple_result.systems_metric_results[sys_x_id].seg_scores
    chart_data["y"] = multiple_result.systems_metric_results[sys_y_id].seg_scores

    if source:
        tool = ["x", "y", "reference", "difference", "source", "x_score", "y_score"]
    else:
        tool = ["x", "y", "reference", "difference", "x_score", "y_score"]

    c = (alt.Chart(chart_data, width="container")
            .mark_circle()
            .encode(
                x="x_score",
                y="y_score",
                size="difference",
                color=alt.Color("difference"),
                tooltip=tool,
            )
        )
    
    if runtime.exists():
        st.altair_chart(c, use_container_width=True)
        if saving_dir and saving_zip:
            saving_zip.writestr(saving_dir + filename, c.properties(width=1300, height=600).to_html())
        
    elif saving_dir is not None:
        if not os.path.exists(saving_dir):
            os.makedirs(saving_dir)
        c.properties(width=1300, height=600).save(
            saving_dir + "/" + filename, 
            format="html"
        )


################################################################################################################################
#######################################################| Classification |#######################################################
################################################################################################################################


def confusion_matrix_image():

    image = Image.open('data/confusion_matrix.png')
    left,right = st.columns([0.7,0.3])
    
    left.image(image, caption="Confusion matrix (adapted from Verma and Rubin (2018)).")
    right.markdown(
            """
            **:blue[PPV:]** Positive Predictive Value or Precision.     
            **:blue[TPR:]** True Positive Rate or Recall.   
            **:blue[FDR:]** False Discovery Rate.    
            **:blue[FPR:]** False Positive Rate.   
            **:blue[FOR:]** False Omission Rate.   
            **:blue[FNR:]** False Negative Rate.   
            **:blue[NPV:]** Negative Predictive Value.   
            **:blue[TNR:]** True Negative Rate.   
            """
        )


def confusion_matrix_of_system(true: List[str], pred: List[str], labels: List[str], system_name:str, show:bool = False, saving_dir: str = None, 
                               saving_zip:zipfile.ZipFile=None):    
    
    matrix = confusion_matrix(true, pred, labels=labels)
    conf_mat = ConfusionMatrixDisplay(confusion_matrix=matrix,display_labels=labels)
    conf_mat.plot()
    filename = "confusion-matrix-" + system_name.replace(" ", "_") + ".png"
    ratio = int((len(labels)/5)) * 3

    _, ax = plt.subplots(figsize=(5 + ratio, 5 + ratio))
    conf_mat.plot(ax=ax)

    plt.title("Confusion Matrix of " + system_name)

    if runtime.exists():
        if show:
            st.pyplot(plt)
        if saving_dir and saving_zip:
            create_and_save_plot_zip(saving_dir + filename, saving_zip, plt)
    elif saving_dir is not None:
        save_plot(saving_dir, filename, plt)

    plt.clf()
    plt.close()



def confusion_matrix_focused_on_one_label(true: List[str], pred: List[str], label: str, labels: List[str], system_name:str, show:bool = False,
                                          saving_dir: str = None, saving_zip:zipfile.ZipFile=None):  
    
    matrix = multilabel_confusion_matrix(true, pred, labels=labels)
    index = labels.index(label)
    name = ["other labels"] + [label] 

    filename = system_name.replace(" ", "_") + "-label-" + label + ".png"
    
    conf_mat = ConfusionMatrixDisplay(confusion_matrix=matrix[index],display_labels=name)
    conf_mat.plot()
    plt.title("Confusion Matrix of " + system_name)

    if runtime.exists():
        if show:
            st.pyplot(plt)
        if saving_dir and saving_zip:
            create_and_save_plot_zip(saving_dir + filename, saving_zip, plt)
    elif saving_dir is not None:
        save_plot(saving_dir, filename, plt)

    plt.clf()
    plt.close()



def rates_table(labels:List[str],true:List[str],pred:List[str],saving_dir:str=None, saving_zip: zipfile.ZipFile = None, show:bool = False):
    table = { "PPV" : [], "TPR": [], "FDR": [], "FPR":[], "FOR": [], "FNR":[], "NPV": [], "TNR": [] }
    
    precison_labels = list(Precision(labels=labels).score([], pred, true).seg_scores)
    recall_labels = list(Recall(labels=labels).score([], pred, true).seg_scores)
    fdr_labels = list(FDRate(labels=labels).score([], pred, true).seg_scores)
    fpr_labels = list(FPRate(labels=labels).score([], pred, true).seg_scores)
    for_labels = list(FORate(labels=labels).score([], pred, true).seg_scores)
    fnr_labels = list(FNRate(labels=labels).score([], pred, true).seg_scores)
    npv_labels = list(NPValue(labels=labels).score([], pred, true).seg_scores)
    tnr_labels = list(TNRate(labels=labels).score([], pred, true).seg_scores)

    num = len(labels)
    for i in range(num):
        table["PPV"].append(precison_labels[i])
        table["TPR"].append(recall_labels[i])
        table["FDR"].append(fdr_labels[i])
        table["FPR"].append(fpr_labels[i])
        table["FOR"].append(for_labels[i])
        table["FNR"].append(fnr_labels[i])
        table["NPV"].append(npv_labels[i])
        table["TNR"].append(tnr_labels[i])

    df = pd.DataFrame(table)
    df.index = labels

    if runtime.exists():
        if show:
            st.dataframe(df)
        if saving_zip is not None and saving_dir is not None:
            create_and_save_table_zip(saving_dir + FILENAME_RATES, saving_zip, df)
    elif saving_dir is not None:
        save_table(saving_dir,FILENAME_RATES,df)




def incorrect_examples(testset:MultipleTestset, system:str, system_name:str, num:int, incorrect_ids: List[str] = [] ,table: List[List[str]] = [], ids:List[int]=[],
                       saving_dir:str = None, all_examples:bool = False):
    src = testset.src
    true = testset.ref
    pred = testset.systems_output[system]
    filename = system_name.replace(" ","_") + "-incorrect-examples.csv"
    
    n = len(true)
    if not ids:
        ids = random.sample(range(n),n)
    
    if all_examples:
        ids = [i for i in range(n)]
        incorrect_ids = []
        table = []

    lines = [int(id.split("\t")[-1]) for id in incorrect_ids]
    
    for i in ids:
        if len(incorrect_ids) == num:
            break
        if (true[i] != pred[i]) and ("line" + "\t" + str(i+1) not in incorrect_ids):
            incorrect_ids.append("line" + "\t" + str(i+1))
            lines.append(i+1)
            table.append([src[i], true[i], pred[i]])
    
    if len(incorrect_ids) != 0:
        df = pd.DataFrame(np.array(table), index=lines, columns=["example", "true label", "predicted label"])
        if saving_dir is not None:
            if not os.path.exists(saving_dir):
                os.makedirs(saving_dir)
            df.to_csv(saving_dir + "/" + filename)
        return df.sort_index()
    else:
        return None


def analysis_labels_plot(seg_scores_dict:Dict[str,List[float]], metric:str, sys_names: List[str], labels:List[str], saving_dir: str = None, saving_zip: zipfile.ZipFile = None):

    filename = metric + FILENAME_ANALYSIS_LABELS
    plt = analysis_bucket(seg_scores_dict, sys_names, labels, "Results by label (with " + metric + " metric)" , "Score") 
    if runtime.exists():
        st.subheader("Stacked bar plot")
        st.pyplot(plt)
        if saving_dir and saving_zip:
            create_and_save_plot_zip(saving_dir + filename, saving_zip, plt)
    elif saving_dir is not None:
        save_plot(saving_dir, filename, plt)
    plt.clf()
    plt.close()

def analysis_labels_table(seg_scores_dict:Dict[str,List[float]], metric:str, sys_names: List[str], saving_dir: str = None, saving_zip: zipfile.ZipFile = None, col=None):
    filename = metric + "_results-by-label-table.csv"
    df = pd.DataFrame.from_dict(seg_scores_dict)
    df.index = sys_names
    if runtime.exists():
        st.subheader("Table")
        st.dataframe(df)
        if saving_dir and saving_zip:
            create_and_save_table_zip(saving_dir + filename,saving_zip,df)
    elif saving_dir is not None:
        save_table(saving_dir,filename,df)

def analysis_labels(result: MultipleMetricResults, sys_names: List[str], labels:List[str], saving_dir: str = None, saving_zip: zipfile.ZipFile = None):
    seg_scores_list = [list(result_sys.seg_scores) for result_sys in list(result.systems_metric_results.values())]
    
    if any(seg_scores_list):
    
        seg_scores_dict = {label: np.array([seg_scores[i] for seg_scores in seg_scores_list])  for i, label in enumerate(labels)}
        metric = result.metric
        analysis_labels_table(seg_scores_dict,metric,sys_names,saving_dir,saving_zip)
        analysis_labels_plot(seg_scores_dict,metric,sys_names,labels,saving_dir,saving_zip)


######################################################################################################################
#######################################################| BIAS |#######################################################
######################################################################################################################


def number_of_correct_labels_of_each_system(sys_names: List[str], true: List[str], systems_pred: List[List[str]], labels: List[str], 
                                            saving_dir: str = None, saving_zip: zipfile.ZipFile = None):
    
    num_of_systems = len(sys_names)
    number_of_correct_labels = { label: np.array([0 for _ in range(num_of_systems)]) for label in labels }
    filename = "number-of-correct-labels-of-each-system.png"

    for sys_i in range(num_of_systems):
        pred = systems_pred[sys_i]
        for t, p in zip(true,pred):
            if t == p:
                number_of_correct_labels[t][sys_i] += 1
    
    plt = analysis_bucket(number_of_correct_labels, sys_names, labels, "Number of times each label was identified correctly", "Number of times")
    if runtime.exists():
        st.pyplot(plt)
        if saving_dir and saving_zip:
            create_and_save_plot_zip(saving_dir + filename, saving_zip, plt)
    elif saving_dir is not None:
        save_plot(saving_dir, filename, plt)
    plt.clf()
    plt.close()




def number_of_incorrect_labels_of_each_system(sys_names: List[str], true: List[str], systems_pred: List[List[str]], labels: List[str], 
                                              saving_dir: str = None, saving_zip: zipfile.ZipFile = None):
    
    num_of_systems = len(sys_names)
    number_of_incorrect_labels = { label: np.array([0 for _ in range(num_of_systems)]) for label in labels }
    filename = "number-of-incorrect-labels-of-each-system.png"

    for sys_i in range(num_of_systems):
        pred = systems_pred[sys_i]
        for t, p in zip(true,pred):
            if t != p:
                number_of_incorrect_labels[t][sys_i] += 1

    plt = analysis_bucket(number_of_incorrect_labels, sys_names, labels, "Number of times each label was identified incorrectly", "Number of times")
    if runtime.exists():
        st.pyplot(plt)
        if saving_dir and saving_zip:
            create_and_save_plot_zip(saving_dir + filename, saving_zip, plt)
    elif saving_dir is not None:
        save_plot(saving_dir, filename, plt)
    plt.clf()
    plt.close()



def bias_segments(system_name:str, ref:List[str], output_sys:List[str], gender_refs_seg: Dict[int, List[str]], gender_sys_seg: Dict[int, List[str]], 
                  text_groups_ref_per_seg: Dict[int, List[Dict[str,str]]],text_groups_sys_per_seg: Dict[int, List[Dict[str,str]]], 
                  ids: List[int], saving_dir:str = None):
        
    def gender_terms(text_groups: List[Dict[str,str]]):
        terms = ""
        for token in text_groups:
            terms += token["term"] + ":" + token["gender"] + ", "
        return terms[:-2]

    filename = system_name.replace(" ","_") + "-bias-segments.csv"
    n = len(gender_refs_seg)
    if not ids: 
        ids = random.sample(range(n),n)
    num = 20
    bias_segments = list()
    lines = list()
    table = list()
    for i in ids:
        if len(bias_segments) == num:
            break
        if (gender_refs_seg[i] != gender_sys_seg[i]) and ("line " + str(i+1) not in bias_segments):
            terms_ref = gender_terms(text_groups_ref_per_seg[i])
            terms_sys = gender_terms(text_groups_sys_per_seg[i])
            bias_segments.append("line " + str(i+1))
            lines.append(i+1)
            table.append([ref[i], output_sys[i], terms_ref, terms_sys])

    if len(bias_segments) != 0:
        df = pd.DataFrame(np.array(table), index=lines, columns=["reference", "system output", 
                                                    "identity term and its gender in reference", "identity term and its gender in output"])
        if saving_dir is not None:
            if not os.path.exists(saving_dir):
                os.makedirs(saving_dir)
            df.to_csv(saving_dir + "/" + filename)
        return df.sort_index()
    else:
        return None 

def all_identity_terms(system_name:str, gender_sys_seg: Dict[int, List[str]], gender_refs_seg: Dict[int, List[str]],text_groups_ref_per_seg: Dict[int, List[Dict[str,str]]],
                       text_groups_sys_per_seg: Dict[int, List[Dict[str,str]]], saving_dir:str = None, saving_zip:str=None):

    def gender_terms(text_groups: List[Dict[str,str]]):
        terms = ""
        for token in text_groups:
            terms += token["term"] + ":" + token["gender"] + ", "
        return terms[:-2]

    filename = system_name.replace(" ","_") + "_all_identity_terms_matched.csv"
    n = len(gender_refs_seg)
    bias_segments = list()
    lines = list()
    table = list()
    for i in range(n):
        terms_ref = gender_terms(text_groups_ref_per_seg[i])
        terms_sys = gender_terms(text_groups_sys_per_seg[i])
        bias_segments.append("line " + str(i+1))
        lines.append(i+1)
        if (gender_refs_seg[i] != gender_sys_seg[i]):
            has_bias = "Yes"
        else:
            has_bias = "No"

        table.append([has_bias, terms_ref, terms_sys])

    if len(bias_segments) != 0:
        df = pd.DataFrame(np.array(table), index=lines, columns=["has_bias", "identity term and its gender in reference", "identity term and its gender in output"])
        
        if runtime.exists():
            if saving_zip is not None and saving_dir is not None:
                create_and_save_table_zip(saving_dir + filename, saving_zip, df)
        
        elif saving_dir is not None:
            if not os.path.exists(saving_dir):
                os.makedirs(saving_dir)
            df.to_csv(saving_dir + "/" + filename)
        return df.sort_index()
    else:
        return None 

def table_identity_terms_found(name:str, identity_terms_found_per_seg:Dict[int, List[dict]], saving_dir:str = None,saving_zip:str=None):

    def gender_terms(text_groups: List[Dict[str,str]]):
        terms = ""
        for token in text_groups:
            terms += token["term"] + ":" + token["gender"] + ", "
        return terms[:-2]

    filename = name.replace(" ","_") + "_all_identity_terms_found.csv"
    n = len(identity_terms_found_per_seg)
    segments = list()
    lines = list()
    table = list()
    for i in range(n):
        terms_ref = gender_terms(identity_terms_found_per_seg[i])
        segments.append("line " + str(i+1))
        lines.append(i+1)
        table.append([terms_ref])

    if len(segments) != 0:
        df = pd.DataFrame(np.array(table), index=lines, columns=["identity term and its gender"])
        if runtime.exists():
            if saving_zip is not None and saving_dir is not None:
                create_and_save_table_zip(saving_dir + filename, saving_zip, df)
        elif saving_dir is not None:
            if not os.path.exists(saving_dir):
                os.makedirs(saving_dir)
            df.to_csv(saving_dir + "/" + filename)
        return df.sort_index()
    else:
        return None 

    