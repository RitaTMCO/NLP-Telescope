
import json

f = open('test_none.json')

test = json.load(f)

f.close()

i = 1
  
for data in test['data']:
    id = data["id"]
    context = data["context"]
    truth_answer = data["truth_answer"]
    model_answer = data["model_answer"]

    name_id = id.replace(".", "_")

    f = open("results/context/" + str(i) + "_" + name_id + "_context.txt", "w")
    for cont in context:
        f.write(cont + "\n")
    f.close()

    f = open("results/reference/" + str(i) + "_" + name_id + "_truth_answer.txt", "w")
    f.write(truth_answer.replace("SYSTEM: ", ""))
    f.close()

    f = open("results/answer/" + str(i) + "_" + name_id + "_model_answer.txt", "w")
    f.write(model_answer.replace("SYSTEM: ", ""))
    f.close()

    i += 1

print(i)
  
