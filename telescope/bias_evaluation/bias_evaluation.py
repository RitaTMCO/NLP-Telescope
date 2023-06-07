import abc
import json
import streamlit as st
from typing import List,Dict
from telescope.bias_evaluation.bias_result import BiasResult, MultipleBiasResult
from telescope.testset import MultipleTestset



class BiasEvaluation(metaclass=abc.ABCMeta):

    name = None
    available_languages = list()
    groups = list()

    def __init__(self, language: str):
        if not self.language_support(language):
            raise Exception(f"{language} is not supported by {self.name} Bias Evaluation.")
        else:
            self.language = language

    @st.cache
    def open_and_read_identify_terms(self, filename:str) -> List[Dict[str,str]]:
        with open(filename) as file:
            identify_terms = json.load(file)
        return identify_terms

    
    @classmethod
    def language_support(cls, language: str):
        return language in cls.available_languages
    
    @abc.abstractmethod
    def evaluation(self, sys: List[str], ref: List[str]) -> BiasResult:
        pass

    def multiple_evaluation(self, testset: MultipleTestset) -> MultipleBiasResult:
        ref = testset.ref
        systems_bias_results = {sys_id: self.evaluation(sys_output,ref) for sys_id,sys_output in testset.systems_output.items()}
        return MultipleBiasResult(systems_bias_results)


