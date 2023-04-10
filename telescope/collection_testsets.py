from typing import List, Tuple, Dict
from telescope.testset import Testset, MultipleTestset
from telescope.utils import read_lines

import streamlit as st
import click
import abc

class CollectionTestsets:
    task = "NLP"
    type_of_source = "Source"
    type_of_references = "References"
    type_of_output = "Systems Outputs"
    message_of_success = "Source, References and Outputs were successfully uploaded!"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, List[Testset]]
    ) -> None:
        self.src_name = src_name
        self.refs_names = refs_names
        self.systems_indexes = systems_indexes
        self.filenames = filenames
        self.testsets = testsets

    def indexes_of_systems(self) -> List[str]:
        return list(self.systems_indexes.keys())
    
    def display_systems(self) -> str:
        text = ""
        for index, system in self.systems_indexes.items():
            text += index + ": " + system + " \n"
        return text

    @staticmethod
    def hash_func(collection):
        return " ".join(collection.filenames)

    @staticmethod
    def validate_files(src,refs,systems_indexes,outputs) -> None:
        refs_name = list(refs.keys())
        refs_list = list(refs.values())
        systems_index = list(outputs.keys())
        output_list = list(outputs.values())

        ref_name = refs_name[0]
        ref = refs_list[0]
        x_name = systems_indexes[systems_index[0]]
        system_x = output_list[0]

        for name, text in zip(refs_name[1:], refs_list[1:]):
           assert len(ref) == len(text), "mismatch between reference {} and reference {} ({} > {})".format(
                ref_name, name, len(ref), len(text))
        assert len(ref) == len(src), "mismatch between references and sources ({} > {})".format(
            len(ref), len(src))
        for y_index, system_y in zip(systems_index[1:], output_list[1:]):
           assert len(system_x) == len(system_y), "mismatch between system {} and system {} ({} > {})".format(
                x_name, systems_indexes[y_index], len(system_x), len(system_y))
        assert len(system_x) == len(ref), "mismatch between systems and references ({} > {})".format(
            len(system_x), len(ref))
    
    @staticmethod
    def upload_files(task:str, source:str, reference:str, type_of_output:str) -> list:
        st.subheader("Upload Files for :blue[" + task + "] analysis:")
        
        source_file = st.file_uploader("Upload **one** file with the " + source, type=["txt"])
        sources = read_lines(source_file)


        ref_files = st.file_uploader("Upload **one** or **more** files with the " + reference, type=["txt"], 
                    accept_multiple_files=True)
        references = {}
        for ref_file in ref_files:
            if ref_file.name not in references:
                references[ref_file.name] = read_lines(ref_file)


        outputs_files = st.file_uploader("Upload **one** or **more** files with the " + type_of_output,  type=["txt"], 
                                    accept_multiple_files=True)
        systems_indexes, outputs = {}, {}
        i = 1
        for output_file in outputs_files:
            if output_file.name not in list(systems_indexes.values()):
                index = "Sys " + str(i)
                i += 1
                systems_indexes[index] = output_file.name
                outputs[index] = read_lines(output_file)

        return [source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs]
    
    @staticmethod
    def create_testsets(files:list) -> Dict[str, Testset]:
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files
        testsets = {}
        for ref_filename, ref in references.items():
            filenames = list(source_file.name) + list(ref_filename) + list(systems_indexes.values())
            testsets[ref_filename] = MultipleTestset(sources, ref, outputs, filenames)
        return testsets
    
    @classmethod
    @abc.abstractmethod
    def read_data(cls):
        return NotImplementedError

    @classmethod
    def read_data_cli_aux(cls, source:click.File, system_output:click.File, reference:click.File):      
        systems_indexes = {}
        outputs = {}
        i = 1
        for sys in system_output:
            if sys.name not in list(systems_indexes.values()):
                index = "Sys " + str(i)
                i += 1
                systems_indexes[index] = sys.name
                outputs[index] = [l.strip() for l in sys.readlines()]
        
        references = {}
        for ref in reference:
            if ref.name not in references:
                references[ref.name] = [l.strip() for l in ref.readlines()]

        src = [l.strip() for l in source.readlines()]
        files = [source,src,reference,references,system_output,systems_indexes,outputs]

        testsets = cls.create_testsets(files)
        return systems_indexes,outputs,references,src,testsets

    @classmethod
    @abc.abstractmethod
    def read_data_cli(cls, source:click.File, system_output:click.File, reference:click.File):
        return NotImplementedError



class NLGTestsets(CollectionTestsets):
    task = "NLG"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, List[Testset]],
        language_pair: str
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, testsets)
        self.language_pair = language_pair
    
    @property
    def source_language(self):
        return self.language_pair.split("-")[0]

    @property
    def target_language(self):
        return self.language_pair.split("-")[1]
    
    @staticmethod
    def upload_language() -> str:
        language_pair = ""
        language = st.text_input(
            "Please input the language of the files to analyse (e.g. 'en'):",
            "",
        )
        if (language != ""):
            language_pair = language + "-" + language
        return language_pair
    
    @classmethod
    def read_data(cls):
        files = cls.upload_files(
            cls.task, 
            cls.type_of_source,
            cls.type_of_references,
            cls.type_of_output
        )
        language = cls.upload_language()
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language != "")):

            cls.validate_files(sources,references,systems_indexes,outputs)
            st.success(cls.message_of_success)

            testsets = cls.create_testsets(files)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                testsets, language)
    
    @classmethod
    def read_data_cli(cls, source:click.File, system_output:click.File, reference:click.File, 
        language:str):
        systems_indexes,outputs,references,src,testsets = cls.read_data_cli(source,system_output,reference) 
        return cls(source.name, references.keys(), systems_indexes,
            [source.name] +  list(references.keys()) + list(systems_indexes.values()), testsets, 
            "X-" + language)


class MTTestsets(NLGTestsets):
    task = "Machine Translation"
    type_of_output = "Systems Translations"
    message_of_success = "Source, References, Translations and LP were successfully uploaded!"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, List[MultipleTestset]],
        language_pair: str,
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, testsets, language_pair)
    
    @staticmethod
    def upload_language():
        language_pair = st.text_input(
            "Please input the language pair of the files to analyse (e.g. 'en-ru'):",
            "",
        )
        return language_pair


class SummTestsets(NLGTestsets):
    task = "Summarization"
    type_of_output = "Systems Summaries"
    message_of_success = "Source, References, Summaries and Language were successfully uploaded!"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, List[MultipleTestset]],
        language_pair: str,
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, testsets,
                        language_pair)
        
    @staticmethod
    def validate_files(src,refs,systems_indexes,outputs):
        refs_name = list(refs.keys())
        refs_list = list(refs.values())
        systems_index = list(outputs.keys())
        output_list = list(outputs.values())

        ref_name = refs_name[0]
        ref = refs_list[0]
        x_name = systems_indexes[systems_index[0]]
        system_x = output_list[0]

        for name, text in zip(refs_name[1:], refs_list[1:]):
           assert len(ref) == len(text), "mismatch between reference {} and reference {} ({} > {})".format(
                ref_name, name, len(ref), len(text))
        for y_index, system_y in zip(systems_index[1:], output_list[1:]):
           assert len(system_x) == len(system_y), "mismatch between system {} and system {} ({} > {})".format(
                x_name, systems_indexes[y_index], len(system_x), len(system_y))
        assert len(system_x) == len(ref), "mismatch between systems and references ({} > {})".format(
            len(system_x), len(ref))
    

class DialogueTestsets(NLGTestsets):
    task = "Dialogue System"
    type_of_source = "Context"
    type_of_references = "Truth Answers"
    type_of_output = "Systems Answers"
    message_of_success = "Source, References, Dialogues and Language were successfully uploaded!"
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, List[MultipleTestset]],
        language_pair: str
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, testsets, language_pair)
   
    @staticmethod
    def validate_files(src,refs,systems_indexes,outputs):
        refs_name = list(refs.keys())
        refs_list = list(refs.values())
        systems_index = list(outputs.keys())
        output_list = list(outputs.values())
        ref_name = refs_name[0]
        ref = refs_list[0]
        x_name = systems_indexes[systems_index[0]]
        system_x = output_list[0]
        for name, text in zip(refs_name[1:], refs_list[1:]):
           assert len(ref) == len(text), "mismatch between reference {} and reference {} ({} > {})".format(
                ref_name, name, len(ref), len(text))
        for y_index, system_y in zip(systems_index[1:], output_list[1:]):
           assert len(system_x) == len(system_y), "mismatch between system {} and system {} ({} > {})".format(
                x_name, systems_indexes[y_index], len(system_x), len(system_y))
        assert len(system_x) == len(ref), "mismatch between systems and references ({} > {})".format(
            len(system_x), len(ref))



class ClassTestsets(CollectionTestsets):
    task = "Classification"
    type_of_source = "Samples"
    type_of_references = "True Labels"
    type_of_output = "Predicated Labels"
    message_of_success = "Source and Labels were successfully uploaded!"

    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        testsets: Dict[str, List[MultipleTestset]],
        labels: List[str]
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, testsets)
        self.labels = labels
    
    @staticmethod
    def upload_labels() -> List[str]:
        labels_list = list()
        labels = st.text_input(
            "Please input the existing labels separated by commas (e.g. 'positive,negative,neutral'):",
            "",
        )
        if (labels != ""):
            labels_list = list(set(labels.split(",")))
        return labels_list
    
    @classmethod
    def read_data(cls):
        files = cls.upload_files(
            cls.task, 
            cls.type_of_source,
            cls.type_of_references,
            cls.type_of_output
        )
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files
        labels = cls.upload_labels()

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (labels != [])):

            cls.validate_files(sources,references,systems_indexes,outputs)
            st.success(cls.message_of_success)

            testsets = cls.create_testsets(files)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                testsets, labels)
    
    @classmethod
    def read_data_cli(cls, source:click.File, system_output:click.File, reference:click.File, 
        labels:str):
        systems_indexes,outputs,references,src, testsets = cls.read_data_cli(source,system_output,reference) 
        return cls(source.name, references.keys(), systems_indexes,
            [source.name] +  list(references.keys()) + list(systems_indexes.values()),
            testsets, labels)