import os
from datasets import load_dataset
from nltk.tokenize import sent_tokenize
from transformers import pipeline, PreTrainedTokenizerFast, BartForConditionalGeneration, AutoTokenizer


def write_sents(filename:str,sents:list):
    file = open(filename, "w")
    for s in sents:
        file.writelines(s + " \n")
    file.close()
    return len(sents)

def write_file(file_name:str,text:str):
    f = open(file_name, "w")
    f.write(text)
    f.close()

dataset = load_dataset("cnn_dailymail", '3.0.0', split="test")

data = dataset.to_pandas()

article = data['article'].to_list()
highlights = data['highlights'].to_list()

num = len(article)
equal = 0
not_equal = 0

for i in range(num):
    if equal == 5 and not_equal == 5:
        break
    
    seg_src = sent_tokenize(article[i])
    seg_ref = sent_tokenize(highlights[i])
    
    model = BartForConditionalGeneration.from_pretrained("sshleifer/distilbart-cnn-12-6")
    tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
    inputs = tokenizer(article[i], return_tensors='pt')
    
    try:
        summary_text_ids = model.generate(
            input_ids=inputs["input_ids"],
            bos_token_id=model.config.bos_token_id,
            eos_token_id=model.config.eos_token_id,
            length_penalty=2.0,
            num_beams=4, 
            min_length=30, 
            max_length=130
            )
    except:
        continue
    text_distilbart = tokenizer.decode(summary_text_ids[0], skip_special_tokens=True)
    seg_output_large = sent_tokenize(text_distilbart)


    tokenizer = PreTrainedTokenizerFast.from_pretrained("ainize/bart-base-cnn")
    model = BartForConditionalGeneration.from_pretrained("ainize/bart-base-cnn")
    input_ids = tokenizer.encode(article[i], return_tensors="pt") 
    try:
        summary_text_ids = model.generate(
            input_ids=input_ids,
            bos_token_id=model.config.bos_token_id,
            eos_token_id=model.config.eos_token_id,
            length_penalty=2.0,
            max_length=130,
            min_length=30,
            num_beams=4,
        )
    except:
        continue
    text_base = tokenizer.decode(summary_text_ids[0], skip_special_tokens=True)
    seg_output_base = sent_tokenize(text_base)
    


    path = "_" + str(i+1) + "/"
    if len(seg_ref) == len(seg_output_base) and len(seg_ref) == len(seg_output_large) and equal != 5:
        if not os.path.exists(path):
            os.mkdir(path)
        write_sents(path + "src-article-" + str(i+1),seg_src)
        write_sents(path + "bart-large-cnn-" + str(i+1),seg_output_large)
        write_sents(path + "bart-base-cnn-" + str(i+1),seg_output_base)
        write_sents(path + "highlights-" + str(i+1),seg_ref)
        equal += 1
    
    elif (len(seg_ref) != len(seg_output_base) or len(seg_ref) != len(seg_output_large)) and not_equal != 5:
        if not os.path.exists(path):
            os.mkdir(path)
        write_sents(path + "src-article-" + str(i+1),seg_src)
        write_file(path + "distilbart-cnn-" + str(i+1),text_distilbart)
        write_file(path + "bart-base-cnn-" + str(i+1),text_base)
        write_file(path + "highlights-" + str(i+1),highlights[i])
        not_equal += 1
