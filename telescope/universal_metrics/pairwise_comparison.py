from typing import Dict, List
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric


class PairwiseComparison(UniversalMetric):

    name = "pairwise-comparison"
    title = "Pairwise Comparison"

    def __init__(self, multiple_metrics_results: Dict[str, MultipleMetricResults], system_a_id:str, system_b_id:str):
        super().__init__(multiple_metrics_results)
        self.system_a_id = system_a_id
        self.system_b_id = system_b_id

    @staticmethod
    def universal_score(systems_keys:List[str], metrics_scores:Dict[str,Dict[str,float]], universal_name:str, system_a_id: str, system_b_id:str,
                        normalize:bool=True) -> Dict[str,float]:
        
        instances_better = {system_a_id:0.0, system_b_id:0.0}

        for metric, sys_metrics_score in metrics_scores.items():
            if normalize:
                sys_scores_a = UniversalMetric.normalize_score(metric,sys_metrics_score[system_a_id])
                sys_scores_b = UniversalMetric.normalize_score(metric,sys_metrics_score[system_b_id])
            else:
                sys_scores_a = sys_metrics_score[system_a_id]
                sys_scores_b = metric,sys_metrics_score[system_b_id]

            if sys_scores_a > sys_scores_b: 
                instances_better[system_a_id] += 1
            elif sys_scores_a < sys_scores_b: 
                instances_better[system_b_id] += 1
        
        return instances_better