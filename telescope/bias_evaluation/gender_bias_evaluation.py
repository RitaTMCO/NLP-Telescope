import nltk
import spacy
import time

from typing import Tuple, List, Dict
from nltk.tokenize import word_tokenize
from spacy.tokens import Token,Doc
from telescope.bias_evaluation.bias_result import BiasResult, MultipleBiasResults
from telescope.bias_evaluation.bias_evaluation import BiasEvaluation
from telescope.testset import MultipleTestset
from telescope.metrics.metric import Metric

class GenderBiasEvaluation(BiasEvaluation):
    name = "Gender"
    available_languages = ["en", "pt"]
    groups = ["neutral", "female", "male"]

    directory = 'telescope/bias_evaluation/data/'
    nltk_languages = {"en":"english", "pt":"portuguese"}
    models = {"en":"en_core_web_lg","pt":"pt_core_news_lg"}
    groups_nlp = {"Neut": "neutral", "Fem" : "female", "Masc":"male"}
    options_bias_evaluation = ["dictionary-based approach","linguistic approach","hybrid approach"]

    def __init__(self, language: str):
        super().__init__(language)
        self.options_bias_evaluation_funs = {"dictionary-based approach": self.evaluation_with_dataset, 
                                             "linguistic approach": self.evaluation_with_library, 
                                             "hybrid approach": self.evaluation_with_combination
                                            }
        self.directory = self.directory + self.language + "/"
        #[{"they":"neutral", "she":"female", "he":"male"},...]
        self.gender_sets_of_gender_terms = self.open_and_read_identify_terms(self.directory + 'gendered_terms.json')
        self.gender_sets_of_occupations = self.open_and_read_identify_terms(self.directory + 'occupations.json')
        self.gender_sets_of_prons = self.open_and_read_identify_terms(self.directory + 'pronouns.json')
        self.gender_sets_of_dets = self.open_and_read_identify_terms(self.directory + 'determiners.json')
        self.gender_sets_of_prep = self.open_and_read_identify_terms(self.directory + 'prepositions.json')
        self.gender_sets_of_suffixes = self.open_and_read_identify_terms(self.directory + 'suffixes.json') 
        
        self.nlp = spacy.load(self.models[self.language])
        self.nltk_language = self.nltk_languages[self.language]
        nltk.download('punkt')
    
    def dep_language(self, token:Token):
        if self.language == "pt":
            return (token.dep_== "nsubj" or token.dep_== "nsubj:pass" or token.dep_== "obj" or token.dep_ == "iobj" or 
                    token.dep_== "obl" or token.dep_== "obl:agent" or token.dep_ == "nmod" or 
                    token.dep_ == "compound") 
        elif self.language == "en":
            return (token.dep_== "nsubj" or token.dep_== "nsubjpass" or token.dep_== "dobj"  or token.dep_ == "iobj" or
                      token.dep_== "pobj" or token.dep_== "agent" or token.dep_ == "nmod" or
                      token.dep_ == "compound")
        
    def is_this_ner(self,term:str, ner:list):
        for term_e, ner_e in ner:
            if term_e == term:
                return (ner_e == "PRODUCT" or ner_e == "TIME" or ner_e == "DATE" or ner_e == "PERCENT" or ner_e == "QUANTITY" or   ner_e == "CARDINAL")

    def find_extract_genders_match_identify_terms(self, output_per_sys:Dict[str,List[str]], ref:List[str], option_bias_evaluation:str):
        num_segs = len(ref)
        sys_ids = list(output_per_sys.keys())
        genders_ref_per_seg = {}
        identity_terms_ref_per_seg = {}
        genders_per_sys_per_seg = {sys_id:{} for sys_id in sys_ids}
        identity_terms_per_sys_per_seg = {sys_id:{} for sys_id in sys_ids}

        for seg_i in range(num_segs):
            genders_ref = list()
            genders_per_sys = {sys_id:list() for sys_id in list(output_per_sys.keys())}
            sys_seg_output = {sys_id:sys_output[seg_i] for sys_id, sys_output in output_per_sys.items()}

            _option_fun = self.options_bias_evaluation_funs[option_bias_evaluation]
            
            genders_ref, genders_per_sys,seg_terms_ref, seg_terms_per_sys = _option_fun(ref[seg_i], sys_seg_output, genders_ref, genders_per_sys)   

            genders_ref_per_seg[seg_i] = genders_ref
            identity_terms_ref_per_seg[seg_i] = seg_terms_ref
            for sys_id in sys_ids:
                genders_per_sys_per_seg[sys_id].update({seg_i:genders_per_sys[sys_id]})
                identity_terms_per_sys_per_seg[sys_id].update({seg_i:seg_terms_per_sys[sys_id]})
        
        return genders_ref_per_seg,genders_per_sys_per_seg,identity_terms_ref_per_seg, identity_terms_per_sys_per_seg
    

    def score_with_metrics(self, ref:str, sys_output:str, genders_ref:List[str], genders_ref_per_seg:Dict[int,List[str]], text_genders_ref_per_seg:dict, 
                           text_genders_sys_per_seg:dict, identity_terms_per_sys_per_sys:dict, init_metrics:List[Metric]) -> BiasResult:
        genders_sys_per_seg = {seg_i: [token_gen["gender"] for token_gen in text_genders] for seg_i, text_genders in text_genders_sys_per_seg.items()}
        genders_sys = [gender for genders in list(genders_sys_per_seg.values()) for gender in genders]
        metrics_results = {metric.name:metric.score([""], genders_sys, genders_ref) for metric in init_metrics}
        return BiasResult(self.groups,ref,sys_output,identity_terms_per_sys_per_sys, genders_ref,genders_ref_per_seg,genders_sys,genders_sys_per_seg, text_genders_ref_per_seg,
                          text_genders_sys_per_seg, metrics_results)
    

    def evaluation(self, testset: MultipleTestset, option_bias_evaluation:str) -> MultipleBiasResults:
        """ Gender Bias Evaluation."""
        start = time.time()
        ref = testset.ref
        output_per_sys = testset.systems_output

        [text_genders_ref_per_seg, text_genders_per_sys_per_seg,identity_terms_ref_per_seg, 
         identity_terms_per_sys_per_seg] = self.find_extract_genders_match_identify_terms(output_per_sys,ref,option_bias_evaluation)
        
        genders_ref_per_seg = {seg_i: [token_gen["gender"] for token_gen in text_genders] for seg_i, text_genders in text_genders_ref_per_seg.items()}
        genders_ref = [gender for genders in list(genders_ref_per_seg.values()) for gender in genders]

        init_metrics = [metric(self.language,self.groups) for metric in self.metrics]

        systems_bias_results = {
            sys_id: self.score_with_metrics(ref,sys_output,genders_ref,genders_ref_per_seg,
                                            text_genders_ref_per_seg,text_genders_per_sys_per_seg[sys_id],identity_terms_per_sys_per_seg[sys_id], init_metrics) 
                                            for sys_id,sys_output in output_per_sys.items()
            }
        end = time.time()
        return MultipleBiasResults(ref, identity_terms_ref_per_seg, genders_ref, genders_ref_per_seg, self.groups, systems_bias_results, 
                                   text_genders_ref_per_seg, self.metrics, (end-start))


#------------------------- Evaluation with dictionary-based approach ---------------------------------
    def intersection_gender_set(self,gender_set_1:dict,gender_set_2:dict):
        for word,gender in gender_set_1.items():
            if word in gender_set_2 and gender_set_2[word] == gender:
                return True
        return False

    def find_gender_from_dictionaries(self, segemnet_words:List[str], word_k:int):
        
        def find_gender_from_gender_set(word:str,gender_set:dict):
         # gender_set:{"they":"neutral", "she":"female", "he":"male"}
            if word in gender_set:
                gender = gender_set.get(word)
            else:
                gender = ""
            return gender

        def find_next_word(segemnet_words:List[str], word_k:int):
            if word_k + 1 < len(segemnet_words): 
                return segemnet_words[word_k + 1]
            else:
                return ""

        def find_pre_word(segemnet_words:List[str], word_k:int):
            if word_k != 0: 
                return segemnet_words[word_k - 1]
            else:
                return ""
        
        def is_word_in_set(word:str, next_word:str, gender_set:Dict[str,str]):
            if word in gender_set:
                return word, find_gender_from_gender_set(word,gender_set)
            elif word + " " + next_word in gender_set:
                return word + " " + next_word, find_gender_from_gender_set(word + " " + next_word,gender_set)
            return word, ""
    
        # Exemple: suffixes --> woman and man
        def find_suffix(word: str, suffixes: Tuple[str]) -> str:
            bigger_suffix = ""
            for suffix in suffixes:
                if word.endswith(suffix) and len(bigger_suffix) < len(suffix):
                    bigger_suffix = suffix
            return bigger_suffix

        def how_many_gender(gender_set):
            genders = []
            for gender in list(gender_set.values()):
                if gender not in genders:
                    genders.append(gender)
            return len(genders)
        
        gender_sets_of_terms = self.gender_sets_of_occupations + self.gender_sets_of_gender_terms + self.gender_sets_of_prons
        dets_prep = self.gender_sets_of_dets + self.gender_sets_of_prep
        word = segemnet_words[word_k]
        next_word = find_next_word(segemnet_words, word_k)
        pre_word = find_pre_word(segemnet_words, word_k)

        # gender_sets_of_terms
        for gender_set in gender_sets_of_terms:
            word, gender = is_word_in_set(word, next_word, gender_set) 
            if gender:
                if how_many_gender(gender_set) == 2:
                #gender_sets_deter_prep
                    for gender_det_set in dets_prep:
                        _, gender_det = is_word_in_set(pre_word, "", gender_det_set) 
                        if gender_det:   
                            return word, gender_det, {}
                return word, gender, gender_set
        
        # gender_sets_of_suffixes
        for gender_set in self.gender_sets_of_suffixes:
            suffixes = tuple(gender_set.keys())
            if word.endswith(suffixes):
                suffix = find_suffix(word,suffixes)
                gender = find_gender_from_gender_set(suffix,gender_set)
                if gender:   
                    return word, gender, gender_set
        
        #gender_sets_deter_prep
        for gender_set in dets_prep:
            _, gender = is_word_in_set(pre_word, "", gender_set) 
            if gender:   
                return word, gender, {}
        return word, "", {}
        

    def find_identify_terms_and_extract_gender_with_dataset(self, segment:str):
        segment_words = word_tokenize(segment.lower(), language=self.nltk_language)
        num_words = len(segment_words)
        terms = []
        for word_k in range(num_words):
            word,gender,gender_set = self.find_gender_from_dictionaries(segment_words, word_k)
            if gender != "":
                terms.append({"term":word, "gender": gender, "gender_set":gender_set})
        return terms
    
    def has_match_with_dataset(self, term_ref:dict, seg_terms_per_sys:Dict[str,List[dict]]):
        return all(
            any(self.is_match_with_dataset(term_ref, term_sys) for term_sys in seg_terms_sys) 
                for seg_terms_sys in list(seg_terms_per_sys.values())
            )
    
    def is_match_with_dataset(self,term_ref:dict,term_sys: dict):
        if term_ref["gender"] != "":
            if term_ref["gender_set"] == {} and term_sys["gender_set"] == {}:
                return term_ref["term"] == term_sys["term"]
            else:
                return self.intersection_gender_set(term_ref["gender_set"],term_sys["gender_set"])


    def match_identify_terms_with_dataset(self, seg_terms_ref:List[dict], seg_terms_per_sys:Dict[str,List[dict]], genders_ref:List[str], 
                                          genders_per_sys:Dict[str,List[str]]):
        for term_ref in seg_terms_ref:
            if self.has_match_with_dataset(term_ref, seg_terms_per_sys):
                for sys_id in list(seg_terms_per_sys.keys()):
                    for term_sys in seg_terms_per_sys[sys_id]:
                        if self.is_match_with_dataset(term_ref,term_sys):
                            genders_per_sys[sys_id].append({"term":term_sys["term"], "gender":term_sys["gender"]})
                            seg_terms_per_sys[sys_id].remove(term_sys)
                            break
                genders_ref.append({"term":term_ref["term"], "gender":term_ref["gender"]})
        return genders_ref, genders_per_sys

    
    def evaluation_with_dataset(self, ref_seg:str, seg_per_sys:Dict[str,str], genders_ref:List[str], genders_per_sys: Dict[str,List[str]]):     
        seg_terms_ref = self.find_identify_terms_and_extract_gender_with_dataset(ref_seg)
        seg_terms_per_sys = {sys_id:self.find_identify_terms_and_extract_gender_with_dataset(seg_per_sys[sys_id]) for sys_id in list(genders_per_sys.keys())}
        
        identity_terms_found_ref = [ {"term":term["term"], "gender":term["gender"]} for term in seg_terms_ref]
        identity_terms_found_per_sys = {sys_id:[ {"term":term["term"], "gender":term["gender"]} for term in seg_terms_per_sys[sys_id]] for sys_id in list(genders_per_sys.keys())}
        
        genders_ref, genders_per_sys = self.match_identify_terms_with_dataset(seg_terms_ref, seg_terms_per_sys, genders_ref, genders_per_sys)
        return genders_ref, genders_per_sys, identity_terms_found_ref, identity_terms_found_per_sys

#------------------------- Evaluation with library ---------------------------------
    def find_gender_from_morph(self,token:Token):
        gen = token.morph.get("Gender")
        gender = self.groups_nlp[gen[0]]
        return gender
    
    def find_prontype_definite_person_case_from_morph(self,token:Token):
        data = [token.morph.get("PronType"), token.morph.get("Definite"), token.morph.get("Person"), token.morph.get("Case"),token.morph.get("Number")]
        info = []
        for dt in data:
            if dt:
                info.append(dt[0])
        return info
    
    def is_determiner_or_preposition(self,token:Token):
        return token.pos_ == "ADP" or (token.pos_ == "DET" and token.dep_ == "det")
    
    def has_gender(self,token:Token):
        return (token.has_morph() and token.morph.get("Gender"))
    
    def find_gender_from_library(self,token:Token, doc:Doc,i:int):
        gender = ""
        if token.pos_ == "NOUN" and not self.has_gender(token) and i!=0 and self.is_determiner_or_preposition(doc[i-1]) and self.has_gender(doc[i-1]):
            gender = self.find_gender_from_morph(doc[i-1])
        elif self.has_gender(token):
            gender = self.find_gender_from_morph(token)
        return gender

    
    def find_identify_terms_and_extract_gender_with_library(self, segment:str):
        doc = self.nlp(segment.lower())  
        n_segs = len(doc)
        term = []
        ents = [(ent.text, ent.label_) for ent in doc.ents]
        for i in range(n_segs):
            token = doc[i]
            if (token.pos_ == "NOUN" or token.pos_ == "PRON") and self.dep_language(token) and  not self.is_this_ner(token.text, ents):
                gender = self.find_gender_from_library(token,doc,i)
                if gender != "":
                    term.append({"term":token.text,"gender":gender,"token":token})
        return term
        
    def has_match_with_library(self,term_ref:dict, seg_terms_per_sys:Dict[str,List[dict]]):
        return all(
            any(self.is_match_with_library(term_ref,term_sys) for term_sys in seg_terms_sys) 
            for seg_terms_sys in list(seg_terms_per_sys.values())    
            )
    
    def is_match_with_library(self,term_ref:dict, term_sys:dict):
        token_ref = term_ref["token"]
        token_sys = term_sys["token"]
        lemma = ((token_ref.lemma_ == token_sys.lemma_) 
                 and self.find_prontype_definite_person_case_from_morph(token_ref) == self.find_prontype_definite_person_case_from_morph(token_sys)
                 and token_ref.pos_ == token_ref.pos_
                 and token_ref.tag_ == token_sys.tag_
                 and token_ref.dep_ == token_sys.dep_)
        pron = (token_ref.pos_ == "PRON" and token_sys.pos_ == "PRON" 
                and token_ref.tag_ == token_sys.tag_
                and self.find_prontype_definite_person_case_from_morph(token_ref) == self.find_prontype_definite_person_case_from_morph(token_sys)
                and token_ref.dep_ == token_sys.dep_)

        return lemma or pron
    
    def match_identify_terms_with_library(self, seg_terms_ref:List[dict], seg_terms_per_sys:Dict[str,List[dict]], genders_ref:List[str], 
                                          genders_per_sys:Dict[str,List[str]]):
        
        for term_ref in seg_terms_ref:
            if self.has_match_with_library(term_ref, seg_terms_per_sys):
                for sys_id in list(seg_terms_per_sys.keys()):
                    for term_sys in seg_terms_per_sys[sys_id]:
                        if self.is_match_with_library(term_ref,term_sys):
                            genders_per_sys[sys_id].append({"term":term_sys["term"], "gender":term_sys["gender"]})
                            seg_terms_per_sys[sys_id].remove(term_sys)
                            break
                genders_ref.append({"term":term_ref["term"], "gender":term_ref["gender"]})
        return genders_ref, genders_per_sys

    
    def evaluation_with_library(self, ref_seg:str, seg_per_sys:Dict[str,str], genders_ref:List[str], genders_per_sys: Dict[str,List[str]]):     
        seg_terms_ref = self.find_identify_terms_and_extract_gender_with_library(ref_seg)
        seg_terms_per_sys = {sys_id:self.find_identify_terms_and_extract_gender_with_library(seg_per_sys[sys_id]) for sys_id in list(genders_per_sys.keys())}

        identity_terms_found_ref = [ {"term":term["term"], "gender":term["gender"]} for term in seg_terms_ref]
        identity_terms_found_per_sys = {sys_id:[ {"term":term["term"], "gender":term["gender"]} for term in seg_terms_per_sys[sys_id]] for sys_id in list(genders_per_sys.keys())}
        
        genders_ref, genders_per_sys = self.match_identify_terms_with_library(seg_terms_ref, seg_terms_per_sys, genders_ref, genders_per_sys)
        return genders_ref, genders_per_sys, identity_terms_found_ref, identity_terms_found_per_sys
    
#------------------------- Evaluation with library and datasets ---------------------------------
    def find_identify_terms_and_extract_gender_with_combination(self, segment:str):
        doc = self.nlp(segment.lower())        
        num_tokens = len(doc)
        segment_words = [token.text for token in doc]
        terms = []
        ents = [(ent.text, ent.label_) for ent in doc.ents]
        for token_k in range(num_tokens):
            token = doc[token_k]
            if (token.pos_ == "NOUN" or token.pos_ == "PRON") and self.dep_language(token) and  not self.is_this_ner(token.text, ents):
                term,gender,gender_set = self.find_gender_from_dictionaries(segment_words, token_k)
                if gender == "" and self.has_gender(token):
                    gender = self.find_gender_from_library(token,doc,token_k)
                if gender:
                    terms.append({"term":term, "gender":gender, "gender_set":gender_set, "token":token})
        return terms  
    
    def has_match_with_combination(self,term_ref:dict,set_tokens_per_sys:Dict[str,List[dict]]):    
        return all(
            any(self.is_match_with_combination(term_ref,term_sys) for term_sys in seg_terms_sys) 
            for seg_terms_sys in list(set_tokens_per_sys.values())    
            )
    
    def is_match_with_combination(self,term_ref:dict,term_sys:dict):
        return (term_ref["token"].dep_ == term_sys["token"].dep_ and 
                term_ref["token"].pos_ == term_sys["token"].pos_ and 
                ((self.is_match_with_dataset(term_ref,term_sys) and term_ref["gender_set"] and term_sys["gender_set"]) or 
                 (self.is_match_with_library(term_ref,term_sys) and not term_ref["gender_set"] and not term_sys["gender_set"])))
    

    def match_identify_terms_with_combination(self, seg_terms_ref:List[dict], seg_terms_per_sys:Dict[str,List[dict]], genders_ref:List[str], 
                                          genders_per_sys:Dict[str,List[str]]):
        for term_ref in seg_terms_ref:
            if self.has_match_with_combination(term_ref,seg_terms_per_sys):
                for sys_id in list(seg_terms_per_sys.keys()):
                    for term_sys in seg_terms_per_sys[sys_id]:
                        if self.is_match_with_combination(term_ref, term_sys):
                            genders_per_sys[sys_id].append({"term":term_sys["term"], "gender":term_sys["gender"]})
                            seg_terms_per_sys[sys_id].remove(term_sys)
                            break
                genders_ref.append({"term":term_ref["term"], "gender":term_ref["gender"]})
        return genders_ref, genders_per_sys
    
    def evaluation_with_combination(self, ref_seg:str, seg_per_sys:Dict[str,str], genders_ref:List[str], genders_per_sys: Dict[str,List[str]]):     
        seg_terms_ref = self.find_identify_terms_and_extract_gender_with_combination(ref_seg)
        seg_terms_per_sys = {sys_id:self.find_identify_terms_and_extract_gender_with_combination(seg_per_sys[sys_id]) for sys_id in list(genders_per_sys.keys())}
        
        identity_terms_found_ref = [ {"term":term["term"], "gender":term["gender"]} for term in seg_terms_ref]
        identity_terms_found_per_sys = {sys_id:[ {"term":term["term"], "gender":term["gender"]} for term in seg_terms_per_sys[sys_id]] for sys_id in list(genders_per_sys.keys())}
        
        genders_ref, genders_per_sys = self.match_identify_terms_with_combination(seg_terms_ref, seg_terms_per_sys, genders_ref, genders_per_sys)
        return genders_ref, genders_per_sys, identity_terms_found_ref, identity_terms_found_per_sys