
import json
import sys

with open('gendered_terms.json', 'r') as f_json:
    list_json = json.load(f_json)
f_json.close()

with open('pronouns_en.json', 'r') as f_json:
    list_pro_json = json.load(f_json)
f_json.close()

def loop(male,female,list):
    for line in list:
        if male in line and female in line:
            return line
    return []

f = open(sys.argv[1], "r")
data = f.read()
f.close()

list_data = list(data.split("\n"))

for line in list_data:
    if line != "":
        male, female = list(line.split("\t"))
        if " " in male:
            male = male.replace(" ", "")
        if " " in female:
            female = female.replace(" ", "")
        neutral = ""
        line_gender = loop(male,female,list_json)
        line_pro = loop(male,female,list_pro_json)

        if not line_pro:
            if "man" in male and "woman" in female:
                neutral = male.replace("man","person")
            elif "men" in male and "women" in female:
                neutral = male.replace("men","people")

            elif "sons" in male and "daughters" in female:
                neutral = male.replace("sons","children")
            elif "son" in male and "daughter" in female:
                neutral = male.replace("son","child")

            elif "dad" in male and "mom" in female:
                neutral = male.replace("dad","parent")

            elif "father" in male and "mother" in female:
                neutral = male.replace("father","parent")

            elif "brother" in male and "sister" in female:
                neutral = male.replace("brother","sibling")

            if line_gender != [] and neutral != "":
                list_json.remove(line_gender)
            elif line_gender != [] and list(line_gender.keys())[0] == "":
                list_json.remove(line_gender)
            
            if not (line_gender != [] and list(line_gender.keys())[0] != ""):            
                gender_dict = {neutral:"neutral",female:"female",male:"male"}
                list_json.append(gender_dict)

print(len(list_json))

with open('gendered_terms.json', "w") as f_json:
    json.dump(list_json, f_json, indent=4)
f_json.close()