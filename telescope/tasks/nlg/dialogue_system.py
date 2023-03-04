from telescope.tasks.nlg.nlg import NLG
from telescope.testset import NLPTestsets, DialogueTestsets
from telescope.metrics import AVAILABLE_DIALOGUE_METRICS

class DialogueSystem(NLG):
    name = "dialogue system"
    metrics = AVAILABLE_DIALOGUE_METRICS + NLG.metrics

    @staticmethod
    def input_interface() -> NLPTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        dialogue_testset = DialogueTestsets.read_data()
        return dialogue_testset