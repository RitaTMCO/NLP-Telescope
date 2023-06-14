import pandas as pd
from typing import List, Dict
from telescope.collection_testsets import CollectionTestsets
from telescope.plotting import ( 
    confusion_matrix_of_system, 
    confusion_matrix_focused_on_one_label,
    number_of_correct_labels_of_each_system,
    number_of_incorrect_labels_of_each_system,
    analysis_labels)
from telescope.metrics.metric import MetricResult, MultipleResult

class BiasResult():
    def __init__(
        self,
        groups: List[str],
        ref: List[str],
        system_output: List[str],
        groups_ref: List[str],
        groups_system: List[str],
        metrics_results_per_metric: Dict[str, MetricResult] # {name_metric:MetricResult}
    ) -> None:
        self.groups = groups
        self.ref = ref
        self.system_output = system_output
        assert len(groups_ref) == len(groups_system)
        self.groups_ref = groups_ref
        self.groups_system = groups_system
        self.metrics_results_per_metric = metrics_results_per_metric

    def display_groups(self) -> str:
        def dispaly_groups_aux(display,sets_of_groups):
            for group in sets_of_groups:
                display += group + "  "
            display += "\n"
            return display
        display = "\nReference:\n "
        display = dispaly_groups_aux(display,self.groups_ref)
        display +="System:\n"
        display = dispaly_groups_aux(display,self.groups_system)
        return display

    def display_confusion_matrix_of_system(self,system_name:str) -> None:
        confusion_matrix_of_system(self.groups_ref, self.groups_system, self.groups, system_name)
    
    def display_confusion_matrix_of_one_group(self,system_name:str,group:str) -> None:
        if group in self.groups:
            confusion_matrix_focused_on_one_label(self.groups_ref, self.groups_system, group,self.groups, system_name)
    



# each reference have one MultipleBiasResult
class MultipleBiasResults():
    def __init__(
        self,
        ref: List[str],
        groups_ref: List[str],
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
        self.groups = groups
        self.systems_bias_results = systems_bias_results
        self.metrics = metrics
        self.multiple_metrics_results_per_metris = { metric: MultipleResult(
                                                                {
                                                                    sys_id: bias_result.metrics_results_per_metric[metric] 
                                                                    for sys_id,bias_result in self.systems_bias_results.items()
                                                                }
                                                            )
            for metric in self.metrics
        }

    
    def metrics_scores_and_number_of_identified_terms_to_dataframe(self,collection_testsets:CollectionTestsets):
        all_multiple_metrics_results = list(self.multiple_metrics_results_per_metris.values())
        summary = { 
            sys_name: [m_res.systems_metric_results[sys_id].sys_score for m_res in all_multiple_metrics_results]
            for sys_id, sys_name in collection_testsets.systems_names.items()
        }
        df = pd.DataFrame.from_dict(summary)
        df.index = [m_res.metric for m_res in all_multiple_metrics_results]
        return df


    def display_groups_of_each_system(self,collection_testsets:CollectionTestsets) -> str:
        display = ""
        for sys_id, bias_result in self.systems_bias_results.items():
            system_name = collection_testsets.systems_names[sys_id]
            display += "---" + system_name + "---"
            display += bias_result.display_groups() 
        return display
    
    def display_confusion_matrix_of_one_system(self,collection_testsets:CollectionTestsets, system_name:str):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        bias_result.display_confusion_matrix_of_system(system_name)

    def display_confusion_matrix_of_one_system_focused_on_one_label(self, collection_testsets:CollectionTestsets, system_name:str, group:str):
        sys_id = collection_testsets.system_name_id(system_name)
        bias_result = self.systems_bias_results[sys_id]
        bias_result.display_confusion_matrix_of_one_group(system_name, group)
    
    def display_number_of_correct_labels_of_each_system(self,collection_testsets:CollectionTestsets):
        systems_names = []
        groups_sys_per_system = []
        for sys_id, bias_result in self.systems_bias_results.items():
            systems_names.append(collection_testsets.systems_names[sys_id])
            groups_sys_per_system.append(bias_result.groups_system)
        number_of_correct_labels_of_each_system(systems_names,self.groups_ref,groups_sys_per_system,self.groups)

    def display_number_of_incorrect_labels_of_each_system(self,collection_testsets:CollectionTestsets):
        systems_names = []
        groups_sys_per_system = []
        for sys_id, bias_result in self.systems_bias_results.items():
            systems_names.append(collection_testsets.systems_names[sys_id])
            groups_sys_per_system.append(bias_result.groups_system)
        number_of_incorrect_labels_of_each_system(systems_names,self.groups_ref,groups_sys_per_system,self.groups)
    
    def display_analysis_labels(self,collection_testsets:CollectionTestsets):
        systems_names = collection_testsets.systems_names.values()
        for metric, multiple_metrics_results in self.multiple_metrics_results_per_metris.items():
            analysis_labels(multiple_metrics_results,systems_names,self.groups)




            