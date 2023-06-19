import abc
import json
from typing import List,Dict
from telescope.bias_evaluation.bias_result import MultipleBiasResults
from telescope.testset import MultipleTestset


class BiasEvaluation(metaclass=abc.ABCMeta):

    name = None
    available_languages = list()
    groups = list()
    metrics = list()

    def __init__(self, language: str):
        if not self.language_support(language):
            raise Exception(f"{language} is not supported by {self.name} Bias Evaluation.")
        else:
            self.language = language 
            self.init_metrics = {metric.name:metric(self.language,self.groups) for metric in self.metrics}

    def open_and_read_identify_terms(self, filename:str) -> List[Dict[str,str]]:
        with open(filename) as file:
            identify_terms = json.load(file)
        return identify_terms

    @classmethod
    def language_support(cls, language: str):
        return language in cls.available_languages

    @abc.abstractmethod
    def evaluation(self, testset: MultipleTestset) -> MultipleBiasResults:
        pass




