import nltk
import streamlit as st
import string

from typing import Tuple, List

from telescope.bias_evaluation.bias_result import BiasResult
from telescope.bias_evaluation.bias_evaluation import BiasEvaluation

from nltk.tokenize import word_tokenize


@st.cache
def download(word:str) -> None:
    nltk.download(word)

class GenderBiasEvaluation(BiasEvaluation):

    name = "Gender"
    available_languages = ["en", "pt"]
    nltk_languages = {"en":"english", "pt":"portuguese"}
    groups = ["neutral", "female", "male"]
    directory = 'telescope/bias_evaluation/data/'


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
    def gender_of_word(self,word:str,set_of_identidy_terms:dict) -> str:
         # [{"they":"neutral", "she":"female", "he":"male"},...]
        gender = set_of_identidy_terms.get(word)
        return gender
    

    @st.cache
    def find_suffix(self, word: str, suffixes: Tuple[str]) -> str:
        bigger_suffix = ""
        for suffix in suffixes:
            if word.endswith(suffix) and len(bigger_suffix) < len(suffix):
                bigger_suffix = suffix
        return bigger_suffix
    


    @st.cache
    def find_and_extract_genders_words(self, set_words_ref:List[str], set_words_sys:List[str], word_k) -> List[str]:
            
            word_ref = set_words_ref[word_k]
            word_sys = set_words_sys[word_k]

            if word_k + 1 < len(set_words_ref): 
                next_word_ref = set_words_ref[word_k + 1]
            else:
                next_word_ref = ""
            if word_k + 1 < len(set_words_sys): 
                next_word_sys = set_words_sys[word_k + 1]
            else:
                next_word_sys = ""

            sets_of_terms = self.sets_of_prons_dets + self.sets_of_occupations + self.sets_of_gender_terms
            for set in sets_of_terms:
                if word_ref in set and word_sys in set:
                    gender_ref = self.gender_of_word(word_ref,set)
                    gender_system = self.gender_of_word(word_sys,set)
                    return [gender_ref,gender_system]
                
                elif word_ref in set and word_sys + " " + next_word_sys in set:
                    gender_ref = self.gender_of_word(word_ref,set)
                    gender_system = self.gender_of_word(word_sys + " " + next_word_sys,set)
                    return [gender_ref,gender_system]
                
                elif word_ref + " " + next_word_ref in set and word_sys in set:
                    gender_ref = self.gender_of_word(word_ref + " " + next_word_ref,set)
                    gender_system = self.gender_of_word(word_sys,set)
                    return [gender_ref,gender_system]
                
                elif word_ref + " " + next_word_ref in set and word_sys + " " + next_word_sys in set:
                    gender_ref = self.gender_of_word(word_ref + " " + next_word_ref,set)
                    gender_system = self.gender_of_word(word_sys + " " + next_word_sys,set)
                    return [gender_ref,gender_system]
 
            for set in self.sets_of_suffixes:
                suffixes = tuple(set.keys())
                if word_ref.endswith(suffixes) and word_sys.endswith(suffixes):
                    suffix_ref = self.find_suffix(word_ref,suffixes)
                    gender_ref = self.gender_of_word(suffix_ref,set)
                    suffix_sys = self.find_suffix(word_sys,suffixes)
                    gender_system = self.gender_of_word(suffix_sys,set)
                    return [gender_ref,gender_system]
            return ["", ""]
    

    def find_extract_genders_all_identify_terms(self, sys_output: List[str], ref: List[str]) -> List[List[str]]:
        language = self.nltk_languages[self.language]

        puns = list(string.punctuation)

        num_segs = len(ref)

        genders_ref = list()
        genders_sys = list()

        for seg_i in range(num_segs):
            words_ref = word_tokenize(ref[seg_i].lower(), language=language)
            num_words = len(words_ref)
            words_sys = word_tokenize(sys_output[seg_i].lower(), language=language)
            num_words_sys = len(words_sys)

            for word_k in range(num_words):
                if  word_k + 1 > num_words_sys:
                        break
                elif words_ref[word_k] in puns or words_sys[word_k] in puns:
                    continue
                else:
                    gender_word_ref, gender_word_sys = self.find_and_extract_genders_words(words_ref,words_sys,word_k)

                    if gender_word_ref and gender_word_sys:
                        genders_ref.append(gender_word_ref)
                        genders_sys.append(gender_word_sys)

        return [genders_ref,genders_sys]

                  
    def evaluation(self, sys_output: List[str], ref: List[str]) -> BiasResult:
        """ Gender Bias Evaluation."""
        genders_ref, genders_sys = self.find_extract_genders_all_identify_terms(sys_output,ref)
        return BiasResult(self.groups,ref,sys_output,genders_ref,genders_sys)
    
    