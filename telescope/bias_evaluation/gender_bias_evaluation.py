import nltk
import spacy
import string
from typing import Tuple, List, Dict
from nltk.tokenize import word_tokenize
from spacy.tokens import Token, Doc
from telescope.bias_evaluation.bias_result import BiasResult, MultipleBiasResults
from telescope.bias_evaluation.bias_evaluation import BiasEvaluation
from telescope.testset import MultipleTestset
from telescope.metrics import Accuracy, F1Score
from telescope.metrics.metric import Metric

class GenderBiasEvaluation(BiasEvaluation):
    name = "Gender"
    available_languages = ["en", "pt"]
    groups = ["neutral", "female", "male", "unidentified"]
    directory = 'telescope/bias_evaluation/data/'
    metrics =  [Accuracy, F1Score]

    nltk_languages = {"en":"english", "pt":"portuguese"}
    models = {"en":"en_core_web_sm","pt":"pt_core_news_sm"}
    groups_nlp = {"Neut": "neutral", "Fem" : "female", "Masc":"male"}

    def __init__(self, language: str):
        super().__init__(language)
        self.options_bias_evaluation_funs = {"with dataset": self.find_extract_genders_identify_terms_with_dataset, 
                                             "with library": self.find_extract_genders_identify_terms_with_library, 
                                             "with datasets and library": self.find_extract_genders_identify_terms_combination
                                            }
        self.directory = self.directory + self.language + "/"
        #[{"they":"neutral", "she":"female", "he":"male"},...]
        self.sets_of_gender_terms = self.open_and_read_identify_terms(self.directory + 'gendered_terms.json')
        self.sets_of_occupations = self.open_and_read_identify_terms(self.directory + 'occupations.json')
        self.sets_of_prons_dets = self.open_and_read_identify_terms(self.directory + 'pronouns_determinants.json')
        self.sets_of_suffixes = self.open_and_read_identify_terms(self.directory + 'suffixes.json') 

        self.nlp = spacy.load(self.models[self.language])

        self.nltk_language = self.nltk_languages[self.language]
        nltk.download('punkt')
            

    def find_extract_genders_identify_terms(self, output_per_sys:Dict[str,List[str]], ref:List[str], option_bias_evaluation:str):
        puns = list(string.punctuation)
        num_segs = len(ref)
        genders_ref_per_seg = {}
        genders_per_sys_per_seg = {sys_id:{} for sys_id in list(output_per_sys.keys())}

        for seg_i in range(num_segs):
            genders_ref = list()
            genders_per_sys = {sys_id:list() for sys_id in list(output_per_sys.keys())}

            option_fun = self.options_bias_evaluation_funs[option_bias_evaluation]
            genders_ref,genders_per_sys = option_fun(output_per_sys, ref, puns, seg_i, genders_ref, genders_per_sys)

            genders_ref_per_seg[seg_i] = genders_ref
            for sys_id, groups in genders_per_sys.items():
                genders_per_sys_per_seg[sys_id].update({seg_i:groups})
        return genders_ref_per_seg,genders_per_sys_per_seg
    

    def score_with_metrics(self, ref:str, sys_output:str, genders_ref:List[str], genders_ref_per_seg:Dict[int,List[str]], genders_sys_per_seg:List[str], 
                           init_metrics:List[Metric]) -> BiasResult:
        genders_sys = [gender for genders in list(genders_sys_per_seg.values()) for gender in genders]
        metrics_results = {metric.name:metric.score([""], genders_sys, genders_ref) for metric in init_metrics}
        return BiasResult(self.groups,ref,sys_output,genders_ref,genders_ref_per_seg,genders_sys,genders_sys_per_seg, metrics_results)
    

    def evaluation(self, testset: MultipleTestset, option_bias_evaluation:str) -> MultipleBiasResults:
        """ Gender Bias Evaluation."""
        ref = testset.ref
        output_per_sys = testset.systems_output

        genders_ref_per_seg, genders_per_sys_per_seg = self.find_extract_genders_identify_terms(output_per_sys,ref,option_bias_evaluation)
        genders_ref = [gender for genders in list(genders_ref_per_seg.values()) for gender in genders]

        init_metrics = [metric(self.language,self.groups) for metric in self.metrics]
        systems_bias_results = {
            sys_id: self.score_with_metrics(ref,sys_output,genders_ref,genders_ref_per_seg,genders_per_sys_per_seg[sys_id],init_metrics)
            for sys_id,sys_output in output_per_sys.items()
            }
        return MultipleBiasResults(ref, genders_ref, genders_ref_per_seg, self.groups, systems_bias_results, self.metrics)


#------------------------- Evaluation with datasets ---------------------------------

    def find_gender_from_set(self, word:str,set_of_words:dict) -> str:
         # [{"they":"neutral", "she":"female", "he":"male"},...]
        if word in set_of_words:
            gender = set_of_words.get(word)
        else:
            gender = "unidentified"
        return gender
    

    def extract_gender_from_dataset(self, set_words_ref:List[str], set_words_per_sys:Dict[str,List[str]], word_k:int, genders_ref:List[str], 
                                    genders_per_sys: Dict[str,List[str]], sets_of_terms:List[Dict[str,str]]):

        def next_word(set_words:List[str], word_k:int):
            if word_k + 1 < len(set_words): 
                return set_words[word_k + 1]
            else:
                return ""
        
        def is_word_in_set(word:str, next_word:str, set:Dict[str,str]):
            if word in set:
                return self.find_gender_from_set(word,set)
            elif word + " " + next_word in set:
                return self.find_gender_from_set(word + " " + next_word,set)
            return ""
    
        # Exemple: suffixes --> woman and man
        def find_suffix(word: str, suffixes: Tuple[str]) -> str:
            bigger_suffix = ""
            for suffix in suffixes:
                if word.endswith(suffix) and len(bigger_suffix) < len(suffix):
                    bigger_suffix = suffix
            return bigger_suffix
        
        word_ref = set_words_ref[word_k]
        next_word_ref = next_word(set_words_ref, word_k)

        word_per_sys,next_word_per_sys = {}, {}
        for sys_id, set_words_sys in set_words_per_sys.items():
            word_per_sys[sys_id] = set_words_sys[word_k]
            next_word_per_sys[sys_id] = next_word(set_words_sys,word_k)
        systems_ids = list(word_per_sys.keys())

        # sets_of_terms
        for set in sets_of_terms:
            gender_ref = is_word_in_set(word_ref, next_word_ref, set)
            if gender_ref and all(is_word_in_set(word_per_sys[sys_id],next_word_per_sys[sys_id],set) for sys_id in systems_ids):
                genders_ref.append(gender_ref)
                for sys_id in systems_ids:
                    gender_system = is_word_in_set(word_per_sys[sys_id], next_word_per_sys[sys_id], set)
                    genders_per_sys[sys_id].append(gender_system) 
                return [genders_ref,genders_per_sys]

        # sets_of_suffixes
        for set in self.sets_of_suffixes:
            suffixes = tuple(set.keys())
            if word_ref.endswith(suffixes) and all(word_per_sys[sys_id].endswith(suffixes) for sys_id in systems_ids):
                suffix_ref = find_suffix(word_ref,suffixes)
                genders_ref.append(self.find_gender_from_set(suffix_ref,set))
                for sys_id, set_words_sys in set_words_per_sys.items():
                    suffix_sys = find_suffix(set_words_sys[word_k],suffixes)
                    genders_per_sys[sys_id].append(self.find_gender_from_set(suffix_sys,set))
                return [genders_ref,genders_per_sys]    
              
        return [genders_ref,genders_per_sys]



    def find_extract_genders_identify_terms_with_dataset(self, output_per_sys: Dict[str,List[str]], ref: List[str], puns:List[str], seg_i:int, 
                                                             genders_ref:List[str], genders_per_sys:Dict[str,List[str]]):

        words_ref = word_tokenize(ref[seg_i].lower(), language=self.nltk_language)
        num_words = len(words_ref)
        words_per_sys = {}
        min_num_words_sys = num_words
        
        for sys_id, sys_output in output_per_sys.items():
            words_per_sys[sys_id] = word_tokenize(sys_output[seg_i].lower(), language=self.nltk_language)
            if min_num_words_sys > len(words_per_sys[sys_id]):
                min_num_words_sys = len(words_per_sys[sys_id])

        for word_k in range(num_words):
            if  word_k + 1 > min_num_words_sys:
                    break
            elif words_ref[word_k] in puns:
                continue
            else:
                genders_ref,genders_per_sys = self.extract_gender_from_dataset(words_ref, 
                                                                               words_per_sys, 
                                                                               word_k, 
                                                                               genders_ref, 
                                                                               genders_per_sys,
                                                                               self.sets_of_prons_dets + self.sets_of_occupations + self.sets_of_gender_terms)        
        return genders_ref,genders_per_sys
    


#------------------------- Evaluation with library ---------------------------------

    def find_gender_morph(self,token:Token):
        gender = token.morph.get("Gender")
        if gender:
            return self.groups_nlp[gender[0]]
        return "unidentified"
    
    def has_morph_gender_and_same_lemma(self,doc_ref:Doc, doc_per_sys:Dict[str,Doc], token_k:int):
        has_morph = doc_ref[token_k].has_morph() and all(doc_sys[token_k].has_morph() for doc_sys in list(doc_per_sys.values()))
        same_lemma = all(doc_ref[token_k].lemma_ == doc_sys[token_k].lemma_ for doc_sys in list(doc_per_sys.values()))
        has_gender_ref = (self.find_gender_morph(doc_ref[token_k]) != "unidentified")
        return has_morph and has_gender_ref and same_lemma
    
    def extract_gender_from_libary(self, doc_ref:Doc, doc_per_sys:Dict[str,Doc], token_k:int, genders_ref:List[str], genders_per_sys:Dict[str,List[str]]):
        gender_ref = self.find_gender_morph(doc_ref[token_k])
        genders_ref.append(gender_ref)
        for sys_id, doc_sys in doc_per_sys.items():
            gender_sys = self.find_gender_morph(doc_sys[token_k])
            genders_per_sys[sys_id].append(gender_sys)
        return genders_ref,genders_per_sys

      
    def find_extract_genders_identify_terms_with_library(self, output_per_sys: Dict[str,List[str]], ref: List[str], puns:List[str],seg_i:int, 
                                                             genders_ref:List[str], genders_per_sys:Dict[str,List[str]]):
        doc_ref = self.nlp(ref[seg_i].lower())
        num_tokens = len(doc_ref)
        doc_per_sys = {}
        min_num_tokens_sys = num_tokens 
        for sys_id, sys_output in output_per_sys.items():
            doc_per_sys[sys_id] = self.nlp(sys_output[seg_i].lower())
            if min_num_tokens_sys > len(doc_per_sys[sys_id]):
                min_num_tokens_sys = len(doc_per_sys[sys_id])

        for token_k in range(num_tokens):
            if  token_k + 1 > min_num_tokens_sys:
                    break
            elif doc_ref[token_k].text in puns:
                continue
            elif self.has_morph_gender_and_same_lemma(doc_ref,doc_per_sys,token_k):
                genders_ref,genders_per_sys = self.extract_gender_from_libary(doc_ref, 
                                                                              doc_per_sys, 
                                                                              token_k, 
                                                                              genders_ref, 
                                                                              genders_per_sys)
        return genders_ref,genders_per_sys
    
#------------------------- Evaluation with library and datasets ---------------------------------
    def find_extract_genders_identify_terms_combination(self, output_per_sys: Dict[str,List[str]], ref: List[str], puns:List[str], seg_i:int, 
                                                             genders_ref:List[str], genders_per_sys:Dict[str,List[str]]):

        doc_ref = self.nlp(ref[seg_i].lower())
        num_tokens = len(doc_ref)
        doc_per_sys = {}
        min_num_tokens_sys = num_tokens 
        for sys_id, sys_output in output_per_sys.items():
            doc_per_sys[sys_id] = self.nlp(sys_output[seg_i].lower())
            min_num_tokens_sys = min(len(doc_per_sys[sys_id]),min_num_tokens_sys)

        for token_k in range(num_tokens):
            if  token_k + 1 > min_num_tokens_sys:
                break
            elif doc_ref[token_k].text in puns:
                continue
            elif self.has_morph_gender_and_same_lemma(doc_ref,doc_per_sys,token_k):
                genders_ref,genders_per_sys = self.extract_gender_from_libary(doc_ref, doc_per_sys, token_k, genders_ref, genders_per_sys)
            else:   
                set_tokes_ref = [token.text for token in doc_ref]
                set_tokes_per_sys = {sys_id:[token.text for token in doc_sys] for sys_id,doc_sys in doc_per_sys.items()}
                genders_ref, genders_per_sys = self.extract_gender_from_dataset(set_tokes_ref,
                                                                                set_tokes_per_sys,
                                                                                token_k,
                                                                                genders_ref,
                                                                                genders_per_sys,
                                                                                self.sets_of_prons_dets + self.sets_of_occupations + self.sets_of_gender_terms)
        return genders_ref,genders_per_sys