
from colorama import Fore
import pandas as pd

def read_file(filename:str):
    f = open(filename, "r")
    data = f.readlines()
    f.close()
    return data

def read_csv_file(filename:str):
    data = pd.read_csv(filename)
    return data.to_dict()

def inter_lists(list1:list,list2:list):
    res = []
    lines = len(list1)
    index_list1 = []
    index_list2 = []
    number_id_terms_g = 0
    number_id_terms_t = 0

    for i in range(lines):
        r = []
        number_id_terms_g += len(list1[i])
        number_id_terms_t += len(list2[i])
        line_list_1 = list1[i].copy()
        line_list_2 = list2[i].copy()
        len_list1 = len(line_list_1)
        for e in range(len_list1):
            if line_list_1[e] in line_list_2:
                r.append(line_list_1[e])
                index_list1.append((i,e))
                index_list2.append((i,list2[i].index(line_list_1[e])))    
                line_list_2.remove(line_list_1[e])
        res += r
    assert len(res) == len(index_list1)
    assert len(res) == len(index_list2)
    return res, index_list1, index_list2, number_id_terms_g, number_id_terms_t


def gender_list(id_list1,id_list2, gender_1,gender_2):
    n = len(id_list1)
    diff_1 = [ id_list1[i] for i in range(n) if gender_1[id_list1[i][0]][id_list1[i][1]] != gender_2[id_list2[i][0]][id_list2[i][1]]]
    diff_2 = [ id_list2[i] for i in range(n) if gender_1[id_list1[i][0]][id_list1[i][1]] != gender_2[id_list2[i][0]][id_list2[i][1]]]
    return diff_1, diff_2


def read_file_identity_terms_golden(filename:str):
    identity_terms = []
    gender_identity_terms = []
    data = read_file(filename)
    for d in data:
        len_c = len(d)
        sep = [c for c in range(len_c) if d[c] == "[" or d[c] == "]" or (d[c] =="," and "[" in d[:c])]
        identity_terms_line, gender_identity_terms_line = find_identity_terms_and_genders(sep,d)
        identity_terms.append(identity_terms_line)
        gender_identity_terms.append(gender_identity_terms_line)
    return identity_terms, gender_identity_terms

def read_file_identity_terms_tool(filename:str):
    identity_terms = []
    gender_identity_terms = []
    data = read_csv_file(filename)
    for _, d in data['identity term and its gender'].items():
        len_c = len(d)
        sep = [-1]
        sep = sep + [c for c in range(len_c) if d[c] ==","]
        sep.append(len_c)
        identity_terms_line, gender_identity_terms_line = find_identity_terms_and_genders(sep,d)
        identity_terms.append(identity_terms_line)
        gender_identity_terms.append(gender_identity_terms_line)
    assert len(identity_terms) == len(gender_identity_terms)
    return identity_terms, gender_identity_terms

def find_identity_terms_and_genders(sep,d):
    identity_terms_line = []
    gender_identity_terms_line = []
    for i in range(len(sep)):
        if sep[i] != sep[-1]:
            b = sep[i] + 1
            e = sep[i+1]
            if ":male" in d[b:e]:
                gender = "male"
            elif ":female" in d[b:e]:
                gender = "female"
            elif ":neutral" in d[b:e]:
                gender = "neutral"
                
            if " " in d[b:e]:
                identity_terms_line.append(d[b:e].replace(":"+ gender, "").replace(" ", ""))
            else:   
                identity_terms_line.append(d[b:e].replace(":"+ gender, ""))
            gender_identity_terms_line.append(gender)
    return identity_terms_line, gender_identity_terms_line

def identity_terms_found_info(s,m):
    ref_id_terms_golden = "test-WinoMT/pt_ref_" + s + "_id_terms.txt"
    ref_id_terms_tool = "test-WinoMT/tool_test-WinoMT/en_source.txt/pt_ref_" + s + ".txt/bias_evaluation/" + m + "/pt_ref_" + s + ".txt_all_identity_terms_found.csv"
    file_info = "test-WinoMT/tool_test-WinoMT/en_source.txt/pt_ref_" + s + ".txt/bias_evaluation/" + m + "/bias_evaluations_information.csv"

    identity_terms_golden, gender_identity_terms_golden = read_file_identity_terms_golden(ref_id_terms_golden)
    identity_terms_tool, gender_identity_terms_tool = read_file_identity_terms_tool(ref_id_terms_tool)

    list_tp,index_list1, index_list2,number_id_golden,number_id_tool = inter_lists(identity_terms_golden, identity_terms_tool)
            
    tp = len(list_tp)
    fp = number_id_tool - tp
    fn = number_id_golden - tp
    diff_1, diff_2 = gender_list(index_list1,index_list2,gender_identity_terms_golden,gender_identity_terms_tool)

    number_of_match = read_csv_file(file_info)["Number of identity terms that were matched"][0]

    return [number_id_golden, number_id_tool, tp, fp, fn, len(list_tp)-len(diff_1), number_of_match]

def time_bias_evlaution(s,m):
    file_info_join = "test-WinoMT/tool_test-WinoMT/en_source.txt/pt_ref_" + s + ".txt/bias_evaluation/" + m + "/bias_evaluations_information.csv"
    file_info_pro = "test-WinoMT-Pro/tool_test-WinoMT-Pro/en_pro_source.txt/pt_pro_ref_" + s + ".txt/bias_evaluation/" + m + "/bias_evaluations_information.csv"
    file_info_anti = "test-WinoMT-Anti/tool_test-WinoMT-Anti/en_anti_source.txt/pt_anti_ref_" + s + ".txt/bias_evaluation/" + m + "/bias_evaluations_information.csv"
    time_join = read_csv_file(file_info_join)["Bias Evaluation Time"][0]
    time_pro = read_csv_file(file_info_pro)["Bias Evaluation Time"][0]
    time_anti = read_csv_file(file_info_anti)["Bias Evaluation Time"][0]
    return [time_join, time_pro, time_anti]

def compare_pro_anti(s,m):

    metrics = ["Demographic-Parity","Accuracy", "Precision","Recall", "F1-score"]
    file_scores_pro = "test-WinoMT-Pro/tool_test-WinoMT-Pro/en_pro_source.txt/pt_pro_ref_" + s + ".txt/bias_evaluation/" + m + "/bias_scores.csv"
    file_scores_anti = "test-WinoMT-Anti/tool_test-WinoMT-Anti/en_anti_source.txt/pt_anti_ref_" + s + ".txt/bias_evaluation/" + m + "/bias_scores.csv"

    data_pro = pd.read_csv(file_scores_pro,index_col=[0])
    metrics_scores_pro = data_pro.to_dict("index")
    scores_pro = {m:list(scores.values())[0] for m, scores in metrics_scores_pro.items()}
    
    data_anti = pd.read_csv(file_scores_anti,index_col=[0])
    metrics_scores_anti = data_anti.to_dict("index")
    scores_anti = {m:list(scores.values())[0] for m, scores in metrics_scores_anti.items()}

    return [scores_pro[m] - scores_anti[m] for m in metrics]

def compare_gender(s,m):
    seg_metrics = ["Accuracy", "F1-score", "PPV","TPR","FDR","FPR","FOR","FNR","NPV","TNR"]
    diff_male_female = []
    diff_male_neutral = []
    diff_female_neutral = []

    file_scores_rates_seg = "test-WinoMT/tool_test-WinoMT/en_source.txt/pt_ref_" + s + ".txt/bias_evaluation/" + m + "/" + s + "/rates.csv"
    file_scores_f1_seg = "test-WinoMT/tool_test-WinoMT/en_source.txt/pt_ref_" + s + ".txt/bias_evaluation/" + m + "/analysis_labels_bucket/F1-score_groups_bias_metrics.csv"
    file_scores_accuracy_seg = "test-WinoMT/tool_test-WinoMT/en_source.txt/pt_ref_" + s + ".txt/bias_evaluation/" + m + "/analysis_labels_bucket/Accuracy_groups_bias_metrics.csv"
    genders = ["neutral", "female", "male"]

    data = pd.read_csv(file_scores_rates_seg,index_col=[0])
    seg_metrics_scores = data.to_dict("index")
    data_f1 = pd.read_csv(file_scores_f1_seg,index_col=[0])
    metrics_scores_f1 = data_f1.to_dict("index")[s]
    data_a = pd.read_csv(file_scores_accuracy_seg,index_col=[0])
    metrics_scores_a = data_a.to_dict("index")[s]

    for g in genders:
        seg_metrics_scores[g]["Accuracy"] = metrics_scores_a[g]
        seg_metrics_scores[g]["F1-score"] = metrics_scores_f1[g]

    for s_m in seg_metrics:
        diff_male_female.append(seg_metrics_scores["male"][s_m] - seg_metrics_scores["female"][s_m])
        diff_male_neutral.append(seg_metrics_scores["male"][s_m] - seg_metrics_scores["neutral"][s_m])
        diff_female_neutral.append(seg_metrics_scores["female"][s_m] - seg_metrics_scores["neutral"][s_m])

    return diff_male_female, diff_male_neutral, diff_female_neutral

def compare_systems(m):
    metrics = ["Demographic-Parity","Accuracy", "Precision","Recall", "F1-score"]
    file_scores_google = "test-WinoMT-Pro/tool_test-WinoMT-Pro/en_pro_source.txt/pt_pro_ref_google.txt/bias_evaluation/" + m + "/bias_scores.csv"
    file_scores_microsoft = "test-WinoMT-Anti/tool_test-WinoMT-Anti/en_anti_source.txt/pt_anti_ref_microsoft.txt/bias_evaluation/" + m + "/bias_scores.csv"

    data_google = pd.read_csv(file_scores_google,index_col=[0])
    metrics_scores_google = data_google.to_dict("index")
    scores_google = {m:list(scores.values())[0] for m, scores in metrics_scores_google.items()}
    
    data_microsoft = pd.read_csv(file_scores_microsoft,index_col=[0])
    metrics_scores_microsoft = data_microsoft.to_dict("index")
    scores_microsoft = {m:list(scores.values())[0] for m, scores in metrics_scores_microsoft.items()}

    return [scores_google[m] - scores_microsoft[m] for m in metrics]



if __name__ == "__main__":
    method = ["dictionary-based approach", "linguistic approach", "hybrid approach"]
    sys = ["google", "microsoft"]
    tp_fp_fn_gender = {"dictionary-based approach":[], "linguistic approach":[], "hybrid approach":[]}
    scores_pro_anti = {}
    times_method = {}
    scores_male_female = {}
    scores_male_neutral = {}
    scores_female_neutral = {}
    scores_sys = {}
    dataset_name = ["test-WinoMT (google)", "test-WinoMT-Pro (google)", "test-WinoMT-Anti (google)", 
                    "test-WinoMT (microsoft)", "test-WinoMT-Pro (microsoft)", "test-WinoMT-Anti (microsoft)"]
    metrics = ["Demographic-Parity","Accuracy", "Precision","Recall", "F1-score"]
    seg_metrics = ["Accuracy", "F1-score", "PPV","TPR","FDR","FPR","FOR","FNR","NPV","TNR"]

    for s in sys:
        print(Fore.GREEN + "-----------------------------------" + s + "-----------------------------------" )
        for m in method:
            print(Fore.WHITE)
            tp_fp_fn_gender[m] = identity_terms_found_info(s,m)
            scores_pro_anti[m] = compare_pro_anti(s,m)
            scores_male_female[m], scores_male_neutral[m], scores_female_neutral[m] = compare_gender(s,m)

        print(Fore.CYAN + "Identity Terms Found Table")
        print(Fore.WHITE)
        p_fp_fn_gender_pd = pd.DataFrame(tp_fp_fn_gender)
        p_fp_fn_gender_pd.index = ["Number of golden identity terms", "Number of identity terms found in tool", "TP", "FP", "FN", "Correct gender in TP", "Number of matchs"]
        print(p_fp_fn_gender_pd)
        print("\n")
        p_fp_fn_gender_pd.to_csv("data_evaluation/" + s.replace(" ","-") + "_identity_terms_found.csv")

        print(Fore.CYAN + "Scores Pro Anti Table")
        print(Fore.WHITE)
        scores_pro_anti_pd = pd.DataFrame(scores_pro_anti)
        scores_pro_anti_pd.index = metrics
        print(scores_pro_anti_pd)
        print("\n")
        scores_pro_anti_pd.to_csv("data_evaluation/" + s.replace(" ","-") + "_scores_pro_anti.csv")

        print(Fore.CYAN + "Scores Male Female Table")
        print(Fore.WHITE)
        scores_male_female_pd = pd.DataFrame(scores_male_female)
        scores_male_female_pd.index = seg_metrics
        print(scores_male_female_pd)
        print("\n")
        scores_male_female_pd.to_csv("data_evaluation/" + s.replace(" ","-") + "_scores_male_female.csv")

        print(Fore.CYAN + "Scores Male Neutral Table")
        print(Fore.WHITE)
        scores_male_neutral_pd = pd.DataFrame(scores_male_neutral)
        scores_male_neutral_pd.index = seg_metrics
        print(scores_male_neutral_pd)
        print("\n")
        scores_male_neutral_pd.to_csv("data_evaluation/" + s.replace(" ","-") + "_scores_male_neutral.csv")

        print(Fore.CYAN + "Scores Female Neutral Table")
        print(Fore.WHITE)
        scores_female_neutral_pd = pd.DataFrame(scores_female_neutral)
        scores_female_neutral_pd.index = seg_metrics
        print(scores_female_neutral_pd)
        print("\n")
        scores_female_neutral_pd.to_csv("data_evaluation/" + s.replace(" ","-") + "_scores_female_neutral.csv")
    
    
    for m in method:
        time = []
        names_datasets_time = []
        for s in sys:
            tp_fp_fn_gender[s] = identity_terms_found_info(s,m)
            time += time_bias_evlaution(s,m)
        times_method[m] = time 
        scores_sys[m] = compare_systems(m)

    print(Fore.CYAN + "Bias Evaluation Time")
    print(Fore.WHITE)
    pd_time = pd.DataFrame(times_method)
    pd_time.index = dataset_name
    print(pd_time)
    print("\n")
    pd_time.to_csv("data_evaluation/time_evaluation.csv")

    print(Fore.CYAN + "Scores Google Microsoft Table")
    print(Fore.WHITE)
    pd_sys = pd.DataFrame(scores_sys)
    pd_sys.index = metrics
    print(pd_sys)
    print("\n")
    pd_sys.to_csv("data_evaluation/scores_google_microsoft.csv")
    

