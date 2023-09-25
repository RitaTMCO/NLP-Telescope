from typing import List

from telescope.metrics.metric import Metric
from telescope.metrics.result import MetricResult
from sklearn.metrics import multilabel_confusion_matrix


class FDRate(Metric):

    name = "False Discovery Rate"
    segment_level = False

    def score(self, src: List[str], cand: List[str], ref: List[str]) -> MetricResult:
        if ref == []:
            label_scores = [0 for _ in self.labels]
        else:
            labels = self.labels
            number_of_labels = len(labels)
            label_scores = []
            matrix = multilabel_confusion_matrix(ref, cand, labels=labels)

            for i in range(number_of_labels):
                _,fp,_,tp = list(list(matrix[i][0]) + list(matrix[i][1]))
                if sum([tp,fp]) == 0:
                    label_scores.append(0)
                else:
                    label_scores.append(fp/sum([tp,fp]))

        
        return MetricResult(None, label_scores, src, cand, ref, self.name)