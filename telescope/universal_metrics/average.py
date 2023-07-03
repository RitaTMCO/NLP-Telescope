from typing import List,Dict
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult

class Average(UniversalMetric):

    name = "average"
    
    def universal_score(self, testset:MultipleTestset) -> MultipleUniversalMetricResult:
        
        ref = testset.ref
        systems_outputs = testset.systems_output
        systems_ids = list(systems_outputs.keys())
        metrics = list(self.multiple_metrics_results.keys())
        num_metrics = len(metrics)
        average_scores = {sys_id:0.0 for sys_id in systems_ids}
    
        for metric_results in list(self.multiple_metrics_results.values()):
            for sys_id, metric_result in metric_results.systems_metric_results.items():
                average_scores[sys_id] += metric_result.sys_score
                
        average_scores = {sys_id:score/num_metrics for sys_id,score in average_scores.items()}
        average_scores = self.ranking_systems(average_scores)
        sys_id_results = {sys_id:UniversalMetricResult(ref,systems_outputs[sys_id],metrics, self.name, average_score) 
                                              for sys_id,average_score in average_scores.items()}
        
        return MultipleUniversalMetricResult(sys_id_results)