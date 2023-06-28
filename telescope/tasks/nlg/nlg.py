import streamlit as st
import pandas as pd
import numpy as np
import os

from telescope.tasks.task import Task
from telescope.collection_testsets import CollectionTestsets, NLGTestsets
from telescope.metrics import AVAILABLE_NLG_METRICS
from telescope.filters import AVAILABLE_NLG_FILTERS
from telescope.bias_evaluation import AVAILABLE_NLG_BIAS_EVALUATIONS
from telescope.plotting import (
    plot_bootstraping_result,
    plot_bucket_multiple_comparison,
    plot_multiple_distributions,
    plot_multiple_segment_comparison,
    export_dataframe
)

class NLG(Task):
    name = "NLG"
    metrics = AVAILABLE_NLG_METRICS 
    filters = AVAILABLE_NLG_FILTERS
    bias_evaluations = AVAILABLE_NLG_BIAS_EVALUATIONS
    bootstrap = True
    segment_result_source = False


    @classmethod
    def plots_web_interface(cls, metric:str, results:dict, collection_testsets: CollectionTestsets, ref_filename: str, 
                            metrics:list, available_metrics:dict, num_samples: int, sample_ratio: float) -> None:
        """Web Interfave to display the plots"""


        directory = os.getenv('HOME')
        path = directory + "/nlp-telescope/images/"  + ref_filename + "/" + cls.name + "/" 

        # -------------- |Error-type analysis| ------------------
        if metric == "COMET" or metric == "BERTScore":
            st.header(":blue[Error-type analysis:]")
            plot_bucket_multiple_comparison(results[metric], collection_testsets.names_of_systems())
            if st.button('Download the Error-type analysis'):
                if not os.path.exists(path):
                    os.makedirs(path)  
                plot_bucket_multiple_comparison(results[metric], collection_testsets.names_of_systems(),path)
        
        # -------------- |Segment-level scores histogram| -----------
        if len(collection_testsets.testsets[ref_filename]) > 1:
            try:
                st.header(":blue[Segment-level scores histogram:]")
                plot_multiple_distributions(results[metric], collection_testsets.names_of_systems())
                if st.button('Download the Segment-level scores histogram'):
                    if not os.path.exists(path):
                        os.makedirs(path)  
                    plot_multiple_distributions(results[metric], collection_testsets.names_of_systems(),path)
            except np.linalg.LinAlgError as err:    
                st.write(err)
            
        
        # -------------- |Pairwise comparison| -----------------
        if len(results[metric].systems_metric_results) > 1:

            st.header(":blue[Pairwise comparison:]")
            left, right = st.columns(2)
            system_x_name = left.selectbox(
                "Select the system x:",
                collection_testsets.names_of_systems(),
                index=0,
                key = ref_filename + "_1"
            )
            system_y_name = right.selectbox(
                "Select the system y:",
                collection_testsets.names_of_systems(),
                index=1,
                key = ref_filename + "_2"
            )

            if system_x_name == system_y_name:
                st.warning("The system x cannot be the same as system y")
            else:
                system_x_id = collection_testsets.system_name_id(system_x_name)
                system_x = [system_x_id, system_x_name]
                system_y_id = collection_testsets.system_name_id(system_y_name)
                system_y = [system_y_id, system_y_name]
        

            #Segment-level comparison
            st.subheader("Segment-level comparison:")
            plot_multiple_segment_comparison(results[metric],system_x,system_y,cls.segment_result_source)
            if st.button('Download the Segment-level comparison'):
                if not os.path.exists(path):
                    os.makedirs(path)  
                plot_multiple_segment_comparison(results[metric],system_x,system_y,cls.segment_result_source, path)

            #Bootstrap Resampling
            _, middle, _ = st.columns(3)
            if middle.button("Perform Bootstrap Resampling",key = ref_filename):
                st.warning(
                    "Running metrics for {} partitions of size {}".format(
                            num_samples, sample_ratio * len(collection_testsets.testsets[ref_filename])
                        )
                    )
                st.subheader("Bootstrap resampling results:")
                list_df = list()
                with st.spinner("Running bootstrap resampling..."):
                    for metric in metrics:
                        bootstrap_result = available_metrics[metric].multiple_bootstrap_resampling(
                                collection_testsets.testsets[ref_filename], int(num_samples), 
                                sample_ratio, system_x_id, system_y_id, collection_testsets.target_language, results[metric])
                        df = plot_bootstraping_result(bootstrap_result)
                        list_df.append(df)
                    name = system_x_name + "-" + system_y_name + "_bootstrap_results.csv"
                    export_dataframe(label="Export bootstrap resampling results", name=name, dataframe=pd.concat(list_df))


    @classmethod
    def plots_cli_interface(cls, metric:str, results:dict, collection_testsets: CollectionTestsets, ref_filename: str, 
                            saving_dir:str, x_id:str ,y_id:str) -> None:
        """CLI Interfave to display the plots"""

        if metric == "COMET" or metric == "BERTScore":
            plot_bucket_multiple_comparison(results[metric], collection_testsets.names_of_systems(), saving_dir)
        
        if len(collection_testsets.testsets[ref_filename]) > 1:
            plot_multiple_distributions(results[metric], collection_testsets.names_of_systems(), saving_dir)
        
        if len(collection_testsets.systems_ids.values()) > 1: 
            x = [x_id,collection_testsets.systems_names[x_id]]
            y = [y_id,collection_testsets.systems_names[y_id]]
            plot_multiple_segment_comparison(results[metric],x,y,cls.segment_result_source,saving_dir)
