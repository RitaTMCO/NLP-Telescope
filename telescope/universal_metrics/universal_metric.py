import abc
import numpy as np
from typing import Dict
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult


class UniversalMetric(metaclass=abc.ABCMeta):

    name = None
    title = None

    def __init__(self, multiple_metrics_results: Dict[str, MultipleMetricResults]):
        self.multiple_metrics_results = multiple_metrics_results #{metric:MultipleMetricResults}
    
    def normalize(self,min_score:float,max_score:float,score:float) -> float:
        return (score-min_score)/(max_score-min_score)
    
    def normalize_metrics(self,metric:str,sys_score:float,max:float,min:float):
        if metric == "TER":
            return self.normalize(1.0,0.0, sys_score)
        elif metric == "COMET":
            return self.normalize(min,max,sys_score)
        else:
            return sys_score
    
    def max_min_COMET(self,metric_results:MultipleMetricResults):
        list_scores = [metric_result.sys_score for metric_result in list(metric_results.systems_metric_results.values())]
        return min(list_scores), max(list_scores)


    def ranking_systems(self, systems_universal_scores:Dict[str,float],reverse:bool=True):
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
        
    @abc.abstractmethod
    def universal_score(self,testset:MultipleTestset) -> Dict[str,float]:
        pass

    def universal_score_calculation_and_ranking(self,testset:MultipleTestset) -> MultipleUniversalMetricResult:
        ref = testset.ref
        systems_outputs = testset.systems_output
        metrics = list(self.multiple_metrics_results.keys())

        universal_scores = self.universal_score(testset)

        ranks = self.ranking_systems(universal_scores)

        sys_id_results = {sys_id:UniversalMetricResult(ref, systems_outputs[sys_id], metrics, self.name, self.title, description["rank"], description["score"]) 
                                              for sys_id,description in ranks.items()}
        return MultipleUniversalMetricResult(sys_id_results)


