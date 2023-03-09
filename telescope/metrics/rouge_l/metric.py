from typing import List

from telescope.metrics.metric import Metric
from telescope.metrics.rouge_l.result import ROUGELResult

from rouge import Rouge


class ROUGEL(Metric):

    name = "ROUGE-L"
    segment_level = False

    def score(self, src: List[str], cand: List[str], ref: List[str]) -> ROUGELResult:
        rouge = Rouge()
        scores = rouge.get_scores(cand, ref, avg=True)
        return ROUGELResult(
            scores["rouge-l"]["f"], [], src, cand, ref, self.name, 
            scores["rouge-l"]["p"], scores["rouge-l"]["r"])
