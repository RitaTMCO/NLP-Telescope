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
    
    #@abc.abstractmethod
    #def plots_interface(self):
    #    """ Interfave to display the plots"""
    #    pass