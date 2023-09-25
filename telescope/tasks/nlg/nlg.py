import streamlit as st
import pandas as pd
import zipfile

from telescope.tasks.task import Task
from telescope.collection_testsets import CollectionTestsets, NLGTestsets
from telescope.metrics import AVAILABLE_NLG_METRICS
from telescope.filters import AVAILABLE_NLG_FILTERS
from telescope.bias_evaluation import AVAILABLE_NLG_BIAS_EVALUATIONS
from telescope.universal_metrics import AVAILABLE_NLG_UNIVERSAL_METRICS

from telescope.plotting import plot_bootstraping_result
from telescope.multiple_plotting import (
    plot_bucket_multiple_comparison,
    plot_multiple_distributions,
    plot_multiple_segment_comparison,
    sentences_similarity,
    save_bootstrap_table,
)

class NLG(Task):
    name = "NLG"
    metrics = AVAILABLE_NLG_METRICS 
    filters = AVAILABLE_NLG_FILTERS
    bias_evaluations = AVAILABLE_NLG_BIAS_EVALUATIONS
    universal_metrics = AVAILABLE_NLG_UNIVERSAL_METRICS
    segment_result_source = False
    sentences_similarity = False


    @classmethod
    def plots_web_interface(cls, metric:str, results:dict, collection_testsets: CollectionTestsets, ref_filename: str, path :str, saving_zip: zipfile.ZipFile,
                            metrics:list = None, available_metrics:dict = None, num_samples: int = None, sample_ratio: float = None) -> None:
        """Web Interfave to display the plots"""

        # --------------- |Source Sentences Similarity| ----------------
        if cls.sentences_similarity and (collection_testsets.target_language == "pt" or collection_testsets.target_language == "en"):
            st.header(":blue[Similar Source Sentences:]")
            system_name = st.selectbox(
                "Select the system:",
                collection_testsets.names_of_systems(),
                index=0,
                key = "sentences_similarity"
            )
            system_id = collection_testsets.system_name_id(system_name)
            output = collection_testsets.testsets[ref_filename].systems_output[system_id]
            sentences_similarity(collection_testsets.testsets[ref_filename].src, output, collection_testsets.target_language,path, saving_zip)


        # -------------- |Error-type analysis| ------------------
        if metric == "COMET" or metric == "BERTScore":
            st.text("\n")
            st.header(":blue[Error-type analysis:]")
            plot_bucket_multiple_comparison(results[metric], collection_testsets.names_of_systems(),path, saving_zip)
        
        # -------------- | Distribution of segment-level scores| -----------
        if len(collection_testsets.testsets[ref_filename]) > 1:
            st.text("\n")
            st.header(":blue[Distribution of segment-level scores:]")
            if plot_multiple_distributions(results[metric], collection_testsets.names_of_systems(), test=True):
                plot_multiple_distributions(results[metric], collection_testsets.names_of_systems(), path, saving_zip)
                
        
        # -------------- |Pairwise comparison| -----------------
        if len(results[metric].systems_metric_results) > 1:

            st.text("\n")
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
                plot_multiple_segment_comparison(results[metric],system_x,system_y,cls.segment_result_source, path, saving_zip)

                #Bootstrap Resampling

                if cls.bootstrap:

                    _, middle, _ = st.columns(3)
                    
                    if middle.button("Perform Bootstrap Resampling", key="button-bootstrap"):
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
                            _, middle, _ = st.columns(3)
                            data_boostrap = pd.concat(list_df)
                            save_bootstrap_table(data_boostrap,system_x_name,system_y_name,path,saving_zip)

                            
    
    
    @classmethod
    def plots_cli_interface(cls, metric:str, results:dict, collection_testsets: CollectionTestsets, ref_filename: str, 
                            saving_dir:str, x_id:str ,y_id:str) -> None:
        """CLI Interfave to display the plots"""

        if cls.sentences_similarity:
            for system_name in collection_testsets.names_of_systems():
                system_id = collection_testsets.system_name_id(system_name)
                output = collection_testsets.testsets[ref_filename].systems_output[system_id]
                output_file = saving_dir + system_name
                sentences_similarity(collection_testsets.testsets[ref_filename].src, output, collection_testsets.target_language,output_file)
                
        if metric == "COMET" or metric == "BERTScore":
            plot_bucket_multiple_comparison(results[metric], collection_testsets.names_of_systems(), saving_dir)
        
        if len(collection_testsets.testsets[ref_filename]) > 1 and plot_multiple_distributions(results[metric], collection_testsets.names_of_systems(), test=True):
            plot_multiple_distributions(results[metric], collection_testsets.names_of_systems(), saving_dir)
        
        if len(collection_testsets.systems_ids.values()) > 1: 
            x = [x_id,collection_testsets.systems_names[x_id]]
            y = [y_id,collection_testsets.systems_names[y_id]]
            plot_multiple_segment_comparison(results[metric],x,y,cls.segment_result_source,saving_dir)