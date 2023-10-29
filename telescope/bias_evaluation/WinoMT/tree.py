import spacy
from spacy import displacy

nlp = spacy.load('pt_core_news_lg')
doc_o = nlp('O mecânico deu um presente à balconista porque ela ganhou na loteria.')
displacy.serve(doc_o, style="dep")