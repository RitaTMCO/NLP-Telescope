import abc
from typing import List,Dict
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult


class UniversalMetric(metaclass=abc.ABCMeta):

    name = None

    def __init__(self, multiple_metrics_results: Dict[str, MultipleMetricResults]):
        self.multiple_metrics_results = multiple_metrics_results

    def ranking_systems(self, systems_universal_scores:Dict[str,float]):
         return {sys_id:systems_universal_scores[sys_id] for sys_id in sorted(systems_universal_scores, key=systems_universal_scores.get, reverse=True)}
        
    @abc.abstractmethod
    def universal_score(self,testset:MultipleTestset) -> MultipleUniversalMetricResult:
        pass