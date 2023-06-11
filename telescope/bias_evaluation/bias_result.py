from typing import List, Dict
from telescope.collection_testsets import CollectionTestsets
from telescope.plotting import confusion_matrix_of_system, confusion_matrix_focused_on_one_label

class BiasResult():
    def __init__(
        self,
        groups: List[str],
        ref: List[str],
        system_output: List[str],
        groups_ref: List[str],
        groups_system: List[str]
    ) -> None:
        self.groups = groups
        self.ref = ref
        self.system_output = system_output

        assert len(groups_ref) == len(groups_system)
        self.groups_ref = groups_ref
        self.groups_system = groups_system

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
class MultipleBiasResult():
    def __init__(
        self,
        groups: List[str],
        systems_bias_results: Dict[str,BiasResult] # {id_of_systems:BiasResults}
    ) -> None:
        
        for bias_results in systems_bias_results.values():
            assert bias_results.groups == groups

        self.groups = groups
        self.systems_bias_results = systems_bias_results
        bias_result = list(systems_bias_results.values())[0]
        self.ref = bias_result.ref

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



            