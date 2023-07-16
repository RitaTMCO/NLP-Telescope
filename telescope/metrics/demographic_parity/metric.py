from typing import List

from telescope.metrics.metric import Metric
from telescope.metrics.result import MetricResult



class DemographicParity(Metric):

    name = "Demographic-Parity"
    segment_level = False

    def score(self, src: List[str], cand: List[str], ref: List[str]) -> MetricResult:
        num_instances = len(ref)
        get_group_right_true = {label:[] for label in self.labels}
        get_group_right_pred = {label:[] for label in self.labels}
        probability_positive_predicted = {}
        demographic_parity = []

        for i in range(num_instances):
            get_group_right_true[ref[i]].append(1)
            if ref[i] == cand[i]:
                get_group_right_pred[ref[i]].append(1)
            else:
                get_group_right_pred[ref[i]].append(0)
        

        for label in self.labels:
            positive_predicted = len([binary for binary in get_group_right_pred[label] if binary == 1])
            num_group = len(get_group_right_pred[label])
            if num_group != 0:
                probability_positive_predicted[label] = positive_predicted/num_group
        
        print(probability_positive_predicted)
        for i in range(len(self.labels)):
            label = self.labels[i]
            if label in probability_positive_predicted:
                for label_2 in self.labels[i:]:
                    if label_2 in probability_positive_predicted:
                        dp = abs(probability_positive_predicted[label] - probability_positive_predicted[label_2])
                        demographic_parity.append(dp)
        
        if not demographic_parity:
            score = 0
        else:
            score = sum(demographic_parity)/len(demographic_parity)


        return MetricResult(score, [], src, cand, ref, self.name)
