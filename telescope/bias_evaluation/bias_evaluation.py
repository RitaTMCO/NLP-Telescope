import abc

from typing import List
from telescope.bias_evaluation.bias_result import BiasResult


class BiasEvaluation(metaclass=abc.ABCMeta):

    name = None
    available_languages = list()
    groups = list()

    def __init__(self, language: str = "X"):
        if not self.language_support(language):
            raise Exception(f"{language} is not supported by {self.name}.")
        else:
            self.language = language
    
    @classmethod
    def language_support(cls, language: str):
        return language in cls.available_languages
    
    @abc.abstractmethod
    def evaluation_with_reference(self, src: List[str], cand: List[str], ref: List[str]) -> BiasResult:
        """ Bias Evaluation."""
        pass

