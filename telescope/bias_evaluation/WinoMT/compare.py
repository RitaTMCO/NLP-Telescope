import pandas as pd
from colorama import Fore

def read_csv_file(filename:str):
    data = pd.read_csv(filename)
    return data.to_dict()

def compare(s,m):
    data_match = read_csv_file("test-WinoMT/tool_test-WinoMT/en_source.txt/pt_ref_" + s + ".txt/bias_evaluation/"+ m + "/" + s + "/" + s +"_all_identity_terms_matched.csv")
    data_found = read_csv_file("test-WinoMT/tool_test-WinoMT/en_source.txt/pt_ref_" + s + ".txt/bias_evaluation/"+ m + "/pt_ref_" + s + ".txt_all_identity_terms_found.csv")
    n = len(data_found['identity term and its gender'])
    for i in range(n):
        if data_match["identity term that were matched in reference"][i] != data_found['identity term and its gender'][i]:
            print(i)
            print(data_match["identity term that were matched in reference"][i])
            print(data_found['identity term and its gender'][i])
            print(data_match['match of identity terms'][i])
            print("-----------------------------------------------------------")


for s in ["google", "microsoft"]:
    print(Fore.GREEN + "-----------------------------------" + s + "-----------------------------------" )
    for m in ["dictionary-based approach", "linguistic approach", "hybrid approach"]:
        print(Fore.GREEN + "-----------------------------------" + m + "-----------------------------------" )
        print(Fore.WHITE)
        compare(s,m)