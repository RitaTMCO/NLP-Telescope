import sys

path = sys.argv[1] 
input_file_name = path + "/mapping.txt"
output_file_name = path + "/all_labels.txt"

input = open(input_file_name, "r")
data_input = input.read()
input.close()

output = open(output_file_name, "w")

list_data_input = data_input.split("\n")

for input in list_data_input:
    data = input.split("\t")
    if list_data_input[0] != input:
        output.writelines("\n" + str(data[0]))
    else:
        output.writelines(str(data[0]))
output.close()

