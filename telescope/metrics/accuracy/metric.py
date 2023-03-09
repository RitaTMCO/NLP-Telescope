from typing import List

from telescope.metrics.metric import Metric
from telescope.metrics.result import MetricResult

from sklearn.metrics import accuracy_score


class Accuracy(Metric):

    name = "Accuracy"
    segment_level = False

    def score(self, src: List[str], cand: List[str], ref: List[str]) -> MetricResult:
        score = accuracy_score(ref, cand)

        return MetricResult(score, [], src, cand, ref, self.name)
