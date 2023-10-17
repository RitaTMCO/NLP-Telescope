import statistics
from typing import Dict, List
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric

class Median(UniversalMetric):

    name = "median"
    title = "Median"

    @staticmethod
    def universal_score(systems_keys:List[str], metrics_scores:Dict[str,Dict[str,float]], universal_name:str, normalize:bool=True) -> Dict[str,float]:
        all_sys_scores = {sys_key:[] for sys_key in systems_keys}
    
        for metric, sys_metrics_score in metrics_scores.items():
            for sys_key, sys_score in sys_metrics_score.items():
                if normalize:
                    all_sys_scores[sys_key].append(UniversalMetric.normalize_score(metric, sys_score))
                else:
                    all_sys_scores[sys_key].append(sys_score)

        median_scores = {sys_key:statistics.median(scores) for sys_key,scores in all_sys_scores.items()}        
        return median_scores