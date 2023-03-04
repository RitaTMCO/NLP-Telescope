from telescope.tasks.nlg.nlg import NLG
from telescope.testset import NLPTestsets, MTTestsets
from telescope.metrics import AVAILABLE_MT_METRICS
from telescope.filters import AVAILABLE_MT_FILTERS

class MachineTranslation(NLG):
    name = "machine translation"
    metrics = AVAILABLE_MT_METRICS + NLG.metrics
    filters = AVAILABLE_MT_FILTERS + NLG.filters

    @staticmethod
    def input_interface() -> NLPTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        mt_testset = MTTestsets.read_data()
        return mt_testset