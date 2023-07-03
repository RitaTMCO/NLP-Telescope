import os
import streamlit as st
import pandas as pd

from typing import List, Dict
from telescope import PATH_DOWNLOADED_PLOTS
from telescope.collection_testsets import CollectionTestsets
from telescope.metrics.metric import Metric, MetricResult, MultipleMetricResults
from telescope.plotting import export_dataframe

class UniversalMetricResult():
    def __init__(
        self,
        ref: List[str],
        system_output: List[str],
        metrics: List[Metric],
        universal_metric: str,
        universal_score: float
    ) -> None:
        self.ref = ref
        self.system_output = system_output
        self.metrics = metrics
        self.universal_metric = universal_metric
        self.universal_score = universal_score

class MultipleUniversalMetricResult():
    def __init__(
        self,
        systems_universal_metrics_results: Dict[str,UniversalMetricResult], # {id_of_systems:UniversalMetricResult}
    ) -> None:
        ref_x = list(systems_universal_metrics_results.values())[0].ref
        metrics_x = list(systems_universal_metrics_results.values())[0].metrics
        universal_metric_x = list(systems_universal_metrics_results.values())[0].universal_metric

        for universal_metric_results in list(systems_universal_metrics_results.values()):
            assert universal_metric_results.ref == ref_x
            assert universal_metric_results.metrics == metrics_x
            assert universal_metric_results.universal_metric == universal_metric_x
        
        self.ref = ref_x
        self.metrics = metrics_x
        self.universal_metric = universal_metric_x
        self.systems_universal_metrics_results = systems_universal_metrics_results
    
    def plots_web_interface(self, collection_testsets:CollectionTestsets, ref_name:str):
        st.header(self.universal_metric)
        for sys_id, universal_metric_result in self.systems_universal_metrics_results.items():
            st.text([sys_id, universal_metric_result.universal_score, universal_metric_result.universal_metric, universal_metric_result.metrics])
            st.text("\n")
            
    
    def plots_cli_interface(self, collection_testsets:CollectionTestsets, saving_dir:str):
        print(self.universal_metric)