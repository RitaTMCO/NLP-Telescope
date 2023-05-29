import abc
from typing import List


class BiasResult(metaclass=abc.ABCMeta):
    def __init__(
        self,
        fairness_metrics_score: List[float],
        src: List[str],
        cand: List[str],
        ref: List[str],
        metric: str,
    ) -> None:
        self.fairness_metrics_score = fairness_metrics_score
        self.src = src
        self.ref = ref
        self.cand = cand
        self.metric = metric
    
    def display_result():
        return NotImplementedError