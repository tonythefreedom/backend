from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from gensim.models.word2vec import Word2Vec
import json

test_str = 'burgerking'
test_str = test_str.lower()

#local path
#MODEL_PATH = "/Users/mac/model/gensim_model_skip_gram"
#TABLE_PATH = "/Users/mac/model/word_count_table.json"

#Server path
MODEL_PATH = "/usr/local/etc/django/model/gensim_model_skip_gram"
TABLE_PATH = "/usr/local/etc/django/model/word_count_table.json"

model = Word2Vec.load(MODEL_PATH)     #yelp review skip_gram으로 돌린 모델#
with open(TABLE_PATH) as f:
    term_frequencys = f.readlines()

######################################################################################
# return frequency function
######################################################################################
term_frequency_list = [json.loads(term_frequency, encoding = 'utf-8') for term_frequency in term_frequencys]
term_frequency_dict = term_frequency_list[0]

#return frequency function (input lower 전처리 추가해야함.)
def return_frequency(word):
    word = word.lower()
    frequency = 0
    try :
        frequency = term_frequency_dict[str(word)]
    except :
        frequency = frequency
    return frequency
#print(return_frequency('nicsdfe'))


######################################################################################
# input word -> similar word list return function(output : 2차원 리스트)
######################################################################################
def return_similar_word_list(word):
    similar_output_list = []
    xx = model.most_similar(positive = [str(word)], topn = 40)
    for i in xx:
        yy = i[0]
        similar_tem_list=[]
        similar_tem_list.append(yy)
        for j in xx:
            if model.similarity(yy, j[0]) >= 0.75:
                similar_tem_list.append(j[0])
                xx.remove(j)
        similar_output_list.append(similar_tem_list)
    return similar_output_list
#print(return_similar_word_list(test_str))


def return_similar_word_name(kb_list):
    similar_output_list_name = []
    for i in kb_list:
        similar_output_list_name.append(i[0])
    return similar_output_list_name



######################################################################################
# similar_word_list -> average frequency function (output: 1차원 리스트)
######################################################################################
def return_avg_frequency(word_list):
    similar_word_frequency = []
    for i in word_list:
        frequency_tem_list = []
        avg = 0
        for j in i:
            frequency_tem_list.append(return_frequency(j))
        avg = sum(frequency_tem_list) / len(frequency_tem_list)
        similar_word_frequency.append(int(avg))
    return(similar_word_frequency)

######################################################################################
# 리퀘스트 id 로 파라미터 보내기
######################################################################################

result = "no reasult"
def index(request):
    if request.GET["id"] == "nlp1" :
        out_list = []
        kb = return_similar_word_list(test_str)
        dic_name = return_similar_word_name(kb)
        dic_frequency = return_avg_frequency(kb)

        for i in range(len(dic_name)):
            out_dict = {}
            out_dict['name'] = dic_name[i]
            out_dict['frequency'] = dic_frequency[i]
            out_list.append(out_dict)

        result = json.dumps(out_list);
    elif request.GET["id"] == "nlp2" :
        result = "";
    return HttpResponse(result)