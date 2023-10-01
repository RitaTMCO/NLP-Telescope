import os
import numpy as np
from typing import List

def random_and_sort(list_input:List[int]):
    lines_ids = np.random.choice(list_input, size=30, replace=False)
    lines_ids.sort()
    return lines_ids

def find_random_lines():
    while True:
        even = [2*i for i in range(792)]
        odds = [2*i + 1 for i in range(792)]
        lines_even = random_and_sort(even)
        for e in lines_even:
            odds.remove(e+1)
        lines_odds = random_and_sort(odds)

        lines_ids = list(lines_even) + list(lines_odds)
        lines_ids.sort()

        data = read_file("en_anti.txt")
        female = 0
        male = 0
        for line in lines_ids:
            data_line = data[line]
            if "female\t" in data_line:
                female += 1
            elif "male\t" in data_line:
                male += 1
        if male == female:
            break
    return lines_ids

def read_file(filename:str):
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    return lines


def write_file(filename:str, data:List[str], lines:List[int]):
    print(filename)
    f = open(filename, "w")
    female = 0
    male = 0
    for line in lines:
        data_line = data[line]
        b = 0
        e = 0
        if "female\t" in data_line:
            female += 1
        elif "male\t" in data_line:
            male += 1
        for c in range(len(data_line)):
            if data_line[c].isupper() and b == 0:
                b = c
            if data_line[c:c+2] == ".\t" and e == 0:
                e = c
        if data_line != data[lines[-1]]:
            f.write(data_line[b:e+1] + "\n")
        else:
            f.write(data_line[b:e+1])
        
    print("male: " + str(male))
    print("female: " + str(female))
    f.close() 

def write_lines_ids(lines_ids:List[int]):
    f = open("lines_ids.txt", "w")
    text = "-".join([str(i) for i in lines_ids])
    print(text)
    f.write(text)
    f.close()

def create_dataset(input_filename:str,output_filename:str, output_dir:str, lines_ids:List[int]):
    data = read_file(input_filename)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    write_file(output_dir + output_filename,data,lines_ids)
    

lines_ids = find_random_lines()
create_dataset("en_anti.txt", "en_anti_source.txt", "test-WinoMT-Anti/", lines_ids)
create_dataset("en_pro.txt","en_pro_source.txt", "test-WinoMT-Pro/", lines_ids)
write_lines_ids(lines_ids)
