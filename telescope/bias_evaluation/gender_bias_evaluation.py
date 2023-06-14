import nltk
import streamlit as st
import string

from typing import Tuple, List, Dict
from nltk.tokenize import word_tokenize
from telescope.bias_evaluation.bias_result import BiasResult, MultipleBiasResults
from telescope.bias_evaluation.bias_evaluation import BiasEvaluation
from telescope.testset import MultipleTestset
from telescope.metrics import Accuracy, F1Score

@st.cache
def download(word:str) -> None:
    nltk.download(word)

class GenderBiasEvaluation(BiasEvaluation):
    name = "Gender"
    available_languages = ["en", "pt"]
    nltk_languages = {"en":"english", "pt":"portuguese"}
    groups = ["neutral", "female", "male", "unidentified"]
    directory = 'telescope/bias_evaluation/data/'
    metrics =  [Accuracy, F1Score]

    def __init__(self, language: str):
        super().__init__(language)
        self.directory = self.directory + self.language + "/"
        
        # [{"they":"neutral", "she":"female", "he":"male"},...]
        self.sets_of_gender_terms = self.open_and_read_identify_terms(self.directory + 'gendered_terms.json')
        self.sets_of_occupations = self.open_and_read_identify_terms(self.directory + 'occupations.json')
        self.sets_of_prons_dets = self.open_and_read_identify_terms(self.directory + 'pronouns_determinants.json')
        self.sets_of_suffixes = self.open_and_read_identify_terms(self.directory + 'suffixes.json') 
        download('punkt')


    @st.cache
    def gender_of_word(self,word:str,set_of_words:dict) -> str:
         # [{"they":"neutral", "she":"female", "he":"male"},...]
        if word in set_of_words:
            gender = set_of_words.get(word)
        else:
            gender = "unidentified"
        return gender
    

    @st.cache
    # suffixes: woman and man
    def find_suffix(self, word: str, suffixes: Tuple[str]) -> str:
        bigger_suffix = ""
        for suffix in suffixes:
            if word.endswith(suffix) and len(bigger_suffix) < len(suffix):
                bigger_suffix = suffix
        return bigger_suffix
    


    @st.cache
    def find_and_extract_genders_words(self, set_words_ref:List[str], set_words_per_sys:Dict[str,List[str]], word_k:int, genders_ref:List[str], 
                                       genders_per_sys: Dict[str,List[str]]):

            word_ref = set_words_ref[word_k]
            if word_k + 1 < len(set_words_ref): 
                next_word_ref = set_words_ref[word_k + 1]
            else:
                next_word_ref = ""

            sets_of_terms = self.sets_of_prons_dets + self.sets_of_occupations + self.sets_of_gender_terms
            for set in sets_of_terms:
                gender_ref = ""
                if word_ref in set:
                    gender_ref = self.gender_of_word(word_ref,set)
                    genders_ref.append(gender_ref)
                elif word_ref + " " + next_word_ref in set:
                    gender_ref = self.gender_of_word(word_ref + " " + next_word_ref,set)
                    genders_ref.append(gender_ref)

                if gender_ref:
                    for sys_id, set_words_sys in set_words_per_sys.items():
                        word_sys = set_words_sys[word_k]
                        gender_system = self.gender_of_word(word_sys,set)
                        if gender_system == "unidentified" and word_k + 1 < len(set_words_sys): 
                            next_word_sys = set_words_sys[word_k + 1]
                            gender_system = self.gender_of_word(word_sys + " " + next_word_sys,set)
                        genders_per_sys[sys_id].append(gender_system) 
                    return [genders_ref,genders_per_sys]
 

            for set in self.sets_of_suffixes:
                suffixes = tuple(set.keys())
                if word_ref.endswith(suffixes):
                    suffix_ref = self.find_suffix(word_ref,suffixes)
                    genders_ref.append(self.gender_of_word(suffix_ref,set))
                    for sys_id, set_words_sys in set_words_per_sys.items():
                        word_sys = set_words_sys[word_k]
                        suffix_sys = self.find_suffix(word_sys,suffixes)
                        genders_per_sys[sys_id].append(self.gender_of_word(suffix_sys,set))
                    return [genders_ref,genders_per_sys]
                
            return [genders_ref,genders_per_sys]
    

    def find_extract_genders_all_identify_terms(self, output_per_sys: Dict[str,List[str]], ref: List[str]):
        language = self.nltk_languages[self.language]
        puns = list(string.punctuation)
        num_segs = len(ref)
        genders_ref = list()
        genders_per_sys = {sys_id:list() for sys_id in list(output_per_sys.keys())}

        for seg_i in range(num_segs):
            words_ref = word_tokenize(ref[seg_i].lower(), language=language)
            num_words = len(words_ref)
            words_per_sys = {}
            min_num_words_sys = num_words
            for sys_id, sys_output in output_per_sys.items():
                words_per_sys[sys_id] = word_tokenize(sys_output[seg_i].lower(), language=language)
                if min_num_words_sys > len(words_per_sys[sys_id]):
                    min_num_words_sys = len(words_per_sys[sys_id])

            for word_k in range(num_words):
                if  word_k + 1 > min_num_words_sys:
                        break
                elif words_ref[word_k] in puns:
                    continue
                else:
                    genders_ref,genders_per_sys = self.find_and_extract_genders_words(words_ref,words_per_sys,word_k,genders_ref,genders_per_sys)
        return genders_ref,genders_per_sys

    def score_with_metrics(self, ref:str, sys_output:str, genders_ref:List[str],genders_sys:List[str]) -> BiasResult:
        metrics_results = {name_metric:metric.score([""], genders_sys, genders_ref) for name_metric, metric in self.init_metrics.items()}
        return BiasResult(self.groups,ref,sys_output,genders_ref,genders_sys,metrics_results)

                                       
    def evaluation(self, testset: MultipleTestset) -> MultipleBiasResults:
        """ Gender Bias Evaluation."""
        ref = testset.ref
        output_per_sys = testset.systems_output
        genders_ref, genders_per_sys = self.find_extract_genders_all_identify_terms(output_per_sys,ref)
        systems_bias_results = {
            sys_id: self.score_with_metrics(ref,sys_output,genders_ref,genders_per_sys[sys_id])
            for sys_id,sys_output in output_per_sys.items()
            }
        return MultipleBiasResults(ref, genders_ref, self.groups, systems_bias_results, list(self.init_metrics.keys()))
    