from typing import List

from telescope.metrics.metric import Metric
from telescope.metrics.rouge_two.result import ROUGETwoResult

from rouge import Rouge


class ROUGETwo(Metric):

    name = "ROUGE-2"
    segment_level = True

    def score(self, src: List[str], cand: List[str], ref: List[str]) -> ROUGETwoResult:
        rouge = Rouge()
        scores = rouge.get_scores(cand, ref, avg=True)
        segs = rouge.get_scores(cand, ref)
        scores_segs = [score["rouge-2"]["f"] for score in segs]

        return ROUGETwoResult(
            scores["rouge-2"]["f"], scores_segs, src, cand, ref, self.name, 
            scores["rouge-2"]["p"], scores["rouge-2"]["r"])
