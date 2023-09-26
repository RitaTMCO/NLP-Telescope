import click
import os
import streamlit as st
import numpy as np
import pandas as pd
import zipfile

from typing import List, Dict
from streamlit import runtime
from telescope.collection_testsets import CollectionTestsets
from telescope.metrics.metric import Metric
from telescope.multiple_plotting  import  download_data_csv

class UniversalMetricResult():
    def __init__(
        self,
        ref: List[str],
        system_output: List[str],
        metrics: List[Metric],
        universal_metric: str,
        title:str,
        rank: int,
        universal_score: float,
    ) -> None:
        self.ref = ref
        self.system_output = system_output
        self.metrics = metrics
        self.universal_metric = universal_metric
        self.title = title
        self.rank = rank
        self.universal_score = universal_score

class MultipleUniversalMetricResult():
    def __init__(
        self,
        systems_universal_metrics_results: Dict[str,UniversalMetricResult], # {id_of_systems:UniversalMetricResult}
    ) -> None:
        ref_x = list(systems_universal_metrics_results.values())[0].ref
        metrics_x = list(systems_universal_metrics_results.values())[0].metrics
        universal_metric_x = list(systems_universal_metrics_results.values())[0].universal_metric
        title_x = list(systems_universal_metrics_results.values())[0].title

        for universal_metric_results in list(systems_universal_metrics_results.values()):
            assert universal_metric_results.ref == ref_x
            assert universal_metric_results.metrics == metrics_x
            assert universal_metric_results.universal_metric == universal_metric_x
            assert universal_metric_results.title == title_x
        
        self.ref = ref_x
        self.metrics = metrics_x
        self.universal_metric = universal_metric_x
        self.title = title_x
        self.systems_universal_metrics_results = systems_universal_metrics_results
        self.universal_filename = self.universal_metric + "_ranks_systems.csv"

    def results_to_dataframe(self,systems_names:Dict[str, str]) -> pd.DataFrame:
        summary = []
        ranks = []
        for sys_id, universal_metric_result in self.systems_universal_metrics_results.items():
            summary.append([systems_names[sys_id], universal_metric_result.universal_score])
            ranks.append("rank " + str(universal_metric_result.rank))

        df = pd.DataFrame(np.array(summary), index=ranks, columns=["System", "Score"])
        return df
    
    def plots_web_interface(self, collection_testsets:CollectionTestsets,ref_filename:str, sys_a:str="", sys_b:str=""):
        st.subheader(self.title)
        df = self.results_to_dataframe(collection_testsets.systems_names)
        st.dataframe(df)

        name = self.universal_filename + "_ranks_systems.csv"
        if self.universal_metric == "pairwise-comparison":
            name = self.universal_metric + "_" + "_".join([sys_a, sys_b]) + "_ranks_systems.csv"
            
        download_data_csv("Export ranks of systems",df,name,"ranks_download")
    
    def plots_cli_interface(self, collection_testsets:CollectionTestsets):
        click.secho("\nModels Rankings:", fg="yellow")
        df = self.results_to_dataframe(collection_testsets.systems_names)
        click.secho(str(df), fg="yellow")
        return df

    def dataframa_to_to_csv(self,collection_testsets:CollectionTestsets,ref_filename:str, sys_a:str="", sys_b:str="", 
                            saving_dir:str=None, saving_zip: zipfile.ZipFile = None):
        df = self.results_to_dataframe(collection_testsets.systems_names)

        filename = self.universal_filename
        if self.universal_metric == "pairwise-comparison":
            filename = self.universal_metric + "_" + "_".join([sys_a, sys_b]) + "_ranks_systems.csv"

        if runtime.exists() and saving_dir and saving_zip:
            saving_zip.writestr(saving_dir + filename, df.to_csv())
        elif saving_dir is not None:
            if not os.path.exists(saving_dir):
                os.makedirs(saving_dir)  
            df.to_csv(saving_dir + "/" + filename)