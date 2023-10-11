from typing import List, Tuple, Dict
from telescope.testset import Testset, MultipleTestset
from telescope.utils import read_lines, sys_ids_sort, ref_ids_sort

import streamlit as st
import click
import abc

def stop_nlp():
    st.session_state["show_results"] = False
    st.session_state["metrics_results_per_ref"] = {}
    st.session_state["bias_results_per_evaluation"] = {}
    st.session_state["collection_testsets"] = None
    st.session_state["metrics"] = None

class CollectionTestsets:

    task = "nlp"
    title = "NLP"
    type_of_source = "source"
    type_of_references = "reference(s)"
    type_of_output = "model(s) output"
    message_of_success = "Source, References and Outputs were successfully uploaded!"
    message_language = "Choose the language of the files (e.g. 'en')"
    last_sys_id = 1
    last_ref_id = 1
    all_languages = ["X", "pt", "ar", "zh", "nl", "en", "fr", "de", "ru", "uk", "cs"]
    all_language_pairs = []
    for l1 in all_languages:
        for l2 in all_languages:
            if l1 != l2 or (l1==l2 and l1=="X"):
                all_language_pairs.append(l1 + "-" + l2)


    def __init__(
        self,
        src_name: str, #filename of source file 
        refs_names: List[str], #filenames of references files 
        refs_ids: Dict[str, str],  #id of each reference file. {filename:ref_id} 
        systems_ids: Dict[str, str], #id of each system. {filename:sys_id} 
        systems_names: Dict[str, str], #name of each system. {sys_id:name} 
        filenames: List[str], # all filenames
        testsets: Dict[str, Testset], # set of testsets. Each testset refers to one reference. {reference_filename:testset}
        language_pair: str,
    ) -> None:
        
        s_ids = sys_ids_sort(list(systems_names.keys()))
        r_ids = ref_ids_sort(list(refs_ids.values()))

        self.src_name = src_name
        self.refs_names = refs_names

        ref_filenames = list(refs_ids.keys())
        ref_filenames_ids = list(refs_ids.values())
        self.refs_ids = {}
        for id in r_ids:
            i = ref_filenames_ids.index(id)
            filename = ref_filenames[i]
            self.refs_ids[filename] = id

        sys_filenames = list(systems_ids.keys())
        sys_filenames_ids = list(systems_ids.values())
        self.systems_ids  = {}
        for id in s_ids:
            i = sys_filenames_ids.index(id)
            filename = sys_filenames[i]
            self.systems_ids[filename] = id

        self.systems_names = {id:systems_names[id] for id in s_ids}


        self.filenames = filenames
        self.testsets = testsets
        self.language_pair = language_pair.lower()

        assert len(self.refs_names) == len(self.refs_ids)
        assert len(self.refs_ids) == len(self.testsets)
        assert len(self.systems_ids) == len(self.systems_names)

    @property
    def source_language(self):
        return self.language_pair.split("-")[0]

    @property
    def target_language(self):
        return self.language_pair.split("-")[1]
    
    @staticmethod
    def hash_func(collection):
        return " ".join(collection.filenames)

    def indexes_of_systems(self) -> List[str]:
        return list(self.systems_ids.values())
    
    def names_of_systems(self) -> List[str]:
        return list(self.systems_names.values())
    
    def system_name_id(self, name:str) -> str:
        for sys_id, sys_name in self.systems_names.items():
            if sys_name == name:
                return sys_id
        return ""
    
    def already_exists(self, name:str) -> bool:
        return name in self.names_of_systems()
    
    def display_systems(self) -> str:
        text = ""
        for sys_filename, sys_id in self.systems_ids.items():
            text += "--> " + sys_filename + " : " + self.systems_names[sys_id] + " \n"
        return text

    @staticmethod
    def validate_files(src,refs,systems_names,outputs) -> None:
        refs_name = list(refs.keys())
        refs_list = list(refs.values())
        systems_index = list(outputs.keys())
        output_list = list(outputs.values())

        ref_name = refs_name[0]
        ref = refs_list[0]
        x_name = systems_names[systems_index[0]]
        system_x = output_list[0]

        for name, text in zip(refs_name[1:], refs_list[1:]):
           assert len(ref) == len(text), "mismatch between reference {} and reference {} ({} > {})".format(
                ref_name, name, len(ref), len(text))
        assert len(ref) == len(src), "mismatch between references and sources ({} > {})".format(
            len(ref), len(src))
        for y_index, system_y in zip(systems_index[1:], output_list[1:]):
           assert len(system_x) == len(system_y), "mismatch between system {} and system {} ({} > {})".format(
                x_name, systems_names[y_index], len(system_x), len(system_y))
        assert len(system_x) == len(ref), "mismatch between systems and references ({} > {})".format(
            len(system_x), len(ref))
    

    @staticmethod
    def create_testsets(files:list, task:str) -> Dict[str, Testset]:
        source_file, sources, _, references, refs_ids, _, systems_ids, _, outputs = files
        testsets = {}
        for ref_filename, ref in references.items():
            filenames = [source_file.name] + [ref_filename] + list(systems_ids.keys())
            testsets[ref_filename] = MultipleTestset(sources, ref, refs_ids[ref_filename], outputs, task, filenames)
        return testsets
    
    @classmethod
    def upload_files(cls) -> list:
        st.subheader("Upload Files for :blue[" + cls.title + "] analysis:")
        
        source_file = st.file_uploader("Upload the **" + cls.type_of_source + "**", on_change=stop_nlp)
        sources = read_lines(source_file)

        ref_files = st.file_uploader("Upload the **" + cls.type_of_references + "**", accept_multiple_files=True, on_change=stop_nlp)
        references, refs_ids = {}, {}
        for ref_file in ref_files:
            if ref_file.name not in references:
                data = read_lines(ref_file)
                ref_id = cls.create_ref_id(ref_file.name,data)
                references[ref_file.name] = data
                refs_ids[ref_file.name] = ref_id

        outputs_files = st.file_uploader("Upload the **" + cls.type_of_output + "**", accept_multiple_files=True, on_change=stop_nlp)
        systems_ids, systems_names, outputs = {}, {}, {}
        for output_file in outputs_files:
            if output_file.name not in systems_ids:
                output = read_lines(output_file)
                sys_id = cls.create_sys_id(output_file.name,output)
                systems_ids[output_file.name] = sys_id
                if cls.task + "_" + sys_id + "_rename" not in st.session_state:
                    systems_names[sys_id] = sys_id
                else:
                    systems_names[sys_id] = st.session_state[cls.task + "_" + sys_id + "_rename" ]
                outputs[sys_id] = output

        return source_file,sources,ref_files,references,refs_ids,outputs_files,systems_ids,systems_names,outputs

    @classmethod
    def upload_language(cls) -> str:
        language_pair = ""
        language  = st.selectbox(
            cls.message_language + ":",
            cls.all_languages,
            index=0,
            help=("If the language is indifferent then select X."),
            on_change=stop_nlp
        )
        if language != "":
            language_pair = language + "-" + language
        return language_pair
    
    @classmethod
    def upload_names(cls, systems_names:Dict[str,str]) -> list:
        load_name = st.checkbox('Upload systems names', on_change=stop_nlp)
        name_file = None
        if load_name:
            name_file = st.file_uploader("Upload the file with systems names", accept_multiple_files=False, on_change=stop_nlp)
            if name_file != None:
                list_new_names = []
                names = read_lines(name_file)
                for name in names:
                    if name not in list_new_names:
                        list_new_names.append(name)
                        
                if len(list_new_names) >= len(systems_names):
                    i = 0
                    for system_id, _ in systems_names.items():  
                        if cls.task + "_" + system_id + "_rename" not in st.session_state:
                            systems_names[system_id] = list_new_names[i]
                        i += 1
        return systems_names,load_name,name_file 
   

    @classmethod
    @st.cache
    def create_sys_id(cls,filename,output):
        sys_id = "Sys " + str(cls.last_sys_id)
        cls.last_sys_id += 1
        return sys_id
    
    @classmethod
    @st.cache
    def create_ref_id(cls,filename,output):
        ref_id = "Ref " + str(cls.last_ref_id)
        cls.last_ref_id += 1
        return ref_id
    
    @classmethod
    @abc.abstractmethod
    def read_data(cls):
        return NotImplementedError

    @classmethod
    def read_data_cli(cls, source:click.File, system_names_file:click.File, systems_output:Tuple[click.File], reference:Tuple[click.File], 
                      language, labels_file:click.File=None): 
    
        systems_ids, systems_names, outputs = {}, {}, {}
        
        if system_names_file:
            sys_names = [l.replace("\n", "") for l in system_names_file.readlines()]

            if len(sys_names) < len(systems_output):
                for i in range(len(systems_output)-len(sys_names)):
                    sys_names.append("Sys " + str(i+1))
            
            id = 1
            for sys_file,sys_name in zip(systems_output,sys_names):
                if sys_file.name not in systems_ids:
                    data = [l.strip() for l in sys_file.readlines()]
                    sys_id = "Sys " + str(id)
                    id += 1
                    systems_ids[sys_file.name] = sys_id
                    systems_names[sys_id] = sys_name
                    outputs[sys_id] = data
            
        else:
            id = 1
            for sys_file in systems_output:
                if sys_file.name not in systems_ids:
                    data = [l.strip() for l in sys_file.readlines()]
                    sys_id = "Sys " + str(id)
                    id += 1
                    systems_ids[sys_file.name] = sys_id
                    systems_names[sys_id] = sys_id
                    outputs[sys_id] = data
        
        id = 1
        references,refs_ids = {},{}
        for ref in reference:
            if ref.name not in references:
                data = [l.strip() for l in ref.readlines()]
                ref_id = "Ref " + str(id)
                id += 1
                references[ref.name] = data
                refs_ids[ref.name] = ref_id

        src = [l.strip() for l in source.readlines()]

        labels = []
        if labels_file:
            labels = [l.strip() for l in labels_file.readlines()]

        cls.validate_files(src,references,systems_names,outputs)

        files = [source,src,reference,references,refs_ids,systems_output,systems_ids,systems_names,outputs] 

        testsets = cls.create_testsets(files,cls.task)

        if labels:
            return cls(source.name, references.keys(), refs_ids, systems_ids, systems_names,
                    [source.name] +  list(references.keys()) + list(systems_ids.values()), testsets, language, labels)

        else:
            return cls(source.name, references.keys(), refs_ids, systems_ids, systems_names,
                    [source.name] +  list(references.keys()) + list(systems_ids.values()), testsets, language)
    

class NLGTestsets(CollectionTestsets):
    task = "nlg"
    title = "NLG"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        refs_ids: Dict[str, str],
        systems_ids: Dict[str, str],
        systems_names: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, Testset],
        language_pair: str
    ) -> None:
        super().__init__(src_name, refs_names, refs_ids, systems_ids, systems_names, filenames, testsets,language_pair)
    
    
    @classmethod
    def read_data(cls):
        files = cls.upload_files()

        language = cls.upload_language()
        
        source_file,sources,ref_files,references, refs_ids, outputs_files,systems_ids, systems_names, outputs = files

        #systems_names,load_name, file_sys_names= cls.upload_names(systems_names)

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language != "")):

            cls.validate_files(sources,references,systems_names,outputs)
            st.success(cls.message_of_success)
            st.session_state["success_upload"] = True

            testsets = cls.create_testsets(files,cls.task)

            return cls(source_file.name, references.keys(), refs_ids, systems_ids, systems_names,
                [source_file.name] +  list(references.keys()) + list(systems_ids.values()),
                testsets, language)
        else:
            st.session_state["success_upload"] = False


class MTTestsets(NLGTestsets):
    task = "machine-translation"
    title = "Machine Translation"
    type_of_source = "file with the source"
    type_of_references = NLGTestsets.type_of_references + " (the file(s) should only contain the true translations)"
    type_of_output = NLGTestsets.type_of_output + " (the file(s) should only contain the predicated translations; one file for each model)"
    message_language = "Choose the language of the samples to translate (e.g. 'en-ru')"
    message_of_success = "Source, References, Translations and LP were successfully uploaded!"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        refs_ids: Dict[str, str],
        systems_ids: Dict[str, str],
        systems_names: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, MultipleTestset],
        language_pair: str,
    ) -> None:
        super().__init__(src_name, refs_names, refs_ids, systems_ids, systems_names, filenames,
                testsets, language_pair)
    
    @classmethod
    def upload_language(cls):
        language_pair  = st.selectbox(
            cls.message_language + ":",
            cls.all_language_pairs,
            index=0,
            help=("If the language is indifferent and BERTScore metric is not used, then select X"),
            on_change=stop_nlp
        )
        return language_pair


class SummTestsets(NLGTestsets):
    task = "summarization"
    title = "Summarization"
    type_of_source = "file with the samples to summarize (no summaries)"
    type_of_references = CollectionTestsets.type_of_references + " (the file(s) should only contain the true summaries)"
    type_of_output = CollectionTestsets.type_of_output + " (the file(s) should only contain the predicated summaries; one file for each model)"
    message_language = "Choose the language of the samples to summarize (e.g. 'en')"
    message_of_success = "Source, References, Summaries and Language were successfully uploaded!"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        refs_ids: Dict[str, str],
        systems_ids: Dict[str, str],
        systems_names: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, MultipleTestset],
        language_pair: str,
    ) -> None:
        super().__init__(src_name, refs_names, refs_ids, systems_ids, systems_names, filenames, 
                testsets, language_pair)
        
    @staticmethod
    def validate_files(src,refs,systems_names,outputs):
        refs_name = list(refs.keys())
        refs_list = list(refs.values())
        systems_index = list(outputs.keys())
        output_list = list(outputs.values())

        ref_name = refs_name[0]
        ref = refs_list[0]
        x_name = systems_names[systems_index[0]]
        system_x = output_list[0]

        for name, text in zip(refs_name[1:], refs_list[1:]):
           assert len(ref) == len(text), "mismatch between reference {} and reference {} ({} > {})".format(
                ref_name, name, len(ref), len(text))
        for y_index, system_y in zip(systems_index[1:], output_list[1:]):
           assert len(system_x) == len(system_y), "mismatch between system {} and system {} ({} > {})".format(
                x_name, systems_names[y_index], len(system_x), len(system_y))
        assert len(system_x) == len(ref), "mismatch between systems and references ({} > {})".format(
            len(system_x), len(ref))
    

class DialogueTestsets(NLGTestsets):
    task = "dialogue-system"
    title = "Dialogue System"
    type_of_source = "file with the context"
    type_of_references = "file with the truth answers"
    type_of_output = "file with the models answer"
    message_language = "Choose the language of the answers (e.g. 'en')"
    message_of_success = "Source, References, Dialogues and Language were successfully uploaded!"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        refs_ids: Dict[str, str],
        systems_ids: Dict[str, str],
        systems_names: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, MultipleTestset],
        language_pair: str
    ) -> None:
        super().__init__(src_name, refs_names, refs_ids, systems_ids, systems_names, filenames, 
                testsets, language_pair)
   
    @staticmethod
    def validate_files(src,refs,systems_names,outputs):
        refs_name = list(refs.keys())
        refs_list = list(refs.values())
        systems_index = list(outputs.keys())
        output_list = list(outputs.values())
        ref_name = refs_name[0]
        ref = refs_list[0]
        x_name = systems_names[systems_index[0]]
        system_x = output_list[0]
        for name, text in zip(refs_name[1:], refs_list[1:]):
           assert len(ref) == len(text), "mismatch between reference {} and reference {} ({} > {})".format(
                ref_name, name, len(ref), len(text))
        for y_index, system_y in zip(systems_index[1:], output_list[1:]):
           assert len(system_x) == len(system_y), "mismatch between system {} and system {} ({} > {})".format(
                x_name, systems_names[y_index], len(system_x), len(system_y))
        assert len(system_x) == len(ref), "mismatch between systems and references ({} > {})".format(
            len(system_x), len(ref))



class ClassTestsets(CollectionTestsets):
    task = "classification"
    title = "Classification"
    type_of_source = "file with the samples to be labeled (no lables)"
    type_of_references = CollectionTestsets.type_of_references + " (the file(s) should only contains the true labels)"
    type_of_output = CollectionTestsets.type_of_output + " (the file(s) should only contain the predicated labels; one file each model)"
    message_language = "Choose the language of the samples to be labeled (e.g. 'en')"
    message_of_success = "Samples and Labels were successfully uploaded!"

    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        refs_ids: Dict[str, str],
        systems_ids: Dict[str, str],
        systems_names: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, MultipleTestset],
        language_pair: str,
        labels: List[str]
    ) -> None:
        super().__init__(src_name, refs_names, refs_ids, systems_ids, systems_names, filenames, testsets, language_pair)
        self.labels = labels
    
    @staticmethod
    def upload_labels() -> List[str]:
        labels_file = st.file_uploader("Upload a file with the full set of labels separated by line", accept_multiple_files=False, on_change=stop_nlp)
        return labels_file
    
    @classmethod
    def read_data(cls):

        files = cls.upload_files()
        source_file,sources,ref_files,references,refs_ids,outputs_files,systems_ids,systems_names,outputs = files
        labels_file = cls.upload_labels()
        language = cls.upload_language()

        #systems_names,load_name, file_sys_names= cls.upload_names(systems_names)

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language != "")
            and (labels_file is not None)):
            
            cls.validate_files(sources,references,systems_names,outputs)
            st.success(cls.message_of_success)
            st.session_state["success_upload"] = True

            testsets = cls.create_testsets(files,cls.task)

            labels = read_lines(labels_file)

            return cls(source_file.name, references.keys(), refs_ids, systems_ids, systems_names,
                [source_file.name] +  list(references.keys()) + list(systems_ids.values()),
                testsets, language, labels)
        else:
            st.session_state["success_upload"] = False