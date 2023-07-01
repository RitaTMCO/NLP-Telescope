from ast import List
import os
import json
from pyexpat import model
from nltk.tokenize import sent_tokenize

def write_sents(text:list, file_name:str):
    f = open(file_name, "w")
    for sent in text:
        f.writelines(sent + "\n")
    f.close()

def write_file(text:list, file_name:str):
    f = open(file_name, "w")
    f.writelines(text)
    f.close()



f = open('test_none.json')
test = json.load(f)
f.close()
equal = 0
not_equal = 0
i = 1
  
for data in test['data']:
    if equal == 4 and not_equal == 5:
        break

    id = data["id"]
    context = data["context"]
    truth_answer = data["truth_answer"]
    model_answer = data["model_answer"]
    path = "_" + str(i) + "/"

    
    truth_answer = truth_answer.replace("SYSTEM: ", "")
    model_answer = model_answer.replace("SYSTEM: ", "")

    sent_truth = sent_tokenize(truth_answer)
    sent_model = sent_tokenize(model_answer)

    name_id = id.replace(".", "_")

    if len(sent_truth) == len(sent_model) and equal !=4:
        if not os.path.exists(path):
            os.mkdir(path)

        f = open(path + str(i) + "_" + name_id + "_context.txt", "w")
        for cont in context:
            f.write(cont + "\n")
        f.close()
        write_sents(sent_truth, path + str(i) + "_" + name_id + "_truth_answer.txt")
        write_sents(sent_model, path + str(i) + "_" + name_id + "_model_answer.txt")
        equal += 1

    elif  len(sent_truth) != len(sent_model) and not_equal !=5:
        if not os.path.exists(path):
            os.mkdir(path)

        f = open(path + str(i) + "_" + name_id + "_context", "w")
        for cont in context:
            f.write(cont + "\n")
        f.close()
        write_file(truth_answer, path + str(i) + "_" + name_id + "_truth_answer.txt")
        write_file(model_answer, path + str(i) + "_" + name_id + "_model_answer.txt")
        not_equal += 1
    i += 1