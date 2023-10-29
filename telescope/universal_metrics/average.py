from typing import Dict, List
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric

class Average(UniversalMetric):

    name = "average"
    title = "Average"
        
    @staticmethod
    def universal_score(systems_keys:List[str], metrics_scores:Dict[str,Dict[str,float]], universal_name:str, normalize:bool=True) -> Dict[str,float]:
        sum = {sys_key:0.0 for sys_key in systems_keys}
        num_metrics = len(metrics_scores)

        for metric, sys_metrics_score in metrics_scores.items():
            for sys_key, sys_score in sys_metrics_score.items():
                if normalize:
                    sum[sys_key] += UniversalMetric.normalize_score(metric, sys_score)
                else:
                    sum[sys_key] += sys_score
        average_scores = {sys_key:sys_sum/num_metrics for sys_key,sys_sum in sum.items()}
        return average_scores