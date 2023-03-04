import abc
from telescope.testset import NLPTestsets

class Task(metaclass=abc.ABCMeta):

    name = None
    metris = list()
    filters = list()
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