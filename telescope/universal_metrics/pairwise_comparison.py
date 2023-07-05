import abc
from typing import List,Dict
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult


class PairwiseComparison(UniversalMetric):

    name = "pairwise-comparison"

    def __init__(self, multiple_metrics_results: Dict[str, MultipleMetricResults], system_a_id:str, system_b_id:str):
        super().__init__(multiple_metrics_results)
        self.system_a_id = system_a_id
        self.system_b_id = system_b_id

    def universal_score(self,testset:MultipleTestset) -> MultipleUniversalMetricResult:
        ref = testset.ref
        systems_outputs = testset.systems_output
        metrics = list(self.multiple_metrics_results.keys())
        instances = len(metrics)
        instances_better = {self.system_a_id:0, self.system_b_id:0}

        for metric, metric_results in self.multiple_metrics_results.items():
            sys_scores_a = metric_results.systems_metric_results[self.system_a_id].sys_score
            sys_scores_b = metric_results.systems_metric_results[self.system_b_id].sys_score
            if (metric == "TER" and sys_scores_a <= sys_scores_b) or (metric != "TER" and sys_scores_a >= sys_scores_b): 
                instances_better[self.system_a_id] += 1

        instances_better[self.system_b_id] = instances - instances_better[self.system_a_id]
        instances_better = self.ranking_systems(instances_better)
        sys_id_results = {sys_id:UniversalMetricResult(ref,systems_outputs[sys_id],metrics, self.name, instances) 
                                              for sys_id,instances in instances_better.items()}
        
        return MultipleUniversalMetricResult(sys_id_results)