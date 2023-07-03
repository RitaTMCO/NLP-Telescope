import abc
from typing import List,Dict
from telescope.metrics.metric import MultipleMetricResults
from telescope.testset import MultipleTestset
from telescope.universal_metrics.universal_metric import UniversalMetric
from telescope.universal_metrics.universal_metric_results import UniversalMetricResult, MultipleUniversalMetricResult

class Median(UniversalMetric):

    name = "median"

    def universal_score(self,testset:MultipleTestset)  -> MultipleUniversalMetricResult:
        return MultipleUniversalMetricResult({"":UniversalMetricResult("","",[], self.name, 0.0)})