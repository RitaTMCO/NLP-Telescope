import os
import streamlit as st

from typing import List, Dict
from telescope.collection_testsets import CollectionTestsets
from telescope.metrics.metric import MetricResult, MultipleMetricResults
from telescope.plotting import ( 
    confusion_matrix_of_system, 
    confusion_matrix_focused_on_one_label,
    number_of_correct_labels_of_each_system,
    number_of_incorrect_labels_of_each_system,
    analysis_labels,
    bias_segments,
    export_dataframe
    )

class BiasResult():
    def __init__(
        self,
        groups: List[str],
        ref: List[str],
        system_output: List[str],
        groups_ref: List[str],
        groups_ref_per_seg: Dict[int,List[str]],
        groups_system: List[str],
        groups_sys_per_seg: Dict[int,List[str]],
        metrics_results_per_metric: Dict[str, MetricResult] # {name_metric:MetricResult}
    ) -> None:
        self.groups = groups
        self.ref = ref
        self.system_output = system_output
        assert len(groups_ref) == len(groups_system)
        self.groups_ref = groups_ref
        self.groups_ref_per_seg = groups_ref_per_seg
        self.groups_system = groups_system
        self.groups_sys_per_seg = groups_sys_per_seg
        self.metrics_results_per_metric = metrics_results_per_metric

    def display_confusion_matrix_of_system(self,system_name:str, saving_dir:str=None) -> None:
        confusion_matrix_of_system(self.groups_ref, self.groups_system, self.groups, system_name, saving_dir)
    
    def display_confusion_matrix_of_one_group(self,system_name:str,group:str,saving_dir:str=None) -> None:
        if group in self.groups:
            confusion_matrix_focused_on_one_label(self.groups_ref, self.groups_system, group,self.groups, system_name, saving_dir)
    
    def display_bias_segments_of_system(self,ids:List[int], saving_dir:str = None):
        return bias_segments(self.ref, self.system_output, self.groups_ref_per_seg, self.groups_sys_per_seg, ids, saving_dir)


# each reference have one MultipleBiasResult
class MultipleBiasResults():
    def __init__(
        self,
        ref: List[str],
        groups_ref: List[str],
        groups_ref_per_seg: Dict[int,List[str]],
        groups: List[str],
        systems_bias_results: Dict[str,BiasResult], # {id_of_systems:BiasResults}
        metrics: List[str]
    ) -> None:
        for bias_results in systems_bias_results.values():
            assert bias_results.ref == ref
            assert bias_results.groups_ref == groups_ref
            assert bias_results.groups == groups
        
        self.ref = ref
        self.groups_ref = groups_ref
        self.groups_ref_per_seg = groups_ref_per_seg
        self.groups = groups
        self.systems_bias_results = systems_bias_results
        self.metrics = metrics
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
        return bias_result.display_bias_segments_of_system(ids,saving_dir)

    def display_confusion_matrix_of_one_system(self,collection_testsets:CollectionTestsets, system_name:str, saving_dir:str=None):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        bias_result.display_confusion_matrix_of_system(system_name,saving_dir)

    def display_confusion_matrix_of_one_system_focused_on_one_label(self, collection_testsets:CollectionTestsets, system_name:str, group:str,
                                                                    saving_dir:str=None):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        bias_result.display_confusion_matrix_of_one_group(system_name, group, saving_dir)
    
    def display_number_of_correct_labels_of_each_system(self,collection_testsets:CollectionTestsets, saving_dir:str=None):
        systems_names = []
        groups_sys_per_system = []
        for sys_id, bias_result in self.systems_bias_results.items():
            systems_names.append(collection_testsets.systems_names[sys_id])
            groups_sys_per_system.append(bias_result.groups_system)
        number_of_correct_labels_of_each_system(systems_names,self.groups_ref,groups_sys_per_system,self.groups, saving_dir)

    def display_number_of_incorrect_labels_of_each_system(self,collection_testsets:CollectionTestsets, saving_dir:str=None):
        systems_names = []
        groups_sys_per_system = []
        for sys_id, bias_result in self.systems_bias_results.items():
            systems_names.append(collection_testsets.systems_names[sys_id])
            groups_sys_per_system.append(bias_result.groups_system)
        number_of_incorrect_labels_of_each_system(systems_names,self.groups_ref,groups_sys_per_system,self.groups, saving_dir)
    
    def display_analysis_labels(self,collection_testsets:CollectionTestsets,saving_dir:str=None):
        systems_names = collection_testsets.systems_names.values()
        for _, multiple_metrics_results in self.multiple_metrics_results_per_metris.items():
            analysis_labels(multiple_metrics_results,systems_names,self.groups, saving_dir)



    def plots_bias_results_web_interface(self, collection_testsets:CollectionTestsets):
        dataframe = MultipleMetricResults.results_to_dataframe(list(self.multiple_metrics_results_per_metris.values()),collection_testsets.systems_names)
        export_dataframe(label="Export table with score", name="bias_results.csv", dataframe=dataframe)
        st.dataframe(dataframe)

        st.subheader("Confusion Matrices")
        system_name = st.selectbox(
            "**Select the System**",
            collection_testsets.names_of_systems(),
            index=0,
            key="cm")
        self.display_confusion_matrix_of_one_system(collection_testsets,system_name)

        group = st.selectbox(
            "**Select the Protected Group**",
            self.groups,
            index=0)

        self.display_confusion_matrix_of_one_system_focused_on_one_label(collection_testsets,system_name,group)

        st.subheader("Analysis Of Each Label")
        self.display_analysis_labels(collection_testsets)

        st.subheader("Number of times each group was identified correctly")           
        self.display_number_of_correct_labels_of_each_system(collection_testsets)

        st.subheader("Number of times each group was identified incorrectly")            
        self.display_number_of_incorrect_labels_of_each_system(collection_testsets)

        st.subheader("Segements with Bias")
        click = 0
        system_name = st.selectbox(
            "**Select the System**",
                collection_testsets.names_of_systems(),
                index=0,
                key="bias")
        
        click = "click_" + system_name
        if click not in st.session_state:
            st.session_state[click] =  0
        def callback():
            st.session_state[click] +=  1
        _, middle, _ = st.columns(3)
        if(middle.button("Show Segments with bias", on_click=callback)):

            if st.session_state[click] == 1:
                dataframe = self.display_bias_segments_of_one_system(collection_testsets,system_name, [i for i in range(len(self.ref))])
            else:
                dataframe = self.display_bias_segments_of_one_system(collection_testsets,system_name, [])

            if dataframe is not None:
                st.dataframe(dataframe)
                export_dataframe(label="Export table with segments", name="bias_segments.csv", dataframe=dataframe)
            else:
                st.warning("There are no segments with bias.")



    
    def plots_bias_results_cli_interface(self, collection_testsets:CollectionTestsets, saving_dir:str):
        self.display_analysis_labels(collection_testsets, saving_dir)        
        self.display_number_of_correct_labels_of_each_system(collection_testsets,saving_dir)       
        self.display_number_of_incorrect_labels_of_each_system(collection_testsets,saving_dir)

        ids = [i for i in range(len(self.ref))]
    
        for system_name in collection_testsets.names_of_systems():
            output_file = saving_dir + system_name + "/"
            if not os.path.exists(output_file):
                os.makedirs(output_file)  
            self.display_confusion_matrix_of_one_system(collection_testsets,system_name,output_file)
            self.display_bias_segments_of_one_system(collection_testsets,system_name, ids, output_file)

            group_file = output_file + "/" + "singular_confusion_matrix/"
            if not os.path.exists(group_file):
                os.makedirs(group_file)  
            for group in self.groups:
                self.display_confusion_matrix_of_one_system_focused_on_one_label(collection_testsets,system_name,group,group_file)
