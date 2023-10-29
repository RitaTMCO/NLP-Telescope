import os
import numpy as np
from typing import List

def read_file(filename:str):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    return lines


def write_file(output_dir:str, data:List[str]):
    f = open(output_dir, "w")
    lines = [i for i in range(len(data))]
    for line in lines:
        if "\n" not in data[line] and line!= 119:
            f.writelines(data[line] + "\n")
        else:
            f.writelines(data[line])
    f.close() 


def create_dataset(pro_filename:str,anti_filename:str, output_dir:str, out_filename:str):
    data_pro = read_file(pro_filename)
    data_anti = read_file(anti_filename)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    write_file(output_dir + out_filename, data_anti + data_pro)
    

create_dataset("test-WinoMT-Pro/en_pro_source.txt", "test-WinoMT-Anti/en_anti_source.txt", "test-WinoMT/", "en_source.txt")
create_dataset("test-WinoMT-Pro/pt_pro_microsoft.txt", "test-WinoMT-Anti/pt_anti_microsoft.txt", "test-WinoMT/", "pt_microsoft.txt")
create_dataset("test-WinoMT-Pro/pt_pro_google.txt", "test-WinoMT-Anti/pt_anti_google.txt", "test-WinoMT/", "pt_google.txt")
create_dataset("test-WinoMT-Pro/pt_pro_ref_microsoft_id_terms.txt", "test-WinoMT-Anti/pt_anti_ref_microsoft_id_terms.txt", "test-WinoMT/", "pt_ref_microsoft_id_terms.txt")
create_dataset("test-WinoMT-Pro/pt_pro_ref_google_id_terms.txt", "test-WinoMT-Anti/pt_anti_ref_google_id_terms.txt", "test-WinoMT/", "pt_ref_google_id_terms.txt")