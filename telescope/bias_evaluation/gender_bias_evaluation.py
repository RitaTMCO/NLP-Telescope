import abc
import streamlit as st

from typing import List
from telescope.bias_evaluation.bias_result import BiasResult
from telescope.bias_evaluation.bias_evaluation import BiasEvaluation


class GenderBiasEvaluation(BiasEvaluation):

    name = "Gender"
    available_languages = ["en", "pt"]
    groups = ["neutral", "female", "male"]

    def evaluation_with_reference(self, cand: List[str], ref: List[str]) -> BiasResult:
        """ Bias Evaluation."""
        st.write(self.language)
        return "TODO"

