from typing import List, Dict
from telescope.collection_testsets import CollectionTestsets

class BiasResult():
    def __init__(
        self,
        ref: List[str],
        system_output: List[str],
        groups_ref: List[str],
        groups_system: List[str]
    ) -> None:
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
        display +="Systems:\n"
        display = dispaly_groups_aux(display,self.groups_system)

        return display
    

# each reference have one MultipleBiasResult
class MultipleBiasResult():
    def __init__(
        self,
        systems_bias_results: Dict[str,BiasResult] # {id_of_systems:BiasResults}
    ) -> None:
        self.systems_bias_results = systems_bias_results
        bias_result = list(systems_bias_results.values())[0]
        self.ref = bias_result.ref

    def display_groups_of_each_systems(self,collection_testsets:CollectionTestsets) -> str:
        display = ""

        for sys_id, bias_result in self.systems_bias_results.items():
            system_name = collection_testsets.systems_names[sys_id]
            display += "---" + system_name + "---"
            display += bias_result.display_groups() 

        return display


            