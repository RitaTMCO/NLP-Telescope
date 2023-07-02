import abc
from typing import List,Dict
from telescope.metrics.metric import MultipleMetricResults
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult


class UniversalMetric(metaclass=abc.ABCMeta):

    name = None

    def __init__(self, multiple_metrics_results: List[MultipleMetricResults]):
        self.multiple_metrics_results = multiple_metrics_results

    @abc.abstractmethod
    def universal_score(self) -> MultipleUniversalMetricResult:
        pass