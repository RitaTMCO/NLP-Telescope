import abc
import pandas as pd
from telescope.collection_testsets import CollectionTestsets
from telescope.filters import AVAILABLE_NLP_FILTERS

class Task(metaclass=abc.ABCMeta):

    name = None
    metris = list()
    filters = AVAILABLE_NLP_FILTERS
    plots = list()

    @staticmethod
    def input_interface() -> CollectionTestsets:
        """Interface to collect the necessary inputs to realization of the task evaluation."""
        nlp_testset = CollectionTestset.read_data()
        return nlp_testset
        
    @classmethod
    @abc.abstractmethod
    def plots_interface(cls,metric:str, metrics:list, available_metrics:dict, results:dict, collection_testsets: CollectionTestsets, 
                        ref_file: str, *args) -> None:
        """ Interfave to display the plots"""
        pass