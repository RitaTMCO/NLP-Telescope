from typing import List

from telescope.metrics.metric import Metric
from telescope.metrics.result import MetricResult

from sklearn.metrics import recall_score


class Recall(Metric):

    name = "Recall"
    segment_level = False

    def score(self, src: List[str], cand: List[str], ref: List[str]) -> MetricResult:
        if ref == []:
            score = 0
            label_scores = [0 for _ in self.labels]
        else:
            score = recall_score(ref, cand, average='macro', zero_division=0)
            label_scores = recall_score(ref, cand, labels=self.labels, average=None, zero_division=0)

        return MetricResult(score, label_scores, src, cand, ref, self.name)
