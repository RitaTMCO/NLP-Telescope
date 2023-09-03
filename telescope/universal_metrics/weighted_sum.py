from typing import Dict
from telescope.metrics import SUM_METRICS_WEIGHTS
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric

class WeightedSum(UniversalMetric):

    title = "Weighted Sum"

    def __init__(self, multiple_metrics_results: Dict[str, MultipleMetricResults], name:str, weights:Dict[str,float]={}):
        super().__init__(multiple_metrics_results)
        if name in list(SUM_METRICS_WEIGHTS.keys()):
            self.metrics_weight = SUM_METRICS_WEIGHTS[name]
        else:
            self.metrics_weight = weights
        self.name = name

    def weight_metric(self, metric:str):
        if metric in list(self.metrics_weight.keys()):
            return float(self.metrics_weight[metric])
        else:
            return 0.0

    def universal_score(self,testset:MultipleTestset) -> Dict[str,float]:
        systems_outputs = testset.systems_output
        systems_ids = list(systems_outputs.keys())
        weighted_scores = {sys_id:0.0 for sys_id in systems_ids}
    
        for metric, metric_results in self.multiple_metrics_results.items():
            weight = self.weight_metric(metric)
            for sys_id, result in metric_results.systems_metric_results.items():
                weighted_scores[sys_id] += result.sys_score * weight
        
        return weighted_scores