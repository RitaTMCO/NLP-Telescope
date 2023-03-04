from telescope.tasks.nlg.nlg import NLG
from telescope.testset import NLPTestsets, SummTestsets
from telescope.metrics import AVAILABLE_SUMMARIZATION_METRICS

class Summarization(NLG):
    name = "summarization"
    metrics = AVAILABLE_SUMMARIZATION_METRICS + NLG.metrics

    @staticmethod
    def input_interface() -> NLPTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        summ_testset = SummTestsets.read_data()
        return summ_testset