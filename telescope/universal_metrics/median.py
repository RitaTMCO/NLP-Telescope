import statistics
from typing import Dict
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric

class Median(UniversalMetric):

    name = "median"
    title = "Median"

    def universal_score(self,testset:MultipleTestset) -> Dict[str,float]:
        systems_outputs = testset.systems_output
        systems_ids = list(systems_outputs.keys())
        sys_scores = {sys_id:[] for sys_id in systems_ids}
    
        for metric, metric_results in self.multiple_metrics_results.items():
            min,max=0,0
            if metric == "COMET":
                min,max = self.max_min_COMET(metric_results)
            for sys_id, metric_result in metric_results.systems_metric_results.items():
                sys_scores[sys_id].append(self.normalize_metrics(metric, metric_result.sys_score,max,min))
        
        median_scores = {sys_id:statistics.median(scores) for sys_id,scores in sys_scores.items()}        
        return median_scores