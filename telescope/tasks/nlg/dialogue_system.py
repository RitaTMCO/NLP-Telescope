from telescope.tasks.nlg.nlg import NLG
from telescope.testset import NLPTestsets, DialogueTestsets

class DialogueSystem(NLG):
    name = "dialogue system"

    def input_interface() -> NLPTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        dialogue_testset = DialogueTestsets.read_data()
        return dialogue_testset