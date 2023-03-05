import abc
from telescope.testset import NLPTestsets
from telescope.filters import AVAILABLE_NLP_FILTERS

class Task(metaclass=abc.ABCMeta):

    name = None
    metris = list()
    filters = AVAILABLE_NLP_FILTERS
    plots = list()

    @staticmethod
    def input_interface() -> NLPTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        nlp_testset = NLPTestsets.read_data()
        return nlp_testset
    
    @staticmethod
    @abc.abstractmethod
    def plots_interface(metric:str, results:dict, testsets: NLPTestsets, ref_file: str, num_samples: int, sample_ratio: float) -> None:
        """ Interfave to display the plots"""
        pass