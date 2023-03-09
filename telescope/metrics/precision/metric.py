from typing import List

from telescope.metrics.metric import Metric
from telescope.metrics.result import MetricResult

from sklearn.metrics import precision_score


class Precision(Metric):

    name = "Precison"
    segment_level = False

    def score(self, src: List[str], cand: List[str], ref: List[str]) -> MetricResult:
        score = precision_score(ref, cand, average='macro')

        return MetricResult(score, [], src, cand, ref, self.name)
