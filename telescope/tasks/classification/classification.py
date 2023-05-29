import click
import os
import streamlit as st
import pandas as pd
import numpy as np

from typing import Tuple
from telescope.tasks.task import Task
from telescope.collection_testsets import CollectionTestsets, ClassTestsets
from telescope.metrics import AVAILABLE_CLASSIFICATION_METRICS
from telescope.filters import AVAILABLE_CLASSIFICATION_FILTERS
from telescope.bias_evaluation import AVAILABLE_CLASSIFICATION_BIAS_EVALUATIONS
from telescope.plotting import (
    overall_confusion_matrix_table,
    singular_confusion_matrix_table,
    analysis_labels,
    incorrect_examples,
    export_dataframe
)


class Classification(Task):
    name = "classification"
    metrics = AVAILABLE_CLASSIFICATION_METRICS
    filters = AVAILABLE_CLASSIFICATION_FILTERS
    bias_evaluations = AVAILABLE_CLASSIFICATION_BIAS_EVALUATIONS

    @staticmethod
    def input_web_interface() -> CollectionTestsets:
        """Web Interface to collect the necessary inputs to realization of the task evaluation."""
        class_testset = ClassTestsets.read_data()
        return class_testset

    @staticmethod
    def input_cli_interface(source:click.File, system_names_file:click.File, systems_output:Tuple[click.File], reference:Tuple[click.File], 
                      extra_info:str) -> CollectionTestsets:
        """CLI Interface to collect the necessary inputs to realization of the task evaluation."""
        labels = extra_info
        return  ClassTestsets.read_data_cli(source, system_names_file, systems_output, reference, labels)
    
    @classmethod
    def plots_web_interface(cls, metric:str, results:dict, collection_testsets: CollectionTestsets, ref_filename: str) -> None:
        """Web Interfave to display the plots"""

        ref_id = collection_testsets.refs_indexes[ref_filename]
        testset = collection_testsets.testsets[ref_filename]
        labels = collection_testsets.labels
        names_of_systems = collection_testsets.names_of_systems()


        #-------------- |Confusion Matrix| --------------------
        st.header(":blue[Confusion Matrix]")
        system_name = st.selectbox(
            "Select the system:",
            names_of_systems,
            index=0
        )

        # Overall Confusion Matrix
        system = collection_testsets.system_name_id(system_name)
        st.subheader("Confusion Matrix of :blue[" + system_name + "]")
        overall_confusion_matrix_table(testset,system,labels,system_name)


        # Singular Confusion Matrix
        st.subheader("Confusion Matrix of :blue[" + system_name + "] focused on one label")
        label = st.selectbox(
            "Select the label:",
            list(labels),
            index=0,
            key = "confusion_matrix"
        )
        singular_confusion_matrix_table(testset,system,labels,label,system_name)


        #-------------- |Analysis Of Each Label| --------------------
        st.header(":blue[Analysis Of Each Label]")
        analysis_labels(results[metric], collection_testsets.names_of_systems(), labels)

        
        #-------------- |Examples| --------------------
        st.header(":blue[Examples That Are Incorrectly Labelled]")
        system_name = st.selectbox(
            "Select the system:",
            names_of_systems,
            index=0,
            key = "examples"
        )

        system = collection_testsets.system_name_id(system_name)

        num = 'num_' + system + "_" + ref_id
        incorrect_ids = 'incorrect_ids_' + system + "_" + ref_id
        table = 'tables_' + system + "_" + ref_id
        num_incorrect_ids = 'num_incorrect_ids_' + system + "_" + ref_id
        
        if num not in st.session_state:
            if len(testset.ref) <= 55:
                st.session_state[num] = int(len(testset.ref)/4) + 1
            else:
                st.session_state[num] = 5
        if incorrect_ids not in st.session_state:
            st.session_state[incorrect_ids] = []
        if table not in st.session_state:
            st.session_state[table] = []
        if num_incorrect_ids  not in st.session_state:
            st.session_state[num_incorrect_ids] = 0

        df = incorrect_examples(testset, system, st.session_state[num], st.session_state[incorrect_ids],st.session_state[table])
        
        export_dataframe(label="Export incorrect examples", name=system_name + "_incorrect-examples.csv", dataframe=df)

        if df is not None:
            st.dataframe(df)
            old_num_incorrect_ids = st.session_state[num_incorrect_ids]
            new_num_incorrect_ids = len(st.session_state[incorrect_ids])

            def callback():
                st.session_state[num] +=  st.session_state[num] 
                st.session_state[num_incorrect_ids] = new_num_incorrect_ids

            if old_num_incorrect_ids != new_num_incorrect_ids:
                _, middle, _ = st.columns(3)
                middle.button("More examples", on_click=callback)
            else:
                st.warning("There are no more examples that are incorrectly labeled.")
        else:
            st.warning("There are no examples that are incorrectly labelled.")


    @classmethod
    def plots_cli_interface(cls, metric:str, results:dict, collection_testsets: CollectionTestsets, ref_filename: str, 
                            saving_dir:str) -> None:
        """CLI Interfave to display the plots"""

        testset = collection_testsets.testsets[ref_filename]
        labels = collection_testsets.labels
        systems_names = collection_testsets.systems_names

        analysis_labels(results[metric], collection_testsets.names_of_systems(), labels, saving_dir)
        
        for sys_id, sys_name in systems_names.items():
            output_file = saving_dir + sys_name
            if not os.path.exists(output_file):
                os.makedirs(output_file)            
            overall_confusion_matrix_table(testset,sys_id,labels,sys_name,output_file)

            num = 15
            incorrect_examples(testset,sys_id,num,[],[], output_file)

            label_file = output_file + "/" + "singular_confusion_matrix"
            if not os.path.exists(label_file):
                os.makedirs(label_file)  
            for label in labels:
                singular_confusion_matrix_table(testset,sys_id,labels,label,sys_name,label_file)
