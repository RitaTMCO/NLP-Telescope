import abc
import numpy as np
from typing import Dict, List
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult


class UniversalMetric(metaclass=abc.ABCMeta):

    name = None
    title = None

    def __init__(self, multiple_metrics_results: Dict[str, MultipleMetricResults]):
        self.multiple_metrics_results = multiple_metrics_results #{metric:MultipleMetricResults}
    

    @staticmethod
    def fix_bound(metric:str, score:float):
        if score > 1.0:
            return 1.0
        if metric == "COMET":
            if score < -1.0:
                return -1.0
            else:
                return score
        else:
            if score < 0.0:
                return 0.0
            else:
                return score
            
    @staticmethod
    def normalize_score(metric:str,score:float):
        score = UniversalMetric.fix_bound(metric,score)
        if metric == "COMET":
            min_score = -1
            max_score = 1
            return (score - min_score) / (max_score - min_score)
        elif metric == "TER":
            return 1 - score
        else:
            return score
        
    @staticmethod
    def ranking_systems(systems_universal_scores:Dict[str,float],reverse:bool=True):
        systems_ranks = {}
        r = 1
        sorted_sys_id = sorted(systems_universal_scores, key=systems_universal_scores.get, reverse=reverse)
        num_sys = len(sorted_sys_id)

        for i in range(num_sys):
            sys_id = sorted_sys_id[i]
            score = systems_universal_scores[sys_id]
            if i != 0 and systems_ranks[sorted_sys_id[i-1]]["score"] == score:
                systems_ranks[sys_id] = {"rank":systems_ranks[sorted_sys_id[i-1]]["rank"], "score":score}  
            else:
                systems_ranks[sys_id] = {"rank":r, "score":score} 
                r += 1
        return systems_ranks
    
    @staticmethod
    @abc.abstractmethod
    def universal_score(systems_keys:List[str], metrics_scores:Dict[str,Dict[str,float]], universal_name:str, normalize:bool=True) -> Dict[str,float]:
        pass

    def universal_score_calculation_and_ranking(self,testset:MultipleTestset) -> MultipleUniversalMetricResult:
        ref = testset.ref
        systems_outputs = testset.systems_output
        metrics = list(self.multiple_metrics_results.keys())
        systems_ids = list(systems_outputs.keys())
        metrics_scores = {}
    
        for metric, metric_results in self.multiple_metrics_results.items():
            sys_metrics_scores = {}
            for sys_id, metric_result in metric_results.systems_metric_results.items():
                sys_metrics_scores[sys_id] = metric_result.sys_score
            metrics_scores[metric] = sys_metrics_scores

        if self.name == "pairwise-comparison":
            universal_scores = self.universal_score(systems_ids,metrics_scores, self.name, self.system_a_id, self.system_b_id)
        elif self.title == "Weighted Mean" or self.title == "Weighted Sum":
            universal_scores = self.universal_score(systems_ids,metrics_scores, self.name, self.metrics_weights)
        else:
            universal_scores = self.universal_score(systems_ids,metrics_scores, self.name)

        ranks = self.ranking_systems(universal_scores)

        sys_id_results = {sys_id:UniversalMetricResult(ref, systems_outputs[sys_id], metrics, self.name, self.title, description["rank"], description["score"]) 
                                              for sys_id,description in ranks.items()}
        return MultipleUniversalMetricResult(sys_id_results)


