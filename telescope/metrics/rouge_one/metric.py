from typing import List

from telescope.metrics.metric import Metric
from telescope.metrics.rouge_one.result import ROUGEOneResult

from rouge import Rouge


class ROUGEOne(Metric):

    name = "ROUGE-1"
    segment_level = True

    def score(self, src: List[str], cand: List[str], ref: List[str]) -> ROUGEOneResult:
        rouge = Rouge()
        scores = rouge.get_scores(cand, ref, avg=True)
        segs = rouge.get_scores(cand, ref)
        scores_segs = [score["rouge-1"]["f"] for score in segs]
        
        return ROUGEOneResult(
            scores["rouge-1"]["f"], scores_segs, src, cand, ref, self.name, 
            scores["rouge-1"]["p"], scores["rouge-1"]["r"])
