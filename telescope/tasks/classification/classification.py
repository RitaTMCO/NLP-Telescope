import click
import os
import streamlit as st
import zipfile

from typing import Tuple,List
from telescope.tasks.task import Task
from telescope.collection_testsets import CollectionTestsets, ClassTestsets
from telescope.metrics import AVAILABLE_CLASSIFICATION_METRICS
from telescope.filters import AVAILABLE_CLASSIFICATION_FILTERS
from telescope.bias_evaluation import AVAILABLE_CLASSIFICATION_BIAS_EVALUATIONS
from telescope.universal_metrics import AVAILABLE_CLASSIFICATION_UNIVERSAL_METRICS
from telescope.multiple_plotting import (
    confusion_matrix_of_system,
    confusion_matrix_focused_on_one_label,
    analysis_labels,
    incorrect_examples,
    rates_table,
    download_data_csv,
    confusion_matrix_image
)


class Classification(Task):
    name = "classification"
    metrics = AVAILABLE_CLASSIFICATION_METRICS
    filters = AVAILABLE_CLASSIFICATION_FILTERS
    bias_evaluations = AVAILABLE_CLASSIFICATION_BIAS_EVALUATIONS
    universal_metrics = AVAILABLE_CLASSIFICATION_UNIVERSAL_METRICS

    @staticmethod
    def input_web_interface() -> CollectionTestsets:
        """Web Interface to collect the necessary inputs to realization of the task evaluation."""
        class_testset = ClassTestsets.read_data()
        return class_testset

    @staticmethod
    def input_cli_interface(source:click.File, system_names_file:click.File, systems_output:Tuple[click.File], reference:Tuple[click.File], 
                      language:str,labels_file:click.File=None) -> CollectionTestsets:
        """CLI Interface to collect the necessary inputs to realization of the task evaluation."""
        return  ClassTestsets.read_data_cli(source, system_names_file, systems_output, reference, language, labels_file)
    
    @classmethod
    def plots_web_interface(cls, metric:str, results:dict, collection_testsets: CollectionTestsets, ref_filename: str, path : str, saving_zip: zipfile.ZipFile,
                            metrics:list = None, available_metrics:dict = None, filters:List[str] = [], length_interval:Tuple[int] = (), num_samples: int = None, sample_ratio: float = None) -> None:
        """Web Interfave to display the plots"""

        ref_id = collection_testsets.refs_ids[ref_filename]
        testset = collection_testsets.testsets[ref_filename]
        labels = collection_testsets.labels
        names_of_systems = collection_testsets.names_of_systems()

        def class_session(system_name:str, system:str, ref_id:str, ref:List[str]):
            num = 'num_' + system_name + "_" + system + "_" + ref_id + "_" +  "_".join(filters) + "_".join([ str(i) for i in length_interval])
            incorrect_ids = 'incorrect_ids_' + system_name + "_" + system + "_" + ref_id + "_" +  "_".join(filters) +  "_".join([ str(i) for i in length_interval])
            table = 'tables_' + system_name + "_" + system + "_" + ref_id + "_" +  "_".join(filters) +  "_".join([ str(i) for i in length_interval])
            num_incorrect_ids = 'num_incorrect_ids_' + system_name + "_" + system + "_" + ref_id + "_" +  "_".join(filters) +  "_".join([ str(i) for i in length_interval])
            click = "click_" + system_name + "_" + system + "_" + ref_id + "_" +  "_".join(filters) +  "_".join([ str(i) for i in length_interval]) + "_class_evaluation"
            if num not in st.session_state:
                if len(ref) <= 55:
                    st.session_state[num] = int(len(ref)/4) + 1
                else:
                    st.session_state[num] = 5
            if incorrect_ids not in st.session_state:
                st.session_state[incorrect_ids] = []
            if table not in st.session_state:
                st.session_state[table] = []
            if num_incorrect_ids  not in st.session_state:
                st.session_state[num_incorrect_ids] = 0
            if click not in st.session_state:
                st.session_state[click] =  1
            return num, incorrect_ids, table, num_incorrect_ids, click

        def click_incorrect_examples(collection_testsets,testset,system,num,incorrect_ids,table,click, ref_filename, system_name):
            if st.session_state[click] == 1:
                num_segments = len(collection_testsets.testsets[ref_filename])
                df = incorrect_examples(testset, system, system_name, st.session_state[num], st.session_state[incorrect_ids],
                                        st.session_state[table], [i for i in range(num_segments)])
            else:
                df = incorrect_examples(testset, system, system_name, st.session_state[num], st.session_state[incorrect_ids],
                                        st.session_state[table])
            return df


        #-------------- |Confusion Matrix| --------------------
        st.header(":blue[Confusion Matrix:]")

        confusion_matrix_image()

        system_name = st.selectbox(
            "Select the system:",
            names_of_systems,
            index=0
        )
        system = collection_testsets.system_name_id(system_name)

        # Rates
        st.subheader("Rates")

        rates_table(labels,testset.ref,testset.systems_output[system],show=True)

        # Overall Confusion Matrix
        st.subheader("Confusion Matrix of :blue[" + system_name + "]")
        confusion_matrix_of_system(testset.ref,testset.systems_output[system],labels,system_name,show = True)

        # Singular Confusion Matrix
        st.subheader("Confusion Matrix of :blue[" + system_name + "] focused on one label")
        label = st.selectbox(
            "Select the label:",
            list(labels),
            index=0,
            key = "confusion_matrix"
        )
        confusion_matrix_focused_on_one_label(testset.ref,testset.systems_output[system],label,labels,system_name, show = True)

        #-------------- |Analysis Of Each Label| --------------------
        st.header(":blue[Results by label:]")
        analysis_labels(results[metric], collection_testsets.systems_names, labels, path, saving_zip)
        
        #-------------- |Examples| --------------------
        st.header(":blue[Examples That Are Incorrectly Labelled:]")
        system_name = st.selectbox(
            "Select the system:",
            names_of_systems,
            index=0,
            key = "examples"
        )

        system = collection_testsets.system_name_id(system_name)
        num, incorrect_ids, table, num_incorrect_ids, click = class_session(system_name, system, ref_id, testset.ref)
        df = click_incorrect_examples(collection_testsets,testset,system,num,incorrect_ids,table,click, ref_filename,system_name)

        if df is not None:
            st.dataframe(df)

            all_df = incorrect_examples(testset, system, system_name, len(testset.src), all_examples=True)
            download_data_csv("Download of the incorrect examples", all_df, system_name.replace(" ","_") + "-incorrect-examples.csv", "incorrect_example_load")
            

            old_num_incorrect_ids = st.session_state[num_incorrect_ids]
            new_num_incorrect_ids = len(st.session_state[incorrect_ids])

            def callback():
                st.session_state[num] +=  st.session_state[num] 
                st.session_state[num_incorrect_ids] = new_num_incorrect_ids
                st.session_state[click] +=  1

            if old_num_incorrect_ids != new_num_incorrect_ids:
                _, middle, _ = st.columns(3)
                middle.button("More examples", on_click=callback)
            else:
                st.warning("There are no more examples that are incorrectly labeled.")
        else:
            st.warning("There are no examples that are incorrectly labelled.")
        
        for sys_name in collection_testsets.names_of_systems():
            path_dir = path + sys_name.replace(" ", "_") + "/"
            sys = collection_testsets.system_name_id(sys_name)
            rates_table(labels,testset.ref,testset.systems_output[sys],path_dir, saving_zip)
            confusion_matrix_of_system(testset.ref,testset.systems_output[sys],labels,sys_name,saving_dir=path_dir, saving_zip=saving_zip)
            save_path = path_dir + "singular_confusion_matrix/"
            for l in labels:
                confusion_matrix_focused_on_one_label(testset.ref,testset.systems_output[sys],l,labels,sys_name, saving_dir=save_path, saving_zip=saving_zip)
    

    @classmethod
    def plots_cli_interface(cls, metric:str, results:dict, collection_testsets: CollectionTestsets, ref_filename: str, 
                            saving_dir:str) -> None:
        """CLI Interfave to display the plots"""

        testset = collection_testsets.testsets[ref_filename]
        labels = collection_testsets.labels
        systems_names = collection_testsets.systems_names

        analysis_labels(results[metric], collection_testsets.systems_names, labels, saving_dir)
        
        for sys_id, sys_name in systems_names.items():
            output_file = saving_dir + sys_name + "/"         
            confusion_matrix_of_system(testset.ref,testset.systems_output[sys_id],labels,sys_name, saving_dir=output_file)
            rates_table(labels,testset.ref,testset.systems_output[sys_id],output_file)
            incorrect_examples(testset, sys_id, sys_name, len(testset),saving_dir=output_file,all_examples=True)
            label_file = output_file + "/" + "singular_confusion_matrix/"
            for label in labels:
                confusion_matrix_focused_on_one_label(testset.ref, testset.systems_output[sys_id], label,labels,sys_name,saving_dir=label_file)