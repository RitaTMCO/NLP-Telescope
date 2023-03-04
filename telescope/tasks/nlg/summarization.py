from telescope.tasks.nlg.nlg import NLG
from telescope.testset import NLPTestsets, SummTestsets

class Summarization(NLG):
    name = "summarization"

    def input_interface() -> NLPTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        summ_testset = SummTestsets.read_data()
        return summ_testset