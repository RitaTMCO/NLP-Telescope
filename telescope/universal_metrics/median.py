import statistics
from typing import List,Dict
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult

class Median(UniversalMetric):

    name = "median"

    def universal_score(self,testset:MultipleTestset)  -> MultipleUniversalMetricResult:
        ref = testset.ref
        systems_outputs = testset.systems_output
        systems_ids = list(systems_outputs.keys())
        metrics = list(self.multiple_metrics_results.keys())
        median_scores = {sys_id:[] for sys_id in systems_ids}
    
        for metric_results in list(self.multiple_metrics_results.values()):
            for sys_id, metric_result in metric_results.systems_metric_results.items():
                median_scores[sys_id].append(metric_result.sys_score)
        
        median_scores = {sys_id:statistics.median(scores) for sys_id,scores in median_scores.items()}
        median_scores = self.ranking_systems(median_scores)
        sys_id_results = {sys_id:UniversalMetricResult(ref,systems_outputs[sys_id],metrics, self.name, median_score) 
                                              for sys_id,median_score in median_scores.items()}
        
        return MultipleUniversalMetricResult(sys_id_results)