from typing import Dict, List
from telescope.metrics import SUM_METRICS_WEIGHTS
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric

class WeightedSum(UniversalMetric):

    title = "Weighted Sum"

    def __init__(self, multiple_metrics_results: Dict[str, MultipleMetricResults], name:str, weights:Dict[str,float]={}):
        super().__init__(multiple_metrics_results)
        if name in list(SUM_METRICS_WEIGHTS.keys()):
            self.metrics_weights = SUM_METRICS_WEIGHTS[name]
        else:
            self.metrics_weights = weights
        self.name = name

    @staticmethod
    def weight_metric(metric:str,metrics_weights:Dict[str,float]):
        if metric in list(metrics_weights.keys()):
            return float(metrics_weights[metric])
        else:
            return 0.0

    @staticmethod
    def universal_score(systems_keys:List[str], metrics_scores:Dict[str,Dict[str,float]], universal_name:str, 
                        metrics_weights_input:Dict[str,float]={}, normalize:bool=True) -> Dict[str,float]:
        weighted_scores = {sys_id:0.0 for sys_id in systems_keys}

        if metrics_weights_input:
            metrics_weights = metrics_weights_input
        else:
            metrics_weights = SUM_METRICS_WEIGHTS[universal_name]

        for metric, sys_metrics_score in metrics_scores.items():
            weight =  WeightedSum.weight_metric(metric,metrics_weights)
            for sys_key, sys_score in sys_metrics_score.items():
                if normalize:
                    weighted_scores[sys_key] += UniversalMetric.normalize_score(metric, sys_score) * weight
                else:
                    weighted_scores[sys_key] += sys_score * weight        
        return weighted_scores