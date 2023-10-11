import os
import streamlit as st
import pandas as pd
import zipfile
import numpy as np

from streamlit import runtime
from typing import List, Dict
from telescope.collection_testsets import CollectionTestsets
from telescope.metrics.metric import MetricResult, MultipleMetricResults, Metric
from telescope.multiple_plotting import ( 
    confusion_matrix_of_system, 
    confusion_matrix_focused_on_one_label,
    rates_table,
    number_of_correct_labels_of_each_system,
    number_of_incorrect_labels_of_each_system,
    analysis_labels,
    bias_segments,
    create_and_save_table_zip,
    save_table,
    download_data_csv,
    all_identity_terms,
    table_identity_terms_found,
    confusion_matrix_image
    )

class BiasResult():
    def __init__(
        self,
        groups: List[str],
        ref: List[str],
        system_output: List[str],
        identity_terms_found_per_seg: Dict[int, List[dict]],
        groups_ref: List[str],
        groups_ref_per_seg: Dict[int,List[str]],
        groups_system: List[str],
        groups_sys_per_seg: Dict[int,List[str]],
        text_groups_ref_per_seg: Dict[int, List[dict]],
        text_groups_sys_per_seg: Dict[int, List[dict]],
        metrics_results_per_metric: Dict[str, MetricResult] # {name_metric:MetricResult}
    ) -> None:
        self.groups = groups
        self.ref = ref
        self.system_output = system_output
        self.identity_terms_found_per_seg = identity_terms_found_per_seg
        assert len(groups_ref) == len(groups_system)
        self.groups_ref = groups_ref
        self.groups_ref_per_seg = groups_ref_per_seg
        self.groups_system = groups_system
        self.groups_sys_per_seg = groups_sys_per_seg
        self.text_groups_ref_per_seg = text_groups_ref_per_seg
        self.text_groups_sys_per_seg = text_groups_sys_per_seg
        self.metrics_results_per_metric = metrics_results_per_metric

    def all_identity_terms_found(self,system_name:str, saving_dir:str=None,saving_zip:zipfile.ZipFile=None):
        return table_identity_terms_found(system_name,self.identity_terms_found_per_seg,saving_dir,saving_zip)

    def display_confusion_matrix_of_system(self,system_name:str, saving_dir:str=None,saving_zip:zipfile.ZipFile = None,show: bool = False) -> None:
        confusion_matrix_of_system(self.groups_ref, self.groups_system, self.groups, system_name, 
                                   show, saving_dir, saving_zip)
    
    def display_confusion_matrix_of_one_group(self,system_name:str,group:str,saving_dir:str=None,saving_zip:zipfile.ZipFile = None,show: bool = False) -> None:
        if group in self.groups:
            confusion_matrix_focused_on_one_label(self.groups_ref, self.groups_system, group,self.groups, system_name,
                                                  show,saving_dir,saving_zip)

    def display_rates(self, saving_dir:str=None,saving_zip:zipfile.ZipFile = None,show: bool = False, col = None):
        return rates_table(self.groups,self.groups_ref,self.groups_system,saving_dir,saving_zip,show)

    def display_bias_segments_of_system(self,system_name:str, ids:List[int], saving_dir:str = None):
        return bias_segments(system_name, self.ref, self.system_output, self.groups_ref_per_seg, self.groups_sys_per_seg, 
                             self.text_groups_ref_per_seg, self.text_groups_sys_per_seg, ids, saving_dir)
    
    def display_identity_terms(self,system_name:str, saving_dir:str = None,saving_zip:zipfile.ZipFile = None):
        return all_identity_terms(system_name, self.groups_sys_per_seg, self.groups_ref_per_seg, self.text_groups_ref_per_seg, 
                                  self.text_groups_sys_per_seg, saving_dir, saving_zip)



# each reference have one MultipleBiasResult
class MultipleBiasResults():
    def __init__(
        self,
        ref: List[str],
        identity_terms_found_ref_per_seg: [int, List[dict]],
        groups_ref: List[str],
        groups_ref_per_seg: Dict[int,List[str]],
        groups: List[str],
        systems_bias_results: Dict[str,BiasResult], # {id_of_systems:BiasResults}
        text_groups_ref_per_seg: Dict[int, List[Dict[str,str]]],
        metrics: List[Metric],
        time: float
    ) -> None:
        for bias_results in systems_bias_results.values():
            assert bias_results.ref == ref
            assert bias_results.groups_ref == groups_ref
            assert bias_results.groups_ref_per_seg == groups_ref_per_seg
            assert bias_results.groups == groups
            assert bias_results.text_groups_ref_per_seg == text_groups_ref_per_seg
            assert list(bias_results.metrics_results_per_metric.keys()) == [metric.name for metric in metrics]
        
        self.ref = ref
        self.identity_terms_found_ref_per_seg = identity_terms_found_ref_per_seg
        self.groups_ref = groups_ref
        self.groups_ref_per_seg = groups_ref_per_seg
        self.groups = groups
        self.systems_bias_results = systems_bias_results
        self.text_groups_ref_per_seg = text_groups_ref_per_seg
        self.metrics = metrics
        self.time=time
        self.multiple_metrics_results_per_metris = { metric.name: MultipleMetricResults(
                                                                {
                                                                    sys_id: bias_result.metrics_results_per_metric[metric.name] 
                                                                    for sys_id,bias_result in self.systems_bias_results.items()
                                                                }
                                                            )
            for metric in self.metrics
        }

    def display_bias_segments_of_one_system(self,collection_testsets:CollectionTestsets,system_name:str, ids:List[int], saving_dir:str = None):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        return bias_result.display_bias_segments_of_system(system_name,ids,saving_dir)

    def display_identity_terms_of_one_system(self,collection_testsets:CollectionTestsets,system_name:str, saving_dir:str = None,saving_zip:zipfile.ZipFile = None):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        return bias_result.display_identity_terms(system_name,saving_dir,saving_zip)

    def display_confusion_matrix_of_one_system(self,collection_testsets:CollectionTestsets, system_name:str,
                                               saving_dir:str=None,saving_zip:zipfile.ZipFile = None,show: bool = False):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        bias_result.display_confusion_matrix_of_system(system_name,saving_dir,saving_zip,show)

    def display_confusion_matrix_of_one_system_focused_on_one_label(self, collection_testsets:CollectionTestsets, system_name:str, group:str,
                                    saving_dir:str=None,saving_zip:zipfile.ZipFile = None,show: bool = False):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        bias_result.display_confusion_matrix_of_one_group(system_name, group, saving_dir,saving_zip,show)
    
    def display_rates_of_one_system(self,collection_testsets:CollectionTestsets, system_name:str, 
                                    saving_dir:str=None,saving_zip:zipfile.ZipFile = None,show: bool = False, col = None):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        return bias_result.display_rates(saving_dir, saving_zip, show, col)
    
    def display_number_of_correct_labels_of_each_system(self,collection_testsets:CollectionTestsets, saving_dir:str=None,saving_zip:zipfile.ZipFile = None):
        systems_names = []
        groups_sys_per_system = []
        for sys_id, bias_result in self.systems_bias_results.items():
            systems_names.append(collection_testsets.systems_names[sys_id])
            groups_sys_per_system.append(bias_result.groups_system)
        number_of_correct_labels_of_each_system(systems_names,self.groups_ref,groups_sys_per_system,self.groups, saving_dir, saving_zip)

    def display_number_of_incorrect_labels_of_each_system(self,collection_testsets:CollectionTestsets, saving_dir:str=None,saving_zip:zipfile.ZipFile = None):
        systems_names = []
        groups_sys_per_system = []
        for sys_id, bias_result in self.systems_bias_results.items():
            systems_names.append(collection_testsets.systems_names[sys_id])
            groups_sys_per_system.append(bias_result.groups_system)
        number_of_incorrect_labels_of_each_system(systems_names,self.groups_ref,groups_sys_per_system,self.groups, saving_dir,saving_zip)
    
    def display_analysis_labels(self,collection_testsets:CollectionTestsets,saving_dir:str=None,saving_zip:zipfile.ZipFile = None):
        systems_names = collection_testsets.systems_names
        for _, multiple_metrics_results in self.multiple_metrics_results_per_metris.items():
            analysis_labels(multiple_metrics_results,systems_names,self.groups, saving_dir,saving_zip)

    def display_bias_evaluations_informations(self, saving_dir:str=None, saving_zip:zipfile.ZipFile=None, col = None):
        table = { 
            "Bias Evaluation Time": [self.time],
            "Number of identity terms that were matched": [len(self.groups_ref)]
        }
        filename = "bias_evaluations_information.csv"
        df = pd.DataFrame.from_dict(table)
        if runtime.exists():
            if col is not None:
                col.dataframe(df)
            else:
                st.dataframe(df)
            if saving_dir and saving_zip:
                create_and_save_table_zip(saving_dir + filename,saving_zip,df)
        elif saving_dir:
            save_table(saving_dir,filename,df)
        return df

    def system_level_scores_bias_table(self, scores:pd.DataFrame, saving_dir: str = None, saving_zip:zipfile.ZipFile = None, col = None):
        filename = "bias_scores.csv"
        if runtime.exists():
            if col is not None:
                col.dataframe(scores)
            else:
                st.dataframe(scores)
            if saving_zip is not None and saving_dir is not None:
                create_and_save_table_zip(saving_dir + filename,saving_zip,scores)
        elif saving_dir:
            save_table(saving_dir,filename,scores)
    
    def all_identity_terms_found_ref(self,ref_name:str,saving_dir:str=None,saving_zip:zipfile.ZipFile=None,):
        return table_identity_terms_found(ref_name,self.identity_terms_found_ref_per_seg,saving_dir,saving_zip)
    
    def all_identity_terms_found_system(self,collection_testsets:CollectionTestsets, sys_name:str,saving_dir:str=None,saving_zip:zipfile.ZipFile=None):
        sys_id = collection_testsets.system_name_id(sys_name)
        bias_result = self.systems_bias_results[sys_id]
        return bias_result.all_identity_terms_found(sys_name,saving_dir,saving_zip)

    def plots_bias_results_web_interface(self, collection_testsets:CollectionTestsets, ref_name:str, 
                                         path:str = None, saving_zip:zipfile.ZipFile = None, option_bias=None):
        if option_bias:
            path = path + "bias_evaluation/" + option_bias + "/"
        else:
            path = path + "bias_evaluation/"

        st.subheader("Information")
        self.display_bias_evaluations_informations(path, saving_zip)

        st.subheader("System-level analysis")
        dataframe = MultipleMetricResults.results_to_dataframe(list(self.multiple_metrics_results_per_metris.values()),collection_testsets.systems_names)
        self.system_level_scores_bias_table(dataframe, path,saving_zip)


        st.subheader("Confusion Matrix Explanation")
        confusion_matrix_image()

        st.subheader("Rates")
        system_name = st.selectbox(
            "**Select the System**",
            collection_testsets.names_of_systems(),
            index=0,
            key="cm")

        self.display_rates_of_one_system(collection_testsets, system_name, show=True)

        st.subheader("Confusion Matrices")
        system_name = st.selectbox(
            "**Select the System**",
            collection_testsets.names_of_systems(),
            index=0,
            key="cm_2")
        self.display_confusion_matrix_of_one_system(collection_testsets,system_name, show=True)
        
        group = st.selectbox(
            "**Select the Protected Group**",
            self.groups,
            index=0)
        self.display_confusion_matrix_of_one_system_focused_on_one_label(collection_testsets,system_name,group,show=True)

        st.text("\n")

        st.subheader("Analysis of each group")
        self.display_analysis_labels(collection_testsets, path + "analysis_labels_bucket/", saving_zip)

        st.subheader("Number of times each group was identified correctly")           
        self.display_number_of_correct_labels_of_each_system(collection_testsets, path, saving_zip)

        st.subheader("Number of times each group was identified incorrectly")            
        self.display_number_of_incorrect_labels_of_each_system(collection_testsets, path, saving_zip)

        st.text("\n")

        st.subheader("20 Segments with Bias")
        click = 0
        system_name = st.selectbox(
            "**Select the System**",
                collection_testsets.names_of_systems(),
                index=0,
                key="bias")
        
        sys_id = collection_testsets.system_name_id(system_name)

        name = system_name.replace(" ", "_") + "_bias_segments.csv"

        click = "click_" + system_name + sys_id + "bias_evaluation" + option_bias
        if click not in st.session_state:
            st.session_state[click] =  0
        if 'dataframe_bias' not in st.session_state:
             st.session_state.dataframe_bias = None

        def callback():
            st.session_state[click] +=  1
        _, middle, _ = st.columns(3)

        if st.session_state.get("export-" + name):
            if not os.path.exists(path):
                os.makedirs(path)  
            st.session_state.dataframe_bias.to_csv(path + "/" + name)

        if(middle.button("Show Random Segments with Bias", on_click=callback)):

            if st.session_state[click] == 1:
                dataframe = self.display_bias_segments_of_one_system(collection_testsets,system_name, [i for i in range(len(self.ref))])
            else:
                dataframe = self.display_bias_segments_of_one_system(collection_testsets,system_name, [])

            if dataframe is not None:
                st.dataframe(dataframe)
                _,middle,_ = st.columns(3)
                st.session_state.dataframe_bias = dataframe
                download_data_csv("Export table with segments", dataframe, system_name.replace(" ","_") + "-bias-segments.csv", "bias_seg_load",middle)
            else:
                st.warning("There are no segments with bias.")

        self.all_identity_terms_found_ref(ref_name,saving_dir=path,saving_zip=saving_zip)
        for sys_name in collection_testsets.names_of_systems():
            path_dir = path + sys_name.replace(" ", "_") + "/"
            self.display_rates_of_one_system(collection_testsets, sys_name, saving_dir=path_dir, saving_zip=saving_zip)
            self.display_confusion_matrix_of_one_system(collection_testsets,sys_name,saving_dir=path_dir,saving_zip=saving_zip)
            self.all_identity_terms_found_system(collection_testsets,sys_name,saving_dir=path_dir,saving_zip=saving_zip)
            self.display_identity_terms_of_one_system(collection_testsets,system_name,saving_dir=path_dir,saving_zip=saving_zip)
            save_path = path_dir + "singular_confusion_matrix/"
            for grop in self.groups:
                self.display_confusion_matrix_of_one_system_focused_on_one_label(collection_testsets,sys_name,grop,saving_dir=save_path,saving_zip=saving_zip)


    def plots_bias_results_cli_interface(self, collection_testsets:CollectionTestsets, saving_dir:str):
        self.display_bias_evaluations_informations(saving_dir)
        self.display_analysis_labels(collection_testsets, saving_dir)        
        self.display_number_of_correct_labels_of_each_system(collection_testsets,saving_dir)       
        self.display_number_of_incorrect_labels_of_each_system(collection_testsets,saving_dir)

        ids = [i for i in range(len(self.ref))]
    
        for system_name in collection_testsets.names_of_systems():
            output_file = saving_dir + system_name + "/"
            self.display_confusion_matrix_of_one_system(collection_testsets,system_name,output_file)
            self.display_bias_segments_of_one_system(collection_testsets,system_name, ids, output_file)
            self.display_rates_of_one_system(collection_testsets, system_name, output_file)

            group_file = output_file + "/" + "singular_confusion_matrix/"
            for group in self.groups:
                self.display_confusion_matrix_of_one_system_focused_on_one_label(collection_testsets,system_name,group,group_file)