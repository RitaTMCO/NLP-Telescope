from typing import List, Tuple, Dict
from telescope.testset import MultipleTestset
from telescope.utils import read_lines

import streamlit as st
import click

class CollectionTestsets:
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: Dict[str, List[MultipleTestset]],
        language_pair: str,
        labels: List[str]
    ) -> None:
        self.src_name = src_name
        self.refs_names = refs_names
        self.systems_indexes = systems_indexes
        self.filenames = filenames
        self.multiple_testsets = multiple_testsets
        self.language_pair = language_pair
        self.labels = labels

    def indexes_of_systems(self) -> List[str]:
        return list(self.systems_indexes.keys())
    
    def display_systems(self) -> None:
        text = "Systems:\n"
        for index, system in self.systems_indexes.items():
            text += index + ": " + system + " \n"
        st.text(text)

    @staticmethod
    def hash_func(testset):
        return " ".join(testset.filenames)

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
        st.subheader("Upload Files for " + task + " analysis:")
        
        source_file = st.file_uploader("Upload " + source, type=["txt"])
        sources = read_lines(source_file)


        ref_files = st.file_uploader("Upload " + reference, type=["txt"], 
                    accept_multiple_files=True)
        references = {}
        for ref_file in ref_files:
            if ref_file.name not in references:
                references[ref_file.name] = read_lines(ref_file)


        outputs_files = st.file_uploader("Upload " + type_of_output,  type=["txt"], 
                                    accept_multiple_files=True)
        systems_indexes, outputs = {}, {}
        i = 1
        for output_file in outputs_files:
            if output_file.name not in list(systems_indexes.values()):
                index = "Sys " + str(i)
                i += 1
                systems_indexes[index] = output_file.name
                outputs[index] = read_lines(output_file)

        return [source_file,sources,ref_files,references,outputs_files,systems_indexes,
                outputs]
    
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
    
    def upload_labels() -> List[str]:
        labels_list = list()
        labels = st.text_input(
            "Please input the existing labels separated by commas (e.g. 'positive,negative,neutral'):",
            "",
        )
        if (labels != ""):
            labels_list = list(set(labels.split(",")))
        return labels_list
    
    @staticmethod
    def create_multiple_testsets(files:list, language_pair:str) -> Dict[str, MultipleTestset]:
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files
        multiple_testsets = {}
        for ref_filename, ref in references.items():
            filenames = list(source_file.name) + list(ref_filename) + list(systems_indexes.values())
            multiple_testsets[ref_filename] = MultipleTestset(sources, ref, outputs, filenames, 
                                            language_pair)
        return multiple_testsets

    @classmethod
    def read_data(cls):
        files = cls.upload_files("NLP", "Source", "References", "Systems Outputs")
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) and (source_file is not None) and (outputs_files != [])):

            cls.validate_files(sources,references,systems_indexes,output)
            st.success("Source, References and Outputs were successfully uploaded!")

            multiple_testsets = cls.create_multiple_testsets(files,"X-X")

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, "X-X", [""])
    
    @classmethod
    def read_cli(cls, source:click.File, system_output:click.File, reference:click.File, 
            language:str, labels: List[str]):
        
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

        multiple_testsets = cls.create_multiple_testsets(files, "X-" + language)

        return cls(source.name, references.keys(), systems_indexes,
                [source.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, "X-" + language, labels)





class MTTestsets(CollectionTestsets):
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: Dict[str, List[MultipleTestset]],
        language_pair: str,
        labels: List[str]
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, multiple_testsets, 
                        language_pair, [""])
    
    @staticmethod
    def upload_language():
        language_pair = st.text_input(
            "Please input the language pair of the files to analyse (e.g. 'en-ru'):",
            "",
        )
        return language_pair
    
    @classmethod
    def read_data(cls):

        files = cls.upload_files("Machine Translation", "Source", "References", 
                            "Systems Translations")
        
        language_pair = cls.upload_language()

        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language_pair != "")):

            cls.validate_files(sources,references,systems_indexes,outputs)

            st.success("Source, References, Translations and LP were successfully uploaded!")
            
            multiple_testsets = cls.create_multiple_testsets(files, language_pair)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, language_pair, [""])
    
    


class SummTestsets(CollectionTestsets):
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: Dict[str, List[MultipleTestset]],
        language_pair: str,
        labels: List[str]
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, multiple_testsets,
                        language_pair, labels)
        
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
    
    @classmethod
    def read_data(cls):
        files = cls.upload_files("Summarization", "Source", "References", "Systems Summaries")

        language_pair = cls.upload_language()
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language_pair != "")):

            cls.validate_files(sources,references,systems_indexes,outputs)

            st.success("Source, References, Summaries and Language were successfully uploaded!")

            multiple_testsets = cls.create_multiple_testsets(files, language_pair)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, language_pair, [""])

    


class DialogueTestsets(CollectionTestsets):
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: Dict[str, List[MultipleTestset]],
        language_pair: str,
        labels: List[str]
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, multiple_testsets,
                        language_pair, labels)
   
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

    @classmethod
    def read_data(cls):
        files = cls.upload_files("Dialogue System", "Context", "References",
                            "Systems Answers")

        language_pair = cls.upload_language()
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language_pair != "")):

            cls.validate_files(sources,references,systems_indexes,outputs)

            st.success("Source, References, Dialogues and Language were successfully uploaded!")

            multiple_testsets = cls.create_multiple_testsets(files, language_pair)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, language_pair, [""])


class ClassTestsets(CollectionTestsets):
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: Dict[str, List[MultipleTestset]],
        language_pair: str,
        labels: List[str]
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, multiple_testsets,
                        language_pair, labels)
    
    @classmethod
    def read_data(cls):
        files = cls.upload_files("Classification", "Samples", "True Labels", 
                        "Systems Predicated Labels")
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        labels = cls.upload_labels()
        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (labels != [])):

            cls.validate_files(sources,references,systems_indexes,outputs)

            st.success("Source and Labels were successfully uploaded!")

            multiple_testsets = cls.create_multiple_testsets(files, "X-X")

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, "X-X", labels)