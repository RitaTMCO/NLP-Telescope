from typing import List, Tuple, Dict
from telescope.testset import MultipleTestset
from telescope.utils import read_lines

import streamlit as st

class CollectionTestsets:
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: List[MultipleTestset],
        language_pair: str
    ) -> None:
        self.src_name = src_name
        self.refs_names = refs_names
        self.systems_indexes = systems_indexes
        self.filenames = filenames
        self.multiple_testsets = multiple_testsets
        self.language_pair = language_pair


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
    def upload_files(task:str, type_of_output:str) -> list:
        st.subheader("Upload Files for " + task + " analysis:")
        
        source_file = st.file_uploader("Upload Sources", type=["txt"])
        sources = read_lines(source_file)


        ref_files = st.file_uploader("Upload References", type=["txt"], 
                    accept_multiple_files=True)
        references = {}
        for ref_file in ref_files:
            if ref_file.name not in references:
                references[ref_file.name] = read_lines(ref_file)


        outputs_files = st.file_uploader("Upload Systems " + type_of_output, 
                        type=["txt"], accept_multiple_files=True)
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
    def upload_language(files:list) -> str:

        language_pair = ""
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files
        
        language = st.text_input(
            "Please input the language of the files to analyse (e.g. 'en'):",
            "",
        )

        if (language != ""):
            language_pair = language + "-" + language
        return language_pair
    
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
        files = CollectionTestsets.upload_files("NLP", "Outputs")

        language_pair = CollectionTestsets.upload_language(files)
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language_pair != "")):

            CollectionTestsets.validate_files(sources,references,systems_indexes,output)

            st.success("Source, References, Outputs and Language were successfully uploaded!")

            multiple_testsets = CollectionTestsets.create_multiple_testsets(files, 
                                                language_pair)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, language_pair)


class MTTestsets(CollectionTestsets):
    task = "Machine Translation"
    type_of_output = "Translations"

    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: List[MultipleTestset],
        language_pair: str,
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, multiple_testsets, 
                        language_pair)
    
    @staticmethod
    def upload_language(files:list):
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files
        
        language_pair = st.text_input(
            "Please input the language pair of the files to analyse (e.g. 'en-ru'):",
            "",
        )
        return language_pair
    
    @classmethod
    def read_data(cls):

        files = MTTestsets.upload_files("Machine Translation", "Translations")
        
        language_pair = MTTestsets.upload_language(files)

        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language_pair != "")):

            MTTestsets.validate_files(sources,references,systems_indexes,outputs)

            st.success("Source, References, Translations and LP were successfully uploaded!")
            
            multiple_testsets = MTTestsets.create_multiple_testsets(files, language_pair)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, language_pair)
    
    


class SummTestsets(CollectionTestsets):
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: List[MultipleTestset],
        language_pair: str
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, multiple_testsets,
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
    
    @classmethod
    def read_data(cls):
        files = SummTestsets.upload_files("Summarization", "Summaries")

        language_pair = SummTestsets.upload_language(files)
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language_pair != "")):

            SummTestsets.validate_files(sources,references,systems_indexes,outputs)

            st.success("Source, References, Summaries and Language were successfully uploaded!")

            multiple_testsets = SummTestsets.create_multiple_testsets(files, language_pair)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, language_pair)

    


class DialogueTestsets(CollectionTestsets):
    task = "Dialogue System"
    type_of_output = "Dialogues"

    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: List[MultipleTestset],
        language_pair: str
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, multiple_testsets,
                        language_pair)
    
    @classmethod
    def read_data(cls):
        files = DialogueTestsets.upload_files("Dialogue System", "Dialogues")

        language_pair = DialogueTestsets.upload_language(files)
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language_pair != "")):

            DialogueTestsets.validate_files(sources,references,systems_indexes,output)

            st.success("Source, References, Dialogues and Language were successfully uploaded!")

            multiple_testsets = DialogueTestsets.create_multiple_testsets(files, language_pair)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, language_pair)


class ClassTestsets(CollectionTestsets):
    def __init__(
        self,
        src_name: str,
        refs_names: List[str],
        systems_indexes: Dict[str, str],
        filenames: List[str],
        multiple_testsets: List[MultipleTestset],
        language_pair: str
    ) -> None:
        super().__init__(src_name, refs_names, systems_indexes, filenames, multiple_testsets,
                        language_pair)
    
    @classmethod
    def read_data(cls):
        files = ClassTestsets.upload_files("Classification", "Classifications")

        language_pair = ClassTestsets.upload_language(files)
        
        source_file,sources,ref_files,references,outputs_files,systems_indexes,outputs = files

        if ((ref_files != []) 
            and (source_file is not None) 
            and (outputs_files != []) 
            and (language_pair != "")):

            ClassTestsets.validate_files(sources,references,systems_indexes,outputs)

            st.success("Source, References, Classifications and Language were successfully uploaded!")

            multiple_testsets = ClassTestsets.create_multiple_testsets(files, language_pair)

            return cls(source_file.name, references.keys(), systems_indexes,
                [source_file.name] +  list(references.keys()) + list(systems_indexes.values()),
                multiple_testsets, language_pair)